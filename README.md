# 📖 Bíblia Sagrada Online

Olá e seja bem-vindo! Meu nome é **Daniel Moreira**, e fico feliz em compartilhar este projeto com você.

Desenvolvi esta aplicação com dois grandes objetivos em mente:

1.  **Missão:** Oferecer uma plataforma de leitura da Bíblia que seja **completa, gratuita e 100% livre de anúncios**, permitindo que qualquer pessoa estude as Escrituras de forma acessível e em qualquer lugar.
2.  **Portfólio:** Criar um projeto pessoal que fosse ao mesmo tempo simples em seu propósito, mas completo em sua execução, para demonstrar minhas habilidades de desenvolvimento web.

Espero que seja uma bênção para você. Aproveite a leitura!

---

### ✨ Funcionalidades Principais

Para garantir a melhor experiência de leitura, o projeto conta com:

* **Interface Limpa e Sem Distrações:** Foco total na Palavra, sem banners, pop-ups ou qualquer tipo de anúncio.
* **Versões da Bíblia:** Cinco traduções (ARA, NAA, NBV, ACF e BLIVRE); dá para trocar de versão sem sair do capítulo.
* **Navegação Intuitiva:** Cada capítulo tem o seu próprio endereço (pode ser salvo nos favoritos ou compartilhado), com capítulo anterior/próximo, lista de livros e "Continuar" de onde você parou.
* **Design Responsivo:** Leia confortavelmente no seu celular, tablet ou computador, com tema claro/escuro e ajuste do tamanho da letra.
* **Funciona Offline:** O site inteiro pode ser baixado e aberto direto do disco, sem internet (veja abaixo).

---

### 💻 Acesse a Bíblia Online

Este projeto está no ar e pode ser acessado por qualquer pessoa através do link abaixo:

➡️ **[https://danielbuenomoreira.github.io/BibliaSagrada/](https://danielbuenomoreira.github.io/BibliaSagrada/)**

---

### 📴 Como usar offline (sem internet)

1. Nesta página do GitHub, clique em **Code > Download ZIP**.
2. Extraia o ZIP em qualquer pasta do computador (ou num pen drive).
3. Abra o arquivo **`index.html`** com dois cliques.

Pronto: a leitura, a troca de versão e a navegação funcionam sem internet, porque cada capítulo é uma página HTML comum.
Abrindo do disco, o tema, o tamanho da letra e o "Continuar" são lembrados no Chrome e no Edge; em outros navegadores a leitura funciona igual, mas essas preferências podem não ser lembradas de uma página para a outra.

---

### 🛠️ Tecnologias Utilizadas

* **HTML5**, **CSS3** e **JavaScript** puros, sem frameworks (tema, tamanho da letra, menu e "Continuar")
* **Python** (gerador das páginas e scripts de correção, validação e conversão em `ferramentas/`)

---

### 🗂️ Como o projeto é organizado

O site é **estático**: as páginas são geradas no meu computador por um script Python e publicadas prontas no GitHub Pages.

```
fonte/<versão>/<livro>.json     os textos (fonte única; é aqui que se corrige um versículo)
ferramentas/livros.py           tabela única dos 66 livros e das versões
ferramentas/modelo.html         molde de todas as páginas
ferramentas/gerar.py            lê fonte/ + modelo.html e grava as páginas
ferramentas/validar.py          confere a estrutura dos JSON (o gerar.py chama sozinho)
ferramentas/verificar_links.py  confere os links das páginas (o gerar.py chama sozinho)
ferramentas/corrigir.py         aplica a errata (correcoes.json) nos JSON
ferramentas/converter_usfm.py   converte uma Bíblia em USFM para o formato de fonte/
ferramentas/migrar.py           uso único: levou os JSON da antiga pasta biblia/ para fonte/
style.css, leitor.js            aparência e comportamento, iguais para todas as páginas
index.html                      página inicial                    (GERADA)
biblia/<versão>/<livro>/3.html  um arquivo por capítulo           (GERADAS)
```

**Nunca edite as páginas geradas** (`index.html` e tudo em `biblia/`): a próxima geração apaga a edição. Mude a fonte, o molde, o `style.css` ou o `leitor.js`.

#### Gerar as páginas

Na pasta do projeto:

```
python ferramentas/gerar.py
```

O script confere os textos, gera as páginas (só regrava as que mudaram), apaga as que sobraram e confere todos os links. Enquanto estiver mexendo no molde, dá para gerar só um pedaço, que é bem mais rápido:

```
python ferramentas/gerar.py --traducoes ara --livros joel,amos
```

#### Testar antes de publicar

* **Do disco:** abra o `index.html` com dois cliques.
* **Como no GitHub Pages:** na pasta **acima** da pasta do projeto, rode `python -m http.server` e abra `http://localhost:8000/BibliaSagrada/`.

#### Publicar

```
python ferramentas/gerar.py
git status          (confira o que mudou)
git add -A
git commit -m "..."
git push
```

#### Corrigir um versículo ou acrescentar uma versão

* **Versículo:** corrija o texto em `fonte/<versão>/<livro>.json` e rode o `gerar.py` (só a página daquele capítulo muda).
* **Nova versão:** coloque os 66 JSON em `fonte/<sigla>/` (veja `converter_usfm.py`), acrescente a versão em `ferramentas/livros.py` e rode o `gerar.py`.

---

### Licença e direitos autorais

* **Código** (molde das páginas, CSS, JavaScript e scripts em `ferramentas/`): licença MIT, veja o arquivo `LICENSE`.
* **Textos bíblicos** (os JSON de `fonte/` e as páginas geradas a partir deles em `biblia/`): não são cobertos pela licença MIT. Pertencem aos respectivos detentores:
  * ARA - Almeida Revista e Atualizada © 1993 Sociedade Bíblica do Brasil
  * NAA - Nova Almeida Atualizada © 2017 Sociedade Bíblica do Brasil
  * ACF - Almeida Corrigida Fiel © 1994, 1995, 2007, 2011 Sociedade Bíblica Trinitariana do Brasil
  * NBV - Biblica® Open Nova Bíblia Viva™ © 2007, 2010 Biblica, Inc., licença CC BY-SA 4.0 (veja `fonte/nbv/LICENCA.md`)
  * BLIVRE - Bíblia Livre © Diego Santos, Mario Sérgio e Marco Teles, licença CC BY 3.0 Brasil (veja `fonte/blivre/LICENCA.md`)

---

### 🌐 Meus Outros Projetos e Redes

Gostou do que viu? Conecte-se comigo ou explore meus outros trabalhos:

* 🎵 **Novo Hinário Adventista:** [Repositório no GitHub](https://github.com/danielbuenomoreira/NovoHinarioAdventista)
* 👤 **Quem Sou Eu (Minhas Redes):** [Página de Contato](https://danielbuenomoreira.github.io/QuemSouEu/)

Obrigado pela visita!
