(function () {
  'use strict';

  var sidebar = document.querySelector('.site-sidebar');
  if (!sidebar) return;

  // Match the existing two-column layout breakpoint in _sass/_base.scss.
  var desktop = window.matchMedia('(min-width: 600px)');
  function syncLayout() {
    sidebar.open = desktop.matches;
  }

  syncLayout();
  desktop.addEventListener('change', syncLayout);
})();
