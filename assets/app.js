/* ===========================================================
   Perazim Mission Church: site behaviour

   1. Theme toggle (light, dark, auto)
   2. Burger menu
   3. Header style once the page is scrolled
   4. Scroll reveal
   5. Copy buttons (for example the M-Pesa paybill number)
   6. Footer year

   Everything works without JavaScript except these enhancements.
   prefers-reduced-motion is respected (no reveal motion).
   =========================================================== */
(function () {
  'use strict';

  var root = document.documentElement;
  var prefersReduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // 1. Theme toggle: light -> dark -> auto -> light. Light is the default.
  var themeBtn = document.getElementById('theme-toggle');
  var ORDER = ['light', 'dark', 'auto'];
  var LABEL = { light: 'Light theme', dark: 'Dark theme', auto: 'Automatic theme' };
  function currentTheme() { return root.getAttribute('data-theme') || 'light'; }
  function setTheme(next, persist) {
    root.setAttribute('data-theme', next);
    if (themeBtn) themeBtn.setAttribute('title', LABEL[next] + '. Click to change.');
    if (persist) {
      try {
        if (next === 'light') localStorage.removeItem('perazim-theme');
        else localStorage.setItem('perazim-theme', next);
      } catch (e) { /* storage blocked: the choice lasts for this page only */ }
    }
  }
  if (themeBtn) {
    setTheme(currentTheme(), false);
    themeBtn.addEventListener('click', function () {
      setTheme(ORDER[(ORDER.indexOf(currentTheme()) + 1) % ORDER.length], true);
    });
    window.addEventListener('storage', function (e) {
      if (e.key === 'perazim-theme') setTheme(e.newValue === 'dark' || e.newValue === 'auto' ? e.newValue : 'light', false);
    });
  }

  // 2. Burger menu (used at every screen width)
  var navBar = document.querySelector('.nav-container');
  var navToggle = document.querySelector('.nav-toggle');
  if (navBar && navToggle) {
    var setMenu = function (open) {
      navBar.classList.toggle('nav-open', open);
      navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    navToggle.addEventListener('click', function () { setMenu(!navBar.classList.contains('nav-open')); });
    navBar.querySelectorAll('.nav-links a').forEach(function (a) {
      a.addEventListener('click', function () { setMenu(false); });
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && navBar.classList.contains('nav-open')) { setMenu(false); navToggle.focus(); }
    });
    document.addEventListener('click', function (e) {
      if (navBar.classList.contains('nav-open') && !navBar.contains(e.target)) setMenu(false);
    });
  }

  // 3. Header turns frosted-light once the page is scrolled
  if (navBar) {
    var scrolled = false;
    var onScroll = function () {
      var now = window.scrollY > 24;
      if (now !== scrolled) { scrolled = now; navBar.classList.toggle('scrolled', now); }
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  // 4. Scroll reveal: only things below the first screen are animated, so the
  //    first view (and link-preview screenshots) is never blank.
  if ('IntersectionObserver' in window && !prefersReduce) {
    var vh = window.innerHeight || document.documentElement.clientHeight;
    var targets = Array.prototype.filter.call(document.querySelectorAll(
      '.main-wrapper .section-heading, .main-wrapper .section-intro, .info-card, .feed-card, .faq-item, ' +
      '.campus-card, .cta-band, .messages-island, .values-section, .leadership-island, .life-grid img, ' +
      '.map-frame, .path, .value-item'
    ), function (el) { return el.getBoundingClientRect().top > vh * 0.9; });
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { entry.target.classList.add('is-revealed'); obs.unobserve(entry.target); }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });
    targets.forEach(function (el) {
      el.classList.add('reveal-on-scroll');
      var i = Array.prototype.indexOf.call(el.parentElement ? el.parentElement.children : [], el);
      if (i > 0) el.classList.add('stagger-' + Math.min((i % 4) + 1, 4));
      observer.observe(el);
    });
  }

  // 5. Copy buttons
  document.querySelectorAll('[data-copy]').forEach(function (btn) {
    var original = btn.textContent;
    btn.addEventListener('click', function () {
      var text = btn.getAttribute('data-copy');
      var done = function () {
        btn.textContent = 'Copied';
        setTimeout(function () { btn.textContent = original; }, 2000);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(text).then(done, function () {});
      } else {
        var t = document.createElement('textarea');
        t.value = text;
        t.setAttribute('readonly', '');
        t.style.position = 'fixed';
        t.style.opacity = '0';
        document.body.appendChild(t);
        t.select();
        try { document.execCommand('copy'); done(); } catch (e) { /* nothing to do */ }
        t.remove();
      }
    });
  });

  // 6. Footer year
  document.querySelectorAll('[data-year]').forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });
})();
