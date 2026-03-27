// Dashboard JavaScript

// Lead status update
function updateLeadStatus(leadId, newStatus) {
    fetch(`/dashboard/leads/${leadId}/update-status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: `status=${newStatus}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error updating status');
        }
    });
}

// Follow-up completion
function completeFollowup(followupId) {
    fetch(`/dashboard/followups/${followupId}/complete/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        }
    });
}

// Chart initialization
function initDashboardCharts() {
    // Leads by source chart
    const sourceCtx = document.getElementById('leadsBySourceChart');
    if (sourceCtx) {
        new Chart(sourceCtx, {
            type: 'doughnut',
            data: {
                labels: sourceLabels,
                datasets: [{
                    data: sourceData,
                    backgroundColor: [
                        '#2563eb',
                        '#10b981',
                        '#f59e0b',
                        '#ef4444',
                        '#8b5cf6'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Leads trend chart
    const trendCtx = document.getElementById('leadsTrendChart');
    if (trendCtx) {
        new Chart(trendCtx, {
            type: 'line',
            data: {
                labels: trendLabels,
                datasets: [{
                    label: 'New Leads',
                    data: trendData,
                    borderColor: '#2563eb',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Export leads to Excel
function exportLeads() {
    window.location.href = '/dashboard/export-leads/';
}

// Import leads from Excel
function importLeads() {
    document.getElementById('importFile').click();
}

document.getElementById('importFile')?.addEventListener('change', function(e) {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/dashboard/import-leads/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert(`Imported ${data.count} leads successfully`);
            location.reload();
        } else {
            alert('Error importing leads');
        }
    });
});

// CSRF token helper
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

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initDashboardCharts();
    
    // Date range picker
    flatpickr('.date-range-picker', {
        mode: 'range',
        dateFormat: 'Y-m-d'
    });
    
    // DataTables initialization
    $('.data-table').DataTable({
        pageLength: 25,
        responsive: true,
        language: {
            search: "_INPUT_",
            searchPlaceholder: "Search..."
        }
    });
});