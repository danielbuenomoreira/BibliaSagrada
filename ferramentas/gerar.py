"""Gera as páginas do site a partir dos JSON de fonte/ e do molde ferramentas/modelo.html.

Uso (na raiz do projeto):
    python ferramentas/gerar.py                               # gera o site inteiro
    python ferramentas/gerar.py --livros joel,amos            # só esses livros (rápido, para testar o molde)
    python ferramentas/gerar.py --traducoes ara               # só essa tradução
    python ferramentas/gerar.py --traducoes ara --livros joao # as duas coisas juntas

O que é gravado (a partir da raiz do projeto):
    index.html                          página inicial
    biblia/<trad>/index.html            livros de uma tradução
    biblia/<trad>/<livro>/index.html    capítulos de um livro
    biblia/<trad>/<livro>/<cap>.html    texto de um capítulo (ex.: biblia/ara/joao/3.html)

Garantias:
  - antes de gerar, chama o validar.py; se a fonte tiver problema, nada é gerado;
  - recusa-se a rodar se houver algum .json ou alguma pasta com letra maiúscula dentro de biblia/;
  - as páginas são montadas só trocando os marcadores {{NOME}} do molde; se faltar um marcador
    no molde ou sobrar "{{" numa página, para e avisa;
  - a saída é sempre a mesma para a mesma fonte (não leva data nem hora): gerar duas vezes não muda nada;
  - apaga as páginas que não deveriam mais existir (órfãs) dentro do que foi gerado;
  - na geração completa, confere no fim todos os links (verificar_links.py).

NÃO edite as páginas geradas: mude fonte/, ferramentas/modelo.html, style.css ou leitor.js e gere de novo.
"""
import argparse
import html
import json
import os
import posixpath
import sys
import time

import livros
import validar
import verificar_links

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
PASTA_FONTE = os.path.join(RAIZ, 'fonte')
PASTA_SAIDA = os.path.join(RAIZ, 'biblia')
ARQUIVO_MODELO = os.path.join(AQUI, 'modelo.html')

NOME_DO_SITE = "Bíblia Sagrada"
AVISO_GERADO = ("<!-- ARQUIVO GERADO por ferramentas/gerar.py — não edite. "
                "Mude fonte/ ou ferramentas/modelo.html e gere de novo. -->\n")

# Marcadores que cada pedaço do molde precisa ter (e os únicos que pode ter).
MARCADORES = {
    'pagina': ['TITULO', 'DESCRICAO', 'RAIZ', 'DADOS', 'TRADUCAO_ATUAL', 'LINKS_TRADUCOES',
               'MENU_VT', 'MENU_NT', 'CONTEUDO'],
    'inicio': ['CREDITOS'],
    'traducao': ['NOME_TRADUCAO', 'SIGLA', 'LIVROS_VT', 'LIVROS_NT', 'RAIZ', 'AVISO'],
    'livro': ['NOME_LIVRO', 'SIGLA', 'CAPITULOS', 'LINK_ANTERIOR', 'LINK_PROXIMO', 'RAIZ', 'AVISO'],
    'capitulo': ['NOME_LIVRO', 'NOME_NO_TITULO', 'CAPITULO', 'SIGLA', 'TOTAL_DE_CAPITULOS',
                 'LINK_ANTERIOR', 'LINK_PROXIMO', 'RAIZ', 'NOTA', 'AVISO', 'VERSICULOS'],
}


def abortar(mensagem):
    print("ERRO: " + mensagem)
    sys.exit(1)


# ---------------------------------------------------------------- molde

