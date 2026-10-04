"""Confere a estrutura dos JSON da Bíblia. Não altera nada.

Uso (na raiz do projeto):
    python ferramentas/validar.py                    # confere todas as traduções em ./fonte
    python ferramentas/validar.py --pasta outra      # confere outra pasta
    python ferramentas/validar.py --gravar-contagens # regrava contagens.json com o estado atual

O que é conferido em cada tradução:
  - os 66 livros da tabela (livros.py) existem, com o nome exato <slug>.json, e são JSON válido;
  - não há arquivo .json sobrando (com nome fora da tabela);
  - capítulos numerados de 1 a N, sem buraco;
  - versículos numerados de 1 a N, sem buraco;
  - todo versículo é um texto não vazio, sem caracteres de controle, sem espaço nas pontas e sem "{{";
  - número de versículos de cada capítulo igual ao registrado em contagens.json (quando a tradução está lá).
Termina com código 0 se estiver tudo certo e 1 se houver problema (serve para automação).
O gerar.py chama esta conferência antes de gerar as páginas.
"""
import argparse
import json
import os
import re
import sys

import livros

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA_FONTE = os.path.join(RAIZ, 'fonte')
ARQUIVO_CONTAGENS = os.path.join(AQUI, 'contagens.json')

CONTROLE = re.compile(r'[\x00-\x1f\x7f-\x9f]')
SLUG = re.compile(r'^[a-z0-9_]+$')


def conferir_tabela():
    """Confere a própria tabela de livros.py. Devolve a lista de problemas."""
    problemas = []
    slugs = [livro['slug'] for livro in livros.LIVROS]
    siglas = [traducao['sigla'] for traducao in livros.TRADUCOES]
    if len(slugs) != 66:
        problemas.append(f"a tabela tem {len(slugs)} livros (esperado 66)")
    if livros.TOTAL_DE_CAPITULOS != 1189:
        problemas.append(f"a tabela soma {livros.TOTAL_DE_CAPITULOS} capítulos (esperado 1189)")
    for nome in slugs + siglas:
        if not SLUG.match(nome):
            problemas.append(f"'{nome}': slug/sigla só pode ter letras minúsculas sem acento, números e '_'")
    for nome in set(slugs + siglas):
        if (slugs + siglas).count(nome) > 1:
            problemas.append(f"'{nome}' aparece mais de uma vez na tabela")
    for livro in livros.LIVROS:
        if livro['testamento'] not in ('vt', 'nt'):
            problemas.append(f"'{livro['slug']}': testamento '{livro['testamento']}' (só vale 'vt' ou 'nt')")
    return problemas


def contagens_por_slug(esperado):
    """contagens.json pode trazer o nome do livro ("Gênesis") ou o slug ("genesis"): devolve tudo por slug."""
    por_slug = {}
    for nome, contagem in (esperado or {}).items():
        livro = livros.livro_pelo_nome(nome)
        if livro:
            por_slug[livro['slug']] = contagem
    return por_slug


