import {createControllerState, readController, controllerEvents, nextFocusIndex} from "./site-nav.mjs";

const root = document.documentElement;
const status = document.getElementById("controllerStatus");
const targets = () => [...document.querySelectorAll('a[href]:not([aria-disabled="true"]),button:not([disabled])')]
  .filter(el => !el.closest("[hidden]"));
const home = document.body.dataset.home || null;
let lastState = createControllerState();
let lastPadIndex = -1;

function focusNext(direction) {
  const controls = targets();
  const index = controls.indexOf(document.activeElement);
  const next = nextFocusIndex(index, controls.length, direction);
  if (next >= 0) controls[next].focus();
}
function onBack() {
  if (home) window.location.assign(home);
  else focusNext(-1);
}
function announce(message) { if (status) status.textContent = message; }

document.addEventListener("keydown", event => {
  if (event.altKey || event.ctrlKey || event.metaKey ||
      ["INPUT","TEXTAREA","SELECT"].includes(document.activeElement?.tagName)) return;
  if (["ArrowDown","ArrowRight","ArrowUp","ArrowLeft"].includes(event.key)) {
    event.preventDefault();
    focusNext(["ArrowDown","ArrowRight"].includes(event.key) ? 1 : -1);
  } else if (event.key === "Escape" || event.key === "Backspace") {
    event.preventDefault();
    onBack();
  }
});

function pollController() {
  let pad = null;
  try {
    const found = navigator.getGamepads?.() || [];
    pad = Array.from(found).find(candidate => candidate && candidate.connected !== false) || null;
  } catch (_) { /* Input may be blocked by browser policy or Xbox Edge. */ }
  const current = readController(pad);
  const actions = controllerEvents(lastState, current);
  if (pad && lastPadIndex !== pad.index) {
    announce("Controller detected. D-pad or left stick moves focus; A opens, B returns. Console compatibility not yet verified.");
    lastPadIndex = pad.index;
  } else if (!pad && lastPadIndex !== -1) {
    announce("Controller disconnected. Keyboard navigation is available.");
    lastPadIndex = -1;
  }
  lastState = current;
  if (actions.move) focusNext(actions.move);
  if (actions.back) onBack();
  else if (actions.activate) {
    const link = document.activeElement;
    if (targets().includes(link)) link.click();
    else focusNext(1);
  }
  window.requestAnimationFrame(pollController);
}

root.classList.add("site-js-ready");
window.requestAnimationFrame(pollController);