def ler_modelo():
    """Lê o modelo.html e devolve um dicionário {nome do pedaço: texto do pedaço}."""
    if not os.path.isfile(ARQUIVO_MODELO):
        abortar("não encontrei o molde das páginas: ferramentas/modelo.html")
    with open(ARQUIVO_MODELO, 'r', encoding='utf-8') as f:
        texto = f.read()
    modelo = {}
    for nome, esperados in MARCADORES.items():
        inicio, fim = f'<!--[PEDACO {nome}]-->', f'<!--[FIM {nome}]-->'
        if texto.count(inicio) != 1 or texto.count(fim) != 1:
            abortar(f"modelo.html: o pedaço '{nome}' precisa de uma linha {inicio} e uma linha {fim}")
        pedaco = texto.split(inicio)[1].split(fim)[0].strip('\n')
        encontrados = [trecho.split('}}')[0] for trecho in pedaco.split('{{')[1:]]
        for marcador in esperados:
            if marcador not in encontrados:
                abortar(f"modelo.html: falta o marcador {{{{{marcador}}}}} no pedaço '{nome}'")
        for marcador in encontrados:
            if marcador not in esperados:
                abortar(f"modelo.html: o pedaço '{nome}' tem um marcador que o gerador não conhece: {{{{{marcador}}}}}")
        modelo[nome] = pedaco
    return modelo


def preencher(pedaco, valores):
    """Troca cada marcador {{NOME}} do pedaço pelo valor correspondente."""
    for nome, valor in valores.items():
        pedaco = pedaco.replace('{{' + nome + '}}', valor)
    return pedaco


# ---------------------------------------------------------------- endereços e links

def caminho(trad=None, livro=None, cap=None):
    """Endereço de uma página, contado a partir da raiz do site.

    É o único lugar do Python que sabe o formato dos endereços. O leitor.js repete esse formato em
    três pontos (procure por .html no leitor.js): o campo "Ir", o link "Continuar" e os links do menu
    da página inicial. Depois de publicado, não mude o formato: os links que as pessoas salvaram
    deixariam de funcionar.
    """
    if trad is None:
        return 'index.html'
    if livro is None:
        return f'biblia/{trad}/index.html'
    if cap is None:
        return f'biblia/{trad}/{livro}/index.html'
    return f'biblia/{trad}/{livro}/{cap}.html'


def link(de, para):
    """Caminho relativo da página 'de' até a página 'para' (ex.: '4.html', '../genesis/1.html').

    Links relativos e com o nome do arquivo funcionam igual no GitHub Pages e abrindo do disco.
    """
    return posixpath.relpath('/' + para, posixpath.dirname('/' + de))


def raiz_de(pagina):
    """Caminho relativo da página até a raiz do site: '' na página inicial, '../../../' num capítulo."""
    return '../' * pagina.count('/')


# ---------------------------------------------------------------- partes repetidas das páginas

def itens_do_menu(pagina, trad, testamento, slug_atual=None, com_dados=False):
    """Itens <li> da lista de livros de um testamento; cada um leva ao capítulo 1 do livro."""
    itens = []
    for livro in livros.LIVROS:
        if livro['testamento'] != testamento:
            continue
        atributos = ' aria-current="true"' if livro['slug'] == slug_atual else ''
        if com_dados:   # só na página inicial: o leitor.js usa estes dados para montar o "Continuar"
            atributos += (f' data-livro="{livro["slug"]}" data-titulo="{html.escape(livro["titulo"])}"'
                          f' data-caps="{livro["capitulos"]}"')
        endereco = link(pagina, caminho(trad, livro['slug'], 1))
        itens.append(f'<li><a href="{endereco}"{atributos}>{html.escape(livro["nome"])}</a></li>')
    return '\n'.join(itens)


def itens_das_traducoes(pagina, trad_atual, livro=None, cap=None):
    """Itens <li> do seletor de versão: a mesma página (mesmo livro e capítulo) em cada tradução."""
    itens = []
    for traducao in livros.TRADUCOES:
        sigla = traducao['sigla']
        atual = ' aria-current="true"' if sigla == trad_atual else ''
        endereco = link(pagina, caminho(sigla, livro, cap))
        itens.append(f'<li><a href="{endereco}" data-trad="{sigla}"{atual}>{html.escape(traducao["rotulo"])}</a></li>')
    return '\n'.join(itens)


