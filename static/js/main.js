/**
 * SitePulse AI — Global Utilities & Theme Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  setupSampleChips();
});

/* Theme Toggle (Dark / Light) */
function initTheme() {
  const savedTheme = localStorage.getItem('sitepulse-theme') || 'dark';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  const toggleBtn = document.getElementById('themeToggleBtn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const nextTheme = currentTheme === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', nextTheme);
      localStorage.setItem('sitepulse-theme', nextTheme);
      updateThemeIcon(nextTheme);
    });
  }
}

function updateThemeIcon(theme) {
  const icon = document.getElementById('themeToggleIcon');
  if (icon) {
    if (theme === 'light') {
      icon.className = 'bi bi-moon-stars-fill';
    } else {
      icon.className = 'bi bi-sun-fill';
    }
  }
}

/* Sample URL quick-fillers */
function setupSampleChips() {
  const chips = document.querySelectorAll('.sample-chip');
  const urlInput = document.getElementById('websiteUrlInput');
  chips.forEach(chip => {
    chip.addEventListener('click', (e) => {
      e.preventDefault();
      const sampleUrl = chip.getAttribute('data-url');
      if (urlInput && sampleUrl) {
        urlInput.value = sampleUrl;
        urlInput.focus();
      }
    });
  });
}

/* Global Toast Notification */
function showToast(message, type = 'info') {
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const iconClass = type === 'success' ? 'bi-check-circle-fill text-success' :
                    type === 'danger' ? 'bi-exclamation-triangle-fill text-danger' :
                    'bi-info-circle-fill text-primary';

  const toastEl = document.createElement('div');
  toastEl.className = 'toast sitepulse-toast align-items-center show mb-2';
  toastEl.setAttribute('role', 'alert');
  toastEl.innerHTML = `
    <div class="d-flex p-2">
      <div class="toast-body d-flex align-items-center gap-2">
        <i class="bi ${iconClass} fs-5"></i>
        <span>${message}</span>
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;

  toastContainer.appendChild(toastEl);

  setTimeout(() => {
    toastEl.classList.remove('show');
    setTimeout(() => toastEl.remove(), 300);
  }, 4000);
}

/* Copy to Clipboard with Toast Fallback */
async function copyToClipboard(text, successMsg = 'Link copied to clipboard!') {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      showToast(successMsg, 'success');
      return true;
    } else {
      // Fallback
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      document.execCommand('copy');
      textArea.remove();
      showToast(successMsg, 'success');
      return true;
    }
  } catch (err) {
    showToast('Failed to copy text', 'danger');
    return false;
  }
}
