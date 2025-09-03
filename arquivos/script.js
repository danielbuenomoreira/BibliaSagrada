document.addEventListener('DOMContentLoaded', () => {
    // --- ELEMENTOS DO HTML ---
    const modoGuiadaRadio = document.getElementById('modo_guiada');
    const modoLivreRadio = document.getElementById('modo_livre');
    const formGuiada = document.getElementById('form_guiada');
    const formLivre = document.getElementById('form_livre');
    const selectLivro = document.getElementById('livro-select');
    const inputCapitulo = document.getElementById('capitulo-input');
    const inputReferencia = document.getElementById('referencia-input');
    const selectVersao = document.getElementById('versao-select');
    const botaoBusca = document.getElementById('buscar-btn');
    const containerResultado = document.getElementById('resultado-busca');

    // --- DADOS E ESTADO DA APLICAÇÃO ---
    const livrosBiblia = [
        "Gênesis", "Êxodo", "Levítico", "Números", "Deuteronômio", "Josué", "Juízes", "Rute",
        "1 Samuel", "2 Samuel", "1 Reis", "2 Reis", "1 Crônicas", "2 Crônicas", "Esdras", "Neemias", "Ester",
        "Jó", "Salmos", "Provérbios", "Eclesiastes", "Cantares", "Isaías", "Jeremias", "Lamentações de Jeremias",
        "Ezequiel", "Daniel", "Oséias", "Joel", "Amós", "Obadias", "Jonas", "Miquéias", "Naum", "Habacuque",
        "Sofonias", "Ageu", "Zacarias", "Malaquias", "Mateus", "Marcos", "Lucas", "João", "Atos",
        "Romanos", "1 Coríntios", "2 Coríntios", "Gálatas", "Efésios", "Filipenses", "Colossenses",
        "1 Tessalonicenses", "2 Tessalonicenses", "1 Timóteo", "2 Timóteo", "Tito", "Filemom", "Hebreus",
        "Tiago", "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas", "Apocalipse"
    ];

    // --- EVENTOS ---
    modoGuiadaRadio.addEventListener('change', alternarModoBusca);
    modoLivreRadio.addEventListener('change', alternarModoBusca);
    botaoBusca.addEventListener('click', processarBusca);
    
    // --- LÓGICA PRINCIPAL - O "DISTRIBUIDOR" ---
    async function processarBusca() {
        containerResultado.innerHTML = '<p>Buscando...</p>';
        const versao = selectVersao.value;
        let livro, capitulo;

        try {
            // 1. Parsear a entrada do usuário (igual para todos)
            if (modoGuiadaRadio.checked) {
                livro = selectLivro.value;
                capitulo = parseInt(inputCapitulo.value, 10);
                if (!livro || !capitulo) throw new Error("Selecione um livro e um capítulo.");
            } else {
                const referencia = inputReferencia.value.trim();
                if (!referencia) throw new Error("Digite uma referência.");
                const parsed = parseReferencia(referencia);
                livro = parsed.livro;
                capitulo = parsed.capitulo;
            }

            // 2. LÓGICA CONDICIONAL: Escolhe o caminho certo com base na versão
            if (versao === 'ara' || versao === 'naa') {
                await buscarEmArquivoUnico(livro, capitulo, versao);
            } else {
                await buscarEmArquivoPorLivro(livro, capitulo, versao);
            }

        } catch (error) {
            containerResultado.innerHTML = `<p style="color: red;">${error.message}</p>`;
        }
    }

    // --- CAMINHO 1: Lógica para ARA e NAA (Arquivo único) ---
    async function buscarEmArquivoUnico(livro, capitulo, versao) {
        const caminhoArquivo = `./biblia/${versao.toUpperCase()}.json`;
        const response = await fetch(caminhoArquivo);
        if (!response.ok) throw new Error(`Não foi possível carregar o arquivo principal ${versao.toUpperCase()}.json`);
        const dadosBiblia = await response.json();

        // Encontra o livro pelo nome no array da Bíblia inteira
        const dadosLivro = dadosBiblia.find(b => b.name === livro);
        if (!dadosLivro) throw new Error(`Livro "${livro}" não encontrado na versão ${versao.toUpperCase()}.`);

        // Acessa o capítulo pelo índice do array (capítulo 1 está no índice 0)
        const dadosCapitulo = dadosLivro.chapters[capitulo - 1];
        if (!dadosCapitulo) throw new Error(`Capítulo ${capitulo} não encontrado em "${livro}".`);

        exibirCapituloArquivoUnico(livro, capitulo, dadosCapitulo);
    }

    // --- CAMINHO 2: Lógica para NVI, ACF, AA (Arquivos por livro) ---
    async function buscarEmArquivoPorLivro(livro, capitulo, versao) {
        const nomeArquivo = normalizarNomeLivro(livro);
        const caminhoArquivo = `./biblia/${versao}/${nomeArquivo}.json`;
        const response = await fetch(caminhoArquivo);
        if (!response.ok) throw new Error(`Não foi possível encontrar o livro "${livro}". Verifique se o arquivo "${nomeArquivo}.json" existe na pasta "${versao}".`);
        const dadosDoLivro = await response.json();

        const objetoCapitulo = dadosDoLivro.find(item => item.hasOwnProperty(capitulo));
        if (!objetoCapitulo) throw new Error(`Capítulo ${capitulo} não encontrado em "${livro}".`);
        
        const versiculos = objetoCapitulo[capitulo];
        exibirCapituloPorLivro(livro, capitulo, versiculos);
    }

    // --- FUNÇÕES DE EXIBIÇÃO (Uma para cada tipo de dado) ---
    function exibirCapituloArquivoUnico(livro, capitulo, versiculosArray) {
        let html = `<h2>${livro} ${capitulo}</h2>`;
        // Itera sobre o array de versículos, usando o índice+1 como número do versículo
        versiculosArray.forEach((texto, index) => {
            const numeroVersiculo = index + 1;
            html += `<p><sup>${numeroVersiculo}</sup> ${texto}</p>`;
        });
        containerResultado.innerHTML = html;
    }
    
    function exibirCapituloPorLivro(livro, capitulo, versiculosObjeto) {
        let html = `<h2>${livro} ${capitulo}</h2>`;
        // Itera sobre as chaves do objeto de versículos
        for (const numeroVersiculo in versiculosObjeto) {
            const textoVersiculo = versiculosObjeto[numeroVersiculo];
            html += `<p><sup>${numeroVersiculo}</sup> ${textoVersiculo}</p>`;
        }
        containerResultado.innerHTML = html;
    }

    // --- FUNÇÕES AUXILIARES (de parsing e normalização) ---
    function parseReferencia(ref) {
        const ultimoEspacoIndex = ref.lastIndexOf(' ');
        if (ultimoEspacoIndex === -1) throw new Error("Formato de referência inválido. Use 'Livro Capítulo'.");
        const nomeLivro = ref.substring(0, ultimoEspacoIndex).trim();
        const numCapitulo = parseInt(ref.substring(ultimoEspacoIndex + 1), 10);
        if (!nomeLivro || isNaN(numCapitulo)) throw new Error("Formato de referência inválido.");
        const livroCanonico = livrosBiblia.find(l => normalizarNomeLivro(l).startsWith(normalizarNomeLivro(nomeLivro)));
        if (!livroCanonico) throw new Error(`Livro "${nomeLivro}" não reconhecido.`);
        return { livro: livroCanonico, capitulo: numCapitulo };
    }

    function normalizarNomeLivro(nome) {
        return nome.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, "");
    }

    function popularLivros() {
        selectLivro.innerHTML = '<option value="">Selecione um livro</option>';
        livrosBiblia.forEach(livro => {
            const option = new Option(livro, livro);
            selectLivro.add(option);
        });
    }

    function alternarModoBusca() {
        formGuiada.classList.toggle('hidden', !modoGuiadaRadio.checked);
        formLivre.classList.toggle('hidden', modoGuiadaRadio.checked);
    }

    // --- INICIALIZAÇÃO ---
    popularLivros();
    alternarModoBusca();
});