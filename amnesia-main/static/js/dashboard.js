function aprovar(btn) {
    const tr = btn.closest('tr');
    // Simulação de lógica que você pode integrar com seu backend depois
    showMessage('Comentário aprovado com sucesso!', 'success');

    tr.style.opacity = '0.5';
    btn.parentElement.innerHTML = '<span class="pill pill-ok">Aprovado</span>';
}

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
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = msg;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 3000);
}