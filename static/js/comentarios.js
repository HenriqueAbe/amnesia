function toggleFav(btn) {
    const icon = btn.querySelector('i');
    btn.classList.toggle('active');

    if (icon.classList.contains('fa-regular')) {
        icon.className = 'fa-solid fa-heart';
        btn.style.color = '#ff4d4d';
        showMessage('Adicionado aos favoritos!', 'success');
    } else {
        icon.className = 'fa-regular fa-heart';
        btn.style.color = 'var(--text-gray)';
        showMessage('Removido dos favoritos.', 'info');
    }
}

function toggleLike(btn) {
    btn.classList.toggle('liked');
    let count = parseInt(btn.textContent);
    btn.innerHTML = btn.classList.contains('liked')
        ? `<i class="fa-solid fa-heart"></i> ${count + 1}`
        : `<i class="fa-regular fa-heart"></i> ${count - 1}`;
}

function enviarAvaliacao(event) {
    event.preventDefault();

    const nota = document.querySelector('input[name="nota"]:checked');
    const comentario = document.getElementById('comentario').value;

    if (!nota) {
        showMessage('Por favor, seleciona uma nota!', 'warning');
        return;
    }

    const lista = document.getElementById('listaComentarios');
    const novoCard = document.createElement('div');
    novoCard.className = 'comment-card';

    novoCard.style.opacity = '0';
    novoCard.style.transform = 'translateY(-10px)';

    novoCard.innerHTML = `
        <div class="comment-user">
            <div class="mini-avatar" style="background: var(--purple)">VC</div>
            <div class="comment-user-info">
                <span class="comment-username">@você</span>
                <span class="comment-date">agora mesmo</span>
            </div>
            <div class="user-score">${nota.value}/10</div>
        </div>
        <p class="comment-text">${comentario || '(Sem comentário)'}</p>
        <div class="comment-footer">
            <button class="btn-like" onclick="toggleLike(this)"><i class="fa-regular fa-heart"></i> 0</button>
        </div>
    `;

    lista.prepend(novoCard);

    setTimeout(() => {
        novoCard.style.transition = 'all 0.4s';
        novoCard.style.opacity = '1';
        novoCard.style.transform = 'translateY(0)';
    }, 50);

    showMessage('Avaliação enviada com sucesso!', 'success');
    document.getElementById('ratingForm').reset();
}