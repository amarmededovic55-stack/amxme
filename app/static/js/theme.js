/*!
 *     █████╗ ███████╗██████╗ ██╗  ██╗███████╗███╗   ███╗
 *    ██╔══██╗██╔════╝██╔══██╗██║  ██║██╔════╝████╗ ████║
 *    ███████║███████╗██║  ██║███████║█████╗  ██╔████╔██║
 *    ██╔══██║╚════██║██║  ██║██╔══██║██╔══╝  ██║╚██╔╝██║
 *    ██║  ██║███████║██████╔╝██║  ██║███████╗██║ ╚═╝ ██║
 *    ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝
 *    ASDHEM | AMXME Web Solutions – theme set before the page paints (no flash).
 *    Dark is the brand default; a visitor's own choice (toggle) is remembered.
 */
(function () {
  "use strict";
  var KEY = "amxme-theme", root = document.documentElement, saved = null;
  root.classList.add("js");
  try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
  root.setAttribute("data-theme", saved === "light" ? "light" : "dark");
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    var next = root.getAttribute("data-theme") === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    var meta = document.querySelector('meta[name="theme-color"]');
    if (meta) meta.setAttribute("content", next === "dark" ? "#090B18" : "#F6F6FA");
    try { localStorage.setItem(KEY, next); } catch (e2) { /* ignore */ }
  });
})();
