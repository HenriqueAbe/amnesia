
function filtrarStatus(status, btn) {
    document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');

    const cards = document.querySelectorAll('.fav-card');
    let visiveis = 0;

    cards.forEach(card => {
        const matches = (status === 'todos' || card.dataset.status === status);

        if (matches) {
            card.style.display = 'block';
            visiveis++;
        } else {
            card.style.display = 'none';
        }
    });

    const emptyState = document.getElementById('emptyState');
    if (emptyState) {
        emptyState.style.display = visiveis === 0 ? 'block' : 'none';
    }
}

function removerFavorito(btn) {
    const card = btn.closest('.fav-card');
    const titulo = card.querySelector('.fav-card-title').textContent;

    if (confirm(`Remover "${titulo}" da sua biblioteca?`)) {
        // Animação de saída
        card.style.transition = 'all 0.3s ease';
        card.style.opacity = '0';
        card.style.transform = 'scale(0.9)';

        setTimeout(() => {
            card.remove();

            if (typeof showMessage === 'function') {
                showMessage('Filme removido com sucesso!', 'info');
            } else {
                alert('Filme removido!');
            }

            atualizarContadores();
        }, 300);
    }
}

function atualizarContadores() {
    const cards = document.querySelectorAll('.fav-card');
    const total = cards.length;

    const totalChip = document.querySelector('.filter-chip.active .count');
    if (totalChip) {
        totalChip.textContent = total;
    }
}