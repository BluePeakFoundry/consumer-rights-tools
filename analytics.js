(function () {
  'use strict';

  function eventName(raw) {
    return String(raw || '')
      .toLowerCase()
      .replace(/[^a-z0-9:_-]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .slice(0, 120);
  }

  function sendAnalyticsEvent(name, title) {
    var clean = eventName(name);
    if (!clean) return;
    if (window.goatcounter && typeof window.goatcounter.count === 'function') {
      window.goatcounter.count({path: clean, title: title || clean, event: true});
    }
  }

  window.BluePeakAnalytics = {track: sendAnalyticsEvent};

  document.addEventListener('click', function (event) {
    var target = event.target.closest('[data-analytics-event]');
    if (!target) return;
    sendAnalyticsEvent(target.getAttribute('data-analytics-event'), target.getAttribute('data-analytics-title') || target.textContent);
  });

  document.addEventListener('submit', function (event) {
    var form = event.target.closest('[data-analytics-submit]');
    if (!form) return;
    sendAnalyticsEvent(form.getAttribute('data-analytics-submit'), form.getAttribute('aria-label') || form.id || 'form submit');
  });
}());
