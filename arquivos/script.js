// O evento 'DOMContentLoaded' espera que todo o HTML da página seja carregado antes de executar o script.
document.addEventListener('DOMContentLoaded', () => {

    // --- SELEÇÃO DOS ELEMENTOS DO HTML ---
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
    const btnProximo = document.getElementById('btn-proximo');

    // --- DADOS DA APLICAÇÃO ---
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
        { display: "Eclesiastes", dataName: "Eclesiastes" },
        { display: "Cânticos de Salomão", dataName: "Cânticos" },
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
    
    const estadoAtual = {
        versao: '',
        livro: '',
        capitulo: 0,
        totalCapitulos: 0
    };

    // --- INICIALIZAÇÃO DA APLICAÇÃO ---
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

    // --- CONFIGURAÇÃO DOS EVENTOS ---
    listaVT.addEventListener('click', selecionarLivro);
    listaNT.addEventListener('click', selecionarLivro);
    
    selectVersao.addEventListener('change', () => {
        if (estadoAtual.livro) {
            carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo);
        }
    });

    irCapituloBtn.addEventListener('click', irParaCapitulo);
    btnAnterior.addEventListener('click', irCapituloAnterior);
    btnProximo.addEventListener('click', irProximoCapitulo);

    // --- FUNÇÕES DE LÓGICA PRINCIPAL ---
    function selecionarLivro(evento) {
        if (evento.target.tagName === 'LI') {
            const nomeLivro = evento.target.dataset.livro;
            
            document.querySelectorAll('#lista-livros li.ativo').forEach(li => li.classList.remove('ativo'));
            evento.target.classList.add('ativo');

            carregarCapitulo(nomeLivro, 1);
        }
    }

    async function carregarCapitulo(livro, capitulo) {
        boasVindas.classList.add('hidden');
        exibicaoCapitulo.classList.remove('hidden');
        textoBiblico.innerHTML = '<p>Carregando...</p>';

        estadoAtual.livro = livro;
        estadoAtual.versao = selectVersao.value;
        
        try {
            if (estadoAtual.versao === 'ara' || estadoAtual.versao === 'naa') {
                await buscarEmArquivoUnico(livro, capitulo);
            } else {
                await buscarEmArquivoPorLivro(livro, capitulo);
            }
        } catch (error) {
            textoBiblico.innerHTML = `<p style="color: red;">${error.message}</p>`;
            btnAnterior.classList.add('hidden');
            btnProximo.classList.add('hidden');
        }
    }

    // --- LÓGICA DE BUSCA DE DADOS ---
    async function buscarEmArquivoUnico(livro, capitulo) {
        const caminho = `./biblia/${estadoAtual.versao.toUpperCase()}.json`;
        const response = await fetch(caminho);
        if (!response.ok) throw new Error(`Arquivo ${caminho} não encontrado.`);
        const dadosBiblia = await response.json();

        const dadosLivro = dadosBiblia.find(b => b.name === livro);
        if (!dadosLivro) throw new Error(`Livro "${livro}" não encontrado na versão ${estadoAtual.versao.toUpperCase()}.`);
        
        estadoAtual.totalCapitulos = dadosLivro.chapters.length;
        const numCapitulo = validarCapitulo(capitulo);
        
        const dadosCapitulo = dadosLivro.chapters[numCapitulo - 1];
        if (!dadosCapitulo) throw new Error(`Capítulo ${numCapitulo} inválido para "${livro}".`);

        estadoAtual.capitulo = numCapitulo;
        exibirCapituloArquivoUnico(dadosCapitulo);
    }

    async function buscarEmArquivoPorLivro(livro, capitulo) {
        const nomeArquivo = normalizarNomeLivro(livro); // Agora esta função irá gerar o nome de arquivo correto
        const caminho = `./biblia/${estadoAtual.versao}/${nomeArquivo}.json`;
        const response = await fetch(caminho);
        if (!response.ok) throw new Error(`Arquivo ${caminho} não encontrado.`);
        const dadosDoLivro = await response.json();

        estadoAtual.totalCapitulos = dadosDoLivro.length;
        const numCapitulo = validarCapitulo(capitulo);

        const objetoCapitulo = dadosDoLivro.find(item => item.hasOwnProperty(numCapitulo));
        if (!objetoCapitulo) throw new Error(`Capítulo ${numCapitulo} inválido para "${livro}".`);
        
        estadoAtual.capitulo = numCapitulo;
        exibirCapituloPorLivro(objetoCapitulo[numCapitulo]);
    }
    
    // --- FUNÇÕES DE EXIBIÇÃO E NAVEGAÇÃO ---
    function exibirCapituloArquivoUnico(versiculosArray) {
        let html = '';
        versiculosArray.forEach((texto, index) => {
            html += `<p><sup>${index + 1}</sup> ${texto}</p>`;
        });
        textoBiblico.innerHTML = html;
        atualizarControles();
    }
    
    function exibirCapituloPorLivro(versiculosObjeto) {
        let html = '';
        for (const numero in versiculosObjeto) {
            html += `<p><sup>${numero}</sup> ${versiculosObjeto[numero]}</p>`;
        }
        textoBiblico.innerHTML = html;
        atualizarControles();
    }
    
    function atualizarControles() {
        const todosOsLivros = [...livrosVT, ...livrosNT];
        const livroInfo = todosOsLivros.find(l => l.dataName === estadoAtual.livro);
        const nomeParaExibir = livroInfo ? livroInfo.display : estadoAtual.livro;

        tituloCapitulo.textContent = `${nomeParaExibir} ${estadoAtual.capitulo}`;
        inputCapitulo.value = estadoAtual.capitulo;

        btnAnterior.classList.toggle('hidden', estadoAtual.capitulo <= 1);
        btnProximo.classList.toggle('hidden', estadoAtual.capitulo >= estadoAtual.totalCapitulos);
    }

    // --- FUNÇÕES DE AÇÃO DO UTILIZADOR ---
    function irParaCapitulo() {
        const numCapitulo = parseInt(inputCapitulo.value);
        carregarCapitulo(estadoAtual.livro, numCapitulo);
    }
    
    function irCapituloAnterior() {
        if (estadoAtual.capitulo > 1) {
            carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo - 1);
        }
    }

    function irProximoCapitulo() {
        if (estadoAtual.capitulo < estadoAtual.totalCapitulos) {
            carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo + 1);
        }
    }

    // --- FUNÇÕES AUXILIARES ---
    function validarCapitulo(num) {
        const capitulo = parseInt(num);
        if (isNaN(capitulo) || capitulo < 1) { return 1; }
        if (capitulo > estadoAtual.totalCapitulos) { return estadoAtual.totalCapitulos; }
        return capitulo;
    }

    // Converte o nome do livro para o formato do nome do arquivo.
    function normalizarNomeLivro(nome) {
        // --- CORREÇÃO AQUI --- 
        // A parte .replace(/\s+/g, '') foi removida para manter os espaços 
        // em nomes como "1 Samuel", gerando "1 samuel" em vez de "1samuel".
        return nome
            .toLowerCase()
            .normalize('NFD')
            .replace(/[\u0300-\u036f]/g, "");
    }
    
    // --- EXECUÇÃO INICIAL ---
    criarListasDeLivros();
});