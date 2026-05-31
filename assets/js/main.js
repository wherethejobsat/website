/* Minimal JS for active navigation and the optional color-theme toggle. */
(function () {
  function cleanPath(pathname) {
    var p = pathname || "/";
    if (p.length > 1 && p.slice(-1) !== "/" && p.indexOf(".") === -1) {
      p += "/";
    }
    if (p.endsWith("/index.html")) {
      p = p.slice(0, -"index.html".length);
    }
    if (p === "") return "/";
    return p;
  }

  function setActiveNav() {
    var current = cleanPath(window.location.pathname);
    var links = document.querySelectorAll("header.site-header nav a");
    for (var i = 0; i < links.length; i++) {
      var a = links[i];
      var href = a.getAttribute("href") || "";
      if (!href || href.charAt(0) === "#") continue;
      var target = cleanPath(new URL(href, window.location.origin).pathname);
      if (target === current) a.setAttribute("aria-current", "page");
    }
  }

  function applyStoredTheme() {
    try {
      var t = localStorage.getItem("siteTheme");
      if (t === "light" || t === "dark") {
        document.documentElement.setAttribute("data-theme", t);
      }
    } catch (e) {}
  }

  function setupThemeToggle() {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;

    function label() {
      var t = document.documentElement.getAttribute("data-theme");
      return t === "dark" ? "Switch to light color theme" : "Switch to dark color theme";
    }

    function syncButton() {
      var isDark = document.documentElement.getAttribute("data-theme") === "dark";
      btn.setAttribute("aria-label", label());
      btn.setAttribute("title", label());
      btn.setAttribute("aria-pressed", isDark ? "true" : "false");
    }

    function toggle() {
      var cur = document.documentElement.getAttribute("data-theme");
      var next = (cur === "dark") ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("siteTheme", next); } catch (e) {}
      syncButton();
    }

    btn.addEventListener("click", toggle);
    syncButton();
  }

  applyStoredTheme();
  setActiveNav();
  setupThemeToggle();
})();
