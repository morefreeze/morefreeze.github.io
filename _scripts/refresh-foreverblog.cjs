const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');

const FEED = 'https://www.foreverblog.cn/daily.xml';
const isArticleUrl = value => {
  try {
    const url = new URL(value);
    return url.origin === 'https://www.foreverblog.cn' && url.pathname.startsWith('/daily/read/');
  } catch { return false; }
};

function parseFeed(xml) {
  let dom;
  try { dom = new JSDOM(xml, { contentType: 'text/xml' }); }
  catch (error) { throw new Error(`Invalid RSS feed XML: ${error.message}`); }
  try {
    const seen = new Set();
    const items = [];
    for (const item of dom.window.document.querySelectorAll('rss > channel > item')) {
      const text = name => item.querySelector(name)?.textContent.trim() || '';
      const title = text('title'), url = text('link'), guid = text('guid');
      const time = Date.parse(text('pubDate'));
      let blog;
      try {
        const original = new URL(guid);
        if (!['http:', 'https:'].includes(original.protocol)) continue;
        blog = original.hostname;
      } catch { continue; }
      if (!title || !isArticleUrl(url) || !Number.isFinite(time) || seen.has(guid)) continue;
      seen.add(guid);
      items.push({ title, url, blog, date: new Date(time + 8 * 3600000).toISOString().slice(0, 10), time });
    }
    items.sort((a, b) => b.time - a.time);
    if (items.length < 3) throw new Error('RSS feed must contain at least three valid recommendations');
    return items.slice(0, 3).map(({ time, ...item }) => item);
  } finally { dom.window.close(); }
}

async function refresh({ target = path.join(__dirname, '../_data/foreverblog.json'), fetchImpl = fetch, warn = console.warn } = {}) {
  try {
    const response = await fetchImpl(FEED, { signal: AbortSignal.timeout(15000) });
    if (!response.ok) throw new Error(`RSS request failed: HTTP ${response.status}`);
    const data = { source: FEED, fetched_at: new Date().toISOString(), items: parseFeed(await response.text()) };
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.writeFileSync(target, JSON.stringify(data, null, 2) + '\n');
    return true;
  } catch (error) {
    let cached;
    try { cached = JSON.parse(fs.readFileSync(target, 'utf8')); } catch {}
    if (!cached || cached.items?.length !== 3 || !cached.items.every(i => i.title && isArticleUrl(i.url) && i.blog && /^\d{4}-\d{2}-\d{2}$/.test(i.date))) throw error;
    warn(`ForeverBlog refresh failed (${error.message}); using cached recommendations fetched at ${cached.fetched_at}.`);
    return false;
  }
}

module.exports = { parseFeed, refresh };
if (require.main === module) refresh().catch(error => { console.error(error.message); process.exitCode = 1; });
