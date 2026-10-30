const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const { JSDOM } = require('jsdom');
const source = fs.readFileSync('assets/js/ga-events.js', 'utf8');
const post = '<div class="post" data-article-id="/2026/03/example.html" data-article-language="zh"><article data-article-content></article><a id="language-switcher" href="/2026/03/example_en.html">EN</a></div>';
const list = '<div class="home-post-item" data-article-id="/2026/03/example.html" data-article-language="zh"><header class="post-header"><a class="post-link" href="/2026/03/example.html">Example</a></header><a class="read-more" href="/2026/03/example.html#read-more">Read more</a></div>';
function setup(html = post, analytics = true) {
  const dom = new JSDOM(html, { url: 'https://blog.morefreeze.top/2026/03/example.html', runScripts: 'outside-only' });
  const w = dom.window, events = [], observers = [], jobs = new Map();
  let now = 0, seq = 0, visible = true, focused = true;
  Object.defineProperty(w.document, 'visibilityState', { get: () => visible ? 'visible' : 'hidden' });
  w.document.hasFocus = () => focused;
  w.Date.now = () => now;
  w.setTimeout = (fn, delay) => { const id = ++seq; jobs.set(id, { fn, at: now + delay }); return id; };
  w.clearTimeout = id => jobs.delete(id);
  w.setInterval = (fn, delay) => { const id = ++seq; jobs.set(id, { fn, at: now + delay, delay }); return id; };
  w.clearInterval = w.clearTimeout;
  w.IntersectionObserver = class {
    constructor(fn) { this.fn = fn; observers.push(this); }
    observe(el) { (this.elements ||= []).push(el); }
    unobserve() {}
  };
  if (analytics) w.gtag = (...args) => events.push(args);
  const body = w.document.querySelector('[data-article-content]');
  let top = 0;
  if (body) body.getBoundingClientRect = () => ({ top, bottom: top + 2000, height: 2000 });
  w.document.addEventListener('click', event => event.preventDefault());
  w.eval(source);
  w.document.dispatchEvent(new w.Event('DOMContentLoaded'));
  return {
    w, events, observers,
    named: name => events.filter(e => e[1] === name),
    tick(ms) {
      const end = now + ms;
      while (true) {
        const next = [...jobs.entries()].filter(([,j]) => j.at <= end).sort((a,b) => a[1].at-b[1].at)[0];
        if (!next) break;
        const [id, job] = next; now = job.at; jobs.delete(id);
        if (job.delay) jobs.set(id, { ...job, at: now + job.delay });
        job.fn();
      }
      now = end;
    },
    visibility(value) { visible = value; w.document.dispatchEvent(new w.Event('visibilitychange')); },
    focus(value) { focused = value; w.dispatchEvent(new w.Event(value ? 'focus' : 'blur')); },
    progress(value) { top = w.innerHeight - 2000 * value / 100; w.dispatchEvent(new w.Event('scroll')); },
    intersect(value) { for (const o of observers) o.fn([{ target: o.elements[0], isIntersecting: value, intersectionRatio: value ? 0.7 : 0 }]); }
  };
}
test('article impressions require continuous visible exposure and are deduplicated', () => {
  const s = setup(list); assert.equal(s.observers.length, 1);
  s.intersect(true); s.tick(600); s.intersect(false); s.tick(1000);
  assert.equal(s.named('article_impression').length, 0);
  s.intersect(true); s.tick(1000); s.intersect(false); s.intersect(true); s.tick(1500);
  assert.equal(s.named('article_impression').length, 1);
  assert.equal(s.named('article_impression')[0][2].article_id, '/2026/03/example.html');
});
test('background impressions are not counted', () => {
  const s = setup(list); s.intersect(true); s.tick(600); s.visibility(false); s.tick(2000);
  assert.equal(s.named('article_impression').length, 0);
});
test('article clicks use the target identity and preserve the real homepage URL', () => {
  const s = setup(list);
  s.w.document.querySelector('.post-link').dispatchEvent(new s.w.MouseEvent('click', { bubbles: true, cancelable: true }));
  const event = s.named('article_click')[0]; assert.ok(event);
  assert.equal(event[2].article_id, '/2026/03/example.html');
  assert.equal(event[2].send_to, 'G-YSYLBZSPC7');
  assert.equal(event[2].link_position, 1);
  assert.equal(s.named('page_view').length, 0);
});
test('qualified reads require BOTH 30 foreground seconds and 75 percent of the article', () => {
  const s = setup(); s.tick(30000); assert.equal(s.named('article_read').length, 0);
  s.progress(75); assert.equal(s.named('article_read').length, 1);
  s.progress(100); s.tick(30000); assert.equal(s.named('article_read').length, 1);
});
test('background or unfocused time does not qualify a read', () => {
  const s = setup(); s.progress(90); s.tick(10000); s.visibility(false); s.tick(60000);
  s.visibility(true); s.focus(false); s.tick(60000); assert.equal(s.named('article_read').length, 0);
  s.focus(true); s.tick(20000); assert.equal(s.named('article_read').length, 1);
});
test('scroll depth measures the article rather than sidebar and footer', () => {
  const s = setup(); s.progress(50);
  assert.equal(s.named('scroll_depth').at(-1)?.[2].percent, 50);
  assert.equal(s.named('scroll_depth').at(-1)?.[2].article_id, '/2026/03/example.html');
});
test('copy is tracked on successful clipboard completion, not a button click', () => {
  const s = setup(post + '<button class="code-copy-btn">Copy</button>');
  s.w.document.querySelector('button').click(); assert.equal(s.named('code_copy').length, 0);
  s.w.document.dispatchEvent(new s.w.CustomEvent('blog:code-copied'));
  assert.equal(s.named('code_copy').length, 1);
});
test('the rendered language switcher records the selected target language', () => {
  const s = setup();
  s.w.document.querySelector('#language-switcher').dispatchEvent(new s.w.MouseEvent('click', { bubbles: true, cancelable: true }));
  assert.equal(s.named('language_switch').length, 1);
  assert.equal(s.named('language_switch')[0][2].target_language, 'en');
});
test('analytics being blocked does not break clicks, scrolling, or timers', () => {
  const s = setup(post, false); s.progress(100); s.tick(40000);
  assert.equal(s.events.length, 0);
});
