"""Tabela ÚNICA dos livros e das traduções do site.

Todos os outros scripts desta pasta (gerar.py, validar.py, corrigir.py, converter_usfm.py, migrar.py)
importam os dados daqui. Se um nome de livro, um aviso de direitos ou a ordem das traduções precisar
mudar, é só neste arquivo.

Para acrescentar uma tradução:
    1. crie a pasta fonte/<sigla>/ com os 66 arquivos <slug>.json (veja converter_usfm.py);
    2. acrescente uma linha em TRADUCOES, na posição em que ela deve aparecer no seletor;
    3. rode: python ferramentas/gerar.py

ATENÇÃO: o "slug" é o endereço público do livro: é o nome do arquivo em fonte/ e o nome da pasta
em biblia/ (biblia/ara/joao/3.html). Depois de publicado, NÃO mude um slug nem uma sigla de tradução:
os links que as pessoas salvaram e o "Continuar" da página inicial deixariam de funcionar.
"""

# Cada linha: slug, nome exibido, nome usado no título do capítulo ("Salmo 23"),
#             número de capítulos, testamento ("vt" ou "nt"), código USFM.
_TABELA_LIVROS = [
    ("genesis", "Gênesis", "Gênesis", 50, "vt", "GEN"),
    ("exodo", "Êxodo", "Êxodo", 40, "vt", "EXO"),
    ("levitico", "Levítico", "Levítico", 27, "vt", "LEV"),
    ("numeros", "Números", "Números", 36, "vt", "NUM"),
    ("deuteronomio", "Deuteronômio", "Deuteronômio", 34, "vt", "DEU"),
    ("josue", "Josué", "Josué", 24, "vt", "JOS"),
    ("juizes", "Juízes", "Juízes", 21, "vt", "JDG"),
    ("rute", "Rute", "Rute", 4, "vt", "RUT"),
    ("1_samuel", "1 Samuel", "1 Samuel", 31, "vt", "1SA"),
    ("2_samuel", "2 Samuel", "2 Samuel", 24, "vt", "2SA"),
    ("1_reis", "1 Reis", "1 Reis", 22, "vt", "1KI"),
    ("2_reis", "2 Reis", "2 Reis", 25, "vt", "2KI"),
    ("1_cronicas", "1 Crônicas", "1 Crônicas", 29, "vt", "1CH"),
    ("2_cronicas", "2 Crônicas", "2 Crônicas", 36, "vt", "2CH"),
    ("esdras", "Esdras", "Esdras", 10, "vt", "EZR"),
    ("neemias", "Neemias", "Neemias", 13, "vt", "NEH"),
    ("ester", "Ester", "Ester", 10, "vt", "EST"),
    ("jo", "Jó", "Jó", 42, "vt", "JOB"),
    ("salmos", "Salmos", "Salmo", 150, "vt", "PSA"),
    ("proverbios", "Provérbios", "Provérbios", 31, "vt", "PRO"),
    ("eclesiastes", "Eclesiastes", "Eclesiastes", 12, "vt", "ECC"),
    ("canticos", "Cântico dos Cânticos", "Cântico dos Cânticos", 8, "vt", "SNG"),
    ("isaias", "Isaías", "Isaías", 66, "vt", "ISA"),
    ("jeremias", "Jeremias", "Jeremias", 52, "vt", "JER"),
    ("lamentacoes", "Lamentações", "Lamentações", 5, "vt", "LAM"),
    ("ezequiel", "Ezequiel", "Ezequiel", 48, "vt", "EZK"),
    ("daniel", "Daniel", "Daniel", 12, "vt", "DAN"),
    ("oseias", "Oseias", "Oseias", 14, "vt", "HOS"),
    ("joel", "Joel", "Joel", 3, "vt", "JOL"),
    ("amos", "Amós", "Amós", 9, "vt", "AMO"),
    ("obadias", "Obadias", "Obadias", 1, "vt", "OBA"),
    ("jonas", "Jonas", "Jonas", 4, "vt", "JON"),
    ("miqueias", "Miqueias", "Miqueias", 7, "vt", "MIC"),
    ("naum", "Naum", "Naum", 3, "vt", "NAM"),
    ("habacuque", "Habacuque", "Habacuque", 3, "vt", "HAB"),
    ("sofonias", "Sofonias", "Sofonias", 3, "vt", "ZEP"),
    ("ageu", "Ageu", "Ageu", 2, "vt", "HAG"),
    ("zacarias", "Zacarias", "Zacarias", 14, "vt", "ZEC"),
    ("malaquias", "Malaquias", "Malaquias", 4, "vt", "MAL"),
    ("mateus", "Mateus", "Mateus", 28, "nt", "MAT"),
    ("marcos", "Marcos", "Marcos", 16, "nt", "MRK"),
    ("lucas", "Lucas", "Lucas", 24, "nt", "LUK"),
    ("joao", "João", "João", 21, "nt", "JHN"),
    ("atos", "Atos", "Atos", 28, "nt", "ACT"),
    ("romanos", "Romanos", "Romanos", 16, "nt", "ROM"),
    ("1_corintios", "1 Coríntios", "1 Coríntios", 16, "nt", "1CO"),
    ("2_corintios", "2 Coríntios", "2 Coríntios", 13, "nt", "2CO"),
    ("galatas", "Gálatas", "Gálatas", 6, "nt", "GAL"),
    ("efesios", "Efésios", "Efésios", 6, "nt", "EPH"),
    ("filipenses", "Filipenses", "Filipenses", 4, "nt", "PHP"),
    ("colossenses", "Colossenses", "Colossenses", 4, "nt", "COL"),
    ("1_tessalonicenses", "1 Tessalonicenses", "1 Tessalonicenses", 5, "nt", "1TH"),
    ("2_tessalonicenses", "2 Tessalonicenses", "2 Tessalonicenses", 3, "nt", "2TH"),
    ("1_timoteo", "1 Timóteo", "1 Timóteo", 6, "nt", "1TI"),
    ("2_timoteo", "2 Timóteo", "2 Timóteo", 4, "nt", "2TI"),
    ("tito", "Tito", "Tito", 3, "nt", "TIT"),
    ("filemom", "Filemom", "Filemom", 1, "nt", "PHM"),
    ("hebreus", "Hebreus", "Hebreus", 13, "nt", "HEB"),
    ("tiago", "Tiago", "Tiago", 5, "nt", "JAS"),
    ("1_pedro", "1 Pedro", "1 Pedro", 5, "nt", "1PE"),
    ("2_pedro", "2 Pedro", "2 Pedro", 3, "nt", "2PE"),
    ("1_joao", "1 João", "1 João", 5, "nt", "1JN"),
    ("2_joao", "2 João", "2 João", 1, "nt", "2JN"),
    ("3_joao", "3 João", "3 João", 1, "nt", "3JN"),
    ("judas", "Judas", "Judas", 1, "nt", "JUD"),
    ("apocalipse", "Apocalipse", "Apocalipse", 22, "nt", "REV"),
]

