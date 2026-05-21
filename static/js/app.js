(function () {
  function initLucide() {
    if (typeof lucide !== 'undefined') lucide.createIcons();
  }

  function initAlerts() {
    document.querySelectorAll('.alert').forEach(function (el) {
      setTimeout(function () {
        el.style.opacity = '0';
        el.style.transform = 'translateY(-6px)';
        setTimeout(function () {
          el.remove();
        }, 300);
      }, 5000);
    });
  }

  function initStagger() {
    document.querySelectorAll('.stagger-in').forEach(function (el, i) {
      el.style.animationDelay = i * 0.07 + 's';
    });
  }

  function initBarCharts() {
    document.querySelectorAll('.bar-fill[data-width]').forEach(function (bar) {
      var w = bar.getAttribute('data-width');
      requestAnimationFrame(function () {
        bar.style.width = w;
      });
    });
  }

  window.toggleSidebar = function () {
    var sidebar = document.getElementById('appSidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (!sidebar) return;
    sidebar.classList.toggle('active');
    if (overlay) overlay.classList.toggle('active');
    document.body.classList.toggle('sidebar-open');
  };

  document.addEventListener('click', function (event) {
    var sidebar = document.getElementById('appSidebar');
    var toggleBtn = document.querySelector('.mobile-menu-btn');
    if (
      window.innerWidth <= 1024 &&
      sidebar &&
      sidebar.classList.contains('active') &&
      !sidebar.contains(event.target) &&
      toggleBtn &&
      !toggleBtn.contains(event.target)
    ) {
      sidebar.classList.remove('active');
      var overlay = document.getElementById('sidebarOverlay');
      if (overlay) overlay.classList.remove('active');
      document.body.classList.remove('sidebar-open');
    }
  });

  document.addEventListener('DOMContentLoaded', function () {
    initLucide();
    initAlerts();
    initStagger();
    initBarCharts();
  });
})();
