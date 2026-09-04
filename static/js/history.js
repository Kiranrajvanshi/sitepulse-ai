/**
 * SitePulse AI — History Manager
 * Handles asynchronous deletion of individual analysis records and clearing all history
 */

document.addEventListener('DOMContentLoaded', () => {
  initHistoryActions();
});

function initHistoryActions() {
  // 1. Delete Individual Record
  const deleteButtons = document.querySelectorAll('.delete-history-btn');
  deleteButtons.forEach(btn => {
    btn.addEventListener('click', async (e) => {
      e.stopPropagation();
      const analysisId = btn.getAttribute('data-id');
      const domain = btn.getAttribute('data-domain') || 'this website';

      if (!confirm(`Are you sure you want to delete the audit report for ${domain}?`)) {
        return;
      }

      try {
        btn.disabled = true;
        const res = await fetch(`/api/history/${analysisId}`, {
          method: 'DELETE',
          headers: { 'Accept': 'application/json' }
        });

        const data = await res.json();
        if (res.ok && data.success) {
          const row = document.getElementById(`history-row-${analysisId}`);
          if (row) {
            row.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
            row.style.opacity = '0';
            row.style.transform = 'translateX(20px)';
            setTimeout(() => {
              row.remove();
              checkEmptyState();
            }, 300);
          }
          showToast('Analysis record deleted successfully.', 'success');
        } else {
          showToast(data.error || 'Failed to delete record.', 'danger');
          btn.disabled = false;
        }
      } catch (err) {
        showToast('Network error while deleting record.', 'danger');
        btn.disabled = false;
      }
    });
  });

  // 2. Clear All History Confirmation
  const confirmClearBtn = document.getElementById('confirmClearHistoryBtn');
  if (confirmClearBtn) {
    confirmClearBtn.addEventListener('click', async () => {
      try {
        confirmClearBtn.disabled = true;
        const res = await fetch('/api/history/clear', {
          method: 'POST',
          headers: { 'Accept': 'application/json' }
        });

        const data = await res.json();
        if (res.ok && data.success) {
          // Hide modal
          const modalEl = document.getElementById('clearHistoryModal');
          const modal = bootstrap.Modal.getInstance(modalEl);
          if (modal) modal.hide();

          // Refresh or clear table
          const tbody = document.getElementById('historyTableBody');
          if (tbody) tbody.innerHTML = '';
          checkEmptyState();

          showToast('All audit history cleared.', 'success');
        } else {
          showToast(data.error || 'Could not clear history.', 'danger');
        }
      } catch (err) {
        showToast('Network error while clearing history.', 'danger');
      } finally {
        confirmClearBtn.disabled = false;
      }
    });
  }
}

function checkEmptyState() {
  const tbody = document.getElementById('historyTableBody');
  const emptyState = document.getElementById('historyEmptyState');
  const tableContainer = document.getElementById('historyTableContainer');

  if (tbody && tbody.children.length === 0) {
    if (tableContainer) tableContainer.style.display = 'none';
    if (emptyState) emptyState.style.display = 'block';
  }
}