def html_dos_versiculos(versiculos, onde):
    """Um <p id="v16"><sup>16</sup> texto</p> por versículo, em ordem numérica."""
    linhas = []
    for numero in sorted(versiculos, key=int):
        texto = versiculos[numero]
        if not isinstance(texto, str):
            abortar(f"{onde}:{numero}: o versículo não é um texto simples")
        if '{{' in texto:
            abortar(f"{onde}:{numero}: o texto contém '{{{{', que é reservado aos marcadores do molde")
        linhas.append(f'<p id="v{numero}"><sup>{numero}</sup> {html.escape(texto, quote=False)}</p>')
    return '\n'.join(linhas)


def montar_pagina(modelo, pagina, titulo, descricao, conteudo, trad, menus, livro=None, cap=None, dados=''):
    """Preenche a casca comum (pedaço 'pagina') e devolve o HTML completo da página."""
    traducao = livros.traducao_pela_sigla(trad)
    texto = preencher(modelo['pagina'], {
        'TITULO': html.escape(titulo),
        'DESCRICAO': html.escape(descricao),
        'DADOS': dados,
        'TRADUCAO_ATUAL': html.escape(traducao['rotulo']),
        'LINKS_TRADUCOES': itens_das_traducoes(pagina, trad, livro, cap),
        'MENU_VT': menus[0],
        'MENU_NT': menus[1],
        'RAIZ': raiz_de(pagina),
        'CONTEUDO': conteudo,      # por último: nada de dentro do conteúdo é trocado de novo
    })
    if '{{' in texto:
        sobra = texto.split('{{')[1][:40]
        abortar(f"{pagina}: sobrou um marcador sem trocar: {{{{{sobra}")
    return AVISO_GERADO + texto + '\n'


# ---------------------------------------------------------------- os quatro tipos de página

def pagina_inicial(modelo):
    primeira = livros.TRADUCOES[0]['sigla']     # tradução do menu enquanto o leitor ainda não leu nada
    pagina = caminho()
    siglas = ', '.join(t['sigla'].upper() for t in livros.TRADUCOES)
    conteudo = preencher(modelo['inicio'], {
        'CREDITOS': '<br>'.join(html.escape(t['aviso']) for t in livros.TRADUCOES),
    })
    menus = (itens_do_menu(pagina, primeira, 'vt', com_dados=True),
             itens_do_menu(pagina, primeira, 'nt', com_dados=True))
    descricao = (f"Leia a Bíblia Sagrada online, de graça e sem anúncios, nas traduções {siglas}. "
                 "Com modo escuro e ajuste do tamanho da letra.")
    return pagina, montar_pagina(modelo, pagina, NOME_DO_SITE, descricao, conteudo, primeira, menus)


def pagina_da_traducao(modelo, traducao):
    trad, sigla = traducao['sigla'], traducao['sigla'].upper()
    pagina = caminho(trad)
    listas = {'vt': [], 'nt': []}
    for livro in livros.LIVROS:
        endereco = link(pagina, caminho(trad, livro['slug']))
        listas[livro['testamento']].append(f'<li><a href="{endereco}">{html.escape(livro["nome"])}</a></li>')
    conteudo = preencher(modelo['traducao'], {
        'NOME_TRADUCAO': html.escape(traducao['nome']),
        'SIGLA': sigla,
        'LIVROS_VT': '\n'.join(listas['vt']),
        'LIVROS_NT': '\n'.join(listas['nt']),
        'RAIZ': raiz_de(pagina),
        'AVISO': html.escape(traducao['aviso']),
    })
    menus = (itens_do_menu(pagina, trad, 'vt'), itens_do_menu(pagina, trad, 'nt'))
    titulo = f"{sigla} — {traducao['nome']} | {NOME_DO_SITE}"
    descricao = f"Os 66 livros da Bíblia na tradução {traducao['nome']} ({sigla})."
    return pagina, montar_pagina(modelo, pagina, titulo, descricao, conteudo, trad, menus)


def link_de_navegacao(pagina, destino, identificador, rel, texto):
    return f'<a id="{identificador}" rel="{rel}" href="{link(pagina, destino)}">{texto}</a>'


