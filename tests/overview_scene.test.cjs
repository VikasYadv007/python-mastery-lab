/* Run with node --test tests/overview_scene.test.cjs. No real browser or network. */
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../mastery_lab/assets/overview.js'), 'utf8');

class Element extends EventTarget {
  constructor() { super(); this.dataset = {}; this.children = []; this.attributes = {}; this.isConnected = true; this.textContent = ''; this.value = ''; this.parent = null; this.styles = {}; this.style = {setProperty: (k, v) => this.styles[k] = v}; const classes = new Set(); this.classList = {add: k => classes.add(k), remove: k => classes.delete(k), toggle: (k, value) => value ? classes.add(k) : classes.delete(k)}; }
  setAttribute(k, v) { this.attributes[k] = v; }
  appendChild(c) { c.parent = this; this.children.push(c); }
  replaceChildren(...nodes) { this.children = []; nodes.forEach(node => this.appendChild(node)); }
  closest(selector) { return selector === 'button' && this.isButton ? this : this.parent?.closest(selector) || null; }
  getBoundingClientRect() { return {left: 0, top: 0, width: 360, height: 400}; }
  setPointerCapture() {}
  hasPointerCapture() { return false; }
  releasePointerCapture() {}
}
function harness(reduced = false) {
  const root = new Element(), stage = new Element(), canvas = new Element(), detail = new Element(), picker = new Element(), motion = new Element(), reset = new Element();
  const summary = {studied: 13, total: 229, mastered: 2, accuracy: 72.2, attempts: 18, streak: 0, due: 13};
  root.dataset = {theme: 'dark', info: JSON.stringify({summary, topics: [{name: '<img onerror="evil()">', lecture: 'Lesson', studied: 2, questions: 5, mcqs: 4, coding: 1, accuracy: 50}]})};
  let paints = 0;
  const ctx = new Proxy({setTransform() {}, clearRect() { paints++; }}, {get: (target, key) => key in target ? target[key] : () => {}});
  canvas.getContext = () => ctx;
  const shapes = ['sphere', 'helix', 'wings'].map(shape => { const e = new Element(); e.dataset.shape = shape; e.isButton = true; return e; });
  const insights = ['explored', 'accuracy', 'streak', 'due'].map(insight => { const e = new Element(); e.dataset.insight = insight; e.isButton = true; e.querySelector = () => ({textContent: insight}); return e; });
  const counters = ['studied', 'streak', 'due'].map((name, i) => { const e = new Element(); e.dataset.counter = name; e.parent = insights[i]; return e; });
  const nodes = {'.ov-stage': stage, '[data-action="motion"]': motion, '[data-action="reset"]': reset, '[data-detail]': detail, '#ov-topic-picker': picker};
  root.querySelector = selector => nodes[selector];
  root.querySelectorAll = selector => ({'[data-shape]': shapes, '[data-insight]': insights, '[data-counter]': counters})[selector] || [];
  stage.querySelector = () => canvas;
  const document = new Element(); document.visibilityState = 'visible'; document.body = new Element(); document.getElementById = () => root; document.createElement = () => new Element();
  const media = new Element(); media.matches = reduced;
  const frames = new Map(); let id = 0, now = 0;
  const observers = {};
  const observer = type => class {constructor(callback) {this.callback = callback; this.closed = false; observers[type] = this;} observe() {} disconnect() {this.closed = true;} };
  const window = {innerWidth: 900, devicePixelRatio: 1, matchMedia: () => media};
  const store = {};
  const context = vm.createContext({window, document, AbortController, performance: {now: () => now},
    sessionStorage: {getItem: k => store[k] || null, setItem: (k, v) => store[k] = v},
    requestAnimationFrame: callback => { frames.set(++id, callback); return id; }, cancelAnimationFrame: key => frames.delete(key),
    ResizeObserver: observer('resize'), IntersectionObserver: observer('intersection'), MutationObserver: observer('removal')});
  vm.runInContext(source, context);
  const click = element => element.dispatchEvent(new Event('click'));
  const step = () => { now += 40; const batch = Array.from(frames); frames.clear(); for (const [, callback] of batch) callback(now); };
  return {root, window, stage, document, media, motion, reset, shapes, insights, detail, picker, frames, observers, click, step, rerender: () => vm.runInContext(source, context), get paints() {return paints;}};
}

