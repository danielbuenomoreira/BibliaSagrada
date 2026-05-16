document.addEventListener('DOMContentLoaded', () => {

    const listaLivros = document.getElementById('lista-livros');
    const btnToggleMenu = document.getElementById('btn-toggle-menu');
    const selectVersao = document.getElementById('versao-select');
    const listaVT = document.getElementById('lista-vt');
    const listaNT = document.getElementById('lista-nt');
    
    const boasVindas = document.getElementById('boas-vindas');
    const exibicaoCapitulo = document.getElementById('exibicao-capitulo');
    const tituloCapitulo = document.getElementById('titulo-capitulo');
    const inputCapitulo = document.getElementById('input-capitulo');
    const irCapituloBtn = document.getElementById('ir-capitulo-btn');
    const textoBiblico = document.getElementById('texto-biblico');
    
    const btnAnterior = document.getElementById('btn-anterior');
    const btnAnteriorLivro = document.getElementById('btn-anterior-livro');
    const btnProximo = document.getElementById('btn-proximo');
    const btnInicio = document.getElementById('btn-inicio');
    const btnProximoLivro = document.getElementById('btn-proximo-livro');

    const btnTema = document.getElementById('btn-tema');
    const btnDiminuirFonte = document.getElementById('btn-diminuir-fonte');
    const btnNormalFonte = document.getElementById('btn-normal-fonte');
    const btnAumentarFonte = document.getElementById('btn-aumentar-fonte');

    const TAMANHO_FONTE_PADRAO = 18;
    let tamanhoFonteAtual = localStorage.getItem('biblia_tamanhoFonte') ? parseInt(localStorage.getItem('biblia_tamanhoFonte')) : TAMANHO_FONTE_PADRAO;
    let modoEscuro = localStorage.getItem('biblia_modoEscuro') === 'true';

    function aplicarConfiguracoesVisuais() {
        document.documentElement.style.setProperty('--tamanho-fonte', `${tamanhoFonteAtual}px`);
        if (modoEscuro) {
            document.body.classList.add('dark-mode');
            btnTema.textContent = '☀️ Claro';
        } else {
            document.body.classList.remove('dark-mode');
            btnTema.textContent = '🌙 Escuro';
        }
    }
    
    aplicarConfiguracoesVisuais();

    btnTema.addEventListener('click', () => {
        modoEscuro = !modoEscuro;
        localStorage.setItem('biblia_modoEscuro', modoEscuro);
        aplicarConfiguracoesVisuais();
    });

    btnAumentarFonte.addEventListener('click', () => {
        if (tamanhoFonteAtual < 36) {
            tamanhoFonteAtual += 2;
            localStorage.setItem('biblia_tamanhoFonte', tamanhoFonteAtual);
            aplicarConfiguracoesVisuais();
        }
    });

    btnDiminuirFonte.addEventListener('click', () => {
        if (tamanhoFonteAtual > 12) {
            tamanhoFonteAtual -= 2;
            localStorage.setItem('biblia_tamanhoFonte', tamanhoFonteAtual);
            aplicarConfiguracoesVisuais();
        }
    });

    btnNormalFonte.addEventListener('click', () => {
        tamanhoFonteAtual = TAMANHO_FONTE_PADRAO;
        localStorage.setItem('biblia_tamanhoFonte', tamanhoFonteAtual);
        aplicarConfiguracoesVisuais();
    });

    // --- INTERAÇÃO DO MENU LATERAL (RESPONSIVO E DESKTOP) ---
    btnToggleMenu.addEventListener('click', () => {
        const container = document.getElementById('container-principal');
        if (window.innerWidth > 800) {
            container.classList.remove('menu-aberto');
            container.classList.toggle('menu-oculto');
        } else {
            container.classList.remove('menu-oculto');
            container.classList.toggle('menu-aberto');
        }
    });

    const livrosVT = [
        { display: "Gênesis", dataName: "Gênesis" }, { display: "Êxodo", dataName: "Êxodo" },
        { display: "Levítico", dataName: "Levítico" }, { display: "Números", dataName: "Números" },
        { display: "Deuteronômio", dataName: "Deuteronômio" }, { display: "Josué", dataName: "Josué" },
        { display: "Juízes", dataName: "Juízes" }, { display: "Rute", dataName: "Rute" },
        { display: "1 Samuel", dataName: "1 Samuel" }, { display: "2 Samuel", dataName: "2 Samuel" },
        { display: "1 Reis", dataName: "1 Reis" }, { display: "2 Reis", dataName: "2 Reis" },
        { display: "1 Crônicas", dataName: "1 Crônicas" }, { display: "2 Crônicas", dataName: "2 Crônicas" },
        { display: "Esdras", dataName: "Esdras" }, { display: "Neemias", dataName: "Neemias" },
        { display: "Ester", dataName: "Ester" }, { display: "Jó", dataName: "Jó" },
        { display: "Salmos", dataName: "Salmos" }, { display: "Provérbios", dataName: "Provérbios" },
        { display: "Eclesiastes", dataName: "Eclesiastes" }, { display: "Cânticos de Salomão", dataName: "Cânticos" },
        { display: "Isaías", dataName: "Isaías" }, { display: "Jeremias", dataName: "Jeremias" },
        { display: "Lamentações de Jeremias", dataName: "Lamentações de Jeremias" }, { display: "Ezequiel", dataName: "Ezequiel" },
        { display: "Daniel", dataName: "Daniel" }, { display: "Oséias", dataName: "Oséias" },
        { display: "Joel", dataName: "Joel" }, { display: "Amós", dataName: "Amós" },
        { display: "Obadias", dataName: "Obadias" }, { display: "Jonas", dataName: "Jonas" },
        { display: "Miquéias", dataName: "Miquéias" }, { display: "Naum", dataName: "Naum" },
        { display: "Habacuque", dataName: "Habacuque" }, { display: "Sofonias", dataName: "Sofonias" },
        { display: "Ageu", dataName: "Ageu" }, { display: "Zacarias", dataName: "Zacarias" },
        { display: "Malaquias", dataName: "Malaquias" }
    ];
    
    const livrosNT = [
        { display: "Mateus", dataName: "Mateus" }, { display: "Marcos", dataName: "Marcos" },
        { display: "Lucas", dataName: "Lucas" }, { display: "João", dataName: "João" }, { display: "Atos", dataName: "Atos" },
        { display: "Romanos", dataName: "Romanos" }, { display: "1 Coríntios", dataName: "1 Coríntios" },
        { display: "2 Coríntios", dataName: "2 Coríntios" }, { display: "Gálatas", dataName: "Gálatas" },
        { display: "Efésios", dataName: "Efésios" }, { display: "Filipenses", dataName: "Filipenses" },
        { display: "Colossenses", dataName: "Colossenses" }, { display: "1 Tessalonicenses", dataName: "1 Tessalonicenses" },
        { display: "2 Tessalonicenses", dataName: "2 Tessalonicenses" }, { display: "1 Timóteo", dataName: "1 Timóteo" },
        { display: "2 Timóteo", dataName: "2 Timóteo" }, { display: "Tito", dataName: "Tito" },
        { display: "Filemom", dataName: "Filemom" }, { display: "Hebreus", dataName: "Hebreus" },
        { display: "Tiago", dataName: "Tiago" }, { display: "1 Pedro", dataName: "1 Pedro" },
        { display: "2 Pedro", dataName: "2 Pedro" }, { display: "1 João", dataName: "1 João" },
        { display: "2 João", dataName: "2 João" }, { display: "3 João", dataName: "3 João" },
        { display: "Judas", dataName: "Judas" }, { display: "Apocalipse", dataName: "Apocalipse" }
    ];

    const todosOsLivros = [...livrosVT, ...livrosNT];

    const estadoAtual = {
        versao: '',
        livro: '',
        capitulo: 0,
        totalCapitulos: 0
    };

    function criarListasDeLivros() {
        livrosVT.forEach(livro => {
            const li = document.createElement('li');
            li.textContent = livro.display;
            li.dataset.livro = livro.dataName;
            listaVT.appendChild(li);
        });
        livrosNT.forEach(livro => {
            const li = document.createElement('li');
            li.textContent = livro.display;
            li.dataset.livro = livro.dataName;
            listaNT.appendChild(li);
        });
    }

    function normalizarNomeLivro(nome) {
        return nome
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, "");
    }

    async function carregarCapitulo(livro, capituloSolicitado) {
        boasVindas.classList.add('hidden');
        exibicaoCapitulo.classList.remove('hidden');
        textoBiblico.innerHTML = '<p>Carregando...</p>';
        
        estadoAtual.livro = livro;
        estadoAtual.versao = selectVersao.value;

        const nomeArquivo = normalizarNomeLivro(livro);
        const caminho = `./biblia/${estadoAtual.versao}/${nomeArquivo}.json?v=${new Date().getTime()}`;

        try {
            const response = await fetch(caminho);
            if (!response.ok) throw new Error(`Arquivo não encontrado.`);
            
            const dadosArray = await response.json();
            const dadosLivro = dadosArray[0];
            
            estadoAtual.totalCapitulos = Object.keys(dadosLivro).length;

            let numCapitulo = parseInt(capituloSolicitado);
            if (isNaN(numCapitulo) || numCapitulo < 1) {
                numCapitulo = 1;
            } else if (numCapitulo > estadoAtual.totalCapitulos) {
                numCapitulo = estadoAtual.totalCapitulos;
            }

            estadoAtual.capitulo = numCapitulo;
            const versiculos = dadosLivro[numCapitulo.toString()];

            if (!versiculos) throw new Error(`Capítulo ${numCapitulo} não encontrado.`);

            exibirCapitulo(versiculos);
            document.getElementById('conteudo-principal').scrollTo(0, 0);

        } catch (error) {
            textoBiblico.innerHTML = `<p style="color: red;">${error.message}</p>`;
            btnAnterior.classList.add('hidden');
            btnAnteriorLivro.classList.add('hidden');
            btnProximo.classList.add('hidden');
            btnProximoLivro.classList.add('hidden');
        }
    }

    function exibirCapitulo(versiculosObjeto) {
        let html = '';
        for (const numero in versiculosObjeto) {
            html += `<p><sup>${numero}</sup> ${versiculosObjeto[numero]}</p>`;
        }
        textoBiblico.innerHTML = html;
        atualizarControles();
    }

    function atualizarControles() {
        const livroInfo = todosOsLivros.find(l => l.dataName === estadoAtual.livro);
        
        tituloCapitulo.textContent = `${livroInfo ? livroInfo.display : estadoAtual.livro} ${estadoAtual.capitulo}`;
        inputCapitulo.value = estadoAtual.capitulo;

        const indexAtual = todosOsLivros.findIndex(l => l.dataName === estadoAtual.livro);

        if (estadoAtual.capitulo <= 1) {
            btnAnterior.classList.add('hidden');
            btnAnteriorLivro.classList.toggle('hidden', indexAtual === 0);
        } else {
            btnAnterior.classList.remove('hidden');
            btnAnteriorLivro.classList.add('hidden');
        }
        
        if (estadoAtual.capitulo >= estadoAtual.totalCapitulos) {
            btnProximo.classList.add('hidden');
            btnProximoLivro.classList.toggle('hidden', indexAtual === todosOsLivros.length - 1);
        } else {
            btnProximo.classList.remove('hidden');
            btnProximoLivro.classList.add('hidden');
        }
    }

    listaVT.addEventListener('click', selecionarLivro);
    listaNT.addEventListener('click', selecionarLivro);

    function selecionarLivro(evento) {
        if (evento.target.tagName === 'LI') {
            const nomeLivro = evento.target.dataset.livro;
            document.querySelectorAll('#lista-livros li.ativo').forEach(li => li.classList.remove('ativo'));
            evento.target.classList.add('ativo');
            
            document.getElementById('container-principal').classList.remove('menu-aberto');
            carregarCapitulo(nomeLivro, 1);
        }
    }

    selectVersao.addEventListener('change', () => {
        if (estadoAtual.livro) {
            carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo);
        }
    });

    irCapituloBtn.addEventListener('click', () => carregarCapitulo(estadoAtual.livro, inputCapitulo.value));

    inputCapitulo.addEventListener('keyup', (evento) => {
        if (evento.key === 'Enter') {
            carregarCapitulo(estadoAtual.livro, inputCapitulo.value);
        }
    });

    btnAnterior.addEventListener('click', () => carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo - 1));
    btnProximo.addEventListener('click', () => carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo + 1));
    
    btnAnteriorLivro.addEventListener('click', () => {
        const indexAtual = todosOsLivros.findIndex(l => l.dataName === estadoAtual.livro);
        if (indexAtual > 0) {
            const livroAnterior = todosOsLivros[indexAtual - 1].dataName;
            document.querySelectorAll('#lista-livros li.ativo').forEach(li => li.classList.remove('ativo'));
            const novoLi = document.querySelector(`li[data-livro="${livroAnterior}"]`);
            if (novoLi) novoLi.classList.add('ativo');
            carregarCapitulo(livroAnterior, 999);
        }
    });

    btnProximoLivro.addEventListener('click', () => {
        const indexAtual = todosOsLivros.findIndex(l => l.dataName === estadoAtual.livro);
        if (indexAtual >= 0 && indexAtual < todosOsLivros.length - 1) {
            const proximoLivro = todosOsLivros[indexAtual + 1].dataName;
            document.querySelectorAll('#lista-livros li.ativo').forEach(li => li.classList.remove('ativo'));
            const novoLi = document.querySelector(`li[data-livro="${proximoLivro}"]`);
            if (novoLi) novoLi.classList.add('ativo');
            carregarCapitulo(proximoLivro, 1);
        }
    });

    btnInicio.addEventListener('click', () => {
        exibicaoCapitulo.classList.add('hidden');
        boasVindas.classList.remove('hidden');
        document.querySelectorAll('#lista-livros li.ativo').forEach(li => li.classList.remove('ativo'));
        estadoAtual.livro = '';
        estadoAtual.capitulo = 0;
    });

    criarListasDeLivros();
});