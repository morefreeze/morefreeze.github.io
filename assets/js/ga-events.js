(function () {
  'use strict';
  var DESTINATION = 'G-YSYLBZSPC7';

  function identity(element) {
    return element ? {
      article_id: element.getAttribute('data-article-id'),
      article_language: element.getAttribute('data-article-language') || 'zh'
    } : {};
  }

  function send(name, parameters) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', name, Object.assign({ send_to: DESTINATION }, parameters));
  }

  function ready() {
    var post = document.querySelector('.post[data-article-id]');
    var context = identity(post);
    var previews = Array.from(document.querySelectorAll('.home-post-item'));
    var exposures = [];

    // Measure the title/preview entering the viewport, never invent page views.
    if (window.IntersectionObserver) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          var exposure = exposures.find(function (item) { return item.target === entry.target; });
          if (!exposure) return;
          exposure.visible = entry.isIntersecting && entry.intersectionRatio >= 0.5;
          scheduleExposure(exposure);
        });
      }, { threshold: [0, 0.5] });
      previews.forEach(function (preview, index) {
        var exposure = { target: preview.querySelector('.post-header'), preview: preview, position: index + 1 };
        if (!exposure.target) return;
        exposures.push(exposure);
        observer.observe(exposure.target);
      });
    }

    function scheduleExposure(exposure) {
      clearTimeout(exposure.timer);
      if (exposure.fired || !exposure.visible || document.visibilityState !== 'visible') return;
      exposure.timer = setTimeout(function () {
        if (document.visibilityState !== 'visible' || !exposure.visible || exposure.fired) return;
        exposure.fired = true;
        send('article_impression', Object.assign(identity(exposure.preview), {
          link_position: exposure.position, link_source: 'home'
        }));
      }, 1000);
    }
    document.addEventListener('visibilitychange', function () { exposures.forEach(scheduleExposure); });

    document.addEventListener('click', function (event) {
      var link = event.target.closest('a');
      if (!link) return;
      var preview = link.closest('.home-post-item');
      if (preview && (link.classList.contains('post-link') || link.classList.contains('read-more'))) {
        send('article_click', Object.assign(identity(preview), {
          link_position: previews.indexOf(preview) + 1,
          link_source: 'home', target_url: link.href
        }));
      }
      if (link.id === 'language-switcher') {
        send('language_switch', Object.assign({}, context, {
          target_url: link.href, target_language: link.pathname.endsWith('_en.html') ? 'en' : 'zh'
        }));
      }
      if (link.closest('#recommend-list')) {
        var target = new URL(link.href);
        var targetContext = {
          article_id: target.pathname.replace(/_en\.html$/, '.html'),
          article_language: target.pathname.endsWith('_en.html') ? 'en' : 'zh',
          link_source: 'recommend', target_url: link.href
        };
        send('article_click', targetContext);
        send('recommend_click', Object.assign({}, context, { target_url: link.href, target_title: link.textContent }));
      }
    });
    document.addEventListener('blog:code-copied', function () { send('code_copy', context); });

    var darkButton = document.getElementById('dark-mode-toggle');
    if (darkButton) darkButton.addEventListener('click', function () {
      send('theme_toggle', { theme: document.documentElement.getAttribute('data-theme') });
    });
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
      var searchTimer;
      searchInput.addEventListener('input', function () {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () {
          if (searchInput.value.trim().length >= 2) send('site_search', { search_term: searchInput.value.trim() });
        }, 1000);
      });
    }

    var article = post && post.querySelector('[data-article-content]');
    if (!article) return;
    var elapsed = 0, previous = Date.now(), maxProgress = 0, read = false;
    var scrollFired = {};
    var wasActive = document.visibilityState === 'visible' && document.hasFocus();

    function active() { return document.visibilityState === 'visible' && document.hasFocus(); }
    function qualify() {
      if (!read && elapsed >= 30000 && maxProgress >= 75) {
        read = true;
        send('article_read', Object.assign({}, context, { reading_seconds: Math.floor(elapsed / 1000), percent: maxProgress }));
      }
    }
    function clock() {
      var now = Date.now();
      // Cap suspended/throttled timer gaps; background time is never credited.
      if (wasActive && active()) elapsed += Math.min(now - previous, 1500);
      previous = now;
      wasActive = active();
      qualify();
    }
    function progress() {
      if (!active()) return;
      var rect = article.getBoundingClientRect();
      if (rect.height <= 0 || rect.top >= window.innerHeight) return;
      var percent = Math.min(100, Math.max(0, Math.floor((window.innerHeight - rect.top) / rect.height * 100)));
      maxProgress = Math.max(maxProgress, percent);
      [25, 50, 75, 100].forEach(function (mark) {
        if (maxProgress >= mark && !scrollFired[mark]) {
          scrollFired[mark] = true;
          send('scroll_depth', Object.assign({}, context, { percent: mark }));
        }
      });
      qualify();
    }
    setInterval(clock, 1000);
    window.addEventListener('scroll', progress, { passive: true });
    window.addEventListener('resize', progress);
    window.addEventListener('focus', function () { clock(); progress(); });
    window.addEventListener('blur', clock);
    document.addEventListener('visibilitychange', function () { clock(); progress(); });
    progress();
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', ready, { once: true });
  else ready();
})();
