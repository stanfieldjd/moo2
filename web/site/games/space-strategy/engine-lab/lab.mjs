import {LAB_SYSTEMS,stepSystem} from "./model.mjs";
import {makeColonyFixture,assignFixtureJob,inspectFixtureColony,JOB_LABELS} from "./colony-lab.mjs";
import {readController,createControllerState,controllerEvents} from "../../../site-nav.mjs";

const byId = id => document.getElementById(id);
const map = byId("stars");
const feedback = byId("controlFeedback");
const bonusButton = byId("bonus");
const fixtures = LAB_SYSTEMS.map((_,i)=>makeColonyFixture(i));
let selected = 0;
let selectedPerson = 0;
let enhanced = false;
let lastState = createControllerState();
let priorBumpers = {left:false,right:false};
let lastPadIndex = -1;
let focusedIndex = -1;

const nodes = LAB_SYSTEMS.map((system,index)=>{
  const node=document.createElement("button");
  node.className="star-node";
  node.type="button";
  node.textContent=system.name;
  node.style.left=system.coordinate[0]+"%";
  node.style.top=system.coordinate[1]+"%";
  node.setAttribute("aria-label","Inspect synthetic system "+system.name);
  node.addEventListener("click",()=>selectSystem(index));
  map.appendChild(node);
  return node;
});
function controls() {
  return [...nodes,...document.querySelectorAll(".deck-controls button, .deck-controls a")];
}
function applyInspectFlag(fixture) {
  const colonyRecord = new Uint8Array(fixture.colonyRecord);
  colonyRecord[0x13a] = enhanced ? 1 : 0;
  return {...fixture,colonyRecord};
}
function repaint() {
  const view=inspectFixtureColony(applyInspectFlag(fixtures[selected]),selectedPerson);
  nodes.forEach((node,i)=>{
    node.dataset.selected=String(i===selected);
    node.setAttribute("aria-pressed",String(i===selected));
  });
  byId("systemName").textContent=LAB_SYSTEMS[selected].name;
  byId("coords").textContent="Synthetic fixture "+(selected+1)+" of "+LAB_SYSTEMS.length;
  byId("food").textContent=(view.perUnitRates.foodDoublePerFarmer/2).toFixed(1);
  byId("industry").textContent=String(view.perUnitRates.industryPerWorker);
  byId("research").textContent=String(view.perUnitRates.researchPerScientist);
  byId("populationCount").textContent=String(view.populationCount);
  byId("foodJobs").textContent=String(view.jobTotals[0]);
  byId("industryJobs").textContent=String(view.jobTotals[1]);
  byId("researchJobs").textContent=String(view.jobTotals[2]);
  byId("foodUpkeep").textContent=String(view.foodUpkeep);
  byId("industryUpkeep").textContent=String(view.industryUpkeep);
  byId("workerCurrent").textContent="Person "+(selectedPerson+1)+"/"+view.populationCount+
    " — "+JOB_LABELS[view.personInfo.jobSlot]+" slot"+(view.personInfo.includedInProductionScan?" (in production scan)":" (excluded from production scan)");
  bonusButton.setAttribute("aria-pressed",String(enhanced));
  bonusButton.textContent="Test bonus: "+(enhanced?"ON":"OFF");
}
function selectSystem(index) {
  selected=index;
  selectedPerson=0;
  repaint();
  feedback.textContent="Inspecting "+LAB_SYSTEMS[index].name+". Synthetic state only; no turn advanced.";
}
function cycleSystem(direction) {
  selectSystem(stepSystem(selected,direction));
  nodes[selected].focus({preventScroll:true});
}
function shiftPerson(direction) {
  const count=fixtures[selected].colonyRecord[0x0a];
  selectedPerson=(selectedPerson+direction+count)%count;
  repaint();
  feedback.textContent="Person "+(selectedPerson+1)+" selected for synthetic record inspection.";
}
function assignJob(jobSlot) {
  fixtures[selected]=assignFixtureJob(fixtures[selected],selectedPerson,jobSlot);
  repaint();
  feedback.textContent="Test person "+(selectedPerson+1)+" assigned to "+JOB_LABELS[jobSlot]+
    ". Counts recalculated from verified packed workforce scan. This does not run a turn.";
}
byId("previous").addEventListener("click",()=>cycleSystem(-1));
byId("next").addEventListener("click",()=>cycleSystem(1));
byId("workerPrevious").addEventListener("click",()=>shiftPerson(-1));
byId("workerNext").addEventListener("click",()=>shiftPerson(1));
byId("jobFood").addEventListener("click",()=>assignJob(0));
byId("jobIndustry").addEventListener("click",()=>assignJob(1));
byId("jobResearch").addEventListener("click",()=>assignJob(2));
bonusButton.addEventListener("click",()=>{
  enhanced=!enhanced;
  repaint();
  feedback.textContent="Synthetic test flag 0x13a "+(enhanced?"enabled":"disabled")+
    " for per-worker calculations. No complete colony totals or turn advanced.";
});
function moveFocus(direction) {
  const elements=controls();
  if (!elements.length)return;
  const active=elements.indexOf(document.activeElement);
  focusedIndex=active<0?0:(active+direction+elements.length)%elements.length;
  elements[focusedIndex].focus({preventScroll:true});
  const target=elements[focusedIndex];
  feedback.textContent="Focused "+(target.getAttribute("aria-label")||target.textContent)+
    ". Press A or Enter to activate.";
}
document.addEventListener("keydown",event=>{
  if (event.altKey||event.ctrlKey||event.metaKey||event.repeat)return;
  if (["ArrowRight","ArrowDown","ArrowLeft","ArrowUp"].includes(event.key)) {
    event.preventDefault();
    moveFocus(["ArrowRight","ArrowDown"].includes(event.key)?1:-1);
  } else if (event.key==="Escape") {
    event.preventDefault();
    window.location.assign("../");
  }
});
function poll() {
  let pad=null;
  try {pad=Array.from(navigator.getGamepads?.()||[]).find(p=>p&&p.connected!==false)||null;}catch{}
  const now=readController(pad);
  const actions=controllerEvents(lastState,now);
  if(pad && lastPadIndex!==pad.index){
    lastPadIndex=pad.index;
    feedback.textContent="Controller detected: D-pad/stick changes focus, A activates, LB/RB selects systems, B returns.";
  } else if(!pad && lastPadIndex!==-1) {
    lastPadIndex=-1;
    feedback.textContent="Controller disconnected. Keyboard navigation remains available.";
  }
  if(actions.move)moveFocus(actions.move);
  const bumpers={left:Boolean(pad?.buttons?.[4]?.pressed),right:Boolean(pad?.buttons?.[5]?.pressed)};
  if(bumpers.left&&!priorBumpers.left)cycleSystem(-1);
  if(bumpers.right&&!priorBumpers.right)cycleSystem(1);
  if(actions.activate) {
    const active=document.activeElement;
    if(controls().includes(active))active.click();
    else {
      nodes[selected].focus({preventScroll:true});
      nodes[selected].click();
    }
  }
  if(actions.back)window.location.assign("../");
  lastState=now;
  priorBumpers=bumpers;
  window.requestAnimationFrame(poll);
}
window.addEventListener("gamepaddisconnected",()=>{
  lastState=createControllerState();priorBumpers={left:false,right:false};
});
document.addEventListener("visibilitychange",()=>{
  if(document.hidden){lastState=createControllerState();priorBumpers={left:false,right:false};}
});
repaint();
window.requestAnimationFrame(poll);