def pagina_do_livro(modelo, traducao, indice, menus):
    """Página com a grade de capítulos de um livro (também é para onde vai o "Ir" sem JavaScript)."""
    livro = livros.LIVROS[indice]
    trad, sigla, slug = traducao['sigla'], traducao['sigla'].upper(), livro['slug']
    pagina = caminho(trad, slug)
    anterior = proximo = ''
    if indice > 0:
        anterior = link_de_navegacao(pagina, caminho(trad, livros.LIVROS[indice - 1]['slug']),
                                     'link-anterior', 'prev', 'Livro Anterior')
    if indice < len(livros.LIVROS) - 1:
        proximo = link_de_navegacao(pagina, caminho(trad, livros.LIVROS[indice + 1]['slug']),
                                    'link-proximo', 'next', 'Próximo Livro')
    capitulos = [f'<a href="{link(pagina, caminho(trad, slug, cap))}">{cap}</a>'
                 for cap in range(1, livro['capitulos'] + 1)]
    conteudo = preencher(modelo['livro'], {
        'NOME_LIVRO': html.escape(livro['nome']),
        'SIGLA': sigla,
        'CAPITULOS': '\n'.join(capitulos),
        'LINK_ANTERIOR': anterior,
        'LINK_PROXIMO': proximo,
        'RAIZ': raiz_de(pagina),
        'AVISO': html.escape(traducao['aviso']),
    })
    titulo = f"{livro['nome']} — {sigla} | {NOME_DO_SITE}"
    descricao = f"{livro['nome']}: os {livro['capitulos']} capítulos na tradução {traducao['nome']} ({sigla})."
    if livro['capitulos'] == 1:
        descricao = f"{livro['nome']}: capítulo único, na tradução {traducao['nome']} ({sigla})."
    dados = f' data-trad="{trad}" data-livro="{slug}" data-caps="{livro["capitulos"]}"'
    return pagina, montar_pagina(modelo, pagina, titulo, descricao, conteudo, trad, menus, slug, dados=dados)


def pagina_do_capitulo(modelo, traducao, indice, cap, versiculos, menus):
    livro = livros.LIVROS[indice]
    trad, sigla, slug = traducao['sigla'], traducao['sigla'].upper(), livro['slug']
    pagina = caminho(trad, slug, cap)

    # Anterior: capítulo anterior; no capítulo 1, o ÚLTIMO capítulo do livro anterior; em Gênesis 1, nada.
    anterior = proximo = ''
    if cap > 1:
        anterior = link_de_navegacao(pagina, caminho(trad, slug, cap - 1), 'link-anterior', 'prev', 'Capítulo Anterior')
    elif indice > 0:
        outro = livros.LIVROS[indice - 1]
        anterior = link_de_navegacao(pagina, caminho(trad, outro['slug'], outro['capitulos']),
                                     'link-anterior', 'prev', 'Livro Anterior')
    # Próximo: capítulo seguinte; no último capítulo, o capítulo 1 do livro seguinte; em Apocalipse 22, nada.
    if cap < livro['capitulos']:
        proximo = link_de_navegacao(pagina, caminho(trad, slug, cap + 1), 'link-proximo', 'next', 'Próximo Capítulo')
    elif indice < len(livros.LIVROS) - 1:
        outro = livros.LIVROS[indice + 1]
        proximo = link_de_navegacao(pagina, caminho(trad, outro['slug'], 1), 'link-proximo', 'next', 'Próximo Livro')

    conteudo = preencher(modelo['capitulo'], {
        'NOME_LIVRO': html.escape(livro['nome']),
        'NOME_NO_TITULO': html.escape(livro['titulo']),
        'CAPITULO': str(cap),
        'SIGLA': sigla,
        'TOTAL_DE_CAPITULOS': str(livro['capitulos']),
        'LINK_ANTERIOR': anterior,
        'LINK_PROXIMO': proximo,
        'RAIZ': raiz_de(pagina),
        'NOTA': html.escape(traducao.get('nota', '')),      # nem toda tradução tem nota: sem ela fica vazio
        'AVISO': html.escape(traducao['aviso']),
        'VERSICULOS': html_dos_versiculos(versiculos, f"{trad} {livro['nome']} {cap}"),   # por último
    })
    titulo = f"{livro['titulo']} {cap} — {sigla} | {NOME_DO_SITE}"
    descricao = f"{livro['titulo']} {cap} na tradução {traducao['nome']} ({sigla}). Bíblia Sagrada online, de graça e sem anúncios."
    dados = f' data-trad="{trad}" data-livro="{slug}" data-cap="{cap}" data-caps="{livro["capitulos"]}"'
    return pagina, montar_pagina(modelo, pagina, titulo, descricao, conteudo, trad, menus, slug, cap, dados)


