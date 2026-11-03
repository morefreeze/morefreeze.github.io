const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');
const html = fs.readFileSync('_includes/sidebar.html', 'utf8');
const scriptPath = 'assets/js/sidebar.js';
const source = fs.existsSync(scriptPath) ? fs.readFileSync(scriptPath, 'utf8') : '';

function setup(desktop) {
  const dom = new JSDOM(html, { runScripts: 'outside-only' });
  let listener;
  const media = { matches: desktop, addEventListener(event, fn) { listener = fn; } };
  dom.window.matchMedia = () => media;
  dom.window.eval(source);
  return { dom, sidebar: dom.window.document.querySelector('details.site-sidebar'),
    resize(value) { media.matches = value; listener?.(); } };
}

test('mobile sidebar starts collapsed and keeps a native disclosure control', () => {
  const s = setup(false);
  assert.ok(s.sidebar, 'sidebar uses a native details element');
  assert.equal(s.sidebar.open, false);
  const toggle = s.sidebar.querySelector('summary');
  assert.ok(toggle.textContent.trim());
  toggle.click();
  assert.equal(s.sidebar.open, true);
  toggle.click();
  assert.equal(s.sidebar.open, false);
  s.dom.window.close();
});

test('desktop sidebar opens automatically and adapts when crossing the column breakpoint', () => {
  const s = setup(true);
  assert.ok(s.sidebar, 'responsive sidebar exists');
  assert.equal(s.sidebar.open, true);
  s.resize(false);
  assert.equal(s.sidebar.open, false);
  s.resize(true);
  assert.equal(s.sidebar.open, true);
  s.dom.window.close();
});
