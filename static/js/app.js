const movieGrid = document.getElementById('movieGrid');
const modal = document.getElementById('modal');
 
const initialMovies = [
    { title: "Pobres Criaturas", info: "Drama • 2023", rating: "4,5", img: "https://picsum.photos/seed/poor/400/600" },
    { title: "Meu Malvado Favorito 4", info: "Animação • 2024", rating: "4,5", img: "https://picsum.photos/seed/minion/400/600" },
    { title: "Deadpool & Wolverine", info: "Ação • 2023", rating: "4,5", img: "https://picsum.photos/seed/dead/400/600" },
    { title: "O Corvo", info: "Fantasia • 2024", rating: "4,5", img: "https://picsum.photos/seed/crow/400/600" }
];
 
function createCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    card.innerHTML = `
        <div class="rating-badge">${movie.rating} / 5 ★</div>
        <img src="${movie.img}" alt="${movie.title}">
        <div class="card-overlay">
            <h3>${movie.title}</h3>
            <p>${movie.info}</p>
        </div>
    `;
    return card;
}
 
function renderMovies() {
    movieGrid.innerHTML = '';
    initialMovies.forEach(m => movieGrid.appendChild(createCard(m)));
}
 
// Modal logic
document.getElementById('btnOpenModal').onclick = () => modal.style.display = 'flex';
function closeModal() { modal.style.display = 'none'; }
 
function addMovie() {
    const title = document.getElementById('m-title').value;
    const genre = document.getElementById('m-genre').value;
    const year = document.getElementById('m-year').value;
    const rating = document.getElementById('m-rating').value;
    const img = document.getElementById('m-img').value || 'https://via.placeholder.com/400x600';
 
    if(!title) return;
 
    initialMovies.push({
        title,
        info: `${genre} • ${year}`,
        rating,
        img
    });
 
    renderMovies();
    closeModal();
    document.querySelectorAll('.modal-content input').forEach(i => i.value = '');
}
 
// Filtro de busca
document.getElementById('searchInput').oninput = function() {
    const term = this.value.toLowerCase();
    const cards = document.querySelectorAll('.movie-card');
    cards.forEach(card => {
        const title = card.querySelector('h3').innerText.toLowerCase();
        card.style.display = title.includes(term) ? 'block' : 'none';
    });
};
 
renderMovies();
 