# ---------------------------------------------------------------- leitura da fonte e gravação

def carregar_livro(trad, slug):
    """Devolve o livro como {capítulo: {versículo: texto}} (chaves em texto: "1", "2"...)."""
    with open(os.path.join(PASTA_FONTE, trad, slug + '.json'), 'r', encoding='utf-8') as f:
        dados = json.load(f)
    return dados[0] if isinstance(dados, list) else dados


def gravar(pagina, texto, gravadas, contagem):
    """Grava a página (em UTF-8, fim de linha LF). Se o arquivo já tem esse conteúdo, não toca nele."""
    destino = os.path.join(RAIZ, pagina)
    gravadas.add(pagina)
    if os.path.exists(destino):
        with open(destino, 'rb') as f:
            if f.read() == texto.encode('utf-8'):
                contagem['iguais'] += 1
                return
        contagem['alteradas'] += 1
    else:
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        contagem['novas'] += 1
    with open(destino, 'w', encoding='utf-8', newline='\n') as f:
        f.write(texto)


def json_dentro_de_biblia():
    """Devolve o primeiro .json encontrado em biblia/ (ou None). biblia/ é pasta de SAÍDA: fonte fica em fonte/."""
    for atual, _, arquivos in os.walk(PASTA_SAIDA):
        for nome in arquivos:
            if nome.lower().endswith('.json'):
                return os.path.join(atual, nome)
    return None


def pasta_com_maiuscula():
    """Devolve a primeira pasta de biblia/ com letra maiúscula no nome (ou None).

    No Windows, 'Joao' e 'joao' são a mesma pasta; no GitHub Pages, não. Todos os slugs são minúsculos.
    """
    for atual, pastas, _ in os.walk(PASTA_SAIDA):
        for nome in pastas:
            if nome != nome.lower():
                return os.path.join(atual, nome)
    return None


def apagar_orfas(pastas, gravadas):
    """Apaga, dentro das pastas dadas, as páginas .html que esta geração não gravou e as pastas que ficarem vazias."""
    apagadas = 0
    for pasta in pastas:
        for atual, _, arquivos in os.walk(os.path.join(RAIZ, pasta), topdown=False):
            for nome in arquivos:
                relativo = os.path.relpath(os.path.join(atual, nome), RAIZ).replace(os.sep, '/')
                if nome.lower().endswith('.html') and relativo not in gravadas:
                    os.remove(os.path.join(atual, nome))
                    apagadas += 1
            if not os.listdir(atual):
                os.rmdir(atual)
    return apagadas


# ---------------------------------------------------------------- programa principal

def escolher(texto, validos, opcao):
    """Transforma 'joel,amos' em ['joel', 'amos'], conferindo se cada nome existe. Vazio = todos."""
    if not texto:
        return list(validos)
    escolhidos = [nome.strip() for nome in texto.split(',') if nome.strip()]
    for nome in escolhidos:
        if nome not in validos:
            abortar(f"{opcao}: '{nome}' não existe. Valem: {', '.join(validos)}")
    return [nome for nome in validos if nome in escolhidos]     # na ordem da tabela


