// O evento 'DOMContentLoaded' espera que todo o HTML da página seja carregado antes de executar o script.
// Isso evita erros de tentar manipular elementos que ainda não existem.
document.addEventListener('DOMContentLoaded', () => {

    // --- SELEÇÃO DOS ELEMENTOS DO HTML ---
    // Guardamos referências aos elementos que vamos manipular frequentemente.
    const listaLivros = document.getElementById('lista-livros'); // A barra lateral inteira
    const btnToggleMenu = document.getElementById('btn-toggle-menu'); // O botão "hambúrguer"
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

    // Evento para o botão do menu responsivo (hambúrguer)
    btnToggleMenu.addEventListener('click', () => {
        listaLivros.classList.toggle('visivel');
    });

    // --- LÓGICA PRINCIPAL ---
    async function carregarCapitulo(livro, capitulo) {
        boasVindas.classList.add('hidden');
        exibicaoCapitulo.classList.remove('hidden');
        textoBiblico.innerHTML = '<p>Carregando...</p>';
        estadoAtual.livro = livro;
        estadoAtual.versao = selectVersao.value;
        
        try {
            // Lógica simplificada após a remoção da versão "AA"
            if (estadoAtual.versao === 'ara' || estadoAtual.versao === 'naa') {
                await buscarEmArquivoUnico(livro, capitulo);
            } else { // Este bloco agora serve para NVI e ACF
                await buscarEmArquivoPorLivro(livro, capitulo);
            }
        } catch (error