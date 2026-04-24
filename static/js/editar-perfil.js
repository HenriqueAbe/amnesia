
/**
 * Cria uma notificação visual dentro do site
 * @param {string} mensagem - O texto que vai aparecer
 * @param {string} tipo - 'sucesso' (roxo) ou 'erro' (vermelho)
 */

function mostrarAviso(mensagem, tipo = 'sucesso') {
    const container = document.getElementById('container-avisos');
    if (!container) return;

    const aviso = document.createElement('div');
    aviso.className = 'aviso-site';
    
    if (tipo === 'erro') {
        aviso.classList.add('erro');
    }
    
    aviso.innerText = mensagem;
    container.appendChild(aviso);

    setTimeout(() => {
        aviso.classList.add('saindo');
        setTimeout(() => aviso.remove(), 300); 
    }, 3000);
}

function showMessage(message, type = 'error') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

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
                    showMessage('Conta excluída com sucesso.', 'success');
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 1500);
                } else {
                    showMessage('Erro ao excluir conta.', 'error');
                }
            })
            .catch(() => showMessage('Erro de conexão.', 'error'));
        });
    }
});


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

    if(errorSpan) errorSpan.textContent = mensagem;
    return mensagem === "";
}

function handleAvatarUpload(event) {
    const file = event.target.files[0];
    const imgPreview = document.getElementById('imgPreview');
    const initials = document.getElementById('avatarInitials');

    if (!file) return;

    if (file.size > 2 * 1024 * 1024) {
        showMessage("A imagem deve ter no máximo 2MB.", "error");
        return;
    }

    const reader = new FileReader();
    reader.onload = function(e) {
        if(imgPreview) {
            imgPreview.src = e.target.result;
            imgPreview.style.display = 'block';
        }
        if (initials) initials.style.display = 'none';
    }
    reader.readAsDataURL(file);

    const formData = new FormData();
    formData.append('foto', file);

    fetch('/api/upload-avatar', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === "success") {
            showMessage("Imagem salva com sucesso!", "success");
        } else {
            showMessage("Erro ao salvar imagem no servidor.", "error");
        }
    })
    .catch(err => {
        console.error("Erro no upload:", err);
        showMessage("Erro de conexão ao enviar imagem.", "error");
    });
}


function handleSaveProfile(event) {
    event.preventDefault();
    const inputNome = document.getElementById('inputUsername');
    
    if (!validaNome(inputNome) || inputNome.value.trim() === "") {
        showMessage("Por favor, corrija os erros no nome antes de salvar.", "error");
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
            showMessage("Perfil atualizado com sucesso!", "success");
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showMessage("Erro ao atualizar perfil.", "error");
        }
    })
    .catch(() => showMessage("Erro de conexão ao salvar o perfil.", "error"));
}


function handleChangePassword(event) {
    event.preventDefault();
    const currentPassword = document.getElementById('inputCurrentPassword').value;
    const newPassword = document.getElementById('inputNewPassword').value;
    const confirm = document.getElementById('inputConfirmPassword').value;

    if (!currentPassword || !newPassword) {
        showMessage("Preencha as senhas.", "error");
        return;
    }
    if (newPassword !== confirm) {
        showMessage("As senhas não coincidem.", "error");
        return;
    }
    if (newPassword.length < 8) {
        showMessage("A nova senha deve ter 8+ caracteres.", "error");
        return;
    }

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
            showMessage("Senha alterada com sucesso!", "success");
            document.getElementById('securityForm').reset();
        } else {
            showMessage("Erro: " + (data.message || "Senha atual incorreta."), "error");
        }
    })
    .catch(() => showMessage("Erro de conexão ao alterar a senha.", "error"));
}