/* Minimal JS:
   - active nav highlighting
   - light/dark toggle stored in localStorage
*/
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
      if (!t) return "Theme";
      return t === "dark" ? "Theme: dark" : "Theme: light";
    }

    function toggle() {
      var cur = document.documentElement.getAttribute("data-theme");
      var next = (cur === "dark") ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", next);
      try { localStorage.setItem("siteTheme", next); } catch (e) {}
      btn.textContent = label();
    }

    btn.addEventListener("click", toggle);
    btn.textContent = label();
  }

  applyStoredTheme();
  setActiveNav();
  setupThemeToggle();
})();
