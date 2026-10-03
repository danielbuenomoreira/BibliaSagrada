"""Converte uma Bíblia em USFM (arquivo .zip) para o formato JSON do site: um arquivo por livro,
com o conteúdo [ { "capítulo": { "versículo": "texto" } } ].

Uso (na raiz do projeto):
    python ferramentas/converter_usfm.py CAMINHO_DO_ZIP SIGLA
    python ferramentas/converter_usfm.py baixados/poronbv_usfm.zip nbv      # grava em biblia/nbv/

Opções:
    --pasta CAMINHO   pasta das traduções (padrão: ./biblia)

O que a conversão faz com o texto:
  - mantém as palavras de cada versículo exatamente como estão no USFM;
  - junta as linhas de poesia e de lista de um mesmo versículo em um parágrafo só;
  - escreve em maiúsculas o nome divino marcado no USFM com \\nd (ex.: SENHOR);
  - NÃO inclui notas de rodapé, referências cruzadas, títulos de seção nem epígrafes dos Salmos.
"""
import argparse
import json
import os
import re
import sys
import unicodedata
import zipfile

# código USFM de cada livro -> nome usado no site, na ordem do cânon protestante
LIVROS = [
    ("GEN", "Gênesis"), ("EXO", "Êxodo"), ("LEV", "Levítico"), ("NUM", "Números"), ("DEU", "Deuteronômio"),
    ("JOS", "Josué"), ("JDG", "Juízes"), ("RUT", "Rute"), ("1SA", "1 Samuel"), ("2SA", "2 Samuel"),
    ("1KI", "1 Reis"), ("2KI", "2 Reis"), ("1CH", "1 Crônicas"), ("2CH", "2 Crônicas"), ("EZR", "Esdras"),
    ("NEH", "Neemias"), ("EST", "Ester"), ("JOB", "Jó"), ("PSA", "Salmos"), ("PRO", "Provérbios"),
    ("ECC", "Eclesiastes"), ("SNG", "Cânticos"), ("ISA", "Isaías"), ("JER", "Jeremias"),
    ("LAM", "Lamentações de Jeremias"), ("EZK", "Ezequiel"), ("DAN", "Daniel"), ("HOS", "Oséias"),
    ("JOL", "Joel"), ("AMO", "Amós"), ("OBA", "Obadias"), ("JON", "Jonas"), ("MIC", "Miquéias"),
    ("NAM", "Naum"), ("HAB", "Habacuque"), ("ZEP", "Sofonias"), ("HAG", "Ageu"), ("ZEC", "Zacarias"),
    ("MAL", "Malaquias"), ("MAT", "Mateus"), ("MRK", "Marcos"), ("LUK", "Lucas"), ("JHN", "João"),
    ("ACT", "Atos"), ("ROM", "Romanos"), ("1CO", "1 Coríntios"), ("2CO", "2 Coríntios"), ("GAL", "Gálatas"),
    ("EPH", "Efésios"), ("PHP", "Filipenses"), ("COL", "Colossenses"), ("1TH", "1 Tessalonicenses"),
    ("2TH", "2 Tessalonicenses"), ("1TI", "1 Timóteo"), ("2TI", "2 Timóteo"), ("TIT", "Tito"),
    ("PHM", "Filemom"), ("HEB", "Hebreus"), ("JAS", "Tiago"), ("1PE", "1 Pedro"), ("2PE", "2 Pedro"),
    ("1JN", "1 João"), ("2JN", "2 João"), ("3JN", "3 João"), ("JUD", "Judas"), ("REV", "Apocalipse"),
]
NOME = dict(LIVROS)

# linhas que não fazem parte do texto dos versículos (cabeçalhos, títulos, epígrafes, rótulos)
IGNORAR = re.compile(r'^\\(id|ide|h|toc\d?|mt\d?|ms\d?|mr|s\d?|sr|r|d|sp|qa|cl|rem|imt\d?|is\d?|ip|iot|io\d?|ie)\b')
NOTA = re.compile(r'\\(f|fe|x)\s.*?\\\1\*', re.S)                 # notas de rodapé e referências cruzadas
NOME_DIVINO = re.compile(r'\\\+?nd\s+(.*?)\\\+?nd\*', re.S)
MARCADOR = re.compile(r'\\\+?[a-z]+\d*\*?')                        # qualquer marcador que sobrar (\q1, \it*, ...)


def nome_do_arquivo(livro):
    base = ''.join(c for c in unicodedata.normalize('NFD', livro) if unicodedata.category(c) != 'Mn')
    return base.lower() + '.json'


def limpar(texto):
    texto = NOTA.sub('', texto)
    texto = NOME_DIVINO.sub(lambda m: m.group(1).upper(), texto)
    texto = MARCADOR.sub(' ', texto)
    return re.sub(r'\s+', ' ', texto).strip()


def converter_livro(usfm):
    """Devolve (código USFM, {capítulo: {versículo: texto}})."""
    codigo, capitulos, cap, verso = None, {}, None, None
    for linha in usfm.splitlines():
        linha = linha.strip()
        if not linha:
            continue
        if linha.startswith('\\id '):
            codigo = linha.split()[1].upper()
            continue
        achou = re.match(r'^\\c\s+(\d+)', linha)
        if achou:
            cap, verso = achou.group(1), None
            capitulos[cap] = {}
            continue
        if IGNORAR.match(linha):
            continue
        achou = re.match(r'^\\v\s+(\S+)\s*(.*)$', linha)
        if achou:
            verso = achou.group(1)
            if not verso.isdigit():
                raise ValueError(f"{codigo} {cap}:{verso}: numeração de versículo não suportada")
            if verso in capitulos[cap]:
                raise ValueError(f"{codigo} {cap}:{verso}: versículo repetido")
            capitulos[cap][verso] = achou.group(2)
        elif cap is not None and verso is not None:
            # continuação do versículo em outra linha (poesia, lista, novo parágrafo)
            resto = re.sub(r'^\\\+?[a-z]+\d*\s*', '', linha) if linha.startswith('\\') else linha
            if '\\v ' in resto:
                raise ValueError(f"{codigo} {cap}: marcador de versículo no meio da linha")
            capitulos[cap][verso] += ' ' + resto
    for cap in capitulos:
        capitulos[cap] = {v: limpar(t) for v, t in capitulos[cap].items()}
    return codigo, capitulos


def main():
    parser = argparse.ArgumentParser(description="Converte uma Bíblia em USFM (.zip) para o JSON do site.")
    parser.add_argument('zip')
    parser.add_argument('sigla', help="nome da pasta da tradução, em minúsculas (ex.: nbv)")
    parser.add_argument('--pasta', default='biblia')
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    livros = {}
    with zipfile.ZipFile(args.zip) as pacote:
        for nome in pacote.namelist():
            if not nome.lower().endswith(('.usfm', '.sfm', '.txt')):
                continue
            codigo, capitulos = converter_livro(pacote.read(nome).decode('utf-8-sig'))
            if codigo in NOME and capitulos:
                livros[codigo] = capitulos

    faltando = [nome for codigo, nome in LIVROS if codigo not in livros]
    if faltando:
        print("Livros não encontrados no pacote: " + ', '.join(faltando))
        return 1

    destino = os.path.join(args.pasta, args.sigla)
    os.makedirs(destino, exist_ok=True)
    total = 0
    for codigo, nome in LIVROS:
        capitulos = livros[codigo]
        vazios = [f"{cap}:{v}" for cap in capitulos for v, t in capitulos[cap].items() if not t]
        if vazios:
            print(f"Aviso: {nome} tem versículo(s) sem texto: {', '.join(vazios)}")
        total += sum(len(c) for c in capitulos.values())
        with open(os.path.join(destino, nome_do_arquivo(nome)), 'w', encoding='utf-8', newline='') as f:
            f.write(json.dumps([capitulos], ensure_ascii=False, separators=(',', ':')))
    print(f"{len(LIVROS)} livros gravados em {destino} ({total} versículos).")
    print(f"Confira com: python ferramentas/validar.py --pasta {args.pasta}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
