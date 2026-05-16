import json
import unicodedata
import os


def remover_acentos(texto):
    """
    Remove os acentos de uma string para a formatação do nome do arquivo.
    """
    nfkd = unicodedata.normalize('NFKD', texto)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])


def converter_biblia_naa(arquivo_entrada):
    """
    Lê o arquivo NAA.json, separa e converte os dados para o novo formato.
    """
    if not os.path.exists(arquivo_entrada):
        print(f"Erro: O arquivo '{arquivo_entrada}' não foi encontrado.")
        return

    # Ler o arquivo de entrada
    with open(arquivo_entrada, 'r', encoding='utf-8') as f_in:
        biblia = json.load(f_in)

    # Processar cada livro iterativamente
    for livro in biblia:
        nome_livro = livro.get('name')
        if not nome_livro:
            continue

        # Formatar o nome do arquivo
        nome_arquivo = remover_acentos(nome_livro).lower() + ".json"

        livro_formatado = {}

        # Iterar sobre os capítulos (índice 0 corresponde ao capítulo 1)
        for indice_capitulo, capitulo in enumerate(livro.get('chapters', [])):
            numero_capitulo = str(indice_capitulo + 1)
            livro_formatado[numero_capitulo] = {}

            # Iterar sobre os versículos (índice 0 corresponde ao versículo 1)
            for indice_versiculo, texto_versiculo in enumerate(capitulo):
                numero_versiculo = str(indice_versiculo + 1)
                livro_formatado[numero_capitulo][numero_versiculo] = texto_versiculo

        # A estrutura exigida consiste em uma lista contendo o dicionário do livro
        dados_saida = [livro_formatado]

        # Salvar o livro em um arquivo JSON individual
        with open(nome_arquivo, 'w', encoding='utf-8') as f_out:
            # A opção ensure_ascii=False assegura que a acentuação seja preservada
            json.dump(dados_saida, f_out, ensure_ascii=False, separators=(',', ':'))

    print("Processo concluído. Os arquivos foram gerados com sucesso.")


if __name__ == "__main__":
    converter_biblia_naa('NAA.json')