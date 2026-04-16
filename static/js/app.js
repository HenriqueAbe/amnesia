const modal = document.getElementById('modal');

// Abrir e Fechar Modal
document.getElementById('btnOpenModal').onclick = () => modal.style.display = 'flex';
function closeModal() { modal.style.display = 'none'; }

// Fechar modal ao clicar fora dele
window.onclick = (event) => {
    if (event.target == modal) closeModal();
}

// Filtro de busca em tempo real (Funciona nos cards renderizados pelo Jinja2)
document.getElementById('searchInput').oninput = function() {
    const term = this.value.toLowerCase();
    const cards = document.querySelectorAll('.movie-card');
    
    cards.forEach(card => {
        const title = card.querySelector('h3').innerText.toLowerCase();
        // Se o título incluir o que foi digitado, mostra, senão esconde
        card.style.display = title.includes(term) ? 'block' : 'none';
    });
};