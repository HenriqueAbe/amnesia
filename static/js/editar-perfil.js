document.addEventListener('DOMContentLoaded', function() {
    // --- Configuração da Zona de Perigo ---
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

/**
 * Alterna visibilidade da senha (Ícone do Olho)
 */
function togglePw(id, btn) {
    const inp = document.getElementById(id);
    const icon = btn.querySelector('i');
    
    if (inp.type === 'password') {
        inp.type = 'text';
        icon.classList.replace('fa-eye', 'fa-eye-slash');
    } else {
        inp.type = 'password';
        icon.classList.replace('fa-eye-slash', 'fa-eye');
    }
}

/**
 * Validação do Nome: Mínimo 8 letras, sem números ou símbolos.
 * Permite digitar, mas exibe erro.
 */
function validaNome(input) {
    const errorSpan = document.getElementById('error-nome');
    const valor = input.value;
    
    const temInvalido = /[^a-zA-ZÀ-ÿ\s]/.test(valor);
    const muitoCurto = valor.length > 0 && valor.length < 8;

    let mensagem = "";

    if (temInvalido) {
        mensagem = "O nome não pode conter números ou símbolos.";
        input.classList.add('has-error');
    } else if (muitoCurto) {
        mensagem = "O nome deve ter no mínimo 8 caracteres.";
        input.classList.add('has-error');
    } else {
        mensagem = "";
        input.classList.remove('has-error');
    }

    errorSpan.textContent = mensagem;
    return mensagem === "";
}

/**
 * Upload de Foto para o Banco (MEDIUMBLOB)
 */
function handleAvatarUpload(event) {
    const file = event.target.files[0];
    const imgPreview = document.getElementById('imgPreview');
    const initials = document.getElementById('avatarInitials');

    if (!file) return;

    // Validação de 2MB
    if (file.size > 2 * 1024 * 1024) {
        alert("A imagem deve ter no máximo 2MB.");
        return;
    }

    // Preview Local
    const reader = new FileReader();
    reader.onload = function(e) {
        imgPreview.src = e.target.result;
        imgPreview.style.display = 'block';
        if (initials) initials.style.display = 'none';
    }
    reader.readAsDataURL(file);

    // Envio FormData para o Backend
    const formData = new FormData();
    formData.append('foto', file); // O nome aqui deve ser 'foto'

    fetch('/api/upload-avatar', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status !== "success") {
            alert("Erro ao salvar imagem no servidor.");
        }
    })
    .catch(err => console.error("Erro no upload:", err));
}

/**
 * Salva as alterações de Perfil (Nome)
 */
function handleSaveProfile(event) {
    event.preventDefault();
    const inputNome = document.getElementById('inputUsername');
    
    if (!validaNome(inputNome) || inputNome.value.trim() === "") {
        alert("Por favor, corrija os erros no nome antes de salvar.");
        return;
    }

    fetch('/api/update-profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nome_usuario: inputNome.value.trim() })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            alert("Perfil atualizado com sucesso!");
            window.location.reload();
        } else {
            alert("Erro ao atualizar perfil.");
        }
    });
}

/**
 * Altera a Senha
 */
function handleChangePassword(event) {
    event.preventDefault();
    const currentPassword = document.getElementById('inputCurrentPassword').value;
    const newPassword = document.getElementById('inputNewPassword').value;
    const confirm = document.getElementById('inputConfirmPassword').value;

    if (!currentPassword || !newPassword) return alert("Preencha as senhas.");
    if (newPassword !== confirm) return alert("As senhas não coincidem.");
    if (newPassword.length < 8) return alert("A nova senha deve ter 8+ caracteres.");

    fetch('/api/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            current_password: currentPassword, 
            new_password: newPassword 
        })
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            alert("Senha alterada!");
            document.getElementById('securityForm').reset();
        } else {
            alert("Erro: " + (data.message || "Senha atual incorreta."));
        }
    });
}