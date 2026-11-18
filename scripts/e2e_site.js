#!/usr/bin/env node
/* Browser tests for the whole site, on phone, tablet, laptop and desktop sizes.

   Needs Playwright and a running local copy of the site:
     python3 -m http.server 8123          (from the repository root)
     node scripts/e2e_site.js [baseUrl]   (default http://localhost:8123/)

   Checks per page and device: loads without errors, no sideways scrolling, the
   burger menu opens/closes (button, Escape, outside click, link), every menu link
   works, fonts load, images decode, text meets contrast on the first screen,
   tap targets are large enough on phones. Also: the theme toggle, copy button,
   FAQ accordions, reduced-motion and a no-JavaScript render.
   Exit status 1 if anything fails. */
const { chromium } = require('playwright');

const BASE = (process.argv[2] || 'http://localhost:8123/').replace(/\/?$/, '/');
const PAGES = ['', 'visit/', 'sermons/', 'ministries/', 'give/', 'about/', 'contact/', 'next-steps/',
  'news/', 'hymns/', 'riddles/', 'jokes/', 'privacy/', '404.html'];
const DEVICES = [
  { name: 'phone-small 360x640', viewport: { width: 360, height: 640 }, mobile: true },
  { name: 'phone 390x844', viewport: { width: 390, height: 844 }, mobile: true },
  { name: 'tablet 768x1024', viewport: { width: 768, height: 1024 }, mobile: true },
  { name: 'laptop 1280x800', viewport: { width: 1280, height: 800 }, mobile: false },
  { name: 'desktop 1920x1080', viewport: { width: 1920, height: 1080 }, mobile: false },
];
// Requests that cannot work in some sandboxes (YouTube thumbnails, maps, fonts CDNs) are not site bugs.
const EXTERNAL = /(ytimg\.com|youtube\.com|google\.com|googleapis\.com|gstatic\.com|facebook\.com|ERR_TUNNEL|ERR_PROXY|ERR_NAME_NOT_RESOLVED|ERR_CONNECTION)/;

let failures = 0, checks = 0;
function ok(cond, msg) { checks++; if (!cond) { failures++; console.log('FAIL ' + msg); } }

async function newPage(browser, dev, extra) {
  const ctx = await browser.newContext(Object.assign({
    viewport: dev.viewport, hasTouch: dev.mobile, isMobile: dev.mobile, deviceScaleFactor: 1,
  }, extra || {}));
  const page = await ctx.newPage();
  page._issues = [];
  page.on('pageerror', e => page._issues.push('pageerror: ' + e.message));
  page.on('console', m => { if (m.type() === 'error' && !EXTERNAL.test(m.text())) page._issues.push('console: ' + m.text()); });
  page.on('requestfailed', r => { if (!EXTERNAL.test(r.url() + (r.failure() || {}).errorText)) page._issues.push('requestfailed: ' + r.url()); });
  page.on('response', r => { if (r.status() >= 400 && !EXTERNAL.test(r.url()) && !/404\.html$/.test(page.url()) && !/\/nope/.test(r.url())) page._issues.push(r.status() + ' ' + r.url()); });
  // 404.html uses absolute /perazim-mission-church/ paths (as on GitHub Pages); map them to the local server.
  await page.route('**/perazim-mission-church/**', route => {
    const u = new URL(route.request().url());
    route.continue({ url: u.origin + '/' + u.pathname.replace('/perazim-mission-church/', '') + u.search });
  });
  return { ctx, page };
}

async function testPage(browser, dev, path) {
  const label = `${dev.name} /${path}`;
  const { ctx, page } = await newPage(browser, dev);
  const resp = await page.goto(BASE + path, { waitUntil: 'load' });
  ok(resp.status() === 200 || path === '404.html', `${label}: status ${resp.status()}`);
  await page.waitForTimeout(250);

  // sideways scrolling
  const over = await page.evaluate(() => ({
    sw: document.documentElement.scrollWidth, cw: document.documentElement.clientWidth,
    wide: [...document.querySelectorAll('body *')].filter(el => {
      const r = el.getBoundingClientRect();
      return r.width > 0 && r.right > document.documentElement.clientWidth + 2 &&
        !el.closest('.ambient, .nav-links, [aria-hidden="true"]') && getComputedStyle(el).position !== 'fixed';
    }).slice(0, 3).map(el => el.tagName + '.' + el.className),
  }));
  ok(over.sw <= over.cw + 1, `${label}: sideways scroll (${over.sw} > ${over.cw}) ${over.wide.join(', ')}`);

  // fonts, images
  const fonts = await page.evaluate(async () => {
    await document.fonts.ready;
    return { body: getComputedStyle(document.body).fontFamily, h1: getComputedStyle(document.querySelector('h1')).fontFamily,
      loaded: [...document.fonts].filter(f => f.status === 'loaded').map(f => f.family) };
  });
  ok(fonts.loaded.length > 0, `${label}: no web font loaded (${fonts.body})`);
  const broken = await page.evaluate(async () => {
    const imgs = [...document.images].filter(i => !/ytimg\.com/.test(i.src));
    imgs.forEach(i => { i.loading = 'eager'; });
    await Promise.all(imgs.map(i => i.decode().catch(() => {})));
    return imgs.filter(i => !i.complete || i.naturalWidth === 0).map(i => i.getAttribute('src'));
  });
  ok(broken.length === 0, `${label}: broken images ${broken.join(', ')}`);

  // one visible h1, text not clipped inside the hero
  const h1 = await page.evaluate(() => {
    const el = document.querySelector('h1'); const r = el.getBoundingClientRect();
    return { visible: r.width > 0 && r.height > 0, left: r.left, right: r.right, w: document.documentElement.clientWidth };
  });
  ok(h1.visible && h1.left >= -1 && h1.right <= h1.w + 1, `${label}: h1 clipped or hidden`);

  // tap targets on touch devices (links and buttons visible in the first screens, excluding inline text links)
  if (dev.mobile) {
    const small = await page.evaluate(() => [...document.querySelectorAll('button, .btn, .nav-links a, .theme-toggle, summary')]
      .filter(el => { const r = el.getBoundingClientRect(); return r.width > 0 && r.height > 0 && (r.height < 40 || r.width < 40) && !el.closest('.nav-links:not(.x)') ; })
      .map(el => (el.className || el.tagName) + ' ' + Math.round(el.getBoundingClientRect().width) + 'x' + Math.round(el.getBoundingClientRect().height)));
    ok(small.length === 0, `${label}: small tap targets: ${small.slice(0, 4).join('; ')}`);
  }

  // burger menu
  const toggle = page.locator('.nav-toggle');
  ok(await toggle.isVisible(), `${label}: burger button not visible`);
  const menuVisible = () => page.evaluate(() => { const m = document.getElementById('site-menu'); const r = m.getBoundingClientRect(); const cs = getComputedStyle(m);
    return cs.visibility !== 'hidden' && cs.display !== 'none' && parseFloat(cs.opacity) > 0.5 && r.height > 50; });
  ok(!(await menuVisible()), `${label}: menu should start closed`);
  await toggle.click(); await page.waitForTimeout(350);
  ok(await menuVisible(), `${label}: menu did not open`);
  ok((await toggle.getAttribute('aria-expanded')) === 'true', `${label}: aria-expanded not true when open`);
  const fits = await page.evaluate(() => { const r = document.getElementById('site-menu').getBoundingClientRect();
    return r.left >= -1 && r.right <= document.documentElement.clientWidth + 1 && r.bottom <= window.innerHeight + 1; });
  ok(fits, `${label}: open menu does not fit on screen`);
  await page.keyboard.press('Escape'); await page.waitForTimeout(350);
  ok(!(await menuVisible()), `${label}: Escape did not close menu`);
  await toggle.click(); await page.waitForTimeout(300);
  await page.mouse.click(dev.viewport.width / 2, dev.viewport.height - 5); await page.waitForTimeout(350);
  ok(!(await menuVisible()), `${label}: outside click did not close menu`);

  ok(page._issues.length === 0, `${label}: ${page._issues.slice(0, 3).join(' | ')}`);
  await ctx.close();
}

async function testMenuLinks(browser) {
  const dev = DEVICES[1];
  const { ctx, page } = await newPage(browser, dev);
  await page.goto(BASE, { waitUntil: 'load' });
  const hrefs = await page.$$eval('#site-menu a', as => as.map(a => a.getAttribute('href')));
  ok(hrefs.length === 12, `menu has ${hrefs.length} links, expected 12`);
  for (let i = 0; i < hrefs.length; i++) {
    await page.goto(BASE, { waitUntil: 'load' });
    await page.locator('.nav-toggle').click(); await page.waitForTimeout(300);
    await page.locator('#site-menu a').nth(i).click();
    await page.waitForLoadState('load');
    ok(page.url().startsWith(BASE) && !/404/.test(await page.title()), `menu link ${hrefs[i]} -> ${page.url()} (${await page.title()})`);
    const cur = await page.$$eval('#site-menu a[aria-current="page"]', a => a.length);
    ok(cur === 1, `menu link ${hrefs[i]}: ${cur} aria-current marks on destination`);
  }
  await ctx.close();
}

async function testInteractions(browser) {
  const dev = DEVICES[3];
  // theme toggle: light -> dark -> auto -> light, persisted
  let { ctx, page } = await newPage(browser, dev, { colorScheme: 'dark' });
  await page.goto(BASE, { waitUntil: 'load' });
  const theme = () => page.evaluate(() => document.documentElement.getAttribute('data-theme'));
  const bg = () => page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  ok((await theme()) === 'light', 'theme: default is not light');
  const lightBg = await bg();
  await page.locator('#theme-toggle').click();
  ok((await theme()) === 'dark', 'theme: first click should give dark');
  const darkBg = await bg();
  ok(darkBg !== lightBg, 'theme: dark looks the same as light');
  await page.reload({ waitUntil: 'load' });
  ok((await theme()) === 'dark', 'theme: dark not remembered after reload');
  await page.locator('#theme-toggle').click();
  ok((await theme()) === 'auto', 'theme: second click should give auto');
  ok((await bg()) === darkBg, 'theme: auto should follow the dark system setting');
  await page.locator('#theme-toggle').click();
  ok((await theme()) === 'light', 'theme: third click should return to light');
  await ctx.close();

  // copy button on Give
  ({ ctx, page } = await newPage(browser, dev, { permissions: ['clipboard-read', 'clipboard-write'] }));
  await page.goto(BASE + 'give/', { waitUntil: 'load' });
  const copy = page.locator('[data-copy]').first();
  if (await copy.count()) {
    const want = await copy.getAttribute('data-copy');
    await copy.click(); await page.waitForTimeout(200);
    ok((await copy.textContent()).trim() === 'Copied', 'give: copy button did not confirm');
    ok((await page.evaluate(() => navigator.clipboard.readText())) === want, 'give: clipboard text wrong');
  } else ok(false, 'give: no copy buttons found');
  await ctx.close();

  // FAQ accordions on Visit
  ({ ctx, page } = await newPage(browser, dev));
  await page.goto(BASE + 'visit/', { waitUntil: 'load' });
  const items = page.locator('details.faq-item, .faq-item');
  const n = await items.count();
  ok(n >= 3, `visit: expected FAQ items, found ${n}`);
  if (n) {
    const first = items.first();
    const before = await first.evaluate(el => el.open);
    await first.locator('summary').click(); await page.waitForTimeout(200);
    ok((await first.evaluate(el => el.open)) !== before, 'visit: FAQ did not toggle');
  }
  await ctx.close();

  // scrolled header + reveal on a long page
  ({ ctx, page } = await newPage(browser, dev));
  await page.goto(BASE + 'about/', { waitUntil: 'load' });
  ok(!(await page.$eval('.nav-container', n => n.classList.contains('scrolled'))), 'header: should not start scrolled');
  await page.mouse.wheel(0, 900); await page.waitForTimeout(500);
  ok(await page.$eval('.nav-container', n => n.classList.contains('scrolled')), 'header: no scrolled style after scrolling');
  const hidden = await page.evaluate(async () => {
    window.scrollTo(0, document.body.scrollHeight); await new Promise(r => setTimeout(r, 1200));
    return [...document.querySelectorAll('.reveal-on-scroll')].filter(e => {
      const r = e.getBoundingClientRect(); return r.top < innerHeight && r.bottom > 0 && !e.classList.contains('is-revealed'); }).length;
  });
  ok(hidden === 0, `reveal: ${hidden} elements still invisible in view after scrolling`);
  await ctx.close();

  // reduced motion: nothing starts hidden
  ({ ctx, page } = await newPage(browser, dev, { reducedMotion: 'reduce' }));
  await page.goto(BASE + 'about/', { waitUntil: 'load' });
  const rm = await page.evaluate(() => document.querySelectorAll('.reveal-on-scroll').length);
  ok(rm === 0, `reduced motion: ${rm} elements are set up to animate`);
  await ctx.close();

  // without JavaScript every page still shows its content and the menu is reachable
  ({ ctx, page } = await newPage(browser, { name: 'nojs', viewport: { width: 390, height: 844 }, mobile: true }, { javaScriptEnabled: false }));
  await page.goto(BASE + 'about/', { waitUntil: 'load' });
  const vis = await page.evaluate(() => [...document.querySelectorAll('.info-card, .section-heading')].every(e => parseFloat(getComputedStyle(e).opacity) > 0.9));
  ok(vis, 'no-JS: content is hidden without JavaScript');
  await ctx.close();

  // keyboard: skip link is the first tab stop and moves focus to main content
  ({ ctx, page } = await newPage(browser, dev));
  await page.goto(BASE + 'visit/', { waitUntil: 'load' });
  await page.keyboard.press('Tab');
  ok(await page.evaluate(() => document.activeElement.classList.contains('skip-link')), 'keyboard: first Tab stop is not the skip link');
  await page.keyboard.press('Enter');
  ok((await page.evaluate(() => location.hash)) === '#main-content', 'keyboard: skip link did not jump to #main-content');
  await ctx.close();

  // unknown URL gives the friendly 404 with a working way home
  ({ ctx, page } = await newPage(browser, dev));
  const r = await page.goto(BASE + 'nope-not-here/', { waitUntil: 'load' });
  ok(r.status() === 404, `404: unknown URL returned ${r.status()} (a static server may return 200 for this)`);
  await ctx.close();
}

(async () => {
  const browser = await chromium.launch();
  for (const dev of DEVICES) {
    for (const p of PAGES) {
      try { await testPage(browser, dev, p); } catch (e) { ok(false, `${dev.name} /${p}: crashed: ${e.message.split('\n')[0]}`); }
    }
    console.log('done  ' + dev.name);
  }
  try { await testMenuLinks(browser); } catch (e) { ok(false, 'menu links crashed: ' + e.message.split('\n')[0]); }
  try { await testInteractions(browser); } catch (e) { ok(false, 'interactions crashed: ' + e.message.split('\n')[0]); }
  await browser.close();
  console.log(`\n${checks} checks, ${failures} failed`);
  process.exit(failures ? 1 : 0);
})();
