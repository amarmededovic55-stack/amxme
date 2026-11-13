/*! ASDHEM | AMXME Web Solutions – theme (dark / light) set before the page paints, no flash */
(function () {
  "use strict";
  var KEY = "amxme-theme", root = document.documentElement, saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* private mode */ }
  var mq = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;
  if (saved === "dark" || saved === "light") root.setAttribute("data-theme", saved);
  else root.setAttribute("data-theme", mq && mq.matches ? "dark" : "light");
  if (mq && mq.addEventListener) mq.addEventListener("change", function (e) {
    var s2 = null; try { s2 = localStorage.getItem(KEY); } catch (x) { /* ignore */ }
    if (!s2) root.setAttribute("data-theme", e.matches ? "dark" : "light");
  });
  function current() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  document.addEventListener("click", function (e) {
    var btn = e.target.closest && e.target.closest("[data-theme-toggle]");
    if (!btn) return;
    var next = current() === "dark" ? "light" : "dark";
    root.classList.add("theme-anim");
    root.setAttribute("data-theme", next);
    try { localStorage.setItem(KEY, next); } catch (e2) { /* ignore */ }
    setTimeout(function () { root.classList.remove("theme-anim"); }, 450);
  });
})();
