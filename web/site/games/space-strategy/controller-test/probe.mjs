// Console-local input diagnostic. Never transmits, persists, or logs controller details.
const focusState = document.getElementById("focusState");
const connectionState = document.getElementById("connectionState");
const pointerState = document.getElementById("pointerState");
const output = document.getElementById("output");
const status = document.getElementById("status");
const keys = document.getElementById("keys");
const browseMode = document.getElementById("browseMode");
const modeHelp = document.getElementById("modeHelp");
let browseEnabled = true;

browseMode.addEventListener("click", () => {
  browseEnabled = !browseEnabled;
  browseMode.textContent = `Page navigation: ${browseEnabled ? "ON" : "OFF"}`;
  browseMode.setAttribute("aria-pressed", String(browseEnabled));
  modeHelp.textContent = browseEnabled ? "ON: page keyboard navigation is enabled. To switch Xbox Edge to Game Controls, hold the controller Menu button and choose Use game controls." : "OFF: page keyboard-arrow scrolling is suppressed. This does not switch Xbox Edge from Browsing Controls to Game Controls. Select this button to turn page navigation back on.";
});
let frame = 0;
let lastInteraction = "none";
const display = document.createElement("p");
display.id = "displayMetrics";
display.className = "probe-keys";
output.insertAdjacentElement("afterend", display);
function environmentDetails() {
  const viewport = window.visualViewport;
  const vv = viewport ? `${Math.round(viewport.width)} × ${Math.round(viewport.height)}` : "unavailable";
  const focused = document.activeElement?.id || document.activeElement?.tagName || "none";
  focusState.textContent = `Page focus: ${document.hasFocus() ? "YES" : "NO"} | Visibility: ${document.visibilityState}`;
  display.textContent = `Viewport: ${innerWidth} × ${innerHeight} CSS px | Visual viewport: ${vv} | Display scale: ${devicePixelRatio || 1} | Focus: ${focused} | Recent pointer/focus: ${lastInteraction}`;
}
const labels = ["A","B","X","Y","LB","RB","LT","RT","View","Menu","LS","RS","D-pad Up","D-pad Down","D-pad Left","D-pad Right"];
function sample() {
  let pads;
  try {
    if (typeof navigator.getGamepads !== "function") {
      output.textContent = "Gamepad API unavailable. Try browser keyboard-mapped inputs.";
    } else {
      pads = Array.from(navigator.getGamepads() || []).filter(p => p && p.connected !== false);
      if (!pads.length) output.textContent = "No connected gamepad reported. Press a controller button to activate it.";
      else {
        const pad = pads[0];
        const buttons = Array.from(pad.buttons || []).map((b,i)=>b?.pressed ? (labels[i] || "Button "+i) : null).filter(Boolean);
        const axes = Array.from(pad.axes || []).map((v,i)=>"Stick axis "+i+": "+(Number.isFinite(v) ? v.toFixed(2) : "n/a"));
        output.textContent = "Controller connected\nMapping: "+String(pad.mapping || "unknown")+"\nButtons detected: "+(buttons.join(", ") || "none")+"\n"+axes.join("\n");
      }
    }
  } catch(error) {
    output.textContent = "Gamepad API blocked: "+String(error?.name || "unknown");
  }
  environmentDetails();
  frame = requestAnimationFrame(sample);
}
status.textContent = "Automatic detection active. Press controller buttons; use Edge’s Use game controls mode."; 
window.addEventListener("gamepadconnected", e => { connectionState.textContent = "Gamepad connected event received (index "+e.gamepad.index+")"; });
window.addEventListener("gamepaddisconnected", e => { connectionState.textContent = "Gamepad disconnected event received (index "+e.gamepad.index+")"; });
sample();
document.addEventListener("pointerdown", event=>{lastInteraction = `pointer ${event.pointerType || "unknown"}`; pointerState.textContent = "Pointer event: "+lastInteraction; environmentDetails();});
document.addEventListener("focusin", event=>{lastInteraction = `focus ${event.target?.id || event.target?.tagName || "unknown"}`; environmentDetails();});
window.addEventListener("resize", environmentDetails);
environmentDetails();
document.addEventListener("keydown", event=>{
  if (!browseEnabled && ["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(event.key)) event.preventDefault();
  keys.textContent = "Most recent keyboard input: "+event.key;
  if (event.key === "Escape" && browseEnabled) window.location.assign("../");
});
window.addEventListener("pagehide", ()=>{cancelAnimationFrame(frame);});
