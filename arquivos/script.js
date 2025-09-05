// O evento 'DOMContentLoaded' espera que todo o HTML da página seja carregado antes de executar o script.
// Isso evita erros de tentar manipular elementos que ainda não existem.
document.addEventListener('DOMContentLoaded', () => {

    // --- SELEÇÃO DOS ELEMENTOS DO HTML ---
    // Guardamos referências aos elementos que vamos manipular frequentemente para não ter que buscá-los toda hora.
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
    // Listas de livros como objetos para separar o nome de exibição do nome de busca.
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

    // 'estadoAtual' guarda o estado da leitura atual (livro, capítulo, etc.).
    const estadoAtual = {
        versao: '',
        livro: '', // Guardará o 'dataName'
        capitulo: 0,
        totalCapitulos: 0
    };

    // --- INICIALIZAÇÃO DA APLICAÇÃO ---

    // Função que cria as listas de livros na barra lateral.
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

    // --- LÓGICA PRINCIPAL - O "DISTRIBUIDOR" ---
    async function carregarCapitulo(livro, capitulo) {
        boasVindas.classList.add('hidden');
        exibicaoCapitulo.classList.remove('hidden');
        textoBiblico.innerHTML = '<p>Carregando...</p>';

        estadoAtual.livro = livro;
        estadoAtual.versao = selectVersao.value;
        
        try {
            // LÓGICA CONDICIONAL: Escolhe o caminho certo com base na versão
            if (estadoAtual.versao === 'ara' || estadoAtual.versao === 'naa') {
                await buscarEmArquivoUnico(livro, capitulo);
            } else if (estadoAtual.versao === 'aa') {
                await buscarNoFormatoVersoPorVerso(livro, capitulo);
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

    // Caminho 1: Lógica para ARA e NAA (Arquivo único).
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

    // Caminho 2: Lógica para AA (formato de lista de versículos).
    async function buscarNoFormatoVersoPorVerso(livro, capitulo) {
        const nomeArquivo = normalizarNomeLivro(livro);
        const caminho = `./biblia/aa/${nomeArquivo}.json`;
        const response = await fetch(caminho);
        if (!response.ok) throw new Error(`Arquivo ${caminho} não encontrado.`);
        
        const dadosDoLivro = await response.json();

        const ultimoCapitulo = Math.max(...dadosDoLivro.map(v => v.chapter));
        estadoAtual.totalCapitulos = ultimoCapitulo;

        const numCapitulo = validarCapitulo(capitulo);

        const versiculosDoCapitulo = dadosDoLivro.filter(v => v.chapter === numCapitulo);
        if (versiculosDoCapitulo.length === 0) {
            throw new Error(`Capítulo ${numCapitulo} inválido ou sem versículos em "${livro}".`);
        }
        
        estadoAtual.capitulo = numCapitulo;
        exibirCapituloVersoPorVerso(versiculosDoCapitulo);
    }

    // Caminho 3: Lógica para NVI, ACF (Arquivos por livro, formato aninhado).
    async function buscarEmArquivoPorLivro(livro, capitulo) {
        const nomeArquivo = normalizarNomeLivro(livro);
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

    // Exibe o capítulo vindo do formato de arquivo único (ARA, NAA).
    function exibirCapituloArquivoUnico(versiculosArray) {
        let html = '';
        versiculosArray.forEach((texto, index) => {
            html += `<p><sup>${index + 1}</sup> ${texto}</p>`;
        });
        textoBiblico.innerHTML = html;
        atualizarControles();
    }

    // Exibe o capítulo vindo do formato de lista de versículos (AA).
    function exibirCapituloVersoPorVerso(versiculosArray) {
        let html = '';
        versiculosArray.forEach(item => {
            html += `<p><sup>${item.verse}</sup> ${item.text}</p>`;
        });
        textoBiblico.innerHTML = html;
        atualizarControles();
    }
    
    // Exibe o capítulo vindo do formato por livro aninhado (ACF, NVI).
    function exibirCapituloPorLivro(versiculosObjeto) {
        let html = '';
        for (const numero in versiculosObjeto) {
            html += `<p><sup>${numero}</sup> ${versiculosObjeto[numero]}</p>`;
        }
        textoBiblico.innerHTML = html;
        atualizarControles();
    }
    
    // Atualiza o título, o campo de input e os botões de navegação.
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

    // Chamada ao clicar no item de lista de livro.
    function selecionarLivro(evento) {
        if (evento.target.tagName === 'LI') {
            const nomeLivro = evento.target.dataset.livro;
            
            document.querySelectorAll('#lista-livros li.ativo').forEach(li => li.classList.remove('ativo'));
            evento.target.classList.add('ativo');

            carregarCapitulo(nomeLivro, 1);
        }
    }

    // Chamada ao clicar no botão "Ir".
    function irParaCapitulo() {
        const numCapitulo = parseInt(inputCapitulo.value);
        carregarCapitulo(estadoAtual.livro, numCapitulo);
    }
    
    // Chamada ao clicar no botão "Anterior".
    function irCapituloAnterior() {
        if (estadoAtual.capitulo > 1) {
            carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo - 1);
        }
    }

    // Chamada ao clicar no botão "Próximo".
    function irProximoCapitulo() {
        if (estadoAtual.capitulo < estadoAtual.totalCapitulos) {
            carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo + 1);
        }
    }

    // --- FUNÇÕES AUXILIARES ---

    // Valida o número do capítulo, retornando 1 ou o último cap. se for inválido.
    function validarCapitulo(num) {
        const capitulo = parseInt(num);
        if (isNaN(capitulo) || capitulo < 1) { return 1; }
        if (capitulo > estadoAtual.totalCapitulos) { return estadoAtual.totalCapitulos; }
        return capitulo;
    }

    // Converte o nome do livro para o formato do nome do arquivo (ex: "1 Crônicas" -> "1cronicas").
    function normalizarNomeLivro(nome) {
        return nome.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "").replace(/\s+/g, '');
    }
    
    // --- EXECUÇÃO INICIAL ---
    // A primeira coisa que o script faz é criar as listas de livros.
    criarListasDeLivros();
});