/**
 * TezMindz Universal Smooth Scroll Reveal Engine
 * Lightweight, hardware-accelerated, child-friendly scroll animations with staggered card reveals.
 */
(function () {
  'use strict';

  function initScrollReveal() {
    // Check for reduced motion preference
    if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
      document.querySelectorAll('.reveal-init, .scroll-reveal, [data-reveal], .stagger-grid > *').forEach(function (el) {
        el.classList.add('is-revealed');
      });
      return;
    }

    // Grid and container selectors whose child cards should automatically stagger
    var staggerSelectors = [
      '.classes-grid-premium',
      '.results-metrics-bar',
      '.achievers-cards-grid',
      '.pricing-cards-grid',
      '.parent-reviews-grid',
      '.parent-reassurance-bar',
      '.parent-trust-summary-bar',
      '.games-row-grid',
      '.leaderboard-podium-grid',
      '.stats-crystals-grid',
      '.subject-cards',
      '.topics-grid',
      '.achievements-grid',
      '.rewards-grid',
      '.stagger-grid',
      '.feature-grid',
      '.about-values-grid',
      '.steps-timeline-grid',
      '.classes-card-grid',
      '.overview-cards-grid',
      '.modules-grid'
    ];

    // Auto-attach reveal & staggered delays to card containers
    staggerSelectors.forEach(function (sel) {
      document.querySelectorAll(sel).forEach(function (container) {
        if (!container.classList.contains('reveal-init') && !container.classList.contains('scroll-reveal')) {
          container.classList.add('scroll-reveal');
        }
        var children = Array.from(container.children);
        children.forEach(function (child, idx) {
          if (!child.classList.contains('reveal-init') && !child.classList.contains('scroll-reveal')) {
            child.classList.add('scroll-reveal');
            var delayMs = Math.min(idx * 80, 480);
            child.style.transitionDelay = delayMs + 'ms';
          }
        });
      });
    });

    // Also auto-target section heading blocks, hero badges, and banners
    document.querySelectorAll('.section-heading-block, .results-bottom-banner, .pricing-trust-strip, .leaderboard-table-card, .final-cta-card, .class-level-banner').forEach(function (el) {
      if (!el.classList.contains('reveal-init') && !el.classList.contains('scroll-reveal')) {
        el.classList.add('scroll-reveal');
      }
    });

    // Collect all elements to reveal
    var revealElements = Array.from(document.querySelectorAll(
      '.reveal-init, .scroll-reveal, [data-reveal], section:not(.no-reveal)'
    ));

    // Deduplicate
    var uniqueTargets = Array.from(new Set(revealElements));

    // Helper: Counter animation
    function animateCounter(el) {
      if (el.dataset.animated === 'true') return;
      el.dataset.animated = 'true';
      var rawTarget = el.getAttribute('data-target') || el.innerText.replace(/[^0-9]/g, '');
      var target = parseInt(rawTarget, 10);
      if (isNaN(target) || target <= 0) return;

      var start = 0;
      var duration = 1200;
      var startTime = null;

      function step(timestamp) {
        if (!startTime) startTime = timestamp;
        var progress = Math.min((timestamp - startTime) / duration, 1);
        // Smooth ease-out cubic
        var easeOut = 1 - Math.pow(1 - progress, 3);
        var current = Math.floor(easeOut * target);
        el.innerText = target > 100 ? current.toLocaleString() : current;
        if (progress < 1) {
          window.requestAnimationFrame(step);
        } else {
          el.innerText = target > 100 ? target.toLocaleString() : target;
        }
      }
      window.requestAnimationFrame(step);
    }

    function revealElement(el) {
      el.classList.add('is-revealed');
      // If element contains counters, animate them
      var counters = el.querySelectorAll('.counter-num, [data-counter]');
      counters.forEach(animateCounter);
      // Also reveal direct children that have scroll-reveal or reveal-init
      var childReveals = el.querySelectorAll('.scroll-reveal, .reveal-init');
      childReveals.forEach(function (c) {
        c.classList.add('is-revealed');
      });
    }

    // Check elements already visible in initial viewport (above fold)
    var vh = window.innerHeight || document.documentElement.clientHeight;
    uniqueTargets.forEach(function (el) {
      var rect = el.getBoundingClientRect();
      if (rect.top < vh * 0.95 && rect.bottom > 0) {
        revealElement(el);
      }
    });

    if ('IntersectionObserver' in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              revealElement(entry.target);
              observer.unobserve(entry.target);
            }
          });
        },
        {
          root: null,
          threshold: 0.08,
          rootMargin: '0px 0px -40px 0px'
        }
      );

      uniqueTargets.forEach(function (el) {
        if (!el.classList.contains('is-revealed')) {
          observer.observe(el);
        }
      });
    } else {
      // Fallback for older browsers
      uniqueTargets.forEach(revealElement);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initScrollReveal);
  } else {
    initScrollReveal();
  }
})();
