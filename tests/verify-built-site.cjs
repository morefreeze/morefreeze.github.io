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