# A mesma tabela em forma de dicionários, que é como os outros scripts a usam:
#   livro['slug'], livro['nome'], livro['titulo'], livro['capitulos'], livro['testamento'], livro['usfm']
_CAMPOS = ("slug", "nome", "titulo", "capitulos", "testamento", "usfm")
LIVROS = [dict(zip(_CAMPOS, linha)) for linha in _TABELA_LIVROS]

TOTAL_DE_CAPITULOS = sum(livro['capitulos'] for livro in LIVROS)   # 1189

# Traduções do site. A ORDEM desta lista é a ordem do seletor de versão; a primeira é a tradução
# usada na página inicial enquanto o leitor ainda não leu nada.
#   sigla  = nome da pasta (fonte/<sigla>/ e biblia/<sigla>/), só letras minúsculas, números e "_"
#   rotulo = texto que aparece no seletor de versão
#   nome   = nome da tradução por extenso
#   aviso  = aviso de direitos mostrado abaixo do texto de cada capítulo (redação pedida pelo detentor)
#   nota   = (opcional) explicação mostrada abaixo do texto de cada capítulo, acima do aviso de direitos
TRADUCOES = [
    {
        "sigla": "ara",
        "rotulo": "ARA (Almeida Revista e Atualizada)",
        "nome": "Almeida Revista e Atualizada",
        "aviso": "Almeida Revista e Atualizada © 1993 Sociedade Bíblica do Brasil. Todos os direitos reservados.",
    },
    {
        "sigla": "naa",
        "rotulo": "NAA (Nova Almeida Atualizada)",
        "nome": "Nova Almeida Atualizada",
        "aviso": "Nova Almeida Atualizada © 2017 Sociedade Bíblica do Brasil. Todos os direitos reservados.",
    },
    {
        "sigla": "nbv",
        "rotulo": "NBV (Nova Bíblia Viva)",
        "nome": "Nova Bíblia Viva",
        "aviso": "Biblica® Open Nova Bíblia Viva™ Copyright © 2007, 2010 by Biblica, Inc. “Biblica” é uma marca "
                 "registrada na Oficina de Patentes e Marcas dos Estados Unidos por Biblica, Inc. Usado com permissão. "
                 "Licença CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/).",
    },
    {
        "sigla": "acf",
        "rotulo": "ACF (Almeida Corrigida Fiel)",
        "nome": "Almeida Corrigida Fiel",
        "aviso": "A Bíblia Sagrada - Almeida Corrigida Fiel (ACF), © 1994, 1995, 2007, 2011 Sociedade Bíblica "
                 "Trinitariana do Brasil, Trinitarian Bible Society.",
    },
    {
        "sigla": "blivre",
        "rotulo": "BLIVRE (Bíblia Livre)",
        "nome": "Bíblia Livre",
        "aviso": "Bíblia Livre (BLIVRE), Copyright © Diego Santos, Mario Sérgio, e Marco Teles, "
                 "http://sites.google.com/site/biblialivre/ - fevereiro de 2018. Licença Creative Commons "
                 "Atribuição 3.0 Brasil (http://creativecommons.org/licenses/by/3.0/br/).",
    },
]

