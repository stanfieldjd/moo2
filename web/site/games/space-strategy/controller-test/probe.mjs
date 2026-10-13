// Console-local input diagnostic. Never transmits, persists, or logs controller details.
const start = document.getElementById("start");
const stop = document.getElementById("stop");
const output = document.getElementById("output");
const status = document.getElementById("status");
const keys = document.getElementById("keys");
let running = false;
let frame = 0;
const labels = ["A","B","X","Y","LB","RB","LT","RT","View","Menu","LS","RS","D-pad Up","D-pad Down","D-pad Left","D-pad Right"];
function sample() {
  if (!running) return;
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
  frame = requestAnimationFrame(sample);
}
start.addEventListener("click", ()=>{
  running = true; start.disabled = true; stop.disabled = false;
  status.textContent = "Test active. Press each controller control."; sample();
});
stop.addEventListener("click", ()=>{
  running = false; cancelAnimationFrame(frame); start.disabled = false; stop.disabled = true;
  status.textContent = "Test stopped.";
});
document.addEventListener("keydown", event=>{
  keys.textContent = "Most recent keyboard input: "+event.key;
  if (event.key === "Escape" && !running) window.location.assign("../");
});
window.addEventListener("pagehide", ()=>{running=false; cancelAnimationFrame(frame);});
