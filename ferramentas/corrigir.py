"""Aplica a errata da auditoria nos JSON da Bíblia (ACF, ARA e NAA).

Uso (na raiz do projeto):
    python ferramentas/corrigir.py --simular     # só mostra o que seria feito, não grava nada
    python ferramentas/corrigir.py               # aplica e grava os arquivos

Opções:
    --pasta CAMINHO       pasta que contém acf/, ara/, naa/ (padrão: ./fonte)
    --correcoes ARQUIVO   lista de correções (padrão: correcoes.json ao lado deste script)

O script é seguro para rodar mais de uma vez: o que já foi corrigido é reconhecido e pulado.
Se qualquer correção não encaixar no texto, nada é gravado e o problema é listado.
Depois de corrigir, rode o gerar.py para refazer as páginas do site.
"""
import argparse
import json
import os
import re
import sys
import unicodedata

import livros

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA_FONTE = os.path.join(RAIZ, 'fonte')

SLUGS = [livro['slug'] for livro in livros.LIVROS]                 # os 66 livros, na ordem da Bíblia
NOME = {livro['slug']: livro['nome'] for livro in livros.LIVROS}   # slug -> nome exibido

LETRAS_HEBRAICAS = ("Álefe|Bete|Guímel|Dálete|Hê|Vau|Zaine|Hete|Tete|Iode|Cafe|Lâmede|Mem|Num|"
                    "Sâmeque|Aim|Pê|Tsadê|Cofe|Rexe|Chim|Tau")


