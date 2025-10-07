// JavaScript para el Centro de Alertas
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const btnRefresh = document.getElementById('btnRefresh');
    const btnMarkAllRead = document.getElementById('btnMarkAllRead');
    const btnMarcarLeidas = document.getElementById('btnMarcarLeidas');
    const btnMarcarResueltas = document.getElementById('btnMarcarResueltas');
    const filtrosForm = document.getElementById('filtrosForm');
    const checkboxes = document.querySelectorAll('.alerta-checkbox'); // Corregido
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
        const selectedCount = document.querySelectorAll('.alerta-checkbox:checked').length; // Corregido
        
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
                marcarAlertasMasivo('leida', selectedIds);
            }
        });
    }

    if (btnMarcarResueltas) {
        btnMarcarResueltas.addEventListener('click', function() {
            const selectedIds = getSelectedAlertIds();
            if (selectedIds.length > 0) {
                marcarAlertasMasivo('resuelta', selectedIds);
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

    // Función unificada para marcar alertas masivo
    function marcarAlertasMasivo(accion, alertaIds) {
        const mensaje = accion === 'leida' ? 'leídas' : 'resueltas';
        
        if (!confirm(`¿Marcar ${alertaIds.length} alertas como ${mensaje}?`)) {
            return;
        }
        
        showLoading(`Marcando alertas como ${mensaje}...`);
        
        fetch('/aves/alertas/marcar-masivo/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken()
            },
            body: JSON.stringify({
                'accion': accion,
                'alertas_ids': alertaIds
            })
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                showNotification(`${data.count} alertas marcadas como ${mensaje}`, 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                showNotification('Error al marcar alertas: ' + data.error, 'error');
            }
        })
        .catch(error => {
            hideLoading();
            showNotification('Error de conexión', 'error');
            console.error('Error:', error);
        });
    }

    function marcarTodasLeidas() {
        fetch('/aves/alertas/marcar-masivo/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                'accion': 'leida',
                'alertas': 'todas'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification('Todas las alertas han sido marcadas como leídas', 'success');
                setTimeout(() => {
                    window.location.reload();
                }, 1500);
            } else {
                showNotification('Error al marcar las alertas: ' + data.error, 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error de conexión', 'error');
        });
    }

    // Utilidades
    function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

    function showLoading(message) {
        // Crear o mostrar indicador de carga
        let loadingDiv = document.getElementById('loadingIndicator');
        if (!loadingDiv) {
            loadingDiv = document.createElement('div');
            loadingDiv.id = 'loadingIndicator';
            loadingDiv.className = 'alert alert-info position-fixed top-0 start-50 translate-middle-x mt-3';
            loadingDiv.style.zIndex = '9999';
            document.body.appendChild(loadingDiv);
        }
        loadingDiv.innerHTML = `<i class="fas fa-spinner fa-spin me-2"></i>${message}`;
        loadingDiv.style.display = 'block';
    }

    function hideLoading() {
        const loadingDiv = document.getElementById('loadingIndicator');
        if (loadingDiv) {
            loadingDiv.style.display = 'none';
        }
    }

    function showNotification(message, type) {
        // Crear notificación toast
        const toastDiv = document.createElement('div');
        toastDiv.className = `alert alert-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'warning'} position-fixed top-0 end-0 mt-3 me-3`;
        toastDiv.style.zIndex = '9999';
        toastDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
        `;
        document.body.appendChild(toastDiv);
        
        // Auto-remover después de 5 segundos
        setTimeout(() => {
            if (toastDiv.parentElement) {
                toastDiv.remove();
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
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Alerta marcada como leída', 'success');
            // Actualizar la fila en la tabla
            const row = document.querySelector(`tr[data-id="${alertaId}"]`);
            if (row) {
                row.classList.remove('table-warning');
                const estadoCell = row.querySelector('td:nth-child(7)');
                if (estadoCell) {
                    estadoCell.innerHTML = '<span class="badge bg-primary">Leída</span>';
                }
            }
        } else {
            showNotification('Error al marcar la alerta: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión', 'error');
    });
}

function marcarResuelta(alertaId) {
    if (!confirm('¿Está seguro de marcar esta alerta como resuelta?')) {
        return;
    }
    
    fetch(`/aves/alertas/${alertaId}/marcar-resuelta/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Alerta marcada como resuelta', 'success');
            // Remover la fila o actualizar su estado
            const row = document.querySelector(`tr[data-id="${alertaId}"]`);
            if (row) {
                row.style.opacity = '0.5';
                const estadoCell = row.querySelector('td:nth-child(7)');
                if (estadoCell) {
                    estadoCell.innerHTML = '<span class="badge bg-success">Resuelta</span>';
                }
            }
        } else {
            showNotification('Error al resolver la alerta: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión', 'error');
    });
}

// Función para marcar múltiples alertas
function marcarAlertasMasivo(accion) {
    const selectedCheckboxes = document.querySelectorAll('.alerta-checkbox:checked');
    const alertaIds = Array.from(selectedCheckboxes).map(cb => cb.value);
    
    if (alertaIds.length === 0) {
        showNotification('Seleccione al menos una alerta', 'warning');
        return;
    }
    
    const mensaje = accion === 'leida' ? 'leídas' : 'resueltas';
    if (!confirm(`¿Marcar ${alertaIds.length} alertas como ${mensaje}?`)) {
        return;
    }
    
    fetch('/aves/alertas/marcar-masivo/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({
            'accion': accion,
            'alertas': alertaIds
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(`${data.count} alertas marcadas como ${mensaje}`, 'success');
            setTimeout(() => {
                window.location.reload();
            }, 1500);
        } else {
            showNotification('Error al procesar las alertas: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error de conexión', 'error');
    });
}