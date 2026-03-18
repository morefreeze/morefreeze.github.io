(function () {
  'use strict';

  var searchIndex = null;
  var searchData = [];

  function getQuery() {
    var params = new URLSearchParams(window.location.search);
    return params.get('q') || '';
  }

  function setQuery(q) {
    var url = new URL(window.location.href);
    if (q) {
      url.searchParams.set('q', q);
    } else {
      url.searchParams.delete('q');
    }
    window.history.replaceState(null, '', url.toString());
  }

  function buildIndex(data) {
    return lunr(function () {
      this.ref('url');
      this.field('title', { boost: 10 });
      this.field('categories', { boost: 5 });
      this.field('content');

      data.forEach(function (doc) {
        this.add(doc);
      }, this);
    });
  }

  function excerpt(content, query) {
    var words = query.trim().split(/\s+/);
    var text = content.replace(/\s+/g, ' ');
    var idx = -1;

    for (var i = 0; i < words.length; i++) {
      idx = text.toLowerCase().indexOf(words[i].toLowerCase());
      if (idx !== -1) break;
    }

    if (idx === -1) return text.slice(0, 160) + '…';

    var start = Math.max(0, idx - 60);
    var end = Math.min(text.length, idx + 160);
    var snippet = (start > 0 ? '…' : '') + text.slice(start, end) + (end < text.length ? '…' : '');

    // highlight matched words
    words.forEach(function (w) {
      if (!w) return;
      snippet = snippet.replace(new RegExp('(' + w.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi'),
        '<mark>$1</mark>');
    });

    return snippet;
  }

  function renderResults(results, query) {
    var container = document.getElementById('search-results');

    if (!query) {
      container.innerHTML = '';
      return;
    }

    if (results.length === 0) {
      container.innerHTML = '<p class="search-no-results">没有找到 "<strong>' +
        query + '</strong>" 相关的文章。</p>';
      return;
    }

    var html = '<p class="search-count">找到 ' + results.length + ' 篇文章</p><ul class="search-result-list">';

    results.forEach(function (r) {
      var doc = searchData.find(function (d) { return d.url === r.ref; });
      if (!doc) return;
      html += '<li class="search-result-item">' +
        '<a class="search-result-title" href="' + doc.url + '">' + doc.title + '</a>' +
        '<div class="search-result-meta">' + doc.date +
        (doc.categories ? ' &nbsp;·&nbsp; ' + doc.categories : '') + '</div>' +
        '<p class="search-result-excerpt">' + excerpt(doc.content, query) + '</p>' +
        '</li>';
    });

    html += '</ul>';
    container.innerHTML = html;
  }

  function doSearch(query) {
    if (!query || !searchIndex) {
      renderResults([], query);
      return;
    }

    var results = [];
    try {
      // try exact + wildcard
      results = searchIndex.search(query);
      if (results.length === 0) {
        results = searchIndex.search(query.split(/\s+/).map(function (w) {
          return w + '*';
        }).join(' '));
      }
    } catch (e) {
      results = [];
    }

    renderResults(results, query);
  }

  function init() {
    var input = document.getElementById('search-input');
    if (!input) return;

    var initialQuery = getQuery();
    if (initialQuery) input.value = initialQuery;

    fetch('/search.json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        searchData = data;
        searchIndex = buildIndex(data);
        if (initialQuery) doSearch(initialQuery);
      });

    var debounceTimer;
    input.addEventListener('input', function () {
      clearTimeout(debounceTimer);
      var q = input.value.trim();
      setQuery(q);
      debounceTimer = setTimeout(function () { doSearch(q); }, 200);
    });

    input.addEventListener('keydown', function (e) {
      if (e.key === 'Enter') {
        clearTimeout(debounceTimer);
        doSearch(input.value.trim());
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