def conferir_traducao(pasta, versao, esperado):
    """Devolve (problemas, contagens, total de versículos). 'esperado' são as contagens por slug."""
    problemas, contagens, total = [], {}, 0
    arquivos = set(os.listdir(os.path.join(pasta, versao)))     # nomes exatos, com maiúsculas/minúsculas
    conhecidos = {livro['slug'] + '.json' for livro in livros.LIVROS}
    for sobra in sorted(a for a in arquivos if a.lower().endswith('.json') and a not in conhecidos):
        problemas.append(f"{sobra}: arquivo com nome fora da tabela de livros")
    for livro in livros.LIVROS:
        nome, slug, n_caps = livro['nome'], livro['slug'], livro['capitulos']
        if slug + '.json' not in arquivos:
            problemas.append(f"{nome}: arquivo {slug}.json não encontrado")
            continue
        try:
            with open(os.path.join(pasta, versao, slug + '.json'), 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except (ValueError, UnicodeDecodeError) as erro:
            problemas.append(f"{nome}: JSON inválido ({erro})")
            continue
        capitulos = dados[0] if isinstance(dados, list) and len(dados) == 1 else dados
        if not isinstance(capitulos, dict):
            problemas.append(f"{nome}: formato inesperado na raiz do arquivo")
            continue
        if sorted(capitulos, key=lambda k: int(k) if k.isdigit() else 0) != [str(i) for i in range(1, n_caps + 1)]:
            problemas.append(f"{nome}: capítulos {len(capitulos)} (esperado 1 a {n_caps}, sem buraco)")
        contagens[slug] = []
        for cap in sorted((k for k in capitulos if k.isdigit()), key=int):
            versos = capitulos[cap]
            if not isinstance(versos, dict) or not versos:
                problemas.append(f"{nome} {cap}: capítulo vazio ou em formato inesperado")
                contagens[slug].append(0)
                continue
            if sorted(versos, key=lambda k: int(k) if k.isdigit() else 0) != [str(i) for i in range(1, len(versos) + 1)]:
                problemas.append(f"{nome} {cap}: numeração de versículos com buraco ou chave estranha")
            for verso, texto in versos.items():
                onde = f"{nome} {cap}:{verso}"
                if not isinstance(texto, str):
                    problemas.append(f"{onde}: valor não é texto ({type(texto).__name__})")
                elif not texto.strip():
                    problemas.append(f"{onde}: versículo vazio")
                elif CONTROLE.search(texto):
                    problemas.append(f"{onde}: caractere de controle ou quebra de linha no texto")
                elif texto != texto.strip():
                    problemas.append(f"{onde}: espaço no início ou no fim")
                elif '{{' in texto:
                    problemas.append(f"{onde}: o texto contém '{{{{', que é reservado aos marcadores do molde")
            contagens[slug].append(len(versos))
            total += len(versos)
        if slug in esperado and contagens[slug] != esperado[slug]:
            for i, (tem, quer) in enumerate(zip(contagens[slug], esperado[slug]), start=1):
                if tem != quer:
                    problemas.append(f"{nome} {i}: {tem} versículos (esperado {quer})")
    return problemas, contagens, total


def conferir_pasta(pasta=PASTA_FONTE, arquivo_contagens=ARQUIVO_CONTAGENS, so_da_tabela=False):
    """Confere a tabela e todas as traduções da pasta, imprimindo o resultado.

    Devolve (houve_problema, contagens). É a função que o gerar.py chama, com so_da_tabela=True:
    assim uma tradução ainda em preparo (pasta que não está em livros.py) não impede de gerar as outras.
    """
    houve_problema, novas = False, {}
    problemas_da_tabela = conferir_tabela()
    if problemas_da_tabela:
        houve_problema = True
        print("TABELA (livros.py): " + "; ".join(problemas_da_tabela))
    if not os.path.isdir(pasta):
        print(f"Pasta não encontrada: {pasta}")
        return True, novas

    esperado = {}
    if os.path.exists(arquivo_contagens):
        with open(arquivo_contagens, 'r', encoding='utf-8') as f:
            esperado = json.load(f)

    # pastas que começam com ponto (.idea, .git...) não são traduções
    versoes = sorted(d for d in os.listdir(pasta)
                     if os.path.isdir(os.path.join(pasta, d)) and not d.startswith('.'))
    siglas = [traducao['sigla'] for traducao in livros.TRADUCOES]
    eh_a_fonte = os.path.abspath(pasta) == os.path.abspath(PASTA_FONTE)
    for sigla in siglas:
        if sigla not in versoes and eh_a_fonte:     # só a fonte/ do site precisa ter todas as traduções da tabela
            houve_problema = True
            print(f"{sigla.upper()}: está na tabela de traduções (livros.py), mas a pasta {sigla}/ não existe")
    for versao in versoes:
        if so_da_tabela and versao not in siglas:
            print(f"{versao.upper()}: não está na tabela de traduções (livros.py): não foi conferida e não terá páginas")
            continue
        problemas, contagens, total = conferir_traducao(pasta, versao, contagens_por_slug(esperado.get(versao)))
        novas[versao] = contagens
        referencia = "" if versao in esperado else " (sem contagem de referência: só a estrutura foi conferida)"
        if problemas:
            houve_problema = True
            print(f"{versao.upper()}: {len(problemas)} problema(s) em {total} versículos{referencia}")
            for p in problemas[:60]:
                print("   - " + p)
            if len(problemas) > 60:
                print(f"   ... e mais {len(problemas) - 60}")
        else:
            print(f"{versao.upper()}: tudo certo — 66 livros, {livros.TOTAL_DE_CAPITULOS} capítulos, "
                  f"{total} versículos{referencia}")
        if versao not in siglas:
            print(f"   aviso: {versao}/ não está na tabela de traduções (livros.py); o gerar.py não gera páginas dela")
    return houve_problema, novas


def main():
    parser = argparse.ArgumentParser(description="Confere a estrutura dos JSON da Bíblia.")
    parser.add_argument('--pasta', default=PASTA_FONTE, help="pasta com as traduções (padrão: fonte)")
    parser.add_argument('--contagens', default=ARQUIVO_CONTAGENS)
    parser.add_argument('--gravar-contagens', action='store_true',
                        help="grava em contagens.json o número de versículos atual de cada capítulo")
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    houve_problema, novas = conferir_pasta(args.pasta, args.contagens)

    if args.gravar_contagens:
        if houve_problema:
            print("Contagens NÃO gravadas, porque há problemas acima.")
        else:
            with open(args.contagens, 'w', encoding='utf-8') as f:
                json.dump(novas, f, ensure_ascii=False, separators=(',', ':'))
            print(f"Contagens gravadas em {args.contagens}")
    return 1 if houve_problema else 0


if __name__ == '__main__':
    sys.exit(main())