def sem_acento(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


class Biblia:
    """Carrega os livros de uma tradução sob demanda e lembra quais foram alterados."""

    def __init__(self, pasta, versao):
        self.pasta = os.path.join(pasta, versao)
        self.versao = versao
        self.livros = {}      # slug do livro -> dicionário {capítulo: {versículo: texto}}
        self.caminhos = {}
        self.originais = {}
        self.alterados = set()

    def existe(self):
        return os.path.isdir(self.pasta)

    def livro(self, slug):
        if slug not in self.livros:
            caminho = os.path.join(self.pasta, slug + '.json')
            if not os.path.exists(caminho):
                raise FileNotFoundError(f"{self.versao}: arquivo {slug}.json não encontrado em {self.pasta}")
            with open(caminho, 'r', encoding='utf-8') as f:
                bruto = f.read()
            dados = json.loads(bruto)
            self.livros[slug] = dados[0] if isinstance(dados, list) else dados
            self.caminhos[slug] = caminho
            self.originais[slug] = bruto
        return self.livros[slug]

    def marcar(self, slug):
        self.alterados.add(slug)

    def gravar(self):
        gravados = 0
        for slug in sorted(self.alterados):
            texto = json.dumps([self.livros[slug]], ensure_ascii=False, separators=(',', ':'))
            if texto != self.originais[slug]:
                with open(self.caminhos[slug], 'w', encoding='utf-8', newline='') as f:
                    f.write(texto)
                gravados += 1
        return gravados


def ordenar(capitulo):
    """Devolve o capítulo com as chaves em ordem numérica."""
    return {k: capitulo[k] for k in sorted(capitulo, key=int)}


# ---------------------------------------------------------------- correções de estrutura

def mover_versiculos_em_lista(biblia, rel):
    """Versículo gravado como lista [a, b]: 'a' é o fim do capítulo anterior; 'b' é o versículo de verdade."""
    for slug in SLUGS:
        nome = NOME[slug]
        livro = biblia.livro(slug)
        for cap in sorted(livro, key=int):
            for verso in sorted(livro[cap], key=int):
                valor = livro[cap][verso]
                if isinstance(valor, list):
                    if len(valor) != 2 or not all(isinstance(x, str) for x in valor) or int(cap) < 2:
                        rel.erro(f"{biblia.versao} {nome} {cap}:{verso}: lista em formato inesperado")
                        continue
                    anterior = livro[str(int(cap) - 1)]
                    novo = str(max(int(k) for k in anterior) + 1)
                    anterior[novo] = valor[0]
                    livro[cap][verso] = valor[1]
                    biblia.marcar(slug)
                    rel.feito(f"{biblia.versao} {nome} {int(cap) - 1}:{novo} recuperado de dentro de {cap}:{verso}")


def mover_versiculo(biblia, rel, slug, cap_errado, verso_errado, cap_certo, verso_certo):
    """Versículo que foi parar no fim do capítulo seguinte (NAA 2 Samuel 22:51 gravado como 23:40)."""
    nome = NOME[slug]
    livro = biblia.livro(slug)
    if verso_certo in livro[cap_certo]:
        return rel.pulado(f"{biblia.versao} {nome} {cap_certo}:{verso_certo} já está no lugar")
    if verso_errado not in livro[cap_errado] or str(int(verso_certo) - 1) not in livro[cap_certo]:
        return rel.erro(f"{biblia.versao} {nome}: estado inesperado ao mover {cap_errado}:{verso_errado}")
    livro[cap_certo][verso_certo] = livro[cap_errado].pop(verso_errado)
    biblia.marcar(slug)
    rel.feito(f"{biblia.versao} {nome} {cap_errado}:{verso_errado} movido para {cap_certo}:{verso_certo}")


def remover_primeiro_duplicado(biblia, rel, slug, cap, total_certo):
    """Capítulo cujo v.1 foi gravado duas vezes (ACF Salmos 63 e 122): apaga a 1ª cópia e renumera."""
    nome = NOME[slug]
    capitulo = biblia.livro(slug)[cap]
    if len(capitulo) == total_certo:
        return rel.pulado(f"{biblia.versao} {nome} {cap} já tem {total_certo} versículos")
    simples = lambda t: re.sub(r'[^a-z]', '', sem_acento(t).lower())
    if len(capitulo) != total_certo + 1 or simples(capitulo['1']) != simples(capitulo['2']):
        return rel.erro(f"{biblia.versao} {nome} {cap}: estado inesperado (esperava v.1 duplicado)")
    biblia.livro(slug)[cap] = {str(int(k) - 1): capitulo[k] for k in sorted(capitulo, key=int) if k != '1'}
    biblia.marcar(slug)
    rel.feito(f"{biblia.versao} {nome} {cap}: v.1 duplicado removido; capítulo renumerado ({total_certo} versículos)")


def recolocar_letras_de_lamentacoes(biblia, rel):
    """NAA: a letra hebraica de cada estrofe ficou no fim do versículo anterior ('... forçados! Bete —')."""
    slug = "lamentacoes"
    nome = NOME[slug]
    livro = biblia.livro(slug)
    padrao = re.compile(r' (' + LETRAS_HEBRAICAS + r') —$')
    movidas = 0
    for cap in ('1', '2', '3', '4'):
        for verso in sorted(livro[cap], key=int):
            achou = padrao.search(livro[cap][verso])
            if not achou:
                continue
            seguinte = str(int(verso) + 1)
            if seguinte not in livro[cap]:
                rel.erro(f"{biblia.versao} {nome} {cap}:{verso}: letra no último versículo do capítulo")
                continue
            livro[cap][verso] = livro[cap][verso][:achou.start()]
            livro[cap][seguinte] = f"{achou.group(1)} — {livro[cap][seguinte]}"
            movidas += 1
    if movidas:
        biblia.marcar(slug)
        rel.feito(f"{biblia.versao} {nome}: {movidas} letras hebraicas recolocadas no início da estrofe certa")
    else:
        rel.pulado(f"{biblia.versao} {nome}: letras hebraicas já estão no lugar")


def corrigir_estrutura(biblias, rel):
    if 'naa' in biblias:
        mover_versiculos_em_lista(biblias['naa'], rel)
        mover_versiculo(biblias['naa'], rel, "2_samuel", '23', '40', '22', '51')
        recolocar_letras_de_lamentacoes(biblias['naa'], rel)
    if 'acf' in biblias:
        remover_primeiro_duplicado(biblias['acf'], rel, "salmos", '63', 11)
        remover_primeiro_duplicado(biblias['acf'], rel, "salmos", '122', 9)
    for biblia in biblias.values():
        for slug in list(biblia.alterados):
            livro = biblia.livro(slug)
            for cap in livro:
                livro[cap] = ordenar(livro[cap])


# ---------------------------------------------------------------- correções de texto

def aplicar_globais(biblias, regras, rel):
    """Troca uma palavra em toda a tradução. A contagem tem de bater com a esperada."""
    for regra in regras:
        biblia = biblias.get(regra['versao'])
        if biblia is None:
            continue
        lugares = []
        for slug in SLUGS:
            livro = biblia.livro(slug)
            for cap in livro:
                for verso, texto in livro[cap].items():
                    if isinstance(texto, str) and regra['de'] in texto:
                        lugares.append((slug, cap, verso, texto.count(regra['de'])))
        total = sum(n for _, _, _, n in lugares)
        rotulo = f"{regra['versao']} «{regra['de']}» → «{regra['para']}»"
        if total == 0:
            rel.pulado(f"{rotulo}: nenhuma ocorrência (já corrigido)")
        elif total != regra['esperado']:
            rel.erro(f"{rotulo}: encontrei {total} ocorrências, esperava {regra['esperado']}")
        else:
            for slug, cap, verso, _ in lugares:
                livro = biblia.livro(slug)
                livro[cap][verso] = livro[cap][verso].replace(regra['de'], regra['para'])
                biblia.marcar(slug)
            rel.feito(f"{rotulo}: {total} ocorrências")


def trecho_alterado(antes, depois, contexto=18):
    """Recorta só o miolo que muda entre os dois textos, para o relatório."""
    i = 0
    while i < min(len(antes), len(depois)) and antes[i] == depois[i]:
        i += 1
    j = 0
    while j < min(len(antes), len(depois)) - i and antes[-1 - j] == depois[-1 - j]:
        j += 1
    a, b = max(0, i - contexto), contexto - j
    corte = lambda t: t[a:len(t) + b if b < 0 else len(t)]
    return corte(antes), corte(depois)


def aplicar_pontuais(biblias, correcoes, rel):
    """Troca o texto de um versículo. Só troca se o versículo estiver exatamente como a auditoria o encontrou."""
    for c in correcoes:
        biblia = biblias.get(c['versao'])
        if biblia is None:
            continue
        onde = f"{c['versao']} {c['livro']} {c['cap']}:{c['verso']}"
        livro = livros.livro_pelo_nome(c['livro'])     # correcoes.json usa o nome do livro (inclusive nomes antigos)
        if livro is None:
            rel.erro(f"{onde}: livro desconhecido (não está na tabela de livros.py)")
            continue
        slug = livro['slug']
        texto = biblia.livro(slug).get(c['cap'], {}).get(c['verso'])
        if texto == c['antes']:
            biblia.livro(slug)[c['cap']][c['verso']] = c['depois']
            biblia.marcar(slug)
            de, para = trecho_alterado(c['antes'], c['depois'])
            rel.feito(f"{onde}: «{de}» → «{para}»", detalhe=True)
        elif texto == c['depois']:
            rel.pulado(f"{onde}: já corrigido", detalhe=True)
        elif texto is None:
            rel.erro(f"{onde}: versículo não encontrado")
        else:
            rel.erro(f"{onde}: o versículo não está como a auditoria o encontrou (foi editado à mão?)")


class Relatorio:
    def __init__(self, detalhado):
        self.detalhado = detalhado
        self.feitos = 0
        self.pulados = 0
        self.erros = []

    def feito(self, msg, detalhe=False):
        self.feitos += 1
        if self.detalhado or not detalhe:
            print("  [ok]   " + msg)

    def pulado(self, msg, detalhe=False):
        self.pulados += 1
        if self.detalhado or not detalhe:
            print("  [pulo] " + msg)

    def erro(self, msg):
        self.erros.append(msg)
        print("  [ERRO] " + msg)


def main():
    parser = argparse.ArgumentParser(description="Aplica a errata da auditoria nos JSON da Bíblia.")
    parser.add_argument('--pasta', default=PASTA_FONTE, help="pasta com acf/, ara/, naa/ (padrão: fonte)")
    parser.add_argument('--correcoes', default=os.path.join(AQUI, 'correcoes.json'))
    parser.add_argument('--simular', action='store_true', help="não grava nada; só mostra o que seria feito")
    parser.add_argument('--detalhado', action='store_true', help="lista cada correção de texto, uma por linha")
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    with open(args.correcoes, 'r', encoding='utf-8') as f:
        correcoes = json.load(f)

    biblias = {}
    for versao in ('acf', 'ara', 'naa'):
        biblia = Biblia(args.pasta, versao)
        if biblia.existe():
            biblias[versao] = biblia
        else:
            print(f"Aviso: pasta {biblia.pasta} não encontrada; tradução {versao.upper()} ignorada.")
    if not biblias:
        print("Nenhuma tradução encontrada. Confira se a pasta fonte/ existe ou informe --pasta.")
        return 1

    rel = Relatorio(args.detalhado)
    print("1) Estrutura (versículos fora do lugar)")
    corrigir_estrutura(biblias, rel)
    print("2) Trocas em toda a tradução")
    aplicar_globais(biblias, correcoes['globais'], rel)
    print("3) Correções pontuais de texto")
    aplicar_pontuais(biblias, correcoes['pontuais'], rel)

    print()
    print(f"Correções aplicadas: {rel.feitos} | já estavam corrigidas: {rel.pulados} | erros: {len(rel.erros)}")
    if rel.erros:
        print("Nada foi gravado, porque houve erro. Confira as linhas marcadas com [ERRO].")
        return 1
    if args.simular:
        print("Simulação: nenhum arquivo foi alterado. Rode sem --simular para gravar.")
        return 0
    total = sum(b.gravar() for b in biblias.values())
    print(f"Arquivos gravados: {total}. Agora rode: python ferramentas/gerar.py (confere e refaz as páginas)")
    return 0


if __name__ == '__main__':
    sys.exit(main())
