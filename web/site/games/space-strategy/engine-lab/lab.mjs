import {LAB_SYSTEMS,inspectFixture,stepSystem} from "./model.mjs";
import {readController,createControllerState,controllerEvents} from "../../../site-nav.mjs";

const map = document.getElementById("stars");
const nameOut = document.getElementById("systemName");
const coordsOut = document.getElementById("coords");
const foodOut = document.getElementById("food");
const industryOut = document.getElementById("industry");
const researchOut = document.getElementById("research");
const feedback = document.getElementById("controlFeedback");
const bonusButton = document.getElementById("bonus");
let selected = 0;
let focused = 0;
let enhanced = false;
let priorPad = createControllerState();
let priorBumpers = {left:false,right:false};
let lastPadIndex = -1;

const nodes = LAB_SYSTEMS.map((system,index) => {
  const button = document.createElement("button");
  button.className = "star-node";
  button.type = "button";
  button.textContent = system.name;
  button.style.left = system.coordinate[0]+"%";
  button.style.top = system.coordinate[1]+"%";
  button.setAttribute("aria-label", "Select synthetic system "+system.name);
  button.addEventListener("click",()=>select(index));
  button.addEventListener("focus",()=>{focused=index;});
  map.appendChild(button);
  return button;
});
function repaint() {
  const result = inspectFixture(selected,enhanced);
  nodes.forEach((button,i) => {
    button.dataset.selected = String(i===selected);
    button.setAttribute("aria-pressed",String(i===selected));
  });
  nameOut.textContent=result.source.name;
  coordsOut.textContent="Synthetic fixture "+(selected+1)+" of "+LAB_SYSTEMS.length;
  foodOut.textContent=(result.foodDouble/2).toFixed(1);
  industryOut.textContent=String(result.industry);
  researchOut.textContent=String(result.research);
  bonusButton.setAttribute("aria-pressed",String(enhanced));
  bonusButton.textContent="Test bonus: "+(enhanced?"ON":"OFF");
}
function select(index) {
  selected=index;focused=index;repaint();
  feedback.textContent="Selected "+LAB_SYSTEMS[index].name+". Read-only engine yield calculations updated.";
}
function move(direction) {
  focused=stepSystem(focused,direction);
  nodes[focused].focus({preventScroll:true});
  feedback.textContent="Focus on "+LAB_SYSTEMS[focused].name+". Press A or Enter to inspect.";
}
function cycle(direction) {
  select(stepSystem(selected,direction));
  nodes[selected].focus({preventScroll:true});
}
document.getElementById("previous").addEventListener("click",()=>cycle(-1));
document.getElementById("next").addEventListener("click",()=>cycle(1));
bonusButton.addEventListener("click",()=>{
  enhanced=!enhanced;repaint();
  feedback.textContent="Verified per-worker flag 0x13a "+(enhanced?"enabled":"disabled")+" in synthetic test inputs. No turn advanced.";
});
document.addEventListener("keydown",event=>{
  if (event.altKey||event.ctrlKey||event.metaKey) return;
  if (["ArrowRight","ArrowDown","ArrowLeft","ArrowUp"].includes(event.key)) {
    event.preventDefault();move(["ArrowRight","ArrowDown"].includes(event.key)?1:-1);
  } else if ((event.key==="Enter"||event.key===" ") && nodes.includes(document.activeElement)) {
    event.preventDefault();select(nodes.indexOf(document.activeElement));
  } else if (event.key==="Escape" && document.activeElement?.tagName==="BUTTON") {
    event.preventDefault();window.location.assign("../");
  }
});
function poll() {
  let pad=null;
  try {pad=Array.from(navigator.getGamepads?.()||[]).find(p=>p&&p.connected!==false)||null;}catch{}
  const now=readController(pad);
  const actions=controllerEvents(priorPad,now);
  if(pad && lastPadIndex!==pad.index) {
    lastPadIndex=pad.index;
    feedback.textContent="Controller detected. D-pad/stick focuses; A selects; LB/RB cycles.";
  } else if(!pad && lastPadIndex!==-1) {
    lastPadIndex=-1;feedback.textContent="Controller disconnected; keyboard remains available.";
  }
  if(actions.move) move(actions.move);
  const bumpers={left:Boolean(pad?.buttons?.[4]?.pressed),right:Boolean(pad?.buttons?.[5]?.pressed)};
  if(bumpers.left&&!priorBumpers.left)cycle(-1);
  if(bumpers.right&&!priorBumpers.right)cycle(1);
  if(actions.activate) {
    const target=document.activeElement;
    if(target instanceof HTMLElement && (nodes.includes(target)||target.id==="bonus"||target.id==="previous"||target.id==="next"))target.click();
    else select(focused);
  }
  if(actions.back)window.location.assign("../");
  priorPad=now;priorBumpers=bumpers;
  window.requestAnimationFrame(poll);
}
window.addEventListener("gamepaddisconnected",()=>{priorPad=createControllerState();priorBumpers={left:false,right:false};});
document.addEventListener("visibilitychange",()=>{if(document.hidden){priorPad=createControllerState();priorBumpers={left:false,right:false};}});
repaint();
window.requestAnimationFrame(poll);
