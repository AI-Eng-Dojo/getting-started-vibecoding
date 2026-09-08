/* Progressive enhancement: without JavaScript every slide remains readable. */
(() => {
  "use strict";

  const slides = [...document.querySelectorAll(".slide")];
  const controls = document.querySelector(".deck-controls");
  const previous = document.querySelector("#previous-slide");
  const next = document.querySelector("#next-slide");
  const jump = document.querySelector("#slide-jump");
  const counter = document.querySelector("#current-slide");
  const overviewButton = document.querySelector("#overview-toggle");
  const fullscreenButton = document.querySelector("#fullscreen-toggle");
  const status = document.querySelector("#deck-status");
  if (!slides.length || !controls) return;

  let current = 0;
  let overview = false;

  function fromHash() {
    const match = /^#slide-(\d+)$/.exec(location.hash);
    return match ? Math.min(slides.length - 1, Math.max(0, Number(match[1]) - 1)) : null;
  }

  function announce() {
    const heading = slides[current].querySelector("h1, h2").textContent;
    status.textContent = `${current + 1} / ${slides.length}：${heading}`;
  }

  function render() {
    slides.forEach((slide, index) => { slide.hidden = !overview && index !== current; });
    previous.disabled = current === 0;
    next.disabled = current === slides.length - 1;
    jump.value = String(current + 1);
    counter.textContent = String(current + 1);
    overviewButton.setAttribute("aria-pressed", String(overview));
    overviewButton.textContent = overview ? "発表に戻る" : "一覧";
    document.body.classList.toggle("is-overview", overview);
    announce();
  }

  function goTo(index, { updateHash = true, focus = false } = {}) {
    const wasInsideSlide = slides.some(slide => slide.contains(document.activeElement));
    current = Math.min(slides.length - 1, Math.max(0, index));
    overview = false;
    render();
    if (updateHash && location.hash !== `#slide-${current + 1}`) {
      history.pushState(null, "", `#slide-${current + 1}`);
    }
    window.scrollTo({ top: 0, behavior: "instant" });
    if (focus || wasInsideSlide) slides[current].focus({ preventScroll: true });
  }

  function toggleOverview() {
    overview = !overview;
    render();
    if (overview) slides[current].scrollIntoView({ block: "start", behavior: "instant" });
    else window.scrollTo({ top: 0, behavior: "instant" });
  }

  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await document.documentElement.requestFullscreen();
    } catch {
      status.textContent = "このブラウザーでは全画面表示を開始できませんでした。";
    }
  }

  previous.addEventListener("click", () => goTo(current - 1));
  next.addEventListener("click", () => goTo(current + 1));
  jump.addEventListener("change", () => goTo(Number(jump.value) - 1));
  overviewButton.addEventListener("click", toggleOverview);
  document.querySelector("#print-slides").addEventListener("click", () => window.print());

  if (document.fullscreenEnabled && document.documentElement.requestFullscreen) {
    fullscreenButton.addEventListener("click", toggleFullscreen);
    document.addEventListener("fullscreenchange", () => {
      const active = Boolean(document.fullscreenElement);
      fullscreenButton.setAttribute("aria-pressed", String(active));
      fullscreenButton.textContent = active ? "全画面を終了" : "全画面";
    });
  } else {
    fullscreenButton.hidden = true;
  }

  document.querySelectorAll("[data-slide-link]").forEach(link => {
    link.addEventListener("click", event => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      goTo(Number(link.dataset.slideLink) - 1, { focus: true });
    });
  });

  document.querySelector(".skip-link").addEventListener("click", event => {
    event.preventDefault();
    slides[current].focus({ preventScroll: true });
    slides[current].scrollIntoView({ block: "start", behavior: "instant" });
  });

  document.addEventListener("keydown", event => {
    if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey || event.isComposing) return;
    if (event.target.closest("input, textarea, select, a, [contenteditable='true'], [role='textbox']")) return;
    const key = event.key.toLowerCase();
    if (key === "o") {
      event.preventDefault();
      toggleOverview();
    } else if (key === "f" && !fullscreenButton.hidden) {
      event.preventDefault();
      toggleFullscreen();
    } else if (key === "escape" && overview) {
      event.preventDefault();
      toggleOverview();
    } else if (!overview) {
      const destinations = {
        arrowright: current + 1, pagedown: current + 1,
        arrowleft: current - 1, pageup: current - 1,
        home: 0, end: slides.length - 1,
      };
      if (Object.prototype.hasOwnProperty.call(destinations, key)) {
        event.preventDefault();
        goTo(destinations[key]);
      }
    }
  });

  // Covers deep links, normal anchor links, and the browser's back/forward keys.
  window.addEventListener("hashchange", () => {
    const index = fromHash();
    if (index !== null) goTo(index, { updateHash: false });
    else if (!location.hash) goTo(0, { updateHash: false });
  });
  controls.hidden = false;
  document.body.classList.add("is-presenting");
  goTo(fromHash() ?? 0, { updateHash: false });
})();
