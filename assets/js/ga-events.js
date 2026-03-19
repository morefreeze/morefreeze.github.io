(function () {
  'use strict';

  // --- Scroll depth tracking (25%, 50%, 75%, 100%) ---
  var scrollMarks = [25, 50, 75, 100];
  var scrollFired = {};

  window.addEventListener('scroll', function () {
    var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    var docHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (docHeight <= 0) return;
    var percent = Math.round((scrollTop / docHeight) * 100);

    scrollMarks.forEach(function (mark) {
      if (percent >= mark && !scrollFired[mark]) {
        scrollFired[mark] = true;
        gtag('event', 'scroll_depth', {
          percent: mark,
          page_title: document.title
        });
      }
    });
  });

  // --- Dark mode toggle tracking ---
  document.addEventListener('DOMContentLoaded', function () {
    var darkBtn = document.getElementById('dark-mode-toggle');
    if (darkBtn) {
      darkBtn.addEventListener('click', function () {
        var newTheme = document.documentElement.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
        gtag('event', 'theme_toggle', { theme: newTheme });
      });
    }

    // --- Language switcher tracking ---
    var langBtn = document.getElementById('lang-switch');
    if (langBtn) {
      langBtn.addEventListener('click', function () {
        gtag('event', 'language_switch', {
          target_url: langBtn.getAttribute('href')
        });
      });
    }

    // --- Recommend post click tracking ---
    var recommendList = document.getElementById('recommend-list');
    if (recommendList) {
      recommendList.addEventListener('click', function (e) {
        var link = e.target.closest('a');
        if (link) {
          gtag('event', 'recommend_click', {
            target_title: link.textContent,
            target_url: link.getAttribute('href')
          });
        }
      });
    }

    // --- Search usage tracking ---
    var searchInput = document.getElementById('search-input');
    if (searchInput) {
      var searchTimer;
      searchInput.addEventListener('input', function () {
        clearTimeout(searchTimer);
        var query = searchInput.value;
        searchTimer = setTimeout(function () {
          if (query.length >= 2) {
            gtag('event', 'site_search', { search_term: query });
          }
        }, 1000);
      });
    }

    // --- Code copy button tracking ---
    document.addEventListener('click', function (e) {
      if (e.target.closest('.copy-btn')) {
        gtag('event', 'code_copy', { page_title: document.title });
      }
    });
  });
})();
