# Technical Architecture & Engineering Standards

## 1. Core Architectural Principles

- **Zero Heavy Dependencies**: Pure semantic HTML5, modern vanilla CSS3, and lightweight ES6+ JavaScript. No bulky external frameworks (React, Next.js, Vue) to guarantee maximum performance, sub-100ms first paint, and total portability.
- **Progressive Enhancement**: All primary content, sermon listings, branch listings, and navigational links remain 100% accessible with JavaScript disabled.
- **Hardware-Accelerated Animation**: Transitions utilize GPU-friendly properties (`transform`, `opacity`, `backdrop-filter`) with strict `prefers-reduced-motion` compliance.

## 2. DOM & Layout Architecture

```
[Viewport]
  ├── <header class="site-header"> (Sticky, dynamic blur on scroll)
  │     ├── <a class="brand-logo">
  │     ├── <nav class="site-nav">
  │     └── <div class="theme-switch-wrapper">
  ├── <main id="main-content">
  │     ├── <section class="hero-island">
  │     ├── <section class="values-grid">
  │     ├── <section class="campus-carousel">
  │     └── <section class="sermon-highlight">
  └── <footer class="site-footer">
        ├── <div class="footer-links">
        └── <div class="footer-copyright">
```

## 3. The 3-State Theme Engine

The theme state is governed by three possible values:
1. `light`: Explicitly forces light surface colors.
2. `dark`: Explicitly forces dark slate colors.
3. `auto`: Dynamically queries `window.matchMedia('(prefers-color-scheme: dark)')` while responding to OS changes.

### Storage & Non-FOUC (Flash of Unstyled Content) Injection
To prevent any visual flash during page load, the following script runs synchronously at the earliest point in `<head>`:
```javascript
(function() {
  const saved = localStorage.getItem('pmc_theme') || 'auto';
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const active = saved === 'auto' ? (prefersDark ? 'dark' : 'light') : saved;
  document.documentElement.setAttribute('data-theme', active);
})();
```

## 4. CSS Engineering & Tokens

### Design System Tokens
All spacing, typography scale, and color values are anchored on standard 4px / 8px geometric grid increments.

```css
:root {
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;

  --radius-sm: 8px;
  --radius-md: 16px;
  --radius-lg: 24px;
  --radius-full: 9999px;
  
  --transition-smooth: cubic-bezier(0.16, 1, 0.3, 1);
}
```

## 5. Automated Quality & Verification Gates

The repository enforces automated verification via `recon/verify_v5upgrade.py`. Prior to merging any branch or deploying to production, all 86 verification criteria must return `true`.
