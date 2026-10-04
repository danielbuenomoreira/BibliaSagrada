"""Confere os links das páginas do site. Não altera nada.

Uso (na raiz do projeto):
    python ferramentas/verificar_links.py

Em cada página (index.html, 404.html e tudo o que está em biblia/), confere que todo href="...",
src="..." e action="..." aponta para um arquivo que existe, com o nome EXATO, inclusive maiúsculas e
minúsculas. No Windows, "Joao/3.html" e "joao/3.html" abrem o mesmo arquivo; no GitHub Pages, não:
um link com a caixa errada funciona no seu computador e quebra depois de publicado.
Confere também que as âncoras (#conteudo, #v16...) existem na página de destino.

Termina com código 0 se estiver tudo certo e 1 se houver problema. O gerar.py chama esta conferência
no fim da geração completa.
"""
import os
import posixpath
import re
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

LINK = re.compile(r'\s(?:href|src|action)="([^"]*)"')
IDENTIFICADOR = re.compile(r'\sid="([^"]*)"')
ENDERECO_EXTERNO = re.compile(r'^[a-zA-Z][a-zA-Z0-9+.-]*:')      # http:, https:, mailto:, data:...
PASTAS_IGNORADAS = ('.git', '.idea', '__pycache__')

# A página 404 é servida pelo GitHub Pages em qualquer endereço, por isso os links dela são absolutos
# e começam pelo nome do repositório: /BibliaSagrada/index.html. Aqui esse começo é descontado.
PAGINAS_COM_LINK_ABSOLUTO = ('404.html',)


def arquivos_do_projeto():
    """Conjunto com o caminho exato de cada arquivo do projeto, a partir da raiz e com '/'."""
    existentes = set()
    for atual, pastas, arquivos in os.walk(RAIZ):
        pastas[:] = [p for p in pastas if p not in PASTAS_IGNORADAS]
        for nome in arquivos:
            existentes.add(os.path.relpath(os.path.join(atual, nome), RAIZ).replace(os.sep, '/'))
    return existentes


def paginas_do_site(existentes):
    """As páginas publicadas: as da raiz e as de biblia/ (o molde em ferramentas/ não é página)."""
    return sorted(a for a in existentes
                  if a.endswith('.html') and ('/' not in a or a.startswith('biblia/')))


def ids_da_pagina(pagina, guardados):
    """Conjunto dos id="..." de uma página (lido uma vez só e guardado)."""
    if pagina not in guardados:
        with open(os.path.join(RAIZ, pagina), 'r', encoding='utf-8') as f:
            guardados[pagina] = set(IDENTIFICADOR.findall(f.read()))
    return guardados[pagina]


def conferir_pagina(pagina, existentes, guardados):
    """Devolve (quantidade de links conferidos, lista de problemas) de uma página."""
    with open(os.path.join(RAIZ, pagina), 'r', encoding='utf-8') as f:
        texto = f.read()
    guardados[pagina] = set(IDENTIFICADOR.findall(texto))
    conferidos, problemas = 0, []
    for endereco in LINK.findall(texto):
        if ENDERECO_EXTERNO.match(endereco):
            continue                                  # link para outro site: não é conferido aqui
        conferidos += 1
        sem_ancora, _, ancora = endereco.partition('#')
        arquivo = sem_ancora.partition('?')[0]
        if arquivo.startswith('/'):
            if pagina not in PAGINAS_COM_LINK_ABSOLUTO:
                problemas.append(f"{pagina}: link absoluto '{endereco}' (não funciona aberto do disco)")
                continue
            destino = '/'.join(arquivo.split('/')[2:])    # tira "/NomeDoRepositorio/"
        elif arquivo:
            destino = posixpath.normpath(posixpath.join(posixpath.dirname(pagina), arquivo))
        else:
            destino = pagina                              # link só com âncora: é na própria página
        if not endereco:
            problemas.append(f"{pagina}: link vazio")
        elif arquivo.endswith('/'):
            problemas.append(f"{pagina}: '{endereco}' não diz o nome do arquivo (link de pasta não abre do disco)")
        elif destino.startswith('..'):
            problemas.append(f"{pagina}: '{endereco}' aponta para fora da pasta do site")
        elif destino not in existentes:
            problemas.append(f"{pagina}: '{endereco}' aponta para um arquivo que não existe ({destino})")
        elif ancora and destino.endswith('.html') and ancora not in ids_da_pagina(destino, guardados):
            problemas.append(f"{pagina}: a âncora '#{ancora}' não existe em {destino}")
    return conferidos, problemas


def conferir_site():
    """Confere todas as páginas e imprime o resultado. Devolve a quantidade de problemas."""
    existentes = arquivos_do_projeto()
    paginas = paginas_do_site(existentes)
    guardados, total, problemas = {}, 0, []
    for pagina in paginas:
        conferidos, achados = conferir_pagina(pagina, existentes, guardados)
        total += conferidos
        problemas.extend(achados)
    for problema in problemas[:40]:
        print("   - " + problema)
    if len(problemas) > 40:
        print(f"   ... e mais {len(problemas) - 40}")
    print(f"   páginas conferidas: {len(paginas)} | links conferidos: {total} | problemas: {len(problemas)}")
    return len(problemas)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    return 1 if conferir_site() else 0


if __name__ == '__main__':
    sys.exit(main())
