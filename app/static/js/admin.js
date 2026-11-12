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
})();
