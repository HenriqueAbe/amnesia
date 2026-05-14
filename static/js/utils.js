/**
 * Arquivo de Utilitários
 * Funções auxiliares reutilizáveis em todo o site
 */

/**
 * Cria e exibe um toast (notificação) na tela
 * @param {string} message - Mensagem a exibir
 * @param {string} type - Tipo: 'success', 'error', 'info', 'warning'
 * @param {number} duration - Duração em ms (padrão: 3000)
 */
function showToast(message, type = 'info', duration = 3000) {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        padding: 12px 20px;
        border-radius: 8px;
        font-size: 14px;
        animation: slideIn 0.3s ease;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    `;

    // Cores por tipo
    const colors = {
        success: { bg: '#4ade80', text: '#fff' },
        error: { bg: '#f87171', text: '#fff' },
        info: { bg: '#3b82f6', text: '#fff' },
        warning: { bg: '#fbbf24', text: '#000' }
    };

    const color = colors[type] || colors.info;
    toast.style.backgroundColor = color.bg;
    toast.style.color = color.text;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Formata um número de filme para o padrão brasileiro
 * @param {number} count - Quantidade
 * @returns {string} Texto formatado
 */
function formatMovieCount(count) {
    if (count === 1) return '1 filme';
    return `${count} filmes`;
}

/**
 * Valida se um email é válido
 * @param {string} email - Email a validar
 * @returns {boolean}
 */
function isValidEmail(email) {
    const re = /^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$/;
    return re.test(email);
}

/**
 * Debounce - Aguarda um tempo antes de executar a função
 * @param {Function} func - Função a executar
 * @param {number} wait - Tempo de espera em ms
 * @returns {Function}
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Formata uma data para o padrão brasileiro
 * @param {Date|string} date - Data a formatar
 * @returns {string}
 */
function formatDate(date) {
    if (typeof date === 'string') date = new Date(date);
    const d = new Date(date);
    const day = String(d.getDate()).padStart(2, '0');
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const year = d.getFullYear();
    return `${day}/${month}/${year}`;
}

/**
 * Copia texto para o clipboard
 * @param {string} text - Texto a copiar
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copiado para a área de transferência!', 'success');
    }).catch(() => {
        showToast('Erro ao copiar', 'error');
    });
}

/**
 * Formata um número com separador de milhares
 * @param {number} num - Número a formatar
 * @returns {string}
 */
function formatNumber(num) {
    return num.toLocaleString('pt-BR');
}
