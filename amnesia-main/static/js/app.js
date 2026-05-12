// Filtro de busca em tempo real
document.getElementById('searchInput').addEventListener('input', function() {
    const term = this.value.toLowerCase();
    const cards = document.querySelectorAll('.movie-card');
    
    cards.forEach(card => {
        const title = card.querySelector('h3').innerText.toLowerCase();
        card.style.display = title.includes(term) ? 'block' : 'none';
    });
});