"""Confere a estrutura dos JSON da Bíblia. Não altera nada.

Uso (na raiz do projeto):
    python ferramentas/validar.py                    # confere todas as traduções em ./biblia
    python ferramentas/validar.py --pasta fonte      # confere outra pasta
    python ferramentas/validar.py --gravar-contagens # regrava contagens.json com o estado atual

O que é conferido em cada tradução:
  - os 66 livros existem e são JSON válido;
  - capítulos numerados de 1 a N, sem buraco;
  - versículos numerados de 1 a N, sem buraco;
  - todo versículo é um texto não vazio, sem caracteres de controle e sem espaço nas pontas;
  - número de versículos de cada capítulo igual ao registrado em contagens.json (quando a tradução está lá).
Termina com código 0 se estiver tudo certo e 1 se houver problema (serve para automação).
"""
import argparse
import json
import os
import re
import sys
import unicodedata

LIVROS = [
    "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
    "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias",
    "Ester", "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cânticos", "Isaías", "Jeremias",
    "Lamentações de Jeremias", "Ezequiel", "Daniel", "Oséias", "Joel", "Amós", "Obadias", "Jonas",
    "Miquéias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias",
    "Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios",
    "Gálatas", "Efésios", "Filipenses", "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses",
    "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago", "1 Pedro", "2 Pedro",
    "1 João", "2 João", "3 João", "Judas", "Apocalipse",
]
CAPITULOS = [50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42, 150, 31, 12, 8, 66, 52, 5,
             48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4, 28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4,
             3, 1, 13, 5, 5, 3, 5, 1, 1, 1, 22]
CONTROLE = re.compile(r'[\x00-\x1f\x7f-\x9f]')


def sem_acento(texto):
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')


def achar_arquivo(pasta, livro):
    base = sem_acento(livro).lower()
    nomes = [base + '.json', base.replace(' ', '_') + '.json']
    if livro == "Lamentações de Jeremias":
        nomes.append('lamentacoes.json')
    for nome in nomes:
        caminho = os.path.join(pasta, nome)
        if os.path.exists(caminho):
            return caminho
    return None


def conferir_traducao(pasta, versao, esperado):
    """Devolve (problemas, contagens, total de versículos)."""
    problemas, contagens, total = [], {}, 0
    for livro, n_caps in zip(LIVROS, CAPITULOS):
        caminho = achar_arquivo(os.path.join(pasta, versao), livro)
        if caminho is None:
            problemas.append(f"{livro}: arquivo não encontrado")
            continue
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except (ValueError, UnicodeDecodeError) as erro:
            problemas.append(f"{livro}: JSON inválido ({erro})")
            continue
        capitulos = dados[0] if isinstance(dados, list) and len(dados) == 1 else dados
        if not isinstance(capitulos, dict):
            problemas.append(f"{livro}: formato inesperado na raiz do arquivo")
            continue
        if sorted(capitulos, key=lambda k: int(k) if k.isdigit() else 0) != [str(i) for i in range(1, n_caps + 1)]:
            problemas.append(f"{livro}: capítulos {len(capitulos)} (esperado 1 a {n_caps}, sem buraco)")
        contagens[livro] = []
        for cap in sorted((k for k in capitulos if k.isdigit()), key=int):
            versos = capitulos[cap]
            if not isinstance(versos, dict) or not versos:
                problemas.append(f"{livro} {cap}: capítulo vazio ou em formato inesperado")
                contagens[livro].append(0)
                continue
            if sorted(versos, key=lambda k: int(k) if k.isdigit() else 0) != [str(i) for i in range(1, len(versos) + 1)]:
                problemas.append(f"{livro} {cap}: numeração de versículos com buraco ou chave estranha")
            for verso, texto in versos.items():
                onde = f"{livro} {cap}:{verso}"
                if not isinstance(texto, str):
                    problemas.append(f"{onde}: valor não é texto ({type(texto).__name__})")
                elif not texto.strip():
                    problemas.append(f"{onde}: versículo vazio")
                elif CONTROLE.search(texto):
                    problemas.append(f"{onde}: caractere de controle ou quebra de linha no texto")
                elif texto != texto.strip():
                    problemas.append(f"{onde}: espaço no início ou no fim")
            contagens[livro].append(len(versos))
            total += len(versos)
        if esperado and livro in esperado and contagens[livro] != esperado[livro]:
            for i, (tem, quer) in enumerate(zip(contagens[livro], esperado[livro]), start=1):
                if tem != quer:
                    problemas.append(f"{livro} {i}: {tem} versículos (esperado {quer})")
    return problemas, contagens, total


def main():
    aqui = os.path.dirname(os.path.abspath(__file__))
    parser = argparse.ArgumentParser(description="Confere a estrutura dos JSON da Bíblia.")
    parser.add_argument('--pasta', default='biblia', help="pasta com as traduções (padrão: biblia)")
    parser.add_argument('--contagens', default=os.path.join(aqui, 'contagens.json'))
    parser.add_argument('--gravar-contagens', action='store_true',
                        help="grava em contagens.json o número de versículos atual de cada capítulo")
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    if not os.path.isdir(args.pasta):
        print(f"Pasta não encontrada: {args.pasta}")
        return 1
    esperado = {}
    if os.path.exists(args.contagens):
        with open(args.contagens, 'r', encoding='utf-8') as f:
            esperado = json.load(f)

    versoes = sorted(d for d in os.listdir(args.pasta) if os.path.isdir(os.path.join(args.pasta, d)))
    houve_problema, novas = False, {}
    for versao in versoes:
        problemas, contagens, total = conferir_traducao(args.pasta, versao, esperado.get(versao))
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
            print(f"{versao.upper()}: tudo certo — 66 livros, {sum(CAPITULOS)} capítulos, {total} versículos{referencia}")

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
