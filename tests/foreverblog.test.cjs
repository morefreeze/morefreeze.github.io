const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const script = '../_scripts/refresh-foreverblog.cjs';
const { parseFeed, refresh } = fs.existsSync(path.join(__dirname, script)) ? require(script) : {};
const item = (id, date = 'Tue, 03 Nov 2026 00:00:09 +0800', title = `Article ${id}`) =>
  `<item><title>${title}</title><link>https://www.foreverblog.cn/daily/read/30/${id}/rss</link><guid>https://blog.example/${id}</guid><pubDate>${date}</pubDate></item>`;
const feed = entries => `<rss version="2.0"><channel>${entries.join('')}</channel></rss>`;

test('RSS parser selects the three latest distinct recommendations and keeps source metadata', () => {
  assert.equal(typeof parseFeed, 'function');
  const result = parseFeed(feed([item(1, 'Mon, 02 Nov 2026 00:00:09 +0800'), item(2), item(2), item(3), item(4)]));
  assert.deepEqual(result.map(i => i.title), ['Article 2', 'Article 3', 'Article 4']);
  assert.equal(result[0].url, 'https://www.foreverblog.cn/daily/read/30/2/rss');
  assert.equal(result[0].blog, 'blog.example');
  assert.equal(result[0].date, '2026-11-03');
});

test('RSS parser rejects malformed or insufficient feeds and skips unsafe article links', () => {
  assert.equal(typeof parseFeed, 'function');
  assert.throws(() => parseFeed('<rss>'), /feed|XML/i);
  assert.throws(() => parseFeed(feed([item(1)])), /three|3/i);
  const unsafe = item(0).replace('https://www.foreverblog.cn/daily/read/30/0/rss', 'javascript:alert(1)');
  const result = parseFeed(feed([unsafe, item(1), item(2), item(3)]));
  assert.equal(result.length, 3);
  assert.ok(result.every(i => i.url.startsWith('https://www.foreverblog.cn/daily/read/')));
});

test('refresh writes valid recommendations and preserves cached data on a feed outage', async () => {
  assert.equal(typeof refresh, 'function');
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'foreverblog-test-'));
  const target = path.join(dir, 'foreverblog.json');
  try {
    await refresh({ target, fetchImpl: async () => ({ ok: true, text: async () => feed([item(1), item(2), item(3)]) }) });
    const cached = fs.readFileSync(target, 'utf8');
    assert.equal(JSON.parse(cached).items.length, 3);
    const warn = [];
    await refresh({ target, fetchImpl: async () => { throw new Error('offline'); }, warn: message => warn.push(message) });
    assert.equal(fs.readFileSync(target, 'utf8'), cached);
    assert.equal(warn.length, 1);
    fs.unlinkSync(target);
    await assert.rejects(refresh({ target, fetchImpl: async () => ({ ok: false, status: 503 }) }), /503/);
  } finally { fs.rmSync(dir, { recursive: true, force: true }); }
});
