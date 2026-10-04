"""Script de USO ÚNICO: leva os JSON de biblia/ para fonte/, já com os nomes novos (slugs).

    biblia/ara/1 corintios.json              ->  fonte/ara/1_corintios.json
    biblia/ara/lamentacoes de jeremias.json  ->  fonte/ara/lamentacoes.json
    biblia/nbv/LICENCA.md                    ->  fonte/nbv/LICENCA.md

Uso (na raiz do projeto):
    python ferramentas/migrar.py --simular    # só mostra o que seria feito, não move nada
    python ferramentas/migrar.py              # move os arquivos

Se a pasta do projeto for um repositório git, os arquivos são movidos com "git mv" (assim o git
continua sabendo o histórico de cada arquivo). Se não for, são movidos normalmente.
O conteúdo dos arquivos não é alterado. Pode rodar de novo: o que já foi movido é pulado.
Se algo estiver fora do esperado, nada é movido e o problema é listado.
"""
import argparse
import os
import shutil
import subprocess
import sys

import livros

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)

# Nome antigo do arquivo, quando ele não é só o slug com espaço no lugar do "_".
ARQUIVOS_ANTIGOS = {"lamentacoes": "lamentacoes de jeremias"}


def arquivo_antigo(slug):
    """Nome que o arquivo do livro tinha em biblia/ ("1_corintios" -> "1 corintios.json")."""
    return ARQUIVOS_ANTIGOS.get(slug, slug.replace('_', ' ')) + '.json'


def eh_repositorio_git():
    """Verdadeiro se a raiz do projeto é a raiz de um repositório git."""
    try:
        resposta = subprocess.run(['git', '-C', RAIZ, 'rev-parse', '--show-toplevel'],
                                  capture_output=True, text=True, encoding='utf-8')
    except OSError:
        return False    # o git não está instalado
    if resposta.returncode != 0:
        return False
    return os.path.normcase(os.path.realpath(resposta.stdout.strip())) == os.path.normcase(os.path.realpath(RAIZ))


def planejar():
    """Monta a lista do que mover. Devolve (movimentos, pulados, erros, avisos).

    Cada movimento é um par (origem, destino), com caminhos contados a partir da raiz do projeto.
    """
    movimentos, pulados, erros, avisos = [], 0, [], []
    pasta_biblia = os.path.join(RAIZ, 'biblia')
    if not os.path.isdir(pasta_biblia):
        return movimentos, pulados, erros, avisos
    siglas = [t['sigla'] for t in livros.TRADUCOES]
    for sigla in sorted(os.listdir(pasta_biblia)):
        if not os.path.isdir(os.path.join(pasta_biblia, sigla)):
            continue
        if sigla not in siglas:
            avisos.append(f"biblia/{sigla}/ não está na tabela de traduções (livros.py): ficou onde está")
            continue
        pares = [(f"biblia/{sigla}/{arquivo_antigo(livro['slug'])}", f"fonte/{sigla}/{livro['slug']}.json")
                 for livro in livros.LIVROS]
        pares.append((f"biblia/{sigla}/LICENCA.md", f"fonte/{sigla}/LICENCA.md"))
        # arquivo que não é livro da tabela nem página gerada: não é movido, mas é avisado
        esperados = {os.path.basename(origem) for origem, _ in pares}
        for nome in sorted(os.listdir(os.path.join(pasta_biblia, sigla))):
            if nome not in esperados and not nome.lower().endswith('.html') \
                    and os.path.isfile(os.path.join(pasta_biblia, sigla, nome)):
                avisos.append(f"biblia/{sigla}/{nome}: não é um livro da tabela; fica onde está "
                              "(se for .json, tire-o de biblia/ à mão: o gerar.py não roda com .json lá dentro)")
        for origem, destino in pares:
            tem_origem = os.path.isfile(os.path.join(RAIZ, origem))
            tem_destino = os.path.isfile(os.path.join(RAIZ, destino))
            if tem_origem and tem_destino:
                erros.append(f"{origem}: o destino {destino} já existe (confira qual dos dois é o certo)")
            elif tem_origem:
                movimentos.append((origem, destino))
            elif tem_destino:
                pulados += 1
            elif not origem.endswith('LICENCA.md'):     # a licença só existe nas traduções livres
                erros.append(f"{origem}: arquivo não encontrado (e {destino} também não existe)")
    return movimentos, pulados, erros, avisos


def mover(origem, destino, usar_git):
    """Move um arquivo. Devolve como moveu: 'git mv' ou 'movido'."""
    os.makedirs(os.path.dirname(os.path.join(RAIZ, destino)), exist_ok=True)
    if usar_git:
        resposta = subprocess.run(['git', '-C', RAIZ, 'mv', origem, destino], capture_output=True)
        if resposta.returncode == 0:
            return 'git mv'
        # o git recusou (por exemplo, arquivo que nunca recebeu "git add"): move do jeito comum
    shutil.move(os.path.join(RAIZ, origem), os.path.join(RAIZ, destino))
    return 'movido'


def apagar_pastas_vazias():
    """Apaga biblia/<trad>/ e biblia/ se tiverem ficado vazias."""
    pasta_biblia = os.path.join(RAIZ, 'biblia')
    if not os.path.isdir(pasta_biblia):
        return
    for nome in os.listdir(pasta_biblia):
        pasta = os.path.join(pasta_biblia, nome)
        if os.path.isdir(pasta) and not os.listdir(pasta):
            os.rmdir(pasta)
    if not os.listdir(pasta_biblia):
        os.rmdir(pasta_biblia)


def main():
    parser = argparse.ArgumentParser(description="Move os JSON de biblia/ para fonte/ (uso único).")
    parser.add_argument('--simular', action='store_true', help="não move nada; só mostra o que seria feito")
    args = parser.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')

    movimentos, pulados, erros, avisos = planejar()
    for aviso in avisos:
        print("  [aviso] " + aviso)
    if erros:
        for erro in erros:
            print("  [ERRO] " + erro)
        print(f"Nada foi movido, porque houve {len(erros)} erro(s).")
        return 1
    if not movimentos:
        print("Nada a mover: não há JSON de livros em biblia/ (a migração já foi feita).")
        return 0

    usar_git = eh_repositorio_git()
    renomeados = sum(1 for origem, destino in movimentos
                     if os.path.basename(origem) != os.path.basename(destino))
    print(f"Arquivos a mover: {len(movimentos)} (dos quais {renomeados} mudam de nome) | já movidos: {pulados}")
    print("Modo: " + ("git mv" if usar_git else "mover arquivos (a pasta não é um repositório git)"))
    if args.simular:
        for origem, destino in movimentos:
            if os.path.basename(origem) != os.path.basename(destino):
                print(f"  {origem}  ->  {destino}")
        print("Simulação: nada foi movido. Rode sem --simular para mover.")
        return 0

    com_git = 0
    for origem, destino in movimentos:
        if mover(origem, destino, usar_git) == 'git mv':
            com_git += 1
    apagar_pastas_vazias()
    print(f"Movidos: {len(movimentos)} ({com_git} com git mv, {len(movimentos) - com_git} do jeito comum).")
    print("Agora rode: python ferramentas/validar.py")
    return 0


if __name__ == '__main__':
    sys.exit(main())
