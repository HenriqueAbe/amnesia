/**
 * Sistema de Comentários
 * Funcionalidades para adicionar, editar e deletar comentários
 */

/**
 * Adiciona um novo comentário
 * @param {number} filmeId - ID do filme
 * @param {string} texto - Texto do comentário
 */
function adicionarComentario(filmeId, texto) {
    if (!texto || texto.trim() === '') {
        showToast('O comentário não pode estar vazio', 'warning');
        return;
    }

    // Enviar comentário para o servidor
    fetch('/api/comentarios', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            filme_id: filmeId,
            texto: texto.trim()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Comentário adicionado com sucesso!', 'success');
            // Recarregar comentários
            carregarComentarios(filmeId);
        } else {
            showToast('Erro ao adicionar comentário', 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao adicionar comentário', 'error');
    });
}

/**
 * Carrega os comentários de um filme
 * @param {number} filmeId - ID do filme
 */
function carregarComentarios(filmeId) {
    fetch(`/api/comentarios/${filmeId}`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            renderizarComentarios(data.comentarios);
        }
    })
    .catch(error => {
        console.error('Erro ao carregar comentários:', error);
    });
}

/**
 * Renderiza os comentários na página
 * @param {Array} comentarios - Array de comentários
 */
function renderizarComentarios(comentarios) {
    const container = document.getElementById('comentarios-container');
    if (!container) return;

    container.innerHTML = '';

    if (comentarios.length === 0) {
        container.innerHTML = '<p class="no-comments">Nenhum comentário ainda. Seja o primeiro!</p>';
        return;
    }

    comentarios.forEach(comentario => {
        const comentarioEl = document.createElement('div');
        comentarioEl.className = 'comentario-item';
        comentarioEl.innerHTML = `
            <div class="comentario-header">
                <strong>${comentario.usuario_nome}</strong>
                <span class="comentario-data">${formatDate(comentario.data_criacao)}</span>
            </div>
            <div class="comentario-texto">${escapeHtml(comentario.texto)}</div>
            <div class="comentario-actions">
                <button onclick="editarComentario(${comentario.id})" class="btn-small">Editar</button>
                <button onclick="deletarComentario(${comentario.id})" class="btn-small btn-danger">Deletar</button>
            </div>
        `;
        container.appendChild(comentarioEl);
    });
}

/**
 * Edita um comentário
 * @param {number} comentarioId - ID do comentário
 */
function editarComentario(comentarioId) {
    const novoTexto = prompt('Edite seu comentário:');
    if (novoTexto === null || novoTexto.trim() === '') return;

    fetch(`/api/comentarios/${comentarioId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            texto: novoTexto.trim()
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Comentário atualizado!', 'success');
            // Recarregar comentários
            location.reload();
        } else {
            showToast('Erro ao editar comentário', 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao editar comentário', 'error');
    });
}

/**
 * Deleta um comentário
 * @param {number} comentarioId - ID do comentário
 */
function deletarComentario(comentarioId) {
    if (!confirm('Tem certeza que deseja deletar este comentário?')) return;

    fetch(`/api/comentarios/${comentarioId}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showToast('Comentário deletado!', 'success');
            location.reload();
        } else {
            showToast('Erro ao deletar comentário', 'error');
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        showToast('Erro ao deletar comentário', 'error');
    });
}

/**
 * Escapa caracteres especiais para evitar XSS
 * @param {string} text - Texto a escapar
 * @returns {string}
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Inicializar comentários ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    const filmeId = document.body.getAttribute('data-filme-id');
    if (filmeId) {
        carregarComentarios(filmeId);
    }
});
