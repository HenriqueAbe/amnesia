document.addEventListener("DOMContentLoaded", function() {
    const nameElement = document.getElementById('userNameDisplay');
    
    // 1. Pega o nome que veio do servidor (Jinja2)
    let currentUserName = nameElement.textContent.trim();

    // 2. Se o nome existir e não for 'Visitante', salva no navegador
    if (currentUserName && currentUserName !== 'Visitante' && currentUserName !== '') {
        localStorage.setItem('userName', currentUserName);
    } 
    // 3. Se por algum motivo o backend não enviou o nome, tenta pegar o salvo anteriormente
    else {
        const savedName = localStorage.getItem('userName');
        if (savedName) {
            nameElement.textContent = savedName;
        }
    }
});

// Função extra: Caso o usuário edite o perfil, chamamos isso para atualizar o menu na hora
function updateMenuName(newName) {
    const nameElement = document.getElementById('userNameDisplay');
    if (nameElement) {
        nameElement.textContent = newName;
        localStorage.setItem('userName', newName);
    }
}

function toggleMenu() {
    const nav = document.getElementById('navMenu');
    nav.classList.toggle('mobile-open');
}

function updateMenuAvatar(base64Image) {
    const avatarImg = document.getElementById('menuAvatar');
    if (avatarImg) {
        avatarImg.src = "data:image/jpeg;base64," + base64Image;
    }
}