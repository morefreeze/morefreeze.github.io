const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');
const source = fs.readFileSync('assets/js/dark-mode.js', 'utf8');
const widget = '<iframe id="foreverblog-today" src="https://www.foreverblog.cn/widget/today.html?theme=light"></iframe>';

function setup({ storedTheme, systemDark = false, withWidget = true } = {}) {
  const dom = new JSDOM('<button id="dark-mode-toggle"></button>' + (withWidget ? widget : ''), {
    url: 'https://blog.morefreeze.top/', runScripts: 'outside-only'
  });
  const w = dom.window;
  w.matchMedia = () => ({ matches: systemDark, addEventListener() {} });
  if (storedTheme) w.localStorage.setItem('theme', storedTheme);
  w.eval(source);
  w.document.dispatchEvent(new w.Event('DOMContentLoaded'));
  return w;
}

test('the footer widget follows the initial saved or system theme', () => {
  for (const [options, expected] of [
    [{}, 'light'],
    [{ systemDark: true }, 'dark'],
    [{ storedTheme: 'dark' }, 'dark'],
    [{ storedTheme: 'light', systemDark: true }, 'light']
  ]) {
    const w = setup(options);
    const url = new URL(w.document.querySelector('iframe').src);
    assert.equal(url.searchParams.get('theme'), expected);
    assert.equal(w.document.documentElement.dataset.theme, expected);
    w.close();
  }
});

test('the theme button changes the widget in both directions', () => {
  const w = setup();
  const button = w.document.querySelector('button');
  button.click();
  assert.equal(new URL(w.document.querySelector('iframe').src).searchParams.get('theme'), 'dark');
  button.click();
  assert.equal(new URL(w.document.querySelector('iframe').src).searchParams.get('theme'), 'light');
  w.close();
});

test('theme switching still works on pages without the widget', () => {
  const w = setup({ withWidget: false });
  w.document.querySelector('button').click();
  assert.equal(w.document.documentElement.dataset.theme, 'dark');
  assert.equal(w.localStorage.getItem('theme'), 'dark');
  w.close();
});
