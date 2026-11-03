(function () {
  'use strict';

  var sidebar = document.querySelector('.site-sidebar');
  if (!sidebar) return;

  // Match $sidebar-breakpoint in css/main.scss and the two-column CSS rules.
  var desktop = window.matchMedia('(min-width: 768px)');
  function syncLayout() {
    sidebar.open = desktop.matches;
  }

  syncLayout();
  desktop.addEventListener('change', syncLayout);
})();
