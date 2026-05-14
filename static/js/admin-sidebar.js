// Sistema de navegação da sidebar

const sidebarItems = document.querySelectorAll('.sidebar-item');
const adminPages = document.querySelectorAll('.admin-page');
const btnToggleSidebar = document.getElementById('btnToggleSidebar');
const adminContainer = document.querySelector('.admin-container');

// Trocar de página
sidebarItems.forEach(item => {
    item.addEventListener('click', function() {
        const pageId = this.getAttribute('data-page');
        
        // Remover ativo de todos
        sidebarItems.forEach(i => i.classList.remove('active'));
        adminPages.forEach(p => p.style.display = 'none');
        
        // Adicionar ativo ao clicado
        this.classList.add('active');
        document.getElementById(`page-${pageId}`).style.display = 'block';
    });
});

// Toggle sidebar
btnToggleSidebar.addEventListener('click', function() {
    adminContainer.classList.toggle('sidebar-collapsed');
    
    if (adminContainer.classList.contains('sidebar-collapsed')) {
        document.querySelector('.admin-sidebar').classList.add('collapsed');
        btnToggleSidebar.innerHTML = '<i class="fa-solid fa-chevron-right"></i>';
    } else {
        document.querySelector('.admin-sidebar').classList.remove('collapsed');
        btnToggleSidebar.innerHTML = '<i class="fa-solid fa-chevron-left"></i>';
    }
});

// Modal de adicionar filme
const modalFilme = document.getElementById('modalFilme');
const formFilme = document.getElementById('formFilme');
const btnAdicionarFilme = document.getElementById('btnAdicionarFilme');
const btnFecharModal = document.getElementById('btnFecharModal');
const btnCancelar = document.getElementById('btnCancelar');

if (btnAdicionarFilme) {
    btnAdicionarFilme.addEventListener('click', function() {
        modalFilme.style.display = 'flex';
        formFilme.reset();
    });
}

if (btnFecharModal) {
    btnFecharModal.addEventListener('click', function() {
        modalFilme.style.display = 'none';
    });
}

if (btnCancelar) {
    btnCancelar.addEventListener('click', function() {
        modalFilme.style.display = 'none';
    });
}

// Fechar modal ao clicar fora
if (modalFilme) {
    modalFilme.addEventListener('click', function(e) {
        if (e.target === modalFilme) {
            modalFilme.style.display = 'none';
        }
    });
}

// Enviar formulário
if (formFilme) {
    formFilme.addEventListener('submit', function(e) {
        e.preventDefault();
        alert('Filme adicionado com sucesso! (A integração salvará no banco de dados)');
        modalFilme.style.display = 'none';
        formFilme.reset();
    });
}

// Botões de ação da tabela de filmes
document.querySelectorAll('.btn-editar').forEach(btn => {
    btn.addEventListener('click', function() {
        const titulo = this.closest('tr').querySelector('.filme-row span').textContent;
        document.getElementById('titulo').value = titulo;
        modalFilme.style.display = 'flex';
    });
});

document.querySelectorAll('.btn-deletar').forEach(btn => {
    btn.addEventListener('click', function() {
        if (confirm('Deseja deletar este item?')) {
            this.closest('tr').remove();
            alert('Item deletado!');
        }
    });
});

// Botões de ação de comentários
document.querySelectorAll('.btn-aprovar').forEach(btn => {
    btn.addEventListener('click', function() {
        alert('Comentário aprovado! (Será salvo no banco de dados)');
        const statusBadge = this.closest('tr').querySelector('.status-badge');
        statusBadge.textContent = 'Aprovado';
        statusBadge.classList.remove('pendente');
        statusBadge.classList.add('ativo');
    });
});

document.querySelectorAll('.btn-rejeitar').forEach(btn => {
    btn.addEventListener('click', function() {
        alert('Comentário rejeitado! (Será deletado no banco de dados)');
        this.closest('tr').remove();
    });
});

// Botão sair
document.querySelector('.btn-sair').addEventListener('click', function() {
    if (confirm('Deseja sair do painel admin?')) {
        window.location.href = '/';
    }
});

console.log('Sistema de admin carregado com sucesso!');
