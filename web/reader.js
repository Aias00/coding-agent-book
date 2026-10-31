"use strict";
(() => {
  const root = document.documentElement;
  const read = (key, fallback) => { try { return localStorage.getItem(key) ?? fallback; } catch { return fallback; } };
  const write = (key, value) => { try { localStorage.setItem(key, value); } catch { /* Storage is optional. */ } };
  const theme = read("coding-agent-theme", window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  root.dataset.theme = theme === "dark" ? "dark" : "light";
  let font = Math.min(25, Math.max(15, Number(read("coding-agent-font", "18")) || 18));
  const setFont = () => { root.style.setProperty("--font-size", `${font}px`); write("coding-agent-font", String(font)); };
  setFont();
  document.getElementById("font-up").addEventListener("click", () => { font = Math.min(25, font + 1); setFont(); });
  document.getElementById("font-down").addEventListener("click", () => { font = Math.max(15, font - 1); setFont(); });
  document.getElementById("theme-button").addEventListener("click", () => {
    root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
    write("coding-agent-theme", root.dataset.theme);
  });
  const menu = document.getElementById("menu-button");
  menu.addEventListener("click", () => {
    const opened = document.body.classList.toggle("menu-open");
    menu.setAttribute("aria-expanded", String(opened));
  });
  document.getElementById("main").addEventListener("click", () => {
    document.body.classList.remove("menu-open"); menu.setAttribute("aria-expanded", "false");
  });
  const chapter = document.body.dataset.chapter;
  const edition = document.body.dataset.edition;
  const bookmarkKey = `coding-agent-${edition}-bookmark`;
  const positionKey = `coding-agent-${edition}-${chapter}`;
  let scheduled = false;
  const updateProgress = () => {
    scheduled = false;
    const limit = Math.max(0, document.documentElement.scrollHeight - window.innerHeight);
    const fraction = limit > 0 ? Math.min(1, Math.max(0, window.scrollY / limit)) : 0;
    const bar = document.querySelector(".reading-progress");
    bar.setAttribute("aria-valuenow", String(Math.round(fraction * 100)));
    bar.querySelector("span").style.width = `${fraction * 100}%`;
    if (chapter) { write(positionKey, String(fraction)); write(bookmarkKey, `${chapter}.html`); }
  };
  window.addEventListener("scroll", () => { if (!scheduled) { scheduled = true; requestAnimationFrame(updateProgress); } }, { passive: true });
  const restore = () => {
    if (chapter && !location.hash) {
      const fraction = Math.min(1, Math.max(0, Number(read(positionKey, "0")) || 0));
      if (fraction > 0) window.scrollTo({ top: fraction * Math.max(0, document.documentElement.scrollHeight - innerHeight), behavior: "instant" });
    }
    updateProgress();
  };
  window.addEventListener("load", restore, { once: true });
  if (!chapter) {
    const resume = document.getElementById("resume-reading");
    const target = read(bookmarkKey, "");
    if (resume && /^\d{2}-[a-z-]+\.html$/.test(target)) { resume.href = target; resume.hidden = false; }
  }
  const dialog = document.getElementById("search-dialog");
  const input = document.getElementById("search-input");
  const status = document.getElementById("search-status");
  const results = document.getElementById("search-results");
  let corpus;
  let loading;
  const loadIndex = () => loading ??= fetch("search-index.json").then(response => {
    if (!response.ok) throw new Error("Search index unavailable");
    return response.json();
  }).then(data => { corpus = data; return data; }).catch(error => { loading = undefined; throw error; });
  const search = () => {
    results.replaceChildren();
    const query = input.value.trim().toLocaleLowerCase();
    if (!query) { status.textContent = "输入关键词，支持中文和源码名称。"; return; }
    if (!corpus) return;
    const terms = query.split(/\s+/);
    const matches = corpus.filter(row => terms.every(term => `${row.title} ${row.text}`.toLocaleLowerCase().includes(term)))
      .sort((a, b) => Number(b.title.toLocaleLowerCase().includes(query)) - Number(a.title.toLocaleLowerCase().includes(query)));
    status.textContent = `找到 ${matches.length} 章，显示前 ${Math.min(20, matches.length)} 项。`;
    for (const row of matches.slice(0, 20)) {
      const li = document.createElement("li");
      const link = document.createElement("a"); link.href = row.url; link.textContent = row.title;
      const at = Math.max(0, row.text.toLocaleLowerCase().indexOf(terms[0]));
      const snippet = document.createElement("p"); snippet.textContent = `${at > 35 ? "…" : ""}${row.text.slice(Math.max(0, at - 35), at + 120).replace(/\s+/g, " ")}…`;
      li.append(link, snippet); results.append(li);
    }
  };
  document.getElementById("search-button").addEventListener("click", async () => {
    dialog.showModal(); input.focus(); status.textContent = "正在加载全文索引…";
    try { await loadIndex(); search(); } catch { status.textContent = "全文索引加载失败，请稍后重试。正文和目录仍可阅读。"; }
  });
  input.addEventListener("input", search);
  dialog.addEventListener("click", event => { if (event.target === dialog) { const r = dialog.getBoundingClientRect(); if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) dialog.close(); } });
  document.addEventListener("keydown", event => {
    if (dialog.open || event.altKey || event.ctrlKey || event.metaKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName) || event.target.isContentEditable) return;
    if (event.key === "/") { event.preventDefault(); document.getElementById("search-button").click(); }
    if (event.key === "Escape") { document.body.classList.remove("menu-open"); menu.setAttribute("aria-expanded", "false"); }
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      const link = document.querySelector(`.pager a[rel="${event.key === "ArrowLeft" ? "prev" : "next"}"]`);
      if (link) location.href = link.href;
    }
  });
})();
