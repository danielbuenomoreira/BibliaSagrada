/* leitor.js — o único script do site.

   Cuida de: tema claro/escuro, tamanho da letra, abrir/fechar o menu, campo "ir para o capítulo"
   e progresso de leitura (o "Continuar" da página inicial).

   As páginas são HTML comum e funcionam sem este arquivo; aqui ficam só as melhorias.
   O tema e a letra gravados são aplicados antes, por um script curto no <head> de cada página
   (veja ferramentas/modelo.html); este arquivo cuida dos cliques. */
(function () {
    'use strict';

    const raiz = document.documentElement;      // <html>: recebe as classes dark-mode, menu-oculto e menu-aberto
    const pagina = document.body.dataset;       // data-trad, data-livro, data-cap, data-caps (gravados pelo gerar.py)
    const telaPequena = window.matchMedia('(max-width: 800px)');   // o mesmo limite do style.css

    // Os limites 12 e 36 também estão no script do <head> em ferramentas/modelo.html: mude nos dois lugares.
    const LETRA_PADRAO = 18;
    const LETRA_MINIMA = 12;
    const LETRA_MAXIMA = 36;
    const LETRA_PASSO = 2;

    // ------------------------------------------------------------ armazenamento local
    // Todo acesso ao localStorage passa por estas duas funções. Se o navegador bloquear o
    // armazenamento, o site continua funcionando; só não lembra as escolhas.

    function ler(chave) {
        try {
            return window.localStorage.getItem(chave);
        } catch (erro) {
            return null;
        }
    }

    function gravar(chave, valor) {
        try {
            window.localStorage.setItem(chave, String(valor));
        } catch (erro) {
            // armazenamento bloqueado ou cheio: segue sem gravar
        }
    }

    // ------------------------------------------------------------ progresso de leitura
    // Só estas duas funções sabem onde o progresso fica guardado. No dia em que houver login,
    // é aqui que a chamada à API entra; o resto do script não muda.
    // Formato: biblia_progresso = {"v":1,"ultima":{"trad":"ara","livro":"joao","cap":3,"quando":"2026-..."}}

    function ehSlug(valor) {
        return typeof valor === 'string' && /^[a-z0-9_]+$/.test(valor);
    }

    function lerProgresso() {
        try {
            const dados = JSON.parse(ler('biblia_progresso'));
            const ultima = dados && dados.v === 1 ? dados.ultima : null;
            if (ultima && ehSlug(ultima.trad) && ehSlug(ultima.livro) && Number.isInteger(ultima.cap) && ultima.cap >= 1) {
                return ultima;
            }
        } catch (erro) {
            // valor estragado: é como se não houvesse progresso
        }
        return null;
    }

    function gravarProgresso(trad, livro, cap) {
        const ultima = { trad: trad, livro: livro, cap: cap, quando: new Date().toISOString() };
        gravar('biblia_progresso', JSON.stringify({ v: 1, ultima: ultima }));
    }

    // ------------------------------------------------------------ tema claro/escuro

    const btnTema = document.getElementById('btn-tema');

    function aplicarTema(escuro) {
        raiz.classList.toggle('dark-mode', escuro);
        btnTema.setAttribute('aria-label', escuro ? 'Mudar para o tema claro' : 'Mudar para o tema escuro');
    }

    btnTema.addEventListener('click', function () {
        const escuro = !raiz.classList.contains('dark-mode');
        aplicarTema(escuro);
        gravar('biblia_modoEscuro', escuro);
    });

    // ------------------------------------------------------------ tamanho da letra

    let letra = LETRA_PADRAO;

    function letraGravada() {
        const gravada = parseInt(ler('biblia_tamanhoFonte'), 10);
        return gravada >= LETRA_MINIMA && gravada <= LETRA_MAXIMA ? gravada : LETRA_PADRAO;
    }

    function aplicarLetra(tamanho) {
        letra = Math.min(LETRA_MAXIMA, Math.max(LETRA_MINIMA, tamanho));
        raiz.style.setProperty('--tamanho-fonte', letra + 'px');
    }

    function mudarLetra(tamanho) {
        aplicarLetra(tamanho);
        gravar('biblia_tamanhoFonte', letra);
    }

    document.getElementById('btn-diminuir-fonte').addEventListener('click', function () { mudarLetra(letra - LETRA_PASSO); });
    document.getElementById('btn-normal-fonte').addEventListener('click', function () { mudarLetra(LETRA_PADRAO); });
    document.getElementById('btn-aumentar-fonte').addEventListener('click', function () { mudarLetra(letra + LETRA_PASSO); });

    // ------------------------------------------------------------ menu de livros
    // Tela grande: o botão ☰ esconde/mostra a barra lateral (classe menu-oculto, lembrada entre páginas).
    // Tela pequena: o botão ☰ abre/fecha o menu por cima do texto (classe menu-aberto, não é lembrada).

    const menu = document.getElementById('lista-livros');
    const btnMenu = document.getElementById('btn-toggle-menu');
    const seletorVersao = document.getElementById('versao-select');

    function menuAberto() {
        return telaPequena.matches ? raiz.classList.contains('menu-aberto') : !raiz.classList.contains('menu-oculto');
    }

    function atualizarBotaoMenu() {
        btnMenu.setAttribute('aria-expanded', String(menuAberto()));
    }

    function abrirMenu(abrir) {
        if (telaPequena.matches) {
            raiz.classList.toggle('menu-aberto', abrir);
        } else {
            raiz.classList.toggle('menu-oculto', !abrir);
            gravar('biblia_menuOculto', !abrir);
        }
        atualizarBotaoMenu();
    }

    btnMenu.addEventListener('click', function (evento) {
        evento.preventDefault();        // sem JavaScript este link abre o menu pela âncora #lista-livros
        const abrir = !menuAberto();
        abrirMenu(abrir);
        if (abrir && telaPequena.matches) {
            document.getElementById('fechar-menu').focus();     // leva o teclado para dentro do menu
        }
    });

    btnMenu.addEventListener('keydown', function (evento) {
        if (evento.key === ' ') {       // o ☰ é um link com papel de botão: a barra de espaço também aciona
            evento.preventDefault();
            btnMenu.click();
        }
    });

    document.getElementById('fechar-menu').addEventListener('click', function (evento) {
        evento.preventDefault();
        abrirMenu(false);
        btnMenu.focus();
    });

    // Fecha o menu do celular e a lista de versões com Esc ou com um toque fora deles
    document.addEventListener('keydown', function (evento) {
        if (evento.key !== 'Escape') return;
        if (seletorVersao.open) {
            seletorVersao.open = false;
            seletorVersao.querySelector('summary').focus();
        } else if (telaPequena.matches && menuAberto()) {
            abrirMenu(false);
            btnMenu.focus();
        }
    });

    document.addEventListener('click', function (evento) {
        if (!seletorVersao.contains(evento.target)) {
            seletorVersao.open = false;
        }
        if (telaPequena.matches && menuAberto() && !menu.contains(evento.target) && !btnMenu.contains(evento.target)) {
            evento.preventDefault();    // o toque fora só fecha o menu: não aciona o link que estava atrás dele
            abrirMenu(false);
        }
    });

    // Teclado: se o Tab leva o foco para fora da lista de versões, ela fecha; se leva para o texto com o
    // menu do celular aberto, o menu fecha. Assim o foco nunca fica escondido atrás deles.
    // (Com o mouse ou o dedo, quem fecha é o clique acima.)
    document.addEventListener('keyup', function (evento) {
        if (evento.key !== 'Tab') return;       // ao soltar o Tab, evento.target já é o elemento que recebeu o foco
        if (!seletorVersao.contains(evento.target)) {
            seletorVersao.open = false;
        }
        if (telaPequena.matches && menuAberto() && evento.target.closest('#conteudo')) {
            abrirMenu(false);
        }
    });

    // Ao passar de tela pequena para grande (ou o contrário), o menu do celular fecha
    function aoMudarLargura() {
        raiz.classList.remove('menu-aberto');
        atualizarBotaoMenu();
    }
    if (telaPequena.addEventListener) {
        telaPequena.addEventListener('change', aoMudarLargura);
    } else if (telaPequena.addListener) {
        telaPequena.addListener(aoMudarLargura);    // navegadores antigos (Safari até a versão 13)
    }

    // Deixa o livro que está sendo lido à vista na lista de livros (sem animação e sem rolar a página)
    function mostrarLivroAtualNaLista() {
        let lista = menu.querySelector('.listas-testamentos');
        const atual = lista.querySelector('a[aria-current]');
        if (window.getComputedStyle(lista).overflowY === 'visible') {
            lista = menu;       // tela baixa: quem rola é o menu inteiro (veja "Tela baixa" no style.css)
        }
        if (atual) {
            const distancia = atual.getBoundingClientRect().top - lista.getBoundingClientRect().top;
            lista.scrollTop += distancia - lista.clientHeight / 2;
        }
    }

    // ------------------------------------------------------------ campo "ir para o capítulo"
    // Sem JavaScript o formulário leva à página com todos os capítulos do livro (index.html).

    const formCapitulo = document.getElementById('form-capitulo');
    const campoCapitulo = document.getElementById('input-capitulo');
    if (formCapitulo) {
        const total = parseInt(pagina.caps, 10);
        formCapitulo.noValidate = true;     // quem confere o número é a função abaixo
        formCapitulo.addEventListener('submit', function (evento) {
            evento.preventDefault();
            let numero = Math.trunc(campoCapitulo.valueAsNumber);
            if (Number.isNaN(numero)) {     // campo vazio ou com algo que não é número: fica onde está
                campoCapitulo.value = pagina.cap;
                return;
            }
            numero = Math.min(total, Math.max(1, numero));      // abaixo de 1 vira 1; acima do último vira o último
            if (String(numero) === pagina.cap) {
                campoCapitulo.value = pagina.cap;
                return;
            }
            window.location.href = numero + '.html';
        });
    }

    // ------------------------------------------------------------ trocar de versão sem perder o versículo
    // Ao trocar de versão no meio de um capítulo, o link clicado ganha a âncora do primeiro versículo
    // que está à vista (#v16), para a outra versão abrir no mesmo ponto da leitura.
    // Sem JavaScript, a outra versão abre no começo do capítulo.

    if (pagina.cap) {       // só nas páginas de capítulo
        seletorVersao.addEventListener('click', function (evento) {
            const linkVersao = evento.target.closest('a[data-trad]');
            if (!linkVersao) return;
            // no celular, a barra fixa cobre o alto da tela: o que está atrás dela não conta como "à vista"
            const topo = telaPequena.matches ? document.getElementById('controles-topo').offsetHeight : 0;
            const versiculos = document.querySelectorAll('#texto-biblico p');
            for (let i = 0; i < versiculos.length; i++) {
                if (versiculos[i].getBoundingClientRect().bottom > topo) {      // primeiro versículo à vista
                    const endereco = linkVersao.getAttribute('href').split('#')[0];
                    // com o versículo 1 à vista (começo do capítulo), o endereço fica sem âncora
                    linkVersao.setAttribute('href', i === 0 ? endereco : endereco + '#' + versiculos[i].id);
                    break;
                }
            }
        });
    }

    // ------------------------------------------------------------ página inicial: "Continuar"

    function prepararPaginaInicial() {
        const caixa = document.getElementById('continuar');
        if (!caixa) return;                 // esta não é a página inicial
        const ultima = lerProgresso();
        if (!ultima) return;                // primeira visita: fica o convite para escolher um livro
        // Só aceita tradução e livro que existem no site hoje (os links da própria página dizem quais são)
        const linkTraducao = seletorVersao.querySelector('a[data-trad="' + ultima.trad + '"]');
        const linkLivro = menu.querySelector('a[data-livro="' + ultima.livro + '"]');
        if (!linkTraducao || !linkLivro || ultima.cap > parseInt(linkLivro.dataset.caps, 10)) return;

        // "Continuar: João 3 (ARA)"
        const link = document.getElementById('link-continuar');
        link.textContent = 'Continuar: ' + linkLivro.dataset.titulo + ' ' + ultima.cap + ' (' + ultima.trad.toUpperCase() + ')';
        link.setAttribute('href', 'biblia/' + ultima.trad + '/' + ultima.livro + '/' + ultima.cap + '.html');
        caixa.hidden = false;

        // O menu e o seletor de versão passam a usar a última tradução lida
        menu.querySelectorAll('a[data-livro]').forEach(function (a) {
            a.setAttribute('href', 'biblia/' + ultima.trad + '/' + a.dataset.livro + '/1.html');
        });
        seletorVersao.querySelectorAll('a[data-trad]').forEach(function (a) {
            a.removeAttribute('aria-current');
        });
        linkTraducao.setAttribute('aria-current', 'true');
        document.getElementById('versao-atual').textContent = linkTraducao.textContent;
    }

    // ------------------------------------------------------------ início

    // Aplica o que está gravado e registra a leitura. Roda ao carregar a página e também quando o
    // navegador a devolve pelo botão Voltar sem recarregar (o tema pode ter sido trocado na página seguinte).
    function iniciar() {
        const temaGravado = ler('biblia_modoEscuro');
        const escuro = temaGravado === null
            ? window.matchMedia('(prefers-color-scheme: dark)').matches
            : temaGravado === 'true';
        aplicarTema(escuro);
        aplicarLetra(letraGravada());
        raiz.classList.toggle('menu-oculto', ler('biblia_menuOculto') === 'true');
        atualizarBotaoMenu();
        prepararPaginaInicial();
        if (pagina.cap) {       // página de capítulo: passa a ser a última leitura
            gravarProgresso(pagina.trad, pagina.livro, parseInt(pagina.cap, 10));
        }
        if (campoCapitulo) {    // ao Voltar, o navegador pode devolver ao campo o número digitado antes
            campoCapitulo.value = pagina.cap;
        }
    }

    iniciar();
    mostrarLivroAtualNaLista();

    // Página devolvida pelo botão Voltar sem recarregar (acontece no site publicado):
    // o menu do celular e a lista de versões reaparecem fechados, e as preferências são reaplicadas.
    window.addEventListener('pageshow', function (evento) {
        if (!evento.persisted) return;
        raiz.classList.remove('menu-aberto');
        seletorVersao.open = false;
        iniciar();
    });
})();
