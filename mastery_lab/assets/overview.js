/* Python Observatory. Authored locally; no external code, requests, or learner-code execution. */
(() => {
  "use strict";
  const root = document.getElementById("python-observatory");
  if (!root) return;
  const signature = `${root.dataset.version || "1"}|${root.dataset.theme}|${root.dataset.info}`;
  if (window.__pmlObservatory?.root === root && window.__pmlObservatory.signature === signature && window.__pmlObservatory.canvas === root.querySelector(".ov-stage").querySelector("canvas")) return;
  window.__pmlObservatory?.dispose();
  delete root.dataset.disposed;
  const info = JSON.parse(root.dataset.info);
  const stage = root.querySelector(".ov-stage");
  const canvas = stage.querySelector("canvas");
  const ctx = canvas.getContext("2d");
  if (!ctx) {
    root.dataset.ready = "fallback";
    root.querySelector("[data-detail]").textContent = "Your browser cannot draw the particle scene. All study controls are available below.";
    return;
  }
  const controller = new AbortController();
  const signal = controller.signal;
  const media = window.matchMedia("(prefers-reduced-motion: reduce)");
  const motionButton = root.querySelector('[data-action="motion"]');
  const detail = root.querySelector("[data-detail]");
  const picker = root.querySelector("#ov-topic-picker");
  let disposed = false, frame = 0, counterFrame = 0, previousTime = 0, elapsed = 0;
  const counters = Array.from(root.querySelectorAll("[data-counter]"));
  let visible = true, dragging = false, pointerId = null;
  let yaw = .24, pitch = .12, pointerX = 0, pointerY = 0, lastX = 0, lastY = 0;
  let width = 350, height = 400, radius = 130, pulse = 0;
  let mode = "sphere", manualMotion = null;
  const allowedModes = ["sphere", "helix", "wings"];
  try {
    const saved = JSON.parse(sessionStorage.getItem("pml-observatory-appearance") || "{}");
    if (allowedModes.includes(saved.mode)) mode = saved.mode;
    if (typeof saved.motion === "boolean") manualMotion = saved.motion;
  } catch (_) { /* Storage may be unavailable in a private or embedded session. */ }
  const blue = root.dataset.theme === "dark" ? [111, 188, 235] : [48, 113, 163];
  const gold = root.dataset.theme === "dark" ? [255, 211, 67] : [172, 126, 22];
  const N = window.innerWidth < 600 ? 400 : 640;
  const random = i => { const value = Math.sin(i * 12.9898 + 78.233) * 43758.5453; return value - Math.floor(value); };
  const rgba = (color, alpha) => `rgba(${color[0]},${color[1]},${color[2]},${alpha})`;
  const shapes = {sphere: [], helix: [], wings: []};
  const points = [];
  for (let i = 0; i < N; i++) {
    const y = 1 - i / (N - 1) * 2;
    const r = Math.sqrt(1 - y * y);
    const angle = i * Math.PI * (3 - Math.sqrt(5));
    const sphere = [Math.cos(angle) * r, y, Math.sin(angle) * r];
    shapes.sphere.push(sphere);
    const strand = i % 2 ? Math.PI : 0;
    const t = i / (N - 1);
    shapes.helix.push([Math.cos(t * Math.PI * 5 + strand) * .62, (t * 2 - 1) * 1.12, Math.sin(t * Math.PI * 5 + strand) * .62]);
    const a = t * Math.PI * 12;
    const wing = (Math.exp(Math.cos(a)) - 2 * Math.cos(4 * a) + Math.pow(Math.sin(a / 12), 5)) / 3.8;
    shapes.wings.push([Math.sin(a) * wing * .9, Math.cos(a) * wing * .9, Math.sin(a * 3) * .12]);
    const initial = shapes[mode][i];
    points.push({x: initial[0], y: initial[1], z: initial[2], color: i % 7 < 2 ? gold : blue, size: 1 + random(i + 1) * .85});
  }
  picker.replaceChildren();
  const placeholder = document.createElement("option");
  placeholder.value = ""; placeholder.textContent = "Choose a topic…"; picker.appendChild(placeholder);
  for (let index = 0; index < info.topics.length; index++) {
    const option = document.createElement("option");
    option.value = String(index);
    option.textContent = `${info.topics[index].name} · ${info.topics[index].lecture}`;
    picker.appendChild(option);
  }
  const moving = () => !disposed && visible && document.visibilityState !== "hidden" && (manualMotion ?? !media.matches);
  function persistAppearance() {
    try { sessionStorage.setItem("pml-observatory-appearance", JSON.stringify({mode, motion: manualMotion})); } catch (_) { /* Optional preference only. */ }
  }
  function paint(now = 0, snap = false) {
    if (disposed || !root.isConnected) return;
    const dpr = Math.min(window.devicePixelRatio || 1, window.innerWidth < 600 ? 1.5 : 1.8);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.clearRect(0, 0, width, height);
    const cx = width * .5, cy = height * .49;
    const autoYaw = mode === "wings" ? Math.sin(elapsed * .25) * .24 : elapsed * .085;
    const ry = yaw + autoYaw + pointerX * .13, rx = pitch + pointerY * .1;
    const cosY = Math.cos(ry), sinY = Math.sin(ry), cosX = Math.cos(rx), sinX = Math.sin(rx);
    // A sparse star field and two light orbital ribbons make the visual feel spatial.
    for (let i = 0; i < 36; i++) {
      const x = random(i + 800) * width, y = random(i + 900) * height;
      ctx.fillStyle = rgba(blue, .1 + (1 + Math.sin(elapsed * .7 + i)) * .07);
      ctx.beginPath(); ctx.arc(x, y, .6 + random(i + 1000) * .6, 0, Math.PI * 2); ctx.fill();
    }
    for (let i = 0; i < 2; i++) {
      ctx.strokeStyle = rgba(i ? gold : blue, .18);
      ctx.lineWidth = .75;
      ctx.beginPath(); ctx.ellipse(cx, cy, radius * 1.13, radius * .36, i ? -.52 : .45, 0, Math.PI * 2); ctx.stroke();
    }
    const projected = [];
    for (let i = 0; i < N; i++) {
      const p = points[i], target = shapes[mode][i], ease = snap ? 1 : .065;
      p.x += (target[0] - p.x) * ease; p.y += (target[1] - p.y) * ease; p.z += (target[2] - p.z) * ease;
      const x = p.x * cosY - p.z * sinY, z = p.x * sinY + p.z * cosY;
      const y = p.y * cosX - z * sinX, depth = p.y * sinX + z * cosX;
      const perspective = 3.6 / (3.6 - depth);
      projected.push({x: cx + x * radius * perspective, y: cy + y * radius * perspective, z: depth, size: p.size * perspective, color: p.color});
    }
    // Fixed candidate edges keep work linear rather than comparing every pair.
    ctx.lineWidth = .5;
    for (let i = 0; i < N - 13; i += 4) {
      const a = projected[i], b = projected[i + 13];
      const distance = Math.hypot(a.x - b.x, a.y - b.y);
      if (distance < radius * .45 && a.z > -.35 && b.z > -.35) {
        ctx.strokeStyle = rgba(blue, (1 - distance / (radius * .45)) * .15);
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
      }
    }
    projected.sort((a, b) => a.z - b.z);
    for (const p of projected) {
      ctx.fillStyle = rgba(p.color, .22 + (p.z + 1.3) / 2.6 * .67);
      ctx.beginPath(); ctx.arc(p.x, p.y, Math.max(.6, p.size), 0, Math.PI * 2); ctx.fill();
    }
    if (pulse > .01) {
      ctx.strokeStyle = rgba(gold, pulse * .55); ctx.lineWidth = 1;
      ctx.beginPath(); ctx.ellipse(cx, cy, radius * (1.5 - pulse * .35), radius * (1.5 - pulse * .35), 0, 0, Math.PI * 2); ctx.stroke();
      pulse *= .9;
    }
  }
  function loop(now) {
    frame = 0;
    if (!moving()) return;
    if (now - previousTime >= 1000 / 30) {
      elapsed += Math.min((now - previousTime) / 1000, .07);
      previousTime = now;
      paint(now);
    }
    if (moving()) frame = requestAnimationFrame(loop);
  }
  function synchronize() {
    if (frame) { cancelAnimationFrame(frame); frame = 0; }
    if (!moving() && counterFrame) {
      cancelAnimationFrame(counterFrame); counterFrame = 0;
      counters.forEach(node => { node.textContent = String(summary[node.dataset.counter]); });
    }
    const enabled = manualMotion ?? !media.matches;
    root.classList.toggle("is-still", !enabled || !visible || document.visibilityState === "hidden");
    root.dataset.motion = enabled ? "playing" : "paused";
    motionButton.textContent = enabled ? "Pause motion" : "Enable motion";
    motionButton.setAttribute("aria-pressed", String(enabled));
    paint(0, !enabled);
    if (moving()) { previousTime = performance.now(); frame = requestAnimationFrame(loop); }
  }
  function resize() {
    const bounds = stage.getBoundingClientRect();
    width = Math.max(1, bounds.width); height = Math.max(1, bounds.height);
    radius = Math.min(width * .37, height * .35);
    const dpr = Math.min(window.devicePixelRatio || 1, window.innerWidth < 600 ? 1.5 : 1.8);
    canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
    paint(0, !moving());
  }
  function showDetail(text) {
    detail.textContent = text; pulse = 1;
    if (!moving()) paint(0, true);
  }
  function setShape(next) {
    if (!allowedModes.includes(next)) return;
    mode = next; root.dataset.shape = mode;
    for (const button of root.querySelectorAll("[data-shape]")) button.setAttribute("aria-pressed", String(button.dataset.shape === mode));
    persistAppearance();
    showDetail({sphere: "Orbit · every dot is part of a bigger picture. Drag the sphere to find a new perspective.", helix: "Double helix · two strands, one direction. A little theory, a little practice, repeated.", wings: "Python wings · let a familiar idea take a different shape. Keep exploring."}[mode]);
  }
  root.querySelectorAll("[data-shape]").forEach(button => button.addEventListener("click", () => setShape(button.dataset.shape), {signal}));
  motionButton.addEventListener("click", () => { manualMotion = !(manualMotion ?? !media.matches); persistAppearance(); synchronize(); }, {signal});
  function reset() { yaw = .24; pitch = .12; pointerX = pointerY = 0; root.style.setProperty("--mx", "0px"); root.style.setProperty("--my", "0px"); showDetail("View reset. Follow your curiosity, one idea at a time."); }
  root.querySelector('[data-action="reset"]').addEventListener("click", reset, {signal});
  const summary = info.summary;
  const insights = {
    explored: () => `${summary.studied} of ${summary.total} questions explored. ${summary.mastered} have a correct streak of at least three. Every new attempt expands your learning universe.`,
    accuracy: () => summary.accuracy === null ? "No attempts yet. Your first quiz will start your accuracy story. Coding results are self-assessed." : `${summary.accuracy}% accuracy across ${summary.attempts} attempts. Coding results are self-assessed. Progress is a pattern, not a single score.`,
    streak: () => `${summary.streak} consecutive practice days. A streak stays active through yesterday; the best way back is a small session today.`,
    due: () => `${summary.due} studied questions are due for review, including overdue items. Open the revision studio below to revisit them.`
  };
  root.querySelectorAll("[data-insight]").forEach(button => button.addEventListener("click", () => showDetail(insights[button.dataset.insight]()), {signal}));
  picker.addEventListener("change", () => {
    const topic = info.topics[Number(picker.value)];
    if (picker.value === "" || !topic) return;
    showDetail(`${topic.name} · ${topic.studied}/${topic.questions} explored · ${topic.mcqs} MCQs · ${topic.coding} coding tasks · ${topic.accuracy === null ? "no attempts yet" : topic.accuracy + "% accuracy"}. Use the topic launchpad below to practise it.`);
  }, {signal});
  root.addEventListener("pointermove", e => {
    const bounds = root.getBoundingClientRect();
    root.style.setProperty("--spot-x", `${e.clientX - bounds.left}px`); root.style.setProperty("--spot-y", `${e.clientY - bounds.top}px`);
  }, {signal, passive: true});
  stage.addEventListener("pointerdown", e => {
    if (e.target.closest("button") || e.button !== 0) return;
    dragging = true; pointerId = e.pointerId; lastX = e.clientX; lastY = e.clientY;
    stage.setPointerCapture(e.pointerId); stage.classList.add("is-dragging");
  }, {signal});
  stage.addEventListener("pointermove", e => {
    if (dragging) { yaw += (e.clientX - lastX) * .008; pitch = Math.max(-.9, Math.min(.9, pitch + (e.clientY - lastY) * .006)); lastX = e.clientX; lastY = e.clientY; }
    const bounds = stage.getBoundingClientRect();
    pointerX = (e.clientX - bounds.left) / width - .5; pointerY = (e.clientY - bounds.top) / height - .5;
    root.style.setProperty("--mx", `${pointerX * 6}px`); root.style.setProperty("--my", `${pointerY * 6}px`);
    if (!moving()) paint(0, true);
  }, {signal, passive: true});
  function release() { dragging = false; stage.classList.remove("is-dragging"); if (pointerId !== null && stage.hasPointerCapture(pointerId)) stage.releasePointerCapture(pointerId); pointerId = null; }
  stage.addEventListener("pointerup", release, {signal}); stage.addEventListener("pointercancel", release, {signal});
  stage.addEventListener("pointerleave", () => { if (!dragging) { pointerX = pointerY = 0; root.style.setProperty("--mx", "0px"); root.style.setProperty("--my", "0px"); if (!moving()) paint(0, true); } }, {signal});
  stage.addEventListener("keydown", e => {
    if (e.target !== stage) return;
    if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown", " ", "Escape"].includes(e.key)) e.preventDefault();
    if (e.key === "ArrowLeft") yaw -= .12; else if (e.key === "ArrowRight") yaw += .12;
    else if (e.key === "ArrowUp") pitch = Math.max(-.9, pitch - .1); else if (e.key === "ArrowDown") pitch = Math.min(.9, pitch + .1);
    else if (e.key === " ") { manualMotion = !(manualMotion ?? !media.matches); persistAppearance(); synchronize(); }
    else if (e.key === "Escape") reset();
    if (!moving()) paint(0, true);
  }, {signal});
  document.addEventListener("visibilitychange", synchronize, {signal});
  media.addEventListener("change", synchronize, {signal});
  const resizer = new ResizeObserver(resize); resizer.observe(stage);
  const intersection = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; synchronize(); }, {threshold: .01}); intersection.observe(stage);
  const removal = new MutationObserver(() => { if (!root.isConnected) dispose(); }); removal.observe(document.body, {childList: true, subtree: true});
  function dispose() {
    if (disposed) return;
    disposed = true;
    if (frame) cancelAnimationFrame(frame);
    if (counterFrame) cancelAnimationFrame(counterFrame);
    controller.abort(); resizer.disconnect(); intersection.disconnect(); removal.disconnect();
    root.dataset.disposed = "true";
    if (window.__pmlObservatory?.root === root) delete window.__pmlObservatory;
  }
  window.__pmlObservatory = {root, canvas, signature, dispose};
  setShape(mode); resize(); synchronize(); root.dataset.ready = "true";
  // A short, non-essential count reveal. Assistive tech receives the true value immediately.
  if (!media.matches && (manualMotion ?? true)) {
    const start = performance.now();
    counters.forEach(node => { node.closest("button").setAttribute("aria-label", `${node.closest("button").querySelector("small").textContent}: ${summary[node.dataset.counter]}`); });
    const reveal = now => {
      if (disposed || !root.isConnected) return;
      const progress = Math.min(1, (now - start) / 650), ease = 1 - Math.pow(1 - progress, 3);
      counters.forEach(node => { node.textContent = String(Math.round(summary[node.dataset.counter] * ease)); });
      counterFrame = progress < 1 ? requestAnimationFrame(reveal) : 0;
    };
    counterFrame = requestAnimationFrame(reveal);
  }
})();
