/**
 * SitePulse AI — Dashboard & Report Visualizer
 * Manages circular gauge animation, Chart.js benchmarks, issue filtering & detail modal
 */

document.addEventListener('DOMContentLoaded', () => {
  initCircularGauge();
  initCoreWebVitalsChart();
  initIssueFilters();
  initShareAndDownload();
});

/* 1. Animate Circular Score Gauge */
function initCircularGauge() {
  const gaugeCircle = document.getElementById('gaugeCircle');
  const scoreEl = document.getElementById('overallScoreValue');
  if (!gaugeCircle || !scoreEl) return;

  const score = parseInt(scoreEl.getAttribute('data-score') || '0', 10);
  const radius = 70;
  const circumference = 2 * Math.PI * radius; // ~440

  gaugeCircle.style.strokeDasharray = circumference;
  
  // Calculate offset (100 = 0 offset, 0 = 440 offset)
  const offset = circumference - (score / 100) * circumference;

  // Determine color based on score
  let strokeColor = '#10B981'; // Green
  if (score < 50) {
    strokeColor = '#EF4444'; // Red
  } else if (score < 80) {
    strokeColor = '#F59E0B'; // Amber
  } else if (score < 90) {
    strokeColor = '#06B6D4'; // Cyan
  }

  gaugeCircle.style.stroke = strokeColor;

  // Trigger animation after slight render delay
  setTimeout(() => {
    gaugeCircle.style.strokeDashoffset = offset;
  }, 150);
}

/* 2. Chart.js Core Web Vitals Comparison */
function initCoreWebVitalsChart() {
  const ctx = document.getElementById('cwvChart');
  if (!ctx || typeof Chart === 'undefined') return;

  // Read data attributes from DOM
  const lcp = parseFloat(ctx.getAttribute('data-lcp') || '2.5');
  const inp = parseFloat(ctx.getAttribute('data-inp') || '150');
  const cls = parseFloat(ctx.getAttribute('data-cls') || '0.05');
  const fcp = parseFloat(ctx.getAttribute('data-fcp') || '1.5');
  const ttfb = parseFloat(ctx.getAttribute('data-ttfb') || '300');

  // Normalize scores to 0-100 percentage for radar/bar comparison
  // LCP: 2.5s is 100%, 4.0s is 50%, >6s is 10%
  const lcpScore = Math.max(10, Math.min(100, Math.round(100 - ((lcp - 1.0) / 4.0) * 100)));
  const inpScore = Math.max(10, Math.min(100, Math.round(100 - (inp / 500) * 100)));
  const clsScore = Math.max(10, Math.min(100, Math.round(100 - (cls / 0.25) * 100)));
  const fcpScore = Math.max(10, Math.min(100, Math.round(100 - ((fcp - 0.8) / 2.5) * 100)));
  const ttfbScore = Math.max(10, Math.min(100, Math.round(100 - (ttfb / 1500) * 100)));

  const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
  const textColor = isDark ? '#94A3B8' : '#475569';
  const gridColor = isDark ? 'rgba(255, 255, 255, 0.08)' : 'rgba(0, 0, 0, 0.08)';

  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['LCP (Loading)', 'INP (Responsiveness)', 'CLS (Stability)', 'FCP (First Paint)', 'TTFB (Server Speed)'],
      datasets: [
        {
          label: 'Your Site Health Benchmark',
          data: [lcpScore, inpScore, clsScore, fcpScore, ttfbScore],
          backgroundColor: 'rgba(99, 102, 241, 0.25)',
          borderColor: '#6366F1',
          pointBackgroundColor: '#06B6D4',
          pointBorderColor: '#FFFFFF',
          pointHoverBackgroundColor: '#FFFFFF',
          pointHoverBorderColor: '#6366F1',
          borderWidth: 2
        },
        {
          label: 'Google "Good" Threshold (100%)',
          data: [100, 100, 100, 100, 100],
          backgroundColor: 'rgba(16, 185, 129, 0.06)',
          borderColor: 'rgba(16, 185, 129, 0.4)',
          borderDash: [4, 4],
          borderWidth: 1.5,
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          min: 0,
          max: 100,
          ticks: {
            stepSize: 25,
            display: false
          },
          grid: {
            color: gridColor
          },
          angleLines: {
            color: gridColor
          },
          pointLabels: {
            color: textColor,
            font: {
              size: 11,
              weight: '600',
              family: "'Inter', sans-serif"
            }
          }
        }
      },
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            color: textColor,
            font: { family: "'Inter', sans-serif", size: 12 },
            boxWidth: 14
          }
        },
        tooltip: {
          backgroundColor: '#0F172A',
          titleFont: { family: "'Inter', sans-serif", weight: 'bold' },
          bodyFont: { family: "'Inter', sans-serif" },
          padding: 10,
          cornerRadius: 8
        }
      }
    }
  });
}