test('sphere, helix and wings render; topic strings remain text', () => {
  const h = harness();
  assert.equal(h.root.dataset.ready, 'true');
  assert.equal(h.root.dataset.shape, 'sphere');
  const before = h.paints; h.step(); h.step(); assert.ok(h.paints > before);
  h.click(h.shapes[1]); assert.equal(h.root.dataset.shape, 'helix');
  h.click(h.shapes[2]); assert.equal(h.root.dataset.shape, 'wings');
  h.picker.value = '0'; h.picker.dispatchEvent(new Event('change'));
  assert.match(h.detail.textContent, /<img onerror="evil\(\)">/);
  assert.equal(h.picker.children.length, 2);
  assert.match(h.picker.children[1].textContent, /<img/);
  h.window.__pmlObservatory.dispose();
});

test('reduced motion starts static and explicit enable is reversible', () => {
  const h = harness(true);
  assert.equal(h.frames.size, 0);
  assert.equal(h.root.dataset.motion, 'paused');
  h.click(h.shapes[2]); assert.equal(h.frames.size, 0);
  h.click(h.motion); assert.equal(h.root.dataset.motion, 'playing'); assert.ok(h.frames.size > 0);
  h.click(h.motion); assert.equal(h.root.dataset.motion, 'paused'); assert.equal(h.frames.size, 0);
  h.window.__pmlObservatory.dispose();
});

test('leaving the viewport and hiding the page stop the animation loop', () => {
  const h = harness();
  h.observers.intersection.callback([{isIntersecting: false}]); assert.equal(h.frames.size, 0);
  h.observers.intersection.callback([{isIntersecting: true}]); assert.ok(h.frames.size > 0);
  h.document.visibilityState = 'hidden'; h.document.dispatchEvent(new Event('visibilitychange')); assert.equal(h.frames.size, 0);
  h.document.visibilityState = 'visible'; h.document.dispatchEvent(new Event('visibilitychange')); assert.ok(h.frames.size > 0);
  h.window.__pmlObservatory.dispose();
});

test('keyboard pause works and removing the scene cleans up frames and listeners', () => {
  const h = harness();
  const key = new Event('keydown', {cancelable: true}); key.key = ' '; h.stage.dispatchEvent(key);
  assert.equal(h.root.dataset.motion, 'paused'); assert.equal(key.defaultPrevented, true);
  h.click(h.motion); assert.ok(h.frames.size > 0);
  h.root.isConnected = false; h.observers.removal.callback();
  assert.equal(h.root.dataset.disposed, 'true'); assert.equal(h.frames.size, 0);
  assert.ok(Object.values(h.observers).every(o => o.closed));
  assert.equal(h.window.__pmlObservatory, undefined);
  h.click(h.motion); assert.equal(h.frames.size, 0);
});

test('rerenders reuse an unchanged scene but refresh changed data without duplicate loops', () => {
  const h = harness();
  const original = h.window.__pmlObservatory;
  const count = h.frames.size;
  h.rerender();
  assert.equal(h.window.__pmlObservatory, original);
  assert.equal(h.frames.size, count);
  const observers = Object.values(h.observers);
  const payload = JSON.parse(h.root.dataset.info); payload.summary.studied = 14;
  h.root.dataset.info = JSON.stringify(payload); h.root.dataset.theme = 'light';
  h.rerender();
  assert.notEqual(h.window.__pmlObservatory, original);
  assert.ok(observers.every(observer => observer.closed));
  assert.ok(h.frames.size <= 2);
  assert.equal(h.picker.children.length, 2);
  h.click(h.insights[0]); assert.match(h.detail.textContent, /14 of 229/);
  h.window.__pmlObservatory.dispose();
});
