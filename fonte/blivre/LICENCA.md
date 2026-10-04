# Bíblia Livre (BLIVRE), edição Textus Receptus

Copyright © Diego Santos, Mario Sérgio, e Marco Teles, http://sites.google.com/site/biblialivre/ - fevereiro de 2018.

## Licença

Licença Creative Commons Atribuição 3.0 Brasil (CC BY 3.0 BR): http://creativecommons.org/licenses/by/3.0/br/

Reprodução permitida desde que devidamente mencionados fonte e autores.

Os arquivos desta pasta e as páginas geradas a partir deles (pasta `biblia/blivre/`) **não** estão sob a licença MIT do restante do repositório; continuam sob CC BY 3.0 BR.

## Fonte

https://github.com/blivre/BibliaLivre/releases/download/2018.2.0/usfm-s-blivre-tr.zip (versão 2018.2.0, baixada em 03/10/2026).

## O que mudou em relação ao original

- Conversão de formato: de USFM para JSON, um arquivo por livro, feita por `ferramentas/converter_usfm.py`.
- As palavras dos versículos não foram alteradas.
- As páginas HTML de `biblia/blivre/` são geradas a partir destes JSON por `ferramentas/gerar.py`, sem alterar as palavras dos versículos.