/* 3. Interactive Issue Filtering, Search & Detail Modal */
function initIssueFilters() {
  const searchInput = document.getElementById('issueSearchInput');
  const categoryFilter = document.getElementById('categoryFilter');
  const severityFilter = document.getElementById('severityFilter');
  const issueRows = document.querySelectorAll('.issue-row');
  const visibleCountEl = document.getElementById('visibleIssueCount');
  const emptyStateEl = document.getElementById('noIssuesFound');

  function applyFilters() {
    const searchVal = (searchInput ? searchInput.value : '').toLowerCase().trim();
    const catVal = categoryFilter ? categoryFilter.value : 'all';
    const sevVal = severityFilter ? severityFilter.value : 'all';

    let visibleCount = 0;

    issueRows.forEach(row => {
      const title = row.getAttribute('data-title') || '';
      const cat = row.getAttribute('data-category') || '';
      const sev = row.getAttribute('data-severity') || '';

      const matchesSearch = !searchVal || title.toLowerCase().includes(searchVal);
      const matchesCat = catVal === 'all' || cat.toLowerCase() === catVal.toLowerCase();
      const matchesSev = sevVal === 'all' || sev.toLowerCase() === sevVal.toLowerCase();

      if (matchesSearch && matchesCat && matchesSev) {
        row.style.display = '';
        visibleCount++;
      } else {
        row.style.display = 'none';
      }
    });

    if (visibleCountEl) visibleCountEl.textContent = visibleCount;
    if (emptyStateEl) {
      emptyStateEl.style.display = visibleCount === 0 ? 'block' : 'none';
    }
  }

  if (searchInput) searchInput.addEventListener('input', applyFilters);
  if (categoryFilter) categoryFilter.addEventListener('change', applyFilters);
  if (severityFilter) severityFilter.addEventListener('change', applyFilters);

  // Modal inspection on row click
  const issueModal = new bootstrap.Modal(document.getElementById('issueDetailModal'));
  const modalTitle = document.getElementById('modalIssueTitle');
  const modalCategory = document.getElementById('modalIssueCategory');
  const modalSeverity = document.getElementById('modalIssueSeverity');
  const modalProblem = document.getElementById('modalIssueProblem');
  const modalWhy = document.getElementById('modalIssueWhy');
  const modalFix = document.getElementById('modalIssueFix');
  const modalBenefit = document.getElementById('modalIssueBenefit');

  issueRows.forEach(row => {
    row.addEventListener('click', () => {
      if (modalTitle) modalTitle.textContent = row.getAttribute('data-title');
      if (modalCategory) modalCategory.textContent = row.getAttribute('data-category');
      if (modalSeverity) {
        const sev = row.getAttribute('data-severity');
        modalSeverity.textContent = sev;
        modalSeverity.className = `badge bg-${sev === 'Critical' ? 'danger' : sev === 'High' ? 'warning' : 'info'}`;
      }
      if (modalProblem) modalProblem.textContent = row.getAttribute('data-description') || 'No additional technical description available.';
      if (modalWhy) modalWhy.textContent = row.getAttribute('data-benefit') || 'Resolving this enhances user experience and lighthouse score.';
      if (modalFix) modalFix.textContent = row.getAttribute('data-recommendation') || 'Inspect audit source code to apply best practice guidelines.';
      if (modalBenefit) modalBenefit.textContent = row.getAttribute('data-benefit') || 'Boosts Core Web Vitals and overall site pulse health.';

      issueModal.show();
    });
  });
}

/* 4. Share & Download Actions */
function initShareAndDownload() {
  // Share Button
  const shareBtn = document.getElementById('shareReportBtn');
  if (shareBtn) {
    shareBtn.addEventListener('click', async () => {
      const shareData = {
        title: document.title,
        text: 'Check out this website health report on SitePulse AI:',
        url: window.location.href
      };

      if (navigator.share) {
        try {
          await navigator.share(shareData);
        } catch (err) {
          // User dismissed or aborted share
        }
      } else {
        await copyToClipboard(window.location.href, 'Report link copied to clipboard.');
      }
    });
  }

  // Download / Print Button
  const downloadBtn = document.getElementById('downloadReportBtn');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', () => {
      // Trigger window print with optimized print.css stylesheet
      window.print();
    });
  }
}
