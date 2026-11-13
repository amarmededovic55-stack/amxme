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

  /* ASDHEM | floating language switcher: tap to open on touch screens, Esc / outside click closes */
  const lf = $("#langFloat"), lfBtn = $("#langBtn");
  if (lf && lfBtn) {
    const setLf = (open) => { lf.classList.toggle("is-open", open); lfBtn.setAttribute("aria-expanded", String(open)); };
    lfBtn.addEventListener("click", (e) => { e.stopPropagation(); setLf(!lf.classList.contains("is-open")); });
    document.addEventListener("click", (e) => { if (!lf.contains(e.target)) setLf(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") { setLf(false); } });
    lf.addEventListener("mouseenter", () => lfBtn.setAttribute("aria-expanded", "true"));
    lf.addEventListener("mouseleave", () => { if (!lf.classList.contains("is-open")) lfBtn.setAttribute("aria-expanded", "false"); });
    let greeted = false;
    try { greeted = sessionStorage.getItem("lfHello") === "1"; sessionStorage.setItem("lfHello", "1"); } catch { /* private mode */ }
    if (!greeted) setTimeout(() => { lf.classList.add("hello"); setTimeout(() => lf.classList.remove("hello"), 1400); }, 1800);
  }

  /* ASDHEM | website check: show progress on the button */
  const chk = $("#checkForm");
  if (chk) chk.addEventListener("submit", () => {
    const b = chk.querySelector("button[data-busy]");
    if (b) { b.disabled = true; b.textContent = b.dataset.busy; }
  });

  /* ASDHEM | signature in the browser console */
  try {
    console.log("%cASDHEM", "font: 900 46px/1.1 system-ui, sans-serif; letter-spacing: .12em; background: linear-gradient(135deg,#4c1d95,#a855f7); color: #fff; padding: 10px 28px; border-radius: 14px;");
    console.log("%cDesigned & built by ASDHEM · AMXME Web Solutions", "font: 600 13px system-ui, sans-serif; color: #7c3aed;");
  } catch { /* no console */ }

  /* sticky nav state */
  const nav = $(".nav");
  const onScroll = () => nav && nav.classList.toggle("is-scrolled", window.scrollY > 10);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  /* mobile menu */
  const toggle = $("#navToggle"), links = $("#navLinks");
  if (toggle && links) {
    const set = (open) => {
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? tr("menu_close", "Close menu") : tr("menu_open", "Open menu"));
      links.classList.toggle("is-open", open);
      nav.classList.toggle("menu-open", open);
    };
    toggle.addEventListener("click", () => set(toggle.getAttribute("aria-expanded") !== "true"));
    links.addEventListener("click", (e) => { if (e.target.closest("a")) set(false); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") set(false); });
    document.addEventListener("click", (e) => { if (!nav.contains(e.target)) set(false); });
  }

  /* reveal on scroll */
  const reveals = $$(".reveal");
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("is-in"); io.unobserve(en.target); } });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });
    reveals.forEach((el) => io.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add("is-in"));
  }

  /* highlight current section in nav */
  const navLinks = $$('.nav-links a[href^="#"]:not(.btn)');
  const targets = navLinks.map((a) => $(a.getAttribute("href"))).filter(Boolean);
  if (targets.length && "IntersectionObserver" in window) {
    const so = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) {
          navLinks.forEach((a) => a.classList.toggle("is-current", a.getAttribute("href") === "#" + en.target.id));
        }
      });
    }, { rootMargin: "-45% 0px -50% 0px" });
    targets.forEach((t) => so.observe(t));
  }

  /* trust strip column count */
  const trust = $(".trust");
  if (trust) trust.style.setProperty("--n", trust.children.length);

  /* portfolio filter */
  const filters = $$(".filter");
  filters.forEach((btn) => btn.addEventListener("click", () => {
    const f = btn.dataset.filter;
    filters.forEach((b) => { const on = b === btn; b.classList.toggle("is-active", on); b.setAttribute("aria-selected", String(on)); });
    $$(".pf").forEach((card) => card.classList.toggle("is-hidden", f !== "*" && card.dataset.category !== f));
  }));

  /* "Ask about this" preselects the service */
  const serviceSelect = $("#f-service");
  $$(".svc-link[data-service]").forEach((a) => a.addEventListener("click", () => {
    if (!serviceSelect) return;
    const opt = [...serviceSelect.options].find((o) => o.value === a.dataset.service);
    if (opt) { serviceSelect.value = opt.value; clearErr("service"); }
    setTimeout(() => $("#f-name")?.focus({ preventScroll: true }), 600);
  }));

  /* contact form */
  const form = $("#contactForm");
  if (!form) return;
  const btn = $("#contactBtn"), okBox = $("#formSuccess"), errBox = $("#formError");
  const EMAIL = /^[^@\s<>]+@[^@\s<>]+\.[A-Za-z]{2,}$/;

  function setErr(name, msg) {
    const el = form.querySelector(`.err[data-for="${name}"]`);
    const field = form.elements[name]?.closest(".field");
    if (el) el.textContent = msg || "";
    if (field) field.classList.toggle("has-error", !!msg);
  }
  function clearErr(name) { setErr(name, ""); }

  function validate() {
    const v = (n) => (form.elements[n].value || "").trim();
    const errors = {};
    if (v("name").length < 2) errors.name = tr("err_name", "Please enter your full name.");
    if (!EMAIL.test(v("email"))) errors.email = tr("err_email", "Please enter a valid email address.");
    if (!v("service")) errors.service = tr("err_service", "Please choose the service you are interested in.");
    if (v("message").length < 10) errors.message = tr("err_message", "Please write a message of at least 10 characters.");
    return errors;
  }

  ["name", "email", "service", "message"].forEach((n) => {
    const el = form.elements[n];
    el.addEventListener("input", () => clearErr(n));
    el.addEventListener("change", () => clearErr(n));
  });

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    okBox.hidden = true; errBox.hidden = true;
    ["name", "email", "service", "message"].forEach(clearErr);
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

  /* ASDHEM | FAQ: categories, live search, "ask this question" hand-off to the contact form, deep links */
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
        if (ok) { it.classList.add("is-in"); shown++; }
      });
      if (empty) {
        empty.hidden = shown > 0;
        if (term) term.textContent = raw;
      }
    };
    cats.forEach((b) => b.addEventListener("click", () => {
      cat = b.dataset.cat;
      cats.forEach((x) => { const on = x === b; x.classList.toggle("is-active", on); x.setAttribute("aria-selected", String(on)); });
      apply();
    }));
    if (search) search.addEventListener("input", apply);

    /* only one answer open at a time */
    items.forEach((it) => it.addEventListener("toggle", () => {
      if (it.open) items.forEach((o) => { if (o !== it && o.open) o.open = false; });
    }));

    /* "Ask this question" -> prefill the contact form message */
    if (ask) ask.addEventListener("click", () => {
      const msg = $("#f-message"), q = search ? search.value.trim() : "";
      if (msg && q && !msg.value.trim()) msg.value = `${tr("faq_q_prefix", "Question")}: ${q}\n\n`;
      setTimeout(() => { const n = $("#f-name"); if (n) n.focus({ preventScroll: true }); }, 700);
    });

    /* deep link: /#faq-12 opens that answer; "copy link" copies it */
    const openFromHash = () => {
      const t = location.hash.startsWith("#faq-") ? document.getElementById(location.hash.slice(1)) : null;
      if (t && t.classList.contains("faq-item")) {
        t.hidden = false; t.classList.add("is-in"); t.open = true;
        t.scrollIntoView({ block: "center" });
      }
    };
    openFromHash();
    window.addEventListener("hashchange", openFromHash);
    $$("[data-copy-link]", faqList).forEach((a) => a.addEventListener("click", async (e) => {
      e.preventDefault();
      const hash = a.getAttribute("href");
      history.replaceState(null, "", hash);
      const span = $("span", a), old = span.textContent;
      try { await navigator.clipboard.writeText(location.origin + location.pathname + hash); span.textContent = tr("faq_copied", "Link copied!"); }
      catch { span.textContent = tr("faq_copy_fail", "Copy the address from your browser bar"); }
      setTimeout(() => { span.textContent = old; }, 2200);
    }));
  }
})();
