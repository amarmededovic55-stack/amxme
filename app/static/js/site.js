/*!
 *     █████╗ ███████╗██████╗ ██╗  ██╗███████╗███╗   ███╗
 *    ██╔══██╗██╔════╝██╔══██╗██║  ██║██╔════╝████╗ ████║
 *    ███████║███████╗██║  ██║███████║█████╗  ██╔████╔██║
 *    ██╔══██║╚════██║██║  ██║██╔══██║██╔══╝  ██║╚██╔╝██║
 *    ██║  ██║███████║██████╔╝██║  ██║███████╗██║ ╚═╝ ██║
 *    ╚═╝  ╚═╝╚══════╝╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝
 *
 *    Designed & built by ASDHEM  ·  AMXME Web Solutions
 */
/* Signed: ASDHEM | AMXME Web Solutions */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  /* ASDHEM | UI strings in the page language (JSON block from the server) */
  let T = {};
  try { T = JSON.parse(($("#i18n") || {}).textContent || "{}"); } catch { T = {}; }
  const tr = (k, fb) => T[k] || fb;

  /* ASDHEM | signature in the browser console */
  try {
    console.log("%cASDHEM", "font: 800 40px/1.1 system-ui, sans-serif; letter-spacing: .14em; background: #090B18; color: #A78BFA; padding: 10px 26px; border-radius: 10px;");
    console.log("%cDesigned & built by ASDHEM · AMXME Web Solutions", "font: 600 13px system-ui, sans-serif; color: #7838D9;");
  } catch { /* no console */ }

  /* ---------------------------------------------------------- header */
  const hdr = $(".hdr");
  if (hdr) {
    const onScroll = () => hdr.classList.toggle("is-scrolled", window.scrollY > 8);
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* mobile menu */
  const toggle = $("#navToggle"), nav = $("#siteNav");
  if (toggle && nav) {
    const set = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? tr("menu_close", "Close menu") : tr("menu_open", "Open menu"));
      nav.classList.toggle("is-open", open);
      document.body.classList.toggle("menu-open", open);
    };
    toggle.addEventListener("click", () => set(toggle.getAttribute("aria-expanded") !== "true"));
    nav.addEventListener("click", (e) => { if (e.target.closest(".hdr-links a, .hdr-cta, .hdr-portal")) set(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape" && nav.classList.contains("is-open")) { set(false); toggle.focus(); } });
    window.matchMedia("(min-width: 1101px)").addEventListener("change", (e) => { if (e.matches) set(false); });
  }

  /* language dropdowns (header, footer, portal) */
  const langs = $$("[data-lang]");
  const closeLangs = (except) => langs.forEach((l) => {
    if (l === except) return;
    l.classList.remove("is-open");
    const b = $(".lang-btn", l); if (b) b.setAttribute("aria-expanded", "false");
  });
  langs.forEach((l) => {
    const b = $(".lang-btn", l);
    if (!b) return;
    b.addEventListener("click", (e) => {
      e.stopPropagation();
      const open = !l.classList.contains("is-open");
      closeLangs(l);
      l.classList.toggle("is-open", open);
      b.setAttribute("aria-expanded", String(open));
    });
  });
  document.addEventListener("click", (e) => { if (!e.target.closest("[data-lang]")) closeLangs(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeLangs(); });

  /* highlight the section in view (homepage) */
  const navLinks = $$('.hdr-links a[href^="#"]');
  const targets = navLinks.map((a) => $(a.getAttribute("href"))).filter(Boolean);
  if (targets.length && "IntersectionObserver" in window) {
    const so = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) navLinks.forEach((a) => a.classList.toggle("is-current", a.getAttribute("href") === "#" + en.target.id));
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    targets.forEach((t) => so.observe(t));
  }

  /* subtle fade-in on scroll (content stays visible without JS) */
  const reveals = $$(".reveal");
  if ("IntersectionObserver" in window && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.06 });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("is-in"));
  }

  /* ASDHEM | portfolio pop-up window ("Projects" in the menu, or /#projekti) */
  const pf = $("#projekti");
  if (pf && pf.tagName === "DIALOG") {
    let opener = null;
    const openPf = () => {
      if (pf.open) return;
      $$("img[data-src]", pf).forEach((im) => { im.src = im.dataset.src; delete im.dataset.src; });
      if (typeof pf.showModal === "function") pf.showModal(); else pf.setAttribute("open", "");
      document.body.classList.add("dialog-open");
      pf.scrollTop = 0;
    };
    const closePf = () => { if (typeof pf.close === "function") pf.close(); else pf.removeAttribute("open"); };
    pf.addEventListener("close", () => {
      document.body.classList.remove("dialog-open");
      if (location.hash === "#projekti") history.replaceState(null, "", location.pathname + location.search);
      if (opener) opener.focus({ preventScroll: true });
    });
    $$("[data-open-portfolio]").forEach((a) => a.addEventListener("click", (e) => { e.preventDefault(); opener = a; openPf(); }));
    $$("[data-close-portfolio]", pf).forEach((b) => b.addEventListener("click", closePf));
    pf.addEventListener("click", (e) => { if (e.target === pf) closePf(); });   // click on the dimmed backdrop
    if (location.hash === "#projekti") openPf();
  }

  /* ASDHEM | perf: pause the hero animation while it is off screen */
  const hv = $(".hv");
  if (hv && "IntersectionObserver" in window) {
    new IntersectionObserver(([en]) => hv.classList.toggle("is-paused", !en.isIntersecting)).observe(hv);
  }

  /* website check: show progress on the button */
  const chk = $("#checkForm");
  if (chk) chk.addEventListener("submit", () => {
    const b = chk.querySelector("button[data-busy]");
    if (b) { b.disabled = true; b.textContent = b.dataset.busy; }
  });

  /* ---------------------------------------------------------- contact form */
  const form = $("#contactForm");
  const serviceSelect = $("#f-service");
  /* "Request a quote" on a service preselects it in the form */
  $$("[data-service]").forEach((a) => a.addEventListener("click", () => {
    if (!serviceSelect) return;
    const opt = [...serviceSelect.options].find((o) => o.value === a.dataset.service);
    if (opt) { serviceSelect.value = opt.value; serviceSelect.dispatchEvent(new Event("change")); }
    setTimeout(() => $("#f-name")?.focus({ preventScroll: true }), 600);
  }));

  if (form) {
    const btn = $("#contactBtn"), okBox = $("#formSuccess"), errBox = $("#formError");
    const EMAIL = /^[^@\s<>]+@[^@\s<>]+\.[A-Za-z]{2,}$/;
    const FIELDS = ["name", "email", "service", "message"];
    const setErr = (name, msg) => {
      const el = form.querySelector(`.err[data-for="${name}"]`);
      const input = form.elements[name];
      const field = input?.closest(".field");
      if (el) { el.textContent = msg || ""; el.id = el.id || `err-${name}`; }
      if (field) field.classList.toggle("has-error", !!msg);
      if (input) {
        if (msg) { input.setAttribute("aria-invalid", "true"); input.setAttribute("aria-describedby", `err-${name}`); }
        else { input.removeAttribute("aria-invalid"); }
      }
    };
    const validate = () => {
      const v = (n) => (form.elements[n].value || "").trim();
      const errors = {};
      if (v("name").length < 2) errors.name = tr("err_name", "Please enter your full name.");
      if (!EMAIL.test(v("email"))) errors.email = tr("err_email", "Please enter a valid email address.");
      if (!v("service")) errors.service = tr("err_service", "Please choose the service you are interested in.");
      if (v("message").length < 10) errors.message = tr("err_message", "Please write a message of at least 10 characters.");
      return errors;
    };
    FIELDS.forEach((n) => {
      const el = form.elements[n];
      el.addEventListener("input", () => setErr(n, ""));
      el.addEventListener("change", () => setErr(n, ""));
    });
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      okBox.hidden = true; errBox.hidden = true;
      FIELDS.forEach((n) => setErr(n, ""));
      const errors = validate();
      if (Object.keys(errors).length) {
        Object.entries(errors).forEach(([k, m]) => setErr(k, m));
        form.elements[Object.keys(errors)[0]].focus();
        return;
      }
      const label = btn.querySelector(".btn-label"), original = label.textContent;
      btn.disabled = true; label.textContent = tr("f_sending", "Sending…");
      try {
        const res = await fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "fetch" } });
        const data = await res.json().catch(() => ({ ok: false, errors: { _: tr("err_unexpected", "Unexpected server response.") } }));
        if (data.ok) {
          form.reset();
          okBox.textContent = data.message || tr("f_success", "Thank you! Your message has been sent.");
          okBox.hidden = false;
          okBox.scrollIntoView({ behavior: "smooth", block: "center" });
        } else {
          const errs = data.errors || {};
          Object.entries(errs).forEach(([k, m]) => { if (k !== "_") setErr(k, m); });
          if (errs._) { errBox.textContent = errs._; errBox.hidden = false; }
        }
      } catch {
        errBox.textContent = tr("err_network", "Could not send your message. Please check your connection or email us directly.");
        errBox.hidden = false;
      } finally {
        btn.disabled = false; label.textContent = original;
      }
    });
  }

  /* ---------------------------------------------------------- FAQ page */
  const faqList = $("#faqList");
  if (faqList) {
    const items = $$(".faq-item", faqList);
    const search = $("#faqSearch"), empty = $("#faqEmpty"), term = $("#faqTerm"), ask = $("#faqAsk");
    const cats = $$(".faq-cat");
    let cat = "*";
    const norm = (t) => (t || "").toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g, "");
    items.forEach((it) => { it.dataset.text = norm(it.textContent); });
    const apply = () => {
      const raw = search ? search.value.trim() : "";
      const words = norm(raw).split(/\s+/).filter(Boolean);
      let shown = 0;
      items.forEach((it) => {
        const ok = (cat === "*" || it.dataset.cat === cat) && words.every((w) => it.dataset.text.includes(w));
        it.hidden = !ok;
        if (ok) shown++;
      });
      if (empty) { empty.hidden = shown > 0; if (term) term.textContent = raw; }
    };
    if (search) search.addEventListener("input", apply);
    cats.forEach((b) => b.addEventListener("click", () => {
      cat = b.dataset.cat;
      cats.forEach((x) => { const on = x === b; x.classList.toggle("is-active", on); x.setAttribute("aria-selected", String(on)); });
      apply();
    }));
    /* "ask this question": hand the search term to the contact form on the homepage */
    if (ask) ask.addEventListener("click", () => {
      const q = search ? search.value.trim() : "";
      try { if (q) sessionStorage.setItem("faqQuestion", q); } catch { /* private mode */ }
    });
    /* deep link: /faq#faq-12 opens that answer; "copy link" copies it */
    const openFromHash = () => {
      const t = location.hash.startsWith("#faq-") ? document.getElementById(location.hash.slice(1)) : null;
      if (t && t.classList.contains("faq-item")) { t.hidden = false; t.open = true; }
    };
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
    $$("[data-copy-link]", faqList).forEach((a) => a.addEventListener("click", async (e) => {
      e.preventDefault();
      const span = a.querySelector("span"), old = span.textContent;
      const hash = a.getAttribute("href");
      try { await navigator.clipboard.writeText(location.origin + location.pathname + hash); span.textContent = tr("faq_copied", "Link copied!"); }
      catch { span.textContent = tr("faq_copy_fail", "Copy the address from your browser bar"); }
      setTimeout(() => { span.textContent = old; }, 2200);
    }));
  }

  /* question handed over from the FAQ page */
  const msg = $("#f-message");
  if (msg) {
    let q = null;
    try { q = sessionStorage.getItem("faqQuestion"); sessionStorage.removeItem("faqQuestion"); } catch { /* ignore */ }
    if (q && !msg.value.trim()) msg.value = `${tr("faq_q_prefix", "Question")}: ${q}\n\n`;
  }
})();
