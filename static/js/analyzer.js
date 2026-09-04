/**
 * SitePulse AI — Analyzer Orchestrator
 * Handles URL validation, interactive step-by-step progress modal, and API submission
 */

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('analyzerForm');
  const urlInput = document.getElementById('websiteUrlInput');
  const errorMsg = document.getElementById('analyzerError');

  if (!form || !urlInput) return;

  // Clean error message on typing
  urlInput.addEventListener('input', () => {
    if (errorMsg) {
      errorMsg.style.display = 'none';
      errorMsg.textContent = '';
    }
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    let rawUrl = urlInput.value.trim();

    // 1. Client-Side Validation
    if (!rawUrl) {
      showError('Please enter a website URL to analyze.');
      urlInput.focus();
      return;
    }

    // Auto-prepend https:// if missing
    if (!/^https?:\/\//i.test(rawUrl)) {
      rawUrl = 'https://' + rawUrl;
      urlInput.value = rawUrl;
    }

    // Domain validation regex
    const urlPattern = /^(https?:\/\/)?([a-zA-Z0-9]([a-zA-Z0-9\-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(:\d+)?(\/.*)?$/i;
    const isLocalhost = /^https?:\/\/(localhost|127\.0\.0\.1)(:\d+)?(\/.*)?$/i.test(rawUrl);

    if (!urlPattern.test(rawUrl) && !isLocalhost) {
      showError('Please enter a valid website address (e.g. example.com or stripe.com).');
      urlInput.focus();
      return;
    }

    // 2. Open Animated Loading Overlay
    openLoadingSequence(rawUrl);

    // 3. Dispatch AJAX Request to Backend
    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({ url: rawUrl })
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        closeLoadingSequence();
        showError(data.error || 'Failed to complete analysis. Please check the URL and try again.');
        return;
      }

      // 4. Smoothly finish step sequence and redirect to report
      completeLoadingSequence(data.report_url);

    } catch (err) {
      closeLoadingSequence();
      showError('Network connection error. Please verify your internet connection and try again.');
    }
  });

  function showError(msg) {
    if (errorMsg) {
      errorMsg.textContent = msg;
      errorMsg.style.display = 'block';
    } else {
      showToast(msg, 'danger');
    }
  }
});

/* Step Animation Orchestration */
const stepIntervals = [];

function openLoadingSequence(targetUrl) {
  const overlay = document.getElementById('loadingOverlay');
  const targetDisplay = document.getElementById('loadingTargetUrl');
  if (targetDisplay) targetDisplay.textContent = targetUrl;
  if (!overlay) return;

  overlay.style.display = 'flex';

  const steps = [
    { id: 'step-1', delay: 400 },   // Checking website...
    { id: 'step-2', delay: 1800 },  // Fetching performance data...
    { id: 'step-3', delay: 3600 },  // Analyzing SEO...
    { id: 'step-4', delay: 5200 },  // Checking accessibility...
    { id: 'step-5', delay: 6800 },  // Processing Core Web Vitals...
    { id: 'step-6', delay: 8400 }   // Preparing your report...
  ];

  // Reset steps
  steps.forEach(s => {
    const el = document.getElementById(s.id);
    if (el) {
      el.className = 'step-item';
      const icon = el.querySelector('i');
      if (icon) icon.className = 'bi bi-circle';
    }
  });

  // Schedule animations
  steps.forEach((s, idx) => {
    const timer = setTimeout(() => {
      // Mark previous completed
      if (idx > 0) {
        const prevEl = document.getElementById(steps[idx - 1].id);
        if (prevEl) {
          prevEl.className = 'step-item completed';
          const icon = prevEl.querySelector('i');
          if (icon) icon.className = 'bi bi-check-circle-fill';
        }
      }
      // Mark current active
      const curEl = document.getElementById(s.id);
      if (curEl) {
        curEl.className = 'step-item active';
        const icon = curEl.querySelector('i');
        if (icon) icon.className = 'bi bi-arrow-repeat spin-icon';
      }
    }, s.delay);
    stepIntervals.push(timer);
  });
}

function completeLoadingSequence(redirectUrl) {
  // Clear any pending timers
  stepIntervals.forEach(t => clearTimeout(t));

  // Mark all steps complete
  for (let i = 1; i <= 6; i++) {
    const el = document.getElementById(`step-${i}`);
    if (el) {
      el.className = 'step-item completed';
      const icon = el.querySelector('i');
      if (icon) icon.className = 'bi bi-check-circle-fill';
    }
  }

  // Short delay so user sees satisfaction of completion
  setTimeout(() => {
    window.location.href = redirectUrl;
  }, 600);
}

function closeLoadingSequence() {
  stepIntervals.forEach(t => clearTimeout(t));
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.style.display = 'none';
}
