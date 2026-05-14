/**
 * Dashboard Admin - JavaScript
 * Funcionalidades da página de painel administrativo
 */

document.addEventListener('DOMContentLoaded', function() {
    // Inicialização do dashboard
    initializeDashboard();
});

/**
 * Inicializa os componentes do dashboard
 */
function initializeDashboard() {
    // Adicionar efeitos de hover aos cards de métrica
    const metricCards = document.querySelectorAll('.metric-card');
    metricCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Atualiza as métricas do dashboard
 */
function refreshMetrics() {
    console.log('Atualizando métricas do dashboard...');
    // Adicione lógica de atualização aqui
}

/**
 * Navega para visualizar todos os usuários
 */
function viewAllUsers() {
    console.log('Navegando para lista de usuários...');
    // Adicione lógica de navegação aqui
}