# Nomes antigos de livros que ainda aparecem dentro de correcoes.json e contagens.json.
# Servem só para esses arquivos continuarem sendo lidos sem precisar reescrevê-los.
NOMES_ANTIGOS = {
    "Cânticos": "canticos",
    "Lamentações de Jeremias": "lamentacoes",
    "Oséias": "oseias",
    "Miquéias": "miqueias",
}


def livro_pelo_nome(nome):
    """Acha um livro pelo slug ("1_corintios"), pelo nome ("1 Coríntios") ou por um nome antigo ("Oséias").

    Devolve o dicionário do livro, ou None se não existir.
    """
    slug = NOMES_ANTIGOS.get(nome, nome)
    for livro in LIVROS:
        if slug in (livro['slug'], livro['nome']):
            return livro
    return None


def traducao_pela_sigla(sigla):
    """Devolve o dicionário da tradução ("ara", "naa"...), ou None se a sigla não estiver na tabela."""
    for traducao in TRADUCOES:
        if traducao['sigla'] == sigla:
            return traducao
    return None


if __name__ == '__main__':
    # Rodar este arquivo sozinho só mostra a tabela, para conferência.
    import sys
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    for numero, livro in enumerate(LIVROS, start=1):
        print(f"{numero:2} {livro['usfm']} {livro['testamento']} {livro['slug']:18} {livro['capitulos']:3}  {livro['nome']}")
    print(f"{len(LIVROS)} livros, {TOTAL_DE_CAPITULOS} capítulos")
    for traducao in TRADUCOES:
        print(f"{traducao['sigla']:7} {traducao['rotulo']}")
