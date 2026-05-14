// Elementos da modal
const modalFilme = document.getElementById('modalFilme');
const modalTitulo = document.getElementById('modalTitulo');
const formFilme = document.getElementById('formFilme');
const btnAdicionarFilme = document.getElementById('btnAdicionarFilme');
const btnFecharModal = document.getElementById('btnFecharModal');
const btnCancelar = document.getElementById('btnCancelar');

// Elementos da confirmação de deleção
const modalConfirmacao = document.getElementById('modalConfirmacao');
const btnCancelarConfirmacao = document.getElementById('btnCancelarConfirmacao');
const btnConfirmarDelecao = document.getElementById('btnConfirmarDelecao');

let modoEdicao = false;
let filmeEmEdicao = null;
let filmeParaDeletar = null;

// Abrir modal para adicionar filme
btnAdicionarFilme.addEventListener('click', function() {
    modoEdicao = false;
    modalTitulo.textContent = 'Adicionar novo filme';
    formFilme.reset();
    abrirModal(modalFilme);
});

// Fechar modal
function fecharModal(modal) {
    modal.style.display = 'none';
}

// Abrir modal
function abrirModal(modal) {
    modal.style.display = 'flex';
}

btnFecharModal.addEventListener('click', function() {
    fecharModal(modalFilme);
});

btnCancelar.addEventListener('click', function() {
    fecharModal(modalFilme);
});

// Fechar modal ao clicar fora
modalFilme.addEventListener('click', function(e) {
    if (e.target === modalFilme) {
        fecharModal(modalFilme);
    }
});

modalConfirmacao.addEventListener('click', function(e) {
    if (e.target === modalConfirmacao) {
        fecharModal(modalConfirmacao);
    }
});

// Botões de editar
document.querySelectorAll('.btn-editar').forEach(btn => {
    btn.addEventListener('click', function() {
        const row = this.closest('tr');
        const titulo = row.querySelector('.filme-row span').textContent;
        
        modoEdicao = true;
        filmeEmEdicao = row;
        modalTitulo.textContent = 'Editar filme';
        
        // Preencher formulário com dados
        document.getElementById('titulo').value = titulo;
        document.getElementById('genero').value = 'drama';
        document.getElementById('ano').value = '2023';
        document.getElementById('diretor').value = 'Diretor';
        document.getElementById('duracao').value = '180';
        document.getElementById('avaliacao').value = '8.5';
        document.getElementById('descricao').value = 'Descrição do filme...';
        
        abrirModal(modalFilme);
    });
});

// Botões de deletar
document.querySelectorAll('.btn-deletar').forEach(btn => {
    btn.addEventListener('click', function() {
        filmeParaDeletar = this.closest('tr');
        abrirModal(modalConfirmacao);
    });
});

// Confirmar deleção
btnConfirmarDelecao.addEventListener('click', function() {
    if (filmeParaDeletar) {
        filmeParaDeletar.remove();
        fecharModal(modalConfirmacao);
        filmeParaDeletar = null;
        atualizarMensagemVazia();
    }
});

btnCancelarConfirmacao.addEventListener('click', function() {
    fecharModal(modalConfirmacao);
    filmeParaDeletar = null;
});

// Enviar formulário
formFilme.addEventListener('submit', function(e) {
    e.preventDefault();

    const titulo = document.getElementById('titulo').value;
    const genero = document.getElementById('genero').value;
    const ano = document.getElementById('ano').value;
    const diretor = document.getElementById('diretor').value;
    const status = document.getElementById('status').value;

    if (modoEdicao && filmeEmEdicao) {
        // Atualizar linha existente
        filmeEmEdicao.querySelector('.filme-row span').textContent = titulo;
        filmeEmEdicao.cells[1].textContent = genero;
        filmeEmEdicao.cells[2].textContent = ano;
        filmeEmEdicao.cells[3].textContent = diretor;
        
        const statusBadge = filmeEmEdicao.querySelector('.status-badge');
        statusBadge.textContent = status === 'ativo' ? 'Ativo' : 'Inativo';
        statusBadge.className = `status-badge ${status}`;
    } else {
        // Criar nova linha
        const novaLinha = document.createElement('tr');
        novaLinha.innerHTML = `
            <td class="col-titulo">
                <div class="filme-row">
                    <img src="https://via.placeholder.com/40x60" alt="${titulo}" class="filme-thumbnail">
                    <span>${titulo}</span>
                </div>
            </td>
            <td>${genero}</td>
            <td>${ano}</td>
            <td>${diretor}</td>
            <td><span class="status-badge ${status}">${status === 'ativo' ? 'Ativo' : 'Inativo'}</span></td>
            <td class="col-acoes">
                <button class="btn-table-acao btn-editar" title="Editar">
                    <i class="fa-solid fa-pen"></i>
                </button>
                <button class="btn-table-acao btn-deletar" title="Deletar">
                    <i class="fa-solid fa-trash"></i>
                </button>
            </td>
        `;

        // Adicionar eventos aos novos botões
        novaLinha.querySelector('.btn-editar').addEventListener('click', function() {
            modoEdicao = true;
            filmeEmEdicao = this.closest('tr');
            modalTitulo.textContent = 'Editar filme';
            document.getElementById('titulo').value = titulo;
            abrirModal(modalFilme);
        });

        novaLinha.querySelector('.btn-deletar').addEventListener('click', function() {
            filmeParaDeletar = this.closest('tr');
            abrirModal(modalConfirmacao);
        });

        document.querySelector('tbody').appendChild(novaLinha);
    }

    fecharModal(modalFilme);
    formFilme.reset();
    atualizarMensagemVazia();
});

// Filtrar filmes
document.querySelector('.search-filmes').addEventListener('keyup', function(e) {
    const termo = e.target.value.toLowerCase();
    const linhas = document.querySelectorAll('tbody tr');

    linhas.forEach(linha => {
        const titulo = linha.querySelector('.filme-row span').textContent.toLowerCase();
        if (titulo.includes(termo)) {
            linha.style.display = '';
        } else {
            linha.style.display = 'none';
        }
    });
});

// Atualizar mensagem de tabela vazia
function atualizarMensagemVazia() {
    const tbody = document.querySelector('tbody');
    const linhasVisiveis = Array.from(tbody.querySelectorAll('tr')).filter(
        linha => linha.style.display !== 'none'
    ).length;

    if (linhasVisiveis === 0) {
        const mensagem = document.createElement('tr');
        mensagem.innerHTML = '<td colspan="6" style="text-align: center; padding: 40px; color: var(--text-gray);">Nenhum filme encontrado</td>';
        tbody.appendChild(mensagem);
    }
}

// Inicializar
console.log('Sistema de gerenciamento de filmes carregado com sucesso!');
