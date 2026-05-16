import json
import os
import glob


def unificar_formato_biblias(diretorio="."):
    """
    Verifica todos os arquivos JSON no diretório e converte o formato
    [{"1": {...}}, {"2": {...}}] para o formato [{"1": {...}, "2": {...}}].
    """
    arquivos_json = glob.glob(os.path.join(diretorio, '*.json'))

    if not arquivos_json:
        print("Nenhum arquivo JSON encontrado no diretório especificado.")
        return

    arquivos_corrigidos = 0

    for caminho_arquivo in arquivos_json:
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            try:
                dados = json.load(f)
            except json.JSONDecodeError:
                print(f"Erro ao ler o arquivo {caminho_arquivo}. Ignorando.")
                continue

        # Verifica se o arquivo é uma lista e tem mais de 1 item (indicativo do padrão antigo)
        # O padrão novo sempre tem tamanho 1 (len(dados) == 1)
        if isinstance(dados, list) and len(dados) > 1:
            livro_unificado = {}

            # Extrai os capítulos de cada dicionário da lista e unifica no novo objeto
            for capitulo_dict in dados:
                if isinstance(capitulo_dict, dict):
                    for num_capitulo, versiculos in capitulo_dict.items():
                        livro_unificado[num_capitulo] = versiculos

            # Coloca o dicionário unificado dentro de uma lista (padrão atual do JS)
            dados_saida = [livro_unificado]

            # Sobrescreve o arquivo com o novo formato
            with open(caminho_arquivo, 'w', encoding='utf-8') as f_out:
                json.dump(dados_saida, f_out, ensure_ascii=False, separators=(',', ':'))

            print(f"Corrigido: {os.path.basename(caminho_arquivo)}")
            arquivos_corrigidos += 1

    print(f"\nProcesso finalizado. {arquivos_corrigidos} arquivo(s) convertido(s).")


if __name__ == "__main__":
    # Execute o script dentro da pasta onde estão os arquivos NVI ou ACF,
    # ou mude o parâmetro "." para o caminho da pasta desejada.
    unificar_formato_biblias(".")
