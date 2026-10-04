"""Converte uma Bíblia em USFM (arquivo .zip) para o formato JSON do site: um arquivo por livro,
com o conteúdo [ { "capítulo": { "versículo": "texto" } } ].

Uso (na raiz do projeto):
    python ferramentas/converter_usfm.py CAMINHO_DO_ZIP SIGLA
    python ferramentas/converter_usfm.py baixados/poronbv_usfm.zip nbv      # grava em fonte/nbv/

Opções:
    --pasta CAMINHO   pasta das traduções (padrão: ./fonte)

O que a conversão faz com o texto:
  - mantém as palavras de cada versículo exatamente como estão no USFM;
  - junta as linhas de poesia e de lista de um mesmo versículo em um parágrafo só;
  - escreve em maiúsculas o nome divino marcado no USFM com \\nd (ex.: SENHOR);
  - NÃO inclui notas de rodapé, referências cruzadas, títulos de seção nem epígrafes dos Salmos.

Depois de converter: acrescente a tradução na tabela TRADUCOES de livros.py e rode o gerar.py.
"""
import argparse
import json
import os
import re
import sys
import zipfile

import livros

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA_FONTE = os.path.join(RAIZ, 'fonte')

# código USFM (GEN, EXO...) -> livro da tabela única (livros.py)
LIVRO_POR_CODIGO = {livro['usfm']: livro for livro in livros.LIVROS}

# linhas que não fazem parte do texto dos versículos (cabeçalhos, títulos, epígrafes, rótulos)
IGNORAR = re.compile(r'^\\(id|ide|h|toc\d?|mt\d?|ms\d?|mr|s\d?|sr|r|d|sp|qa|cl|rem|imt\d?|is\d?|ip|iot|io\d?|ie)\b')
NOTA = re.compile(r'\\(f|fe|x)\s.*?\\\1\*', re.S)                 # notas de rodapé e referências cruzadas
NOME_DIVINO = re.compile(r'\\\+?nd\s+(.*?)\\\+?nd\*', re.S)
MARCADOR = re.compile(r'\\\+?[a-z]+\d*\*?')                        # qualquer marcador que sobrar (\q1, \it*, ...)


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
    parser.add_argument('--pasta', default=PASTA_FONTE)
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    if not re.fullmatch(r'[a-z0-9_]+', args.sigla):
        print(f"Sigla inválida: '{args.sigla}'. Use só letras minúsculas sem acento, números e '_' (ex.: nbv).")
        return 1

    convertidos = {}      # código USFM -> capítulos do livro
    with zipfile.ZipFile(args.zip) as pacote:
        for nome in pacote.namelist():
            if not nome.lower().endswith(('.usfm', '.sfm', '.txt')):
                continue
            codigo, capitulos = converter_livro(pacote.read(nome).decode('utf-8-sig'))
            if codigo in LIVRO_POR_CODIGO and capitulos:
                convertidos[codigo] = capitulos

    faltando = [livro['nome'] for livro in livros.LIVROS if livro['usfm'] not in convertidos]
    if faltando:
        print("Livros não encontrados no pacote: " + ', '.join(faltando))
        return 1

    destino = os.path.join(args.pasta, args.sigla)
    os.makedirs(destino, exist_ok=True)
    total = 0
    for livro in livros.LIVROS:
        nome = livro['nome']
        capitulos = convertidos[livro['usfm']]
        vazios = [f"{cap}:{v}" for cap in capitulos for v, t in capitulos[cap].items() if not t]
        if vazios:
            print(f"Aviso: {nome} tem versículo(s) sem texto: {', '.join(vazios)}")
        total += sum(len(c) for c in capitulos.values())
        with open(os.path.join(destino, livro['slug'] + '.json'), 'w', encoding='utf-8', newline='') as f:
            f.write(json.dumps([capitulos], ensure_ascii=False, separators=(',', ':')))
    print(f"{len(livros.LIVROS)} livros gravados em {destino} ({total} versículos).")
    print(f"Confira com: python ferramentas/validar.py --pasta {args.pasta}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
