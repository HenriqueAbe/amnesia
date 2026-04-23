document.addEventListener('DOMContentLoaded', function() {
    const openBtn = document.getElementById('openConfirm');
    const cancelBtn = document.getElementById('cancelConfirm');
    const confirmBox = document.getElementById('confirmBox');
    const confirmInput = document.getElementById('confirmInput');
    const btnDelete = document.getElementById('btnDelete');
    const PHRASE = 'excluir minha conta';

    if (openBtn) {
        openBtn.addEventListener('click', () => {
            confirmBox.classList.add('visible');
            openBtn.disabled = true;
        });
    }

    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            confirmBox.classList.remove('visible');
            confirmInput.value = '';
            btnDelete.classList.remove('active');
            openBtn.disabled = false;
        });
    }

    if (confirmInput) {
        confirmInput.addEventListener('input', () => {
            const isMatch = confirmInput.value.trim().toLowerCase() === PHRASE;
            btnDelete.classList.toggle('active', isMatch);
        });
    }

    if (btnDelete) {
        btnDelete.addEventListener('click', () => {
            fetch('/api/delete-account', { method: 'POST' })
            .then(res => {
                if (res.ok) {
                    alert('Conta excluída.');
                    window.location.href = '/';
                }
            });
        });
    }
});

function handleSaveProfile(event) {
    event.preventDefault();
    const data = {
        nome_usuario: document.getElementById('inputUsername').value
    };

    fetch('/api/update-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(res => {
        if (res.status === "success") {
            alert("Perfil atualizado!");
            window.location.reload();
        } else {
            alert("Erro ao atualizar.");
        }
    });
}

function handleChangePassword(event) {
    event.preventDefault();
    const currentPassword = document.getElementById('inputCurrentPassword').value;
    const newPassword = document.getElementById('inputNewPassword').value;
    const confirm = document.getElementById('inputConfirmPassword').value;

    if (newPassword !== confirm) return alert("Senhas não coincidem.");

    fetch('/api/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
    })
    .then(res => res.json())
    .then(res => {
        if (res.status === "success") {
            alert("Senha alterada!");
            document.getElementById('securityForm').reset();
        } else {
            alert("Erro: " + (res.message || "Senha atual incorreta"));
        }
    });
}