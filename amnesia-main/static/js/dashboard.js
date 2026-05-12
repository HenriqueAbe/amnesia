
function remover(btn) {
    if(confirm('Tem certeza que deseja remover este item?')) {
        const tr = btn.closest('tr');
        tr.style.transition = '0.3s';
        tr.style.transform = 'translateX(20px)';
        tr.style.opacity = '0';
        setTimeout(() => tr.remove(), 300);
        showMessage('Item removido do sistema.', 'info');
    }
}

function showMessage(msg, type) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}

function aprovar(btn) {
    const tr = btn.closest('tr');
    showMessage('Operação realizada com sucesso!', 'success');

    tr.style.opacity = '0.5';
    btn.parentElement.innerHTML = '<span class="pill pill-ok">Ativo</span>';
}

const userInput = document.getElementById('userInput');
if (userInput) {
    userInput.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const trs = document.querySelectorAll('.admin-table tbody tr');

        trs.forEach(tr => {
            // Pega todo o texto da linha (nome, email, etc) para filtrar
            const text = tr.textContent.toLowerCase();
            tr.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

function toggleModal(id) {
    const modal = document.getElementById(id);
    if (modal) {
        modal.style.display = (modal.style.display === 'flex') ? 'none' : 'flex';
    }
}

const movieForm = document.querySelector('.admin-form');

if (movieForm) {
    movieForm.addEventListener('submit', function(e) {
        // Aqui você pode validar campos manualmente se quiser
        const titulo = this.querySelector('input[name="titulo"]').value;

        if (titulo.length < 2) {
            e.preventDefault(); // Impede o envio
            showMessage('O título é muito curto!', 'error');
            return;
        }

    });
}