def main():
    parser = argparse.ArgumentParser(description="Gera as páginas do site a partir de fonte/ e do modelo.html.")
    parser.add_argument('--livros', default='', help="só estes livros, pelos slugs separados por vírgula (ex.: joel,amos)")
    parser.add_argument('--traducoes', default='', help="só estas traduções, pelas siglas separadas por vírgula (ex.: ara,naa)")
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    inicio = time.time()

    siglas = escolher(args.traducoes, [t['sigla'] for t in livros.TRADUCOES], "--traducoes")
    slugs = escolher(args.livros, [livro['slug'] for livro in livros.LIVROS], "--livros")
    completa = not args.livros and not args.traducoes

    achado = json_dentro_de_biblia()
    if achado:
        abortar(f"há um arquivo .json dentro de biblia/ ({achado}).\n"
                "      biblia/ é a pasta das páginas geradas; os JSON ficam em fonte/.\n"
                "      Se a migração ainda não foi feita, rode: python ferramentas/migrar.py\n"
                "      Se já foi, esse arquivo sobrou: tire-o de dentro de biblia/ (mova ou apague) e gere de novo.")
    achado = pasta_com_maiuscula()
    if achado:
        abortar(f"há uma pasta com letra maiúscula dentro de biblia/ ({achado}).\n"
                "      Renomeie para minúsculas (ou apague a pasta) e gere de novo.")

    print("1) Conferindo a fonte (validar.py)")
    houve_problema, _ = validar.conferir_pasta(PASTA_FONTE, so_da_tabela=True)
    if houve_problema:
        abortar("a fonte tem problemas (veja acima). Nada foi gerado.")

    print("2) Gerando as páginas")
    modelo = ler_modelo()
    gravadas = set()                                   # todas as páginas gravadas nesta geração
    contagem = {'novas': 0, 'alteradas': 0, 'iguais': 0}

    pagina, texto = pagina_inicial(modelo)
    gravar(pagina, texto, gravadas, contagem)
    for sigla in siglas:
        traducao = livros.traducao_pela_sigla(sigla)
        pagina, texto = pagina_da_traducao(modelo, traducao)
        gravar(pagina, texto, gravadas, contagem)
        for indice, livro in enumerate(livros.LIVROS):
            if livro['slug'] not in slugs:
                continue
            capitulos = carregar_livro(sigla, livro['slug'])
            # o menu é igual em todas as páginas da pasta do livro: monta uma vez só
            pagina_exemplo = caminho(sigla, livro['slug'])
            menus = (itens_do_menu(pagina_exemplo, sigla, 'vt', livro['slug']),
                     itens_do_menu(pagina_exemplo, sigla, 'nt', livro['slug']))
            pagina, texto = pagina_do_livro(modelo, traducao, indice, menus)
            gravar(pagina, texto, gravadas, contagem)
            for cap in sorted(int(numero) for numero in capitulos):
                pagina, texto = pagina_do_capitulo(modelo, traducao, indice, cap, capitulos[str(cap)], menus)
                gravar(pagina, texto, gravadas, contagem)

    # Páginas órfãs: só procura dentro do que esta geração cobriu.
    if completa:
        pastas = ['biblia']
    elif not args.livros:
        pastas = [f'biblia/{sigla}' for sigla in siglas]
    else:
        pastas = [f'biblia/{sigla}/{slug}' for sigla in siglas for slug in slugs]
    apagadas = apagar_orfas(pastas, gravadas)

    print(f"   páginas: {len(gravadas)} (novas: {contagem['novas']}, alteradas: {contagem['alteradas']}, "
          f"iguais: {contagem['iguais']}) | órfãs apagadas: {apagadas} | tempo: {time.time() - inicio:.1f} s")

    if not completa:
        print("Geração parcial: os links não foram conferidos. Antes de publicar, gere o site inteiro (sem opções).")
        return 0
    print("3) Conferindo os links (verificar_links.py); quando muitas páginas acabaram de ser gravadas, "
          "pode levar 1 a 2 minutos")
    problemas = verificar_links.conferir_site()
    return 1 if problemas else 0


if __name__ == '__main__':
    sys.exit(main())
