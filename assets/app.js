/* ===========================================================
   Perazim Church Site v5 — Unified Dynamic Engine
   Reference: VOUS / ELEVATION / PASSION City Church benchmarks.

   STRUCTURE (in IIFE order, all DOMContentLoaded-aware):
   1. Mouse-parallax ambient SVG (hero + values)
   2. 3D tilt on .tilt-card / .campus-card
   3. Slider prev/next on .campus-grid
   4. Smooth scroll for hash anchors
   5. Nav link focus class
   6. Image onerror → CSS gradient fallback
   7. Theme toggle (3-state cycle: light → dark → auto)
   8. Scroll-reveal (IntersectionObserver)
   9. Sticky navbar morph on scroll

   prefers-reduced-motion respected globally.
   =========================================================== */

(function () {
  'use strict';

  var prefersReduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ============================================================
  // 1. MOUSE-PARALLAX for ambient SVG watermarks
  //    v5 spec: hero intensity 0.045, values intensity 0.035
  // ============================================================
  function attachParallax(container, element, intensity) {
    if (!container || !element || prefersReduce) return;
    var rafId = null;
    container.addEventListener('mousemove', function (e) {
      if (rafId) return;
      rafId = requestAnimationFrame(function () {
        var rect = container.getBoundingClientRect();
        var x = (e.clientX - rect.left - rect.width / 2) * intensity;
        var y = (e.clientY - rect.top - rect.height / 2) * intensity;
        element.style.transform =
          'translate3d(' + x + 'px,' + y + 'px,0) rotate(' + (x * 0.03) + 'deg)';
        rafId = null;
      });
    });
    container.addEventListener('mouseleave', function () {
      element.style.transform = 'translate3d(0,0,0) rotate(0deg)';
    });
  }

  var heroIsland   = document.querySelector('.hero-island');
  var heroVector   = document.querySelector('.hero-vector-layer');
  var valuesIsland = document.querySelector('.values-section');
  var valuesVector = document.querySelector('.ambient-vector-bg');
  attachParallax(heroIsland,   heroVector,   0.045);
  attachParallax(valuesIsland, valuesVector, 0.035);

  // ============================================================
  // 2. 3D TILT on .tilt-card and .campus-card
  //    v5 spec: ±5deg (slightly subtler than v4's ±6deg)
  // ============================================================
  var tiltCards = document.querySelectorAll('.tilt-card, .campus-card');
  if (!prefersReduce) {
    tiltCards.forEach(function (card) {
      var tiltRaf = null;
      card.addEventListener('mousemove', function (e) {
        if (tiltRaf) return;
        tiltRaf = requestAnimationFrame(function () {
          var rect = card.getBoundingClientRect();
          var x = e.clientX - rect.left;
          var y = e.clientY - rect.top;
          var centerX = rect.width / 2;
          var centerY = rect.height / 2;
          var rotateX = ((y - centerY) / centerY) * -5;
          var rotateY = ((x - centerX) / centerX) *  5;
          card.style.transform =
            'perspective(1000px) rotateX(' + rotateX + 'deg) rotateY(' + rotateY + 'deg) translateY(-6px)';
          tiltRaf = null;
        });
      });
      card.addEventListener('mouseleave', function () {
        card.style.transform =
          'perspective(1000px) rotateX(0deg) rotateY(0deg) translateY(0)';
      });
    });
  }

  // ============================================================
  // 3. SLIDER prev/next on .campus-grid
  // ============================================================
  var slider  = document.querySelector('.campus-grid');
  var prevBtn = document.getElementById('slider-prev');
  var nextBtn = document.getElementById('slider-next');
  if (slider && prevBtn && nextBtn) {
    prevBtn.addEventListener('click', function () {
      slider.scrollBy({ left: -360, behavior: 'smooth' });
    });
    nextBtn.addEventListener('click', function () {
      slider.scrollBy({ left: 360, behavior: 'smooth' });
    });
  }

  // ============================================================
  // 4. SMOOTH SCROLL for hash anchors
  // ============================================================
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var href = a.getAttribute('href');
      if (!href || href === '#' || href.length < 2) return;
      var target = document.querySelector(href);
      if (!target) return;
      e.preventDefault();
      target.scrollIntoView({ behavior: prefersReduce ? 'auto' : 'smooth', block: 'start' });
    });
  });

  // ============================================================
  // 5. NAV LINK focus parity
  // ============================================================
  document.querySelectorAll('.nav-links a').forEach(function (a) {
    a.addEventListener('focus', function () { a.classList.add('is-focused'); });
    a.addEventListener('blur',  function () { a.classList.remove('is-focused'); });
  });

  // ============================================================
  // 6. IMAGE onerror → CSS gradient fallback (offline-safe)
  // ============================================================
  document.querySelectorAll('img').forEach(function (img) {
    img.addEventListener('error', function () {
      img.style.visibility = 'hidden';
      img.style.opacity = '0';
    });
  });

  // ============================================================
  // 7. THEME TOGGLE (light / dark / auto cycle) — preserved from v4
  // ============================================================
  var themeBtn = document.getElementById('theme-toggle');
  if (themeBtn) {
    var ORDER = ['light', 'dark', 'auto'];
    function current() { return document.documentElement.getAttribute('data-theme') || 'auto'; }
    function setTheme(next, persist) {
      document.documentElement.setAttribute('data-theme', next);
      if (persist) {
        try {
          if (next === 'auto') localStorage.removeItem('perazim-theme');
          else localStorage.setItem('perazim-theme', next);
        } catch (e) { /* storage blocked */ }
      }
    }
    themeBtn.addEventListener('click', function () {
      var idx = ORDER.indexOf(current());
      setTheme(ORDER[(idx + 1) % ORDER.length], true);
    });
    window.addEventListener('storage', function (e) {
      if (e.key === 'perazim-theme' && e.newValue) setTheme(e.newValue, false);
    });
  }

  // ============================================================
  // 8. SCROLL REVEAL (IntersectionObserver)
  //    v5 spec: target the major sections + grid children, add stagger
  // ============================================================
  if ('IntersectionObserver' in window && !prefersReduce) {
    var revealTargets = document.querySelectorAll(
      '.hero-content, .section-header, .campus-card, ' +
      '.leadership-island, .values-section, .value-item, ' +
      '.poster-card, .messages-island, .section-eyebrow-wrap'
    );
    revealTargets.forEach(function (el) {
      el.classList.add('reveal-on-scroll');
      if (el.classList.contains('campus-card') ||
          el.classList.contains('value-item') ||
          el.classList.contains('poster-card')) {
        // Auto-stagger: cycle through stagger-1..stagger-4 by document order
        var allSiblings = Array.from(el.parentElement ? el.parentElement.children : []);
        var i = allSiblings.indexOf(el);
        var staggerN = (i % 4) + 1;
        el.classList.add('stagger-' + staggerN);
      }
    });
    var revealObserver = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-revealed');
          obs.unobserve(entry.target); // Reveal once, then stop observing
        }
      });
    }, { root: null, rootMargin: '0px 0px -60px 0px', threshold: 0.12 });
    revealTargets.forEach(function (el) { revealObserver.observe(el); });
  } else {
    // No IntersectionObserver OR reduced-motion: make sure everything is visible
    // so no content gets stuck at opacity:0.
    document.querySelectorAll('.reveal-on-scroll').forEach(function (el) {
      el.classList.add('is-revealed');
    });
  }

  // ============================================================
  // 9. STICKY NAVBAR morph on scroll
  //    v5 spec: .scrolled class added after 40px
  // ============================================================
  var navbar = document.querySelector('.nav-container');
  if (navbar && !prefersReduce) {
    var lastScrolled = false;
    function onScroll() {
      var scrolled = window.scrollY > 40;
      if (scrolled !== lastScrolled) {
        navbar.classList.toggle('scrolled', scrolled);
        lastScrolled = scrolled;
      }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll(); // initial state
  }
})();
