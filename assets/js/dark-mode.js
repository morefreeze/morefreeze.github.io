(function () {
  'use strict';

  var STORAGE_KEY = 'theme';
  var root = document.documentElement;

  function getPreferred() {
    var stored = localStorage.getItem(STORAGE_KEY);
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }

  function applyTheme(theme) {
    root.setAttribute('data-theme', theme);
    localStorage.setItem(STORAGE_KEY, theme);
    updateButton(theme);

    var widget = document.getElementById('foreverblog-today');
    if (widget) {
      var src = 'https://www.foreverblog.cn/widget/today.html?theme=' + theme;
      if (widget.getAttribute('src') !== src) widget.setAttribute('src', src);
    }
  }

  function updateButton(theme) {
    var btn = document.getElementById('dark-mode-toggle');
    if (!btn) return;
    btn.textContent = theme === 'dark' ? '☀' : '☾';
    btn.title = theme === 'dark' ? '切换为亮色模式' : '切换为暗色模式';
  }

  function toggle() {
    var current = root.getAttribute('data-theme') || 'light';
    applyTheme(current === 'dark' ? 'light' : 'dark');
  }

  // Apply immediately to avoid flash
  applyTheme(getPreferred());

  document.addEventListener('DOMContentLoaded', function () {
    var btn = document.getElementById('dark-mode-toggle');
    if (btn) {
      btn.addEventListener('click', toggle);
      updateButton(root.getAttribute('data-theme'));
    }

    // Listen for system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
      if (!localStorage.getItem(STORAGE_KEY)) {
        applyTheme(e.matches ? 'dark' : 'light');
      }
    });
  });
})();
