// Dashboard Aves - Scripts Modulares

// Configuración global de Chart.js
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.color = '#6c757d';

// Variables globales
let produccionChart, clasificacionChart, mortalidadChart, financieroChart;

// Inicialización del Dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeProductionForm();
    initializeExportButtons();
    setupAutoRefresh();
});

// Inicializar todas las gráficas
function initializeCharts() {
    initProduccionChart();
    initClasificacionChart();
    initMortalidadChart();
    initFinancieroChart();
}

// Gráfica de Producción (30 días)
function initProduccionChart() {
    const ctx = document.getElementById('produccionChart');
    if (!ctx) return;
    
    produccionChart = new Chart(ctx.getContext('2d'), {
        type: 'line',
        data: {
            labels: window.produccionLabels || [],
            datasets: [{
                label: 'Huevos Comerciales',
                data: window.produccionData || [],
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}

// Gráfica de Clasificación de Huevos
function initClasificacionChart() {
    const ctx = document.getElementById('clasificacionChart');
    if (!ctx) return;
    
    clasificacionChart = new Chart(ctx.getContext('2d'), {
        type: 'doughnut',
        data: {
            labels: ['Yumbo', 'Extra', 'AA', 'A', 'B', 'C', 'Pipo', 'Sucios', 'Totiados', 'Yema'],
            datasets: [{
                data: window.clasificacionData || [0,0,0,0,0,0,0,0,0,0],
                backgroundColor: [
                    '#667eea', '#764ba2', '#f093fb', '#f5576c',
                    '#4facfe', '#00f2fe', '#fa709a', '#fee140',
                    '#a8edea', '#fed6e3'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Gráfica de Mortalidad
function initMortalidadChart() {
    const ctx = document.getElementById('mortalidadChart');
    if (!ctx) return;
    
    mortalidadChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: window.mortalidadLabels || [],
            datasets: [{
                label: 'Mortalidad Diaria',
                data: window.mortalidadData || [],
                backgroundColor: 'rgba(255, 107, 107, 0.8)',
                borderColor: '#ff6b6b',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 10,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            }
        }
    });
}

// Gráfica Financiera
function initFinancieroChart() {
    const ctx = document.getElementById('financieroChart');
    if (!ctx) return;
    
    financieroChart = new Chart(ctx.getContext('2d'), {
        type: 'bar',
        data: {
            labels: ['Ingresos', 'Costos'],
            datasets: [{
                label: 'Monto ($)',
                data: [
                    window.totalIngresos || 0,
                    window.totalCostos || 0
                ],
                backgroundColor: ['#51cf66', '#ff6b6b'],
                borderColor: ['#40c057', '#ff5252'],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        color: 'rgba(0,0,0,0.1)'
                    }
                }
            }
        }
    });
}

// Inicializar formulario de producción diaria
function initializeProductionForm() {
    const form = document.getElementById('dailyProductionForm');
    if (!form) return;
    
    // Establecer fecha actual
    const today = new Date().toISOString().split('T')[0];
    const fechaInput = form.querySelector('#fecha_produccion');
    if (fechaInput) {
        fechaInput.value = today;
    }
    
    // Validación en tiempo real
    const inputs = form.querySelectorAll('input[type="number"]');
    inputs.forEach(input => {
        input.addEventListener('input', validateProductionInput);
    });
    
    // Envío del formulario
    form.addEventListener('submit', handleProductionSubmit);
}

// Validar inputs de producción
function validateProductionInput(event) {
    const input = event.target;
    const value = parseInt(input.value) || 0;
    
    // Validar que no sea negativo
    if (value < 0) {
        input.value = 0;
        showToast('Los valores no pueden ser negativos', 'warning');
    }
    
    // Calcular total automáticamente
    calculateTotalEggs();
}

// Calcular total de huevos
function calculateTotalEggs() {
    const form = document.getElementById('dailyProductionForm');
    if (!form) return;
    
    const eggInputs = form.querySelectorAll('.egg-input');
    let total = 0;
    
    eggInputs.forEach(input => {
        total += parseInt(input.value) || 0;
    });
    
    const totalDisplay = document.getElementById('totalEggs');
    if (totalDisplay) {
        totalDisplay.textContent = total.toLocaleString();
    }
}

// Manejar envío del formulario de producción
function handleProductionSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // Validar que al menos un campo tenga valor
    const eggInputs = form.querySelectorAll('.egg-input');
    let hasValue = false;
    
    eggInputs.forEach(input => {
        if (parseInt(input.value) > 0) {
            hasValue = true;
        }
    });
    
    if (!hasValue) {
        showToast('Debe ingresar al menos un tipo de huevo', 'error');
        return;
    }
    
    // Mostrar loading
    const submitBtn = form.querySelector('.btn-save-production');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Guardando...';
    submitBtn.disabled = true;
    
    // Enviar datos
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
            // Actualizar métricas
            updateDashboardMetrics();
        } else {
            showToast(data.message || 'Error al guardar', 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error de conexión', 'error');
    })
    .finally(() => {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    });
}

// Inicializar botones de exportación
function initializeExportButtons() {
    const exportBtn = document.getElementById('exportHistoryBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportProductionHistory);
    }
}

// Exportar historial de producción
function exportProductionHistory() {
    const btn = document.getElementById('exportHistoryBtn');
    const originalText = btn.textContent;
    
    btn.textContent = 'Exportando...';
    btn.disabled = true;
    
    fetch('/aves/export-production-history/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => {
        if (response.ok) {
            return response.blob();
        }
        throw new Error('Error en la exportación');
    })
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `historial_produccion_${new Date().toISOString().split('T')[0]}.xlsx`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        showToast('Archivo exportado exitosamente', 'success');
    })
    .catch(error => {
        console.error('Error:', error);
        showToast('Error al exportar archivo', 'error');
    })
    .finally(() => {
        btn.textContent = originalText;
        btn.disabled = false;
    });
}

// Actualizar métricas del dashboard
function updateDashboardMetrics() {
    fetch('/aves/dashboard-metrics/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        // Actualizar cards de métricas
        updateMetricCard('total_aves_activas', data.total_aves_activas);
        updateMetricCard('total_huevos_hoy', data.total_huevos_hoy);
        updateMetricCard('postura_7_dias', data.postura_7_dias + '%');
        updateMetricCard('porcentaje_mortalidad', data.porcentaje_mortalidad + '%');
        
        // Actualizar gráficas si es necesario
        if (data.update_charts) {
            updateCharts(data.chart_data);
        }
    })
    .catch(error => {
        console.error('Error updating metrics:', error);
    });
}

// Actualizar card de métrica
function updateMetricCard(metricId, value) {
    const card = document.querySelector(`[data-metric="${metricId}"] .metric-value`);
    if (card) {
        card.textContent = value;
        // Animación de actualización
        card.style.transform = 'scale(1.1)';
        setTimeout(() => {
            card.style.transform = 'scale(1)';
        }, 200);
    }
}

// Actualizar gráficas
function updateCharts(chartData) {
    if (chartData.produccion && produccionChart) {
        produccionChart.data.labels = chartData.produccion.labels;
        produccionChart.data.datasets[0].data = chartData.produccion.data;
        produccionChart.update();
    }
    
    if (chartData.clasificacion && clasificacionChart) {
        clasificacionChart.data.datasets[0].data = chartData.clasificacion.data;
        clasificacionChart.update();
    }
}

// Sistema de notificaciones toast
function showToast(message, type = 'info') {
    // Crear toast si no existe el contenedor
    let toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.id = 'toastContainer';
        toastContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
        `;
        document.body.appendChild(toastContainer);
    }
    
    // Crear toast
    const toast = document.createElement('div');
    const bgColor = {
        'success': '#28a745',
        'error': '#dc3545',
        'warning': '#ffc107',
        'info': '#17a2b8'
    }[type] || '#17a2b8';
    
    toast.style.cssText = `
        background: ${bgColor};
        color: white;
        padding: 12px 20px;
        border-radius: 8px;
        margin-bottom: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    toast.textContent = message;
    
    toastContainer.appendChild(toast);
    
    // Animación de entrada
    setTimeout(() => {
        toast.style.transform = 'translateX(0)';
    }, 100);
    
    // Auto-remove
    setTimeout(() => {
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, 3000);
}

// Auto-refresh del dashboard
function setupAutoRefresh() {
    // Refresh cada 5 minutos
    setInterval(() => {
        updateDashboardMetrics();
    }, 300000);
}

// Utilidades
function formatNumber(num) {
    return new Intl.NumberFormat('es-CO').format(num);
}

function formatCurrency(num) {
    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP'
    }).format(num);
}

// Dashboard JavaScript Functions

// Configuración de gráficas
document.addEventListener('DOMContentLoaded', function() {
    initializeCharts();
    initializeFormHandlers();
});

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
                    showAlert('Producción registrada exitosamente', 'success');
                    form.reset();
                    // Actualizar métricas
                    setTimeout(() => {
                        location.reload();
                    }, 1500);
                } else {
                    showAlert('Error al registrar producción: ' + data.error, 'danger');
                }
            })
            .catch(error => {
                showAlert('Error de conexión', 'danger');
                console.error('Error:', error);
            });
        });
    }
}

// Función para exportar historial
function exportarHistorial() {
    const table = document.getElementById('historialTable');
    const rows = table.querySelectorAll('tr');
    
    let csv = [];
    
    rows.forEach(row => {
        const cols = row.querySelectorAll('td, th');
        const rowData = [];
        
        cols.forEach((col, index) => {
            if (index < cols.length - 1) { // Excluir columna de acciones
                rowData.push('"' + col.textContent.trim() + '"');
            }
        });
        
        if (rowData.length > 0) {
            csv.push(rowData.join(','));
        }
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

// Función para editar producción
function editarProduccion(id) {
    // Implementar modal de edición
    showAlert('Función de edición en desarrollo', 'info');
}

// Función para mostrar alertas
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>
    `;
    
    const container = document.querySelector('.container-fluid');
    container.insertBefore(alertDiv, container.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

// Auto-refresh cada 5 minutos
setInterval(function() {
    location.reload();
}, 300000);