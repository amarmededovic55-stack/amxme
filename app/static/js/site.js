/* Signed: ASDHEM | AMXME Web Solutions */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];

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
      toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
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
    if (v("name").length < 2) errors.name = "Please enter your full name.";
    if (!EMAIL.test(v("email"))) errors.email = "Please enter a valid email address.";
    if (!v("service")) errors.service = "Please choose the service you are interested in.";
    if (v("message").length < 10) errors.message = "Please write a message of at least 10 characters.";
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
    btn.disabled = true; label.textContent = "Sending…";
    try {
      const res = await fetch(form.action, { method: "POST", body: new FormData(form), headers: { "X-Requested-With": "fetch" } });
      const data = await res.json().catch(() => ({ ok: false, errors: { _: "Unexpected server response." } }));
      if (data.ok) {
        form.reset();
        okBox.textContent = data.message || "Thank you! Your message has been sent.";
        okBox.hidden = false;
        okBox.scrollIntoView({ behavior: "smooth", block: "center" });
      } else {
        const errs = data.errors || {};
        Object.entries(errs).forEach(([k, m]) => { if (k !== "_") setErr(k, m); });
        if (errs._) { errBox.textContent = errs._; errBox.hidden = false; }
      }
    } catch {
      errBox.textContent = "Could not send your message. Please check your connection or email us directly.";
      errBox.hidden = false;
    } finally {
      btn.disabled = false; label.textContent = original;
    }
  });
})();
