/* Forectra site: header state and the mobile menu. */
(function () {
  var head = document.getElementById('site-head');
  if (head) {
    // The homepage header sits clear over the hero and turns solid on scroll.
    // Workspace pages use the light header, which is always solid.
    var togglesOnScroll = !head.classList.contains('light');
    var onScroll = function () {
      if (!togglesOnScroll) return;
      head.classList.toggle('solid', window.scrollY > 40);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    var btn = head.querySelector('.menu-btn');
    var panel = document.getElementById('mobile-nav');
    if (btn && panel) {
      var close = function () {
        panel.classList.remove('open');
        head.classList.remove('menu-open');
        btn.setAttribute('aria-expanded', 'false');
        btn.textContent = 'Menu';
      };
      btn.addEventListener('click', function () {
        var open = !panel.classList.contains('open');
        panel.classList.toggle('open', open);
        head.classList.toggle('menu-open', open);
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
        btn.textContent = open ? 'Close' : 'Menu';
      });
      panel.querySelectorAll('a').forEach(function (a) { a.addEventListener('click', close); });
    }
  }

})();
