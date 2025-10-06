// JavaScript para el Centro de Alertas
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const btnRefresh = document.getElementById('btnRefresh');
    const btnMarkAllRead = document.getElementById('btnMarkAllRead');
    const btnMarcarLeidas = document.getElementById('btnMarcarLeidas');
    const btnMarcarResueltas = document.getElementById('btnMarcarResueltas');
    const filtrosForm = document.getElementById('filtrosForm');
    const checkboxes = document.querySelectorAll('.alert-checkbox');
    const selectAll = document.getElementById('selectAll');

    // Auto-refresh cada 30 segundos
    let autoRefreshInterval;
    
    function startAutoRefresh() {
        autoRefreshInterval = setInterval(() => {
            if (document.visibilityState === 'visible') {
                refreshAlertas();
            }
        }, 30000);
    }

    function stopAutoRefresh() {
        if (autoRefreshInterval) {
            clearInterval(autoRefreshInterval);
        }
    }

    // Iniciar auto-refresh
    startAutoRefresh();

    // Parar auto-refresh cuando la página no está visible
    document.addEventListener('visibilitychange', function() {
        if (document.visibilityState === 'visible') {
            startAutoRefresh();
        } else {
            stopAutoRefresh();
        }
    });

    // Función para refrescar alertas
    function refreshAlertas() {
        if (btnRefresh) {
            btnRefresh.classList.add('spinning');
            btnRefresh.disabled = true;
            
            // Simular refresh (recargar página)
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        }
    }

    // Event listeners
    if (btnRefresh) {
        btnRefresh.addEventListener('click', refreshAlertas);
    }

    if (btnMarkAllRead) {
        btnMarkAllRead.addEventListener('click', function() {
            if (confirm('¿Marcar todas las alertas como leídas?')) {
                marcarTodasLeidas();
            }
        });
    }

    // Manejo de checkboxes
    if (selectAll) {
        selectAll.addEventListener('change', function() {
            checkboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
            });
            updateBulkActions();
        });
    }

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', updateBulkActions);
    });

    function updateBulkActions() {
        const selectedCount = document.querySelectorAll('.alert-checkbox:checked').length;
        
        if (btnMarcarLeidas) {
            btnMarcarLeidas.disabled = selectedCount === 0;
        }
        if (btnMarcarResueltas) {
            btnMarcarResueltas.disabled = selectedCount === 0;
        }

        // Actualizar texto del botón
        if (selectedCount > 0) {
            if (btnMarcarLeidas) {
                btnMarcarLeidas.innerHTML = `<i class="fas fa-eye me-1"></i>Marcar como Leídas (${selectedCount})`;
            }
            if (btnMarcarResueltas) {
                btnMarcarResueltas.innerHTML = `<i class="fas fa-check me-1"></i>Marcar como Resueltas (${selectedCount})`;
            }
        } else {
            if (btnMarcarLeidas) {
                btnMarcarLeidas.innerHTML = '<i class="fas fa-eye me-1"></i>Marcar como Leídas';
            }
            if (btnMarcarResueltas) {
                btnMarcarResueltas.innerHTML = '<i class="fas fa-check me-1"></i>Marcar como Resueltas';
            }
        }
    }

    // Acciones en lote
    if (btnMarcarLeidas) {
        btnMarcarLeidas.addEventListener('click', function() {
            const selectedIds = getSelectedAlertIds();
            if (selectedIds.length > 0) {
                marcarAlertasLeidas(selectedIds);
            }
        });
    }

    if (btnMarcarResueltas) {
        btnMarcarResueltas.addEventListener('click', function() {
            const selectedIds = getSelectedAlertIds();
            if (selectedIds.length > 0) {
                marcarAlertasResueltas(selectedIds);
            }
        });
    }

    function getSelectedAlertIds() {
        const selected = [];
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                selected.push(checkbox.value);
            }
        });
        return selected;
    }

    // Filtros automáticos
    if (filtrosForm) {
        const filterInputs = filtrosForm.querySelectorAll('select, input');
        filterInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Auto-submit después de un pequeño delay
                setTimeout(() => {
                    filtrosForm.submit();
                }, 300);
            });
        });
    }

    // Funciones AJAX
    function marcarAlertasLeidas(alertIds) {
        showLoading('Marcando alertas como leídas...');
        
        fetch('/aves/alertas/marcar-leidas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ alert_ids: alertIds })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showNotification('Alertas marcadas como leídas', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showNotification('Error al marcar alertas', 'error');
            }
        })
        .catch(error => {
            hideLoading();
            showNotification('Error de conexión', 'error');
            console.error('Error:', error);
        });
    }

    function marcarAlertasResueltas(alertIds) {
        showLoading('Marcando alertas como resueltas...');
        
        fetch('/aves/alertas/marcar-resueltas/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({ alert_ids: alertIds })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showNotification('Alertas marcadas como resueltas', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showNotification('Error al marcar alertas', 'error');
            }
        })
        .catch(error => {
            hideLoading();
            showNotification('Error de conexión', 'error');
            console.error('Error:', error);
        });
    }

    function marcarTodasLeidas() {
        showLoading('Marcando todas las alertas como leídas...');
        
        fetch('/aves/alertas/marcar-todas-leidas/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCsrfToken()
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showNotification('Todas las alertas han sido marcadas como leídas', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showNotification('Error al marcar alertas', 'error');
            }
        })
        .catch(error => {
            hideLoading();
            showNotification('Error de conexión', 'error');
            console.error('Error:', error);
        });
    }

    // Utilidades
    function getCsrfToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    function showLoading(message = 'Cargando...') {
        // Crear overlay de loading si no existe
        let overlay = document.getElementById('loadingOverlay');
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.id = 'loadingOverlay';
            overlay.innerHTML = `
                <div class="d-flex justify-content-center align-items-center h-100">
                    <div class="text-center">
                        <div class="loading-spinner mb-2"></div>
                        <div id="loadingMessage">${message}</div>
                    </div>
                </div>
            `;
            overlay.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0,0,0,0.5);
                z-index: 9999;
                color: white;
            `;
            document.body.appendChild(overlay);
        } else {
            document.getElementById('loadingMessage').textContent = message;
            overlay.style.display = 'block';
        }
    }

    function hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    }

    function showNotification(message, type = 'info') {
        // Crear notificación toast
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'success' ? 'success' : 'danger'} alert-dismissible fade show position-fixed`;
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
        toast.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // Auto-remove después de 5 segundos
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 5000);
    }

    // Animaciones de entrada
    const alertCards = document.querySelectorAll('.alert-card, .alert-list-item');
    alertCards.forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('alert-fade-in');
    });

    // Tooltips para botones
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (typeof bootstrap !== 'undefined') {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Funciones globales para uso en templates
function marcarLeida(alertaId) {
    fetch(`/aves/alertas/${alertaId}/marcar-leida/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error al marcar la alerta como leída');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error de conexión');
    });
}

function eliminarAlerta(alertaId) {
    if (confirm('¿Está seguro de que desea eliminar esta alerta?')) {
        fetch(`/aves/alertas/${alertaId}/eliminar/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al eliminar la alerta');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error de conexión');
        });
    }
}

function verDetalleAlerta(alertaId) {
    // Abrir modal con detalles de la alerta
    fetch(`/aves/alertas/${alertaId}/detalle/`)
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostrar modal con los detalles
            const modal = new bootstrap.Modal(document.getElementById('detalleModal'));
            document.getElementById('detalleModalContent').innerHTML = data.html;
            modal.show();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al cargar los detalles');
    });
}