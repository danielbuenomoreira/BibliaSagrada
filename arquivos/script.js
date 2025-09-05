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
    // Dividimos os livros em dois arrays para popular as listas separadamente.
    const livrosVT = ["Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute", "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester", "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cantares", "Isaías", "Jeremias", "Lamentações de Jeremias", "Ezequiel", "Daniel", "Oséias", "Joel", "Amós", "Obadias", "Jonas", "Miquéias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias"];
    const livrosNT = ["Mateus", "Marcos", "Lucas", "João", "Atos", "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses", "Colossenses", "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus", "Tiago", "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"];

    // 'estadoAtual' é um objeto que guarda o estado da leitura atual.
    // Isso é crucial para as funções de navegação saberem qual é o livro e capítulo atual.
    const estadoAtual = {
        versao: '',
        livro: '',
        capitulo: 0,
        totalCapitulos: 0
    };

    // --- INICIALIZAÇÃO DA APLICAÇÃO ---

    // Função que cria as listas de livros na barra lateral.
    function criarListasDeLivros() {
        // Popula a lista do Velho Testamento
        livrosVT.forEach(livro => {
            const li = document.createElement('li');
            li.textContent = livro;
            li.dataset.livro = livro; // 'data-livro' armazena o nome do livro no próprio elemento
            listaVT.appendChild(li);
        });

        // Popula a lista do Novo Testamento
        livrosNT.forEach(livro => {
            const li = document.createElement('li');
            li.textContent = livro;
            li.dataset.livro = livro;
            listaNT.appendChild(li);
        });
    }

    // --- CONFIGURAÇÃO DOS EVENTOS ---

    // Adiciona um "ouvinte" de evento de clique nas duas listas de livros.
    // Usamos 'event delegation': um único ouvinte na lista pai (UL) para gerenciar cliques em todos os filhos (LI).
    // É mais eficiente do que adicionar um ouvinte para cada um dos 66 livros.
    listaVT.addEventListener('click', selecionarLivro);
    listaNT.addEventListener('click', selecionarLivro);
    
    // Evento para quando o utilizador muda a versão da Bíblia.
    selectVersao.addEventListener('change', () => {
        // Se um livro já estiver selecionado, recarrega o capítulo atual na nova versão.
        if (estadoAtual.livro) {
            carregarCapitulo(estadoAtual.livro, estadoAtual.capitulo);
        }
    });

    // Eventos para os botões de navegação.
    irCapituloBtn.addEventListener('click', irParaCapitulo);
    btnAnterior.addEventListener('click', irCapituloAnterior);
    btnProximo.addEventListener('click', irProximoCapitulo);

    // --- FUNÇÕES DE LÓGICA PRINCIPAL ---

    // Chamada quando um livro é clicado na lista.
    function selecionarLivro(evento) {
        // Verifica se o clique foi realmente em um item de lista (LI).
        if (evento.target.tagName === 'LI') {
            const nomeLivro = evento.target.dataset.livro; // Pega o nome do livro do 'data-livro'
            
            // Remove a classe 'ativo' de qualquer livro que esteja selecionado.
            document.querySelectorAll('#lista-livros li.ativo').forEach(li => li.classList.remove('ativo'));
            // Adiciona a classe 'ativo' ao livro que foi clicado.
            evento.target.classList.add('ativo');

            // Por padrão, carrega o capítulo 1 do livro selecionado.
            carregarCapitulo(nomeLivro, 1);
        }
    }

    // Função central que carrega os dados de um capítulo específico.
    async function carregarCapitulo(livro, capitulo) {
        // Esconde a mensagem de boas-vindas e mostra a área de leitura.
        boasVindas.classList.add('hidden');
        exibicaoCapitulo.classList.remove('hidden');
        textoBiblico.innerHTML = '<p>Carregando...</p>';

        // Atualiza o estado global da aplicação.
        estadoAtual.livro = livro;
        estadoAtual.versao = selectVersao.value;
        
        try {
            // Usa a lógica condicional para chamar a função de busca correta.
            if (estadoAtual.versao === 'ara' || estadoAtual.versao === 'naa') {
                await buscarEmArquivoUnico(livro, capitulo);
            } else {
                await buscarEmArquivoPorLivro(livro, capitulo);
            }
        } catch (error) {
            // Em caso de erro, exibe uma mensagem amigável.
            textoBiblico.innerHTML = `<p style="color: red;">${error.message}</p>`;
            // Esconde os botões de navegação se houver erro.
            btnAnterior.classList.add('hidden');
            btnProximo.classList.add('hidden');
        }
    }

    // --- LÓGICA DE BUSCA DE DADOS (OS DOIS CAMINHOS) ---

    // Busca dados nos arquivos ARA.json ou NAA.json (Bíblia inteira).
    async function buscarEmArquivoUnico(livro, capitulo) {
        const caminho = `./biblia/${estadoAtual.versao.toUpperCase()}.json`;
        const response = await fetch(caminho);
        if (!response.ok) throw new Error(`Arquivo ${caminho} não encontrado.`);
        const dadosBiblia = await response.json();

        const dadosLivro = dadosBiblia.find(b => b.name === livro);
        if (!dadosLivro) throw new Error(`Livro "${livro}" não encontrado.`);
        
        estadoAtual.totalCapitulos = dadosLivro.chapters.length; // Armazena o total de capítulos
        // Validação do número do capítulo.
        const numCapitulo = validarCapitulo(capitulo);
        
        const dadosCapitulo = dadosLivro.chapters[numCapitulo - 1]; // Índice é capítulo - 1
        if (!dadosCapitulo) throw new Error(`Capítulo ${numCapitulo} inválido para "${livro}".`);

        estadoAtual.capitulo = numCapitulo; // Atualiza o capítulo no estado
        exibirCapituloArquivoUnico(dadosCapitulo); // Exibe os dados
    }

    // Busca dados nos arquivos por livro (NVI, ACF, AA).
    async function buscarEmArquivoPorLivro(livro, capitulo) {
        const nomeArquivo = normalizarNomeLivro(livro);
        const caminho = `./biblia/${estadoAtual.versao}/${nomeArquivo}.json`;
        const response = await fetch(caminho);
        if (!response.ok) throw new Error(`Arquivo ${caminho} não encontrado.`);
        const dadosDoLivro = await response.json();

        estadoAtual.totalCapitulos = dadosDoLivro.length; // O total de capítulos é o tamanho do array
        const numCapitulo = validarCapitulo(capitulo);

        const objetoCapitulo = dadosDoLivro.find(item => item.hasOwnProperty(numCapitulo));
        if (!objetoCapitulo) throw new Error(`Capítulo ${numCapitulo} inválido para "${livro}".`);
        
        estadoAtual.capitulo = numCapitulo;
        exibirCapituloPorLivro(objetoCapitulo[numCapitulo]);
    }
    
    // --- FUNÇÕES DE EXIBIÇÃO E NAVEGAÇÃO ---

    // Exibe o capítulo vindo do formato de arquivo único.
    function exibirCapituloArquivoUnico(versiculosArray) {
        let html = '';
        versiculosArray.forEach((texto, index) => {
            html += `<p><sup>${index + 1}</sup> ${texto}</p>`;
        });
        textoBiblico.innerHTML = html;
        atualizarControles();
    }

    // Exibe o capítulo vindo do formato de arquivo por livro.
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
        tituloCapitulo.textContent = `${estadoAtual.livro} ${estadoAtual.capitulo}`;
        inputCapitulo.value = estadoAtual.capitulo;

        // Lógica para mostrar/esconder o botão "Anterior".
        btnAnterior.classList.toggle('hidden', estadoAtual.capitulo <= 1);
        // Lógica para mostrar/esconder o botão "Próximo".
        btnProximo.classList.toggle('hidden', estadoAtual.capitulo >= estadoAtual.totalCapitulos);
    }

    // --- FUNÇÕES DE AÇÃO DO UTILIZADOR ---

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

    // Valida o número do capítulo, retornando 1 se for inválido.
    function validarCapitulo(num) {
        const capitulo = parseInt(num);
        if (isNaN(capitulo) || capitulo < 1) {
            return 1; // Retorna 1 como padrão se for inválido
        }
        if (capitulo > estadoAtual.totalCapitulos) {
            return estadoAtual.totalCapitulos; // Retorna o último capítulo se o número for muito alto
        }
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