// Aves Module - Scripts sin plantillas Django

// Configuración global de Chart.js
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.color = '#6c757d';

// Variables globales para las gráficas
let produccionChart, clasificacionChart, mortalidadChart, financieroChart;

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeFormHandlers();
    initializeExportButtons();
    setupAutoRefresh();
});

function initializeCharts() {
    // Obtener datos del JSON script
    const chartData = JSON.parse(document.getElementById('chart-data').textContent);
    
    // Gráfica de Producción
    const produccionCtx = document.getElementById('produccionChart');
    if (produccionCtx && chartData.fechas_produccion) {
        new Chart(produccionCtx, {
            type: 'line',
            data: {
                labels: chartData.fechas_produccion,
                datasets: [{
                    label: 'Huevos Producidos',
                    data: chartData.datos_produccion,
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // Gráfica de Clasificación
    const clasificacionCtx = document.getElementById('clasificacionChart');
    if (clasificacionCtx && chartData.datos_clasificacion) {
        new Chart(clasificacionCtx, {
            type: 'doughnut',
            data: {
                labels: ['Extra', 'AA', 'A', 'B', 'C'],
                datasets: [{
                    data: chartData.datos_clasificacion,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    }

    // Gráfica de Mortalidad
    const mortalidadCtx = document.getElementById('mortalidadChart');
    if (mortalidadCtx && chartData.fechas_mortalidad) {
        new Chart(mortalidadCtx, {
            type: 'bar',
            data: {
                labels: chartData.fechas_mortalidad,
                datasets: [{
                    label: 'Mortalidad Real',
                    data: chartData.datos_mortalidad,
                    backgroundColor: 'rgba(255, 99, 132, 0.8)'
                }, {
                    label: 'Objetivo (< 0.1%)',
                    data: Array(chartData.fechas_mortalidad.length).fill(0.1),
                    type: 'line',
                    borderColor: 'rgb(255, 205, 86)',
                    backgroundColor: 'rgba(255, 205, 86, 0.2)'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 1
                    }
                }
            }
        });
    }

    // Gráfica Financiera
    const financieroCtx = document.getElementById('financieroChart');
    if (financieroCtx && chartData.costos_mes) {
        new Chart(financieroCtx, {
            type: 'bar',
            data: {
                labels: ['Ingresos', 'Costos'],
                datasets: [{
                    label: 'Monto ($)',
                    data: [
                        chartData.costos_mes.total_ingresos || 0, 
                        chartData.costos_mes.total_costos || 0
                    ],
                    backgroundColor: ['rgba(40, 167, 69, 0.8)', 'rgba(220, 53, 69, 0.8)']
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
}

function initializeFormHandlers() {
    // Manejo del formulario de producción diaria
    const form = document.getElementById('produccionDiariaForm');
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(form);
            
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Producción registrada exitosamente', 'success');
                    form.reset();
                    updateDashboardMetrics();
                } else {
                    showToast('Error al registrar producción: ' + data.error, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showToast('Error de conexión', 'error');
            });
        });
    }
}

function initializeExportButtons() {
    const exportBtn = document.getElementById('exportHistorial');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportProductionHistory);
    }
}

function exportProductionHistory() {
    const table = document.getElementById('historialTable');
    if (!table) return;
    
    const rows = table.querySelectorAll('tr');
    let csv = [];

    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        cols.forEach(col => {
            rowData.push('"' + col.textContent.replace(/"/g, '""') + '"');
        });
        csv.push(rowData.join(','));
    });

    const csvContent = csv.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');

    if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', 'historial_produccion_' + new Date().toISOString().split('T')[0] + '.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

function updateDashboardMetrics() {
    fetch('/aves/api/metrics/')
        .then(response => response.json())
        .then(data => {
            updateMetricCard('total-aves', data.total_aves_activas);
            updateMetricCard('huevos-hoy', data.huevos_comerciales_hoy);
            updateMetricCard('gramos-ave', data.gramos_ave_dia);
            updateMetricCard('utilidad-mes', data.utilidad_mes);
        })
        .catch(error => console.error('Error updating metrics:', error));
}

function updateMetricCard(metricId, value) {
    const element = document.getElementById(metricId);
    if (element) {
        element.textContent = formatNumber(value);
    }
}

function showToast(message, type = 'info') {
    // Crear elemento toast
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <div class="toast-content">
            <span class="toast-message">${message}</span>
            <button class="toast-close" onclick="this.parentElement.parentElement.remove()">&times;</button>
        </div>
    `;
    
    // Agregar al DOM
    document.body.appendChild(toast);
    
    // Auto-remover después de 5 segundos
    setTimeout(() => {
        if (toast.parentElement) {
            toast.remove();
        }
    }, 5000);
}

function setupAutoRefresh() {
    // Actualizar métricas cada 5 minutos
    setInterval(updateDashboardMetrics, 300000);
}

function formatNumber(num) {
    return new Intl.NumberFormat('es-CO').format(num);
}

function formatCurrency(num) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
    }).format(num);
}