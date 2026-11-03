const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');

const root = path.resolve(process.argv[2] || '_site');
const pages = [1, ...fs.readdirSync(root).filter(name => /^page\d+$/.test(name))
  .map(name => Number(name.slice(4)))].sort((a, b) => a - b);
const pagePath = n => n === 1 ? '/' : `/page${n}/`;
function readPage(n) {
  return new JSDOM(fs.readFileSync(path.join(root, n === 1 ? 'index.html' : `page${n}/index.html`), 'utf8'));
}

test('pagination fills every non-final page with five distinct Chinese articles', () => {
  const seen = new Set();
  for (const [i, n] of pages.entries()) {
    assert.equal(n, i + 1, 'pagination has no gaps');
    const dom = readPage(n);
    const document = dom.window.document;
    const articles = [...document.querySelectorAll('.home-post-item')];
    if (i < pages.length - 1) assert.equal(articles.length, 5, `page ${n} must contain five articles`);
    else assert.ok(articles.length > 0 && articles.length <= 5, 'last page contains one to five articles');
    for (const article of articles) {
      const url = article.querySelector('.post-link').getAttribute('href');
      assert.ok(!url.endsWith('_en.html'), `English version occupies a pagination slot: ${url}`);
      assert.ok(!seen.has(url), `duplicate article across pages: ${url}`);
      seen.add(url);
    }
    assert.equal(document.querySelector('.pager .previous a')?.getAttribute('href'), n > 1 ? pagePath(n - 1) : undefined);
    assert.equal(document.querySelector('.pager .next a')?.getAttribute('href'), i < pages.length - 1 ? pagePath(n + 1) : undefined);
    dom.window.close();
  }
});

test('sidebar long lists start collapsed and keep their navigation links', () => {
  const dom = readPage(2);
  const panels = [...dom.window.document.querySelectorAll('.sidebar-module details')];
  assert.equal(panels.length, 3, 'categories, tags and archives are collapsible');
  for (const panel of panels) {
    assert.ok(!panel.hasAttribute('open'), 'long list is collapsed by default');
    assert.ok(panel.querySelector('summary')?.textContent.trim(), 'panel has a named native toggle');
    assert.ok(panel.querySelectorAll('a[href]').length > 0, 'navigation links remain available');
  }
  dom.window.close();
});

test('English articles remain published with a working Chinese counterpart link', () => {
  const sitemap = fs.readFileSync(path.join(root, 'sitemap.xml'), 'utf8');
  const urls = [...sitemap.matchAll(/<loc>([^<]+_en\.html)<\/loc>/g)].map(match => new URL(match[1]).pathname);
  assert.ok(urls.length > 0, 'English articles remain in the sitemap');
  for (const url of urls) {
    const dom = new JSDOM(fs.readFileSync(path.join(root, url.slice(1)), 'utf8'));
    const link = dom.window.document.querySelector('#language-switcher');
    assert.equal(link?.getAttribute('href'), url.replace('_en.html', '.html'));
    assert.ok(fs.existsSync(path.join(root, url.replace('_en.html', '.html').slice(1))), `Chinese counterpart exists: ${url}`);
    dom.window.close();
  }
});

test('the mobile sidebar starts collapsed without enclosing the footer widget', () => {
  for (const n of [1, 2]) {
    const dom = readPage(n);
    const document = dom.window.document;
    const sidebar = document.querySelector('details.site-sidebar');
    assert.ok(sidebar, 'whole sidebar has a native disclosure control');
    assert.equal(sidebar.open, false, 'mobile is collapsed even before scripts run');
    assert.equal(sidebar.querySelectorAll('.sidebar-module').length, 8, 'all sidebar modules remain accessible');
    const widget = document.querySelector('footer #foreverblog-today');
    assert.ok(widget, 'daily reading widget remains in the footer');
    assert.equal(widget.closest('details'), null, 'closing navigation cannot hide the widget');
    assert.equal(widget.tagName, 'SECTION', 'recommendations render directly in the page');
    const articles = [...widget.querySelectorAll('.foreverblog-article')];
    assert.equal(articles.length, 3, 'wide screens have three recommendations');
    assert.equal(new Set(articles.map(a => a.href)).size, 3, 'recommendations are distinct');
    for (const article of articles) {
      assert.ok(article.textContent.trim(), 'article has a visible title');
      assert.ok(article.href.startsWith('https://www.foreverblog.cn/daily/read/'), 'article uses the official feed link');
      assert.equal(article.target, '_blank');
      assert.ok(article.relList.contains('noopener'));
      assert.match(article.parentElement.querySelector('time').dateTime, /^\d{4}-\d{2}-\d{2}$/);
    }
    const script = document.querySelector('script[src$="/assets/js/sidebar.js"]');
    assert.ok(script, 'responsive sidebar behavior is loaded');
    assert.ok(fs.existsSync(path.join(root, script.getAttribute('src').replace(/^\//, ''))));
    dom.window.close();
  }
});
