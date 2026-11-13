/* Signed: ASDHEM | AMXME Web Solutions */
(() => {
  "use strict";
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const csrf = $('meta[name="csrf-token"]')?.content || "";

  /* mobile sidebar */
  const side = $("#side"), scrim = $("#sideScrim"), menuBtn = $("#menuBtn");
  const setMenu = (open) => { side?.classList.toggle("open", open); scrim?.classList.toggle("open", open); };
  menuBtn?.addEventListener("click", () => setMenu(true));
  scrim?.addEventListener("click", () => setMenu(false));

  /* flash dismiss + auto-hide success */
  $$(".flash").forEach((f) => {
    f.querySelector(".flash-x")?.addEventListener("click", () => f.remove());
    if (f.classList.contains("flash-success")) setTimeout(() => f.remove(), 5000);
  });

  /* confirm dialogs */
  $$("form[data-confirm]").forEach((f) => f.addEventListener("submit", (e) => {
    if (!confirm(f.dataset.confirm)) e.preventDefault();
  }));

  /* autosize textareas */
  const autosize = (t) => { t.style.height = "auto"; t.style.height = t.scrollHeight + 4 + "px"; };
  $$("textarea[data-autosize]").forEach((t) => { autosize(t); t.addEventListener("input", () => autosize(t)); });

  /* image preview */
  $$("input[data-image-input]").forEach((inp) => inp.addEventListener("change", () => {
    const file = inp.files[0];
    const prev = inp.closest(".imgfield")?.querySelector("[data-preview]");
    if (!file || !prev) return;
    const url = URL.createObjectURL(file);
    prev.innerHTML = "";
    const img = new Image(); img.src = url; img.alt = ""; prev.appendChild(img);
  }));

  /* warn about unsaved changes */
  $$("form[data-dirty-guard]").forEach((f) => {
    let dirty = false;
    f.addEventListener("input", () => { dirty = true; });
    f.addEventListener("change", () => { dirty = true; });
    f.addEventListener("submit", () => { dirty = false; });
    window.addEventListener("beforeunload", (e) => { if (dirty) { e.preventDefault(); e.returnValue = ""; } });
  });

  /* toggle visibility without reload */
  $$(".toggle-form").forEach((f) => f.addEventListener("submit", async (e) => {
    e.preventDefault();
    const btn = f.querySelector(".switch");
    try {
      const res = await fetch(f.action, { method: "POST", body: new FormData(f), headers: { "X-Requested-With": "fetch" } });
      const data = await res.json();
      if (!data.ok) throw new Error();
      btn.classList.toggle("on", data.enabled);
      btn.setAttribute("aria-checked", String(data.enabled));
      btn.title = data.enabled ? "Visible – click to hide" : "Hidden – click to show";
      f.closest(".row")?.classList.toggle("off", !data.enabled);
    } catch { f.submit(); }
  }));

  /* drag & drop reorder */
  const list = $(".sortable");
  if (list) {
    let dragged = null;
    const clear = () => $$(".row", list).forEach((r) => r.classList.remove("drop-before", "drop-after"));
    list.addEventListener("dragstart", (e) => {
      dragged = e.target.closest(".row");
      if (!dragged) return;
      dragged.classList.add("dragging");
      e.dataTransfer.effectAllowed = "move";
      e.dataTransfer.setData("text/plain", dragged.dataset.id);
    });
    list.addEventListener("dragover", (e) => {
      const row = e.target.closest(".row");
      if (!dragged || !row || row === dragged) return;
      e.preventDefault();
      clear();
      const r = row.getBoundingClientRect();
      row.classList.add(e.clientY < r.top + r.height / 2 ? "drop-before" : "drop-after");
    });
    list.addEventListener("drop", (e) => {
      const row = e.target.closest(".row");
      if (!dragged || !row || row === dragged) return;
      e.preventDefault();
      const before = row.classList.contains("drop-before");
      row.parentNode.insertBefore(dragged, before ? row : row.nextSibling);
      save();
    });
    list.addEventListener("dragend", () => { dragged?.classList.remove("dragging"); dragged = null; clear(); });

    list.addEventListener("click", (e) => {
      const b = e.target.closest("[data-move]");
      if (!b) return;
      const row = b.closest(".row");
      const sib = b.dataset.move === "-1" ? row.previousElementSibling : row.nextElementSibling;
      if (!sib) return;
      row.parentNode.insertBefore(row, b.dataset.move === "-1" ? sib : sib.nextSibling);
      save();
    });

    async function save() {
      const ids = $$(".row", list).map((r) => r.dataset.id);
      try {
        const res = await fetch(list.dataset.reorder, {
          method: "POST",
          headers: { "Content-Type": "application/json", "X-CSRFToken": csrf, "X-Requested-With": "fetch" },
          body: JSON.stringify({ ids }),
        });
        if (!res.ok) throw new Error();
        toast("Order saved");
      } catch { toast("Could not save the order – please reload", true); }
    }
  }

  function toast(text, error) {
    const t = document.createElement("div");
    t.className = "flash " + (error ? "flash-error" : "flash-success");
    t.style.cssText = "position:fixed;right:20px;bottom:20px;z-index:99;box-shadow:0 10px 30px -10px rgba(0,0,0,.3)";
    t.textContent = text;
    document.body.appendChild(t);
    setTimeout(() => t.remove(), 2500);
  }

  // ASDHEM | copy-to-clipboard buttons (preview link)
  document.querySelectorAll("[data-copy]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const el = document.querySelector(btn.dataset.copy);
      if (!el) return;
      el.select();
      try { await navigator.clipboard.writeText(el.value); } catch (e) { document.execCommand("copy"); }
      const old = btn.innerHTML;
      btn.textContent = "Copied!";
      setTimeout(() => { btn.innerHTML = old; }, 1600);
    });
  });
  document.querySelectorAll("[data-select-all]").forEach((el) => el.addEventListener("focus", () => el.select()));
  /* ASDHEM | auto-submit selects / file pickers */
  $$("[data-autosubmit-change]").forEach((el) => el.addEventListener("change", () => el.form.submit()));
  $$("[data-autosubmit]").forEach((el) => el.addEventListener("change", () => el.form.submit()));

  /* ASDHEM | media library drag & drop */
  const dz = $("#dropzone");
  if (dz) {
    const input = dz.querySelector('input[type="file"]');
    ["dragenter", "dragover"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.add("over"); }));
    ["dragleave", "drop"].forEach((ev) => dz.addEventListener(ev, (e) => { e.preventDefault(); dz.classList.remove("over"); }));
    dz.addEventListener("drop", (e) => { if (e.dataTransfer.files.length) { input.files = e.dataTransfer.files; dz.submit(); } });
  }

  /* ASDHEM | backups: "Restore" in the table pre-selects the backup below */
  $$("[data-restore]").forEach((b) => b.addEventListener("click", () => {
    const sel = $("#rName"); if (!sel) return;
    sel.value = b.dataset.restore; $("#restoreForm").scrollIntoView({ behavior: "smooth" }); $("#rPw").focus({ preventScroll: true });
  }));

  /* ASDHEM | Google search preview (SEO section) */
  const st = $("#site_title"), md = $("#meta_description"), sT = $("#serpTitle"), sD = $("#serpDesc"), sH = $("#serpHint");
  if (st && md && sT) {
    const upd = () => {
      const tt = st.value || st.placeholder, dd = md.value || md.placeholder;
      sT.textContent = tt.length > 60 ? tt.slice(0, 58) + "…" : tt;
      sD.textContent = dd.length > 158 ? dd.slice(0, 155) + "…" : dd;
      const tips = [];
      if (tt.length > 60) tips.push(`Title is ${tt.length} characters – Google shows about 60.`);
      if (dd.length < 70) tips.push("Description is short – aim for 120–158 characters.");
      if (dd.length > 158) tips.push(`Description is ${dd.length} characters – Google cuts after about 158.`);
      sH.textContent = tips.join(" ") || "✓ Length looks good.";
    };
    [st, md].forEach((el) => el.addEventListener("input", upd)); upd();
  }

  /* ASDHEM | live preview: renders the homepage with your unsaved text in a side panel */
  const lpBtn = $("#lpToggle"), lpWrap = $("#lpWrap"), lpPane = $("#lpPane"), lpFrame = $("#lpFrame");
  if (lpBtn && lpWrap && lpPane) {
    const form = lpWrap.querySelector("form");
    let timer = null, busy = false, again = false;
    const render = async () => {
      if (busy) { again = true; return; }
      busy = true;
      try {
        const fd = new FormData(form);
        const res = await fetch(lpWrap.dataset.url, { method: "POST", body: fd, headers: { "X-Requested-With": "fetch" } });
        const html = await res.text();
        const y = lpFrame.contentWindow ? lpFrame.contentWindow.scrollY : 0;
        lpFrame.srcdoc = html;
        lpFrame.onload = () => { try { lpFrame.contentWindow.scrollTo(0, y); } catch { /* ignore */ } };
      } catch { /* offline */ }
      busy = false;
      if (again) { again = false; render(); }
    };
    lpBtn.addEventListener("click", () => {
      const on = lpPane.hidden;
      lpPane.hidden = !on; lpWrap.classList.toggle("on", on); lpBtn.classList.toggle("on", on);
      if (on) render();
    });
    form.addEventListener("input", () => { if (lpPane.hidden) return; clearTimeout(timer); timer = setTimeout(render, 500); });
  }

  /* ASDHEM | invoice form: add/remove lines, live totals, confirm on send */
  const inv = $("#invForm");
  if (inv) {
    const box = $("#invItems"), small = $("#invSmall"), vatIn = $("#invVat");
    const num = (v) => parseFloat(String(v || "").replace(/\s|€/g, "").replace(/\.(?=\d{3}(\D|$))/g, "").replace(",", ".")) || 0;
    const fmt = (v) => v.toLocaleString("de-DE", { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + " €";
    const calc = () => {
      let net = 0;
      $$(".inv-item", box).forEach((row) => {
        const q = num(row.querySelector('[name="qty"]').value || "1"), p = num(row.querySelector('[name="price"]').value);
        const tot = Math.round(q * p * 100) / 100; net += tot;
        row.querySelector(".inv-line").textContent = p ? fmt(tot) : "–";
      });
      const vat = small.checked ? 0 : Math.round(net * num(vatIn.value) / 100 * 100) / 100;
      $("#tNet").textContent = fmt(net); $("#tVat").textContent = fmt(vat); $("#tGross").textContent = fmt(net + vat);
      $("#tVatWrap").style.display = small.checked ? "none" : ""; vatIn.disabled = small.checked;
    };
    $("#invAdd").addEventListener("click", () => {
      const rows = $$(".inv-item", box), copy = rows[rows.length - 1].cloneNode(true);
      copy.querySelectorAll("input, textarea").forEach((el) => { el.value = el.name === "qty" ? "1" : ""; });
      box.appendChild(copy); copy.querySelector("textarea").focus(); calc();
    });
    box.addEventListener("click", (e) => {
      const b = e.target.closest("[data-del-row]"); if (!b) return;
      if ($$(".inv-item", box).length > 1) { b.closest(".inv-item").remove(); calc(); }
    });
    inv.addEventListener("input", calc); small.addEventListener("change", calc); calc();
    inv.querySelectorAll("[data-confirm-click]").forEach((b) => b.addEventListener("click", (e) => {
      if (!confirm(b.dataset.confirmClick)) e.preventDefault();
    }));
  }
})();
