/* ══════════════════════════════════════════════════════════════
   ELEMENT EXPLORER – game.js
   Four mini-games: Compound Forge | Element Hunt |
                    Category Sorter | Atom Builder
   + Web Audio API sound effects  (no external files needed)
══════════════════════════════════════════════════════════════ */

"use strict";

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   1. PERIODIC TABLE DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const ELEMENTS = [
  /* Z, sym, name, mass, cat, period, group, protons, neutrons, electrons */
  {z:1,  sym:"H",  name:"Hydrogen",   mass:1.008,  cat:"Nonmetal",           period:1, group:1,  p:1,  n:0,  e:1},
  {z:2,  sym:"He", name:"Helium",     mass:4.003,  cat:"Noble Gas",          period:1, group:18, p:2,  n:2,  e:2},
  {z:3,  sym:"Li", name:"Lithium",    mass:6.941,  cat:"Alkali Metal",       period:2, group:1,  p:3,  n:4,  e:3},
  {z:4,  sym:"Be", name:"Beryllium",  mass:9.012,  cat:"Alkaline Earth Metal",period:2,group:2,  p:4,  n:5,  e:4},
  {z:5,  sym:"B",  name:"Boron",      mass:10.811, cat:"Metalloid",          period:2, group:13, p:5,  n:6,  e:5},
  {z:6,  sym:"C",  name:"Carbon",     mass:12.011, cat:"Nonmetal",           period:2, group:14, p:6,  n:6,  e:6},
  {z:7,  sym:"N",  name:"Nitrogen",   mass:14.007, cat:"Nonmetal",           period:2, group:15, p:7,  n:7,  e:7},
  {z:8,  sym:"O",  name:"Oxygen",     mass:15.999, cat:"Nonmetal",           period:2, group:16, p:8,  n:8,  e:8},
  {z:9,  sym:"F",  name:"Fluorine",   mass:18.998, cat:"Halogen",            period:2, group:17, p:9,  n:10, e:9},
  {z:10, sym:"Ne", name:"Neon",       mass:20.180, cat:"Noble Gas",          period:2, group:18, p:10, n:10, e:10},
  {z:11, sym:"Na", name:"Sodium",     mass:22.990, cat:"Alkali Metal",       period:3, group:1,  p:11, n:12, e:11},
  {z:12, sym:"Mg", name:"Magnesium",  mass:24.305, cat:"Alkaline Earth Metal",period:3,group:2,  p:12, n:12, e:12},
  {z:13, sym:"Al", name:"Aluminum",   mass:26.982, cat:"Post-Transition Metal",period:3,group:13,p:13, n:14, e:13},
  {z:14, sym:"Si", name:"Silicon",    mass:28.086, cat:"Metalloid",          period:3, group:14, p:14, n:14, e:14},
  {z:15, sym:"P",  name:"Phosphorus", mass:30.974, cat:"Nonmetal",           period:3, group:15, p:15, n:16, e:15},
  {z:16, sym:"S",  name:"Sulfur",     mass:32.065, cat:"Nonmetal",           period:3, group:16, p:16, n:16, e:16},
  {z:17, sym:"Cl", name:"Chlorine",   mass:35.453, cat:"Halogen",            period:3, group:17, p:17, n:18, e:17},
  {z:18, sym:"Ar", name:"Argon",      mass:39.948, cat:"Noble Gas",          period:3, group:18, p:18, n:22, e:18},
  {z:19, sym:"K",  name:"Potassium",  mass:39.098, cat:"Alkali Metal",       period:4, group:1,  p:19, n:20, e:19},
  {z:20, sym:"Ca", name:"Calcium",    mass:40.078, cat:"Alkaline Earth Metal",period:4,group:2,  p:20, n:20, e:20},
  {z:21, sym:"Sc", name:"Scandium",   mass:44.956, cat:"Transition Metal",   period:4, group:3,  p:21, n:24, e:21},
  {z:22, sym:"Ti", name:"Titanium",   mass:47.867, cat:"Transition Metal",   period:4, group:4,  p:22, n:26, e:22},
  {z:23, sym:"V",  name:"Vanadium",   mass:50.942, cat:"Transition Metal",   period:4, group:5,  p:23, n:28, e:23},
  {z:24, sym:"Cr", name:"Chromium",   mass:51.996, cat:"Transition Metal",   period:4, group:6,  p:24, n:28, e:24},
  {z:25, sym:"Mn", name:"Manganese",  mass:54.938, cat:"Transition Metal",   period:4, group:7,  p:25, n:30, e:25},
  {z:26, sym:"Fe", name:"Iron",       mass:55.845, cat:"Transition Metal",   period:4, group:8,  p:26, n:30, e:26},
  {z:27, sym:"Co", name:"Cobalt",     mass:58.933, cat:"Transition Metal",   period:4, group:9,  p:27, n:32, e:27},
  {z:28, sym:"Ni", name:"Nickel",     mass:58.693, cat:"Transition Metal",   period:4, group:10, p:28, n:30, e:28},
  {z:29, sym:"Cu", name:"Copper",     mass:63.546, cat:"Transition Metal",   period:4, group:11, p:29, n:34, e:29},
  {z:30, sym:"Zn", name:"Zinc",       mass:65.38,  cat:"Transition Metal",   period:4, group:12, p:30, n:35, e:30},
  {z:31, sym:"Ga", name:"Gallium",    mass:69.723, cat:"Post-Transition Metal",period:4,group:13,p:31, n:38, e:31},
  {z:32, sym:"Ge", name:"Germanium",  mass:72.630, cat:"Metalloid",          period:4, group:14, p:32, n:40, e:32},
  {z:33, sym:"As", name:"Arsenic",    mass:74.922, cat:"Metalloid",          period:4, group:15, p:33, n:42, e:33},
  {z:34, sym:"Se", name:"Selenium",   mass:78.971, cat:"Nonmetal",           period:4, group:16, p:34, n:44, e:34},
  {z:35, sym:"Br", name:"Bromine",    mass:79.904, cat:"Halogen",            period:4, group:17, p:35, n:44, e:35},
  {z:36, sym:"Kr", name:"Krypton",    mass:83.798, cat:"Noble Gas",          period:4, group:18, p:36, n:47, e:36},
  {z:37, sym:"Rb", name:"Rubidium",   mass:85.468, cat:"Alkali Metal",       period:5, group:1,  p:37, n:48, e:37},
  {z:38, sym:"Sr", name:"Strontium",  mass:87.620, cat:"Alkaline Earth Metal",period:5,group:2,  p:38, n:50, e:38},
  {z:47, sym:"Ag", name:"Silver",     mass:107.87, cat:"Transition Metal",   period:5, group:11, p:47, n:61, e:47},
  {z:50, sym:"Sn", name:"Tin",        mass:118.71, cat:"Post-Transition Metal",period:5,group:14,p:50, n:68, e:50},
  {z:53, sym:"I",  name:"Iodine",     mass:126.90, cat:"Halogen",            period:5, group:17, p:53, n:74, e:53},
  {z:54, sym:"Xe", name:"Xenon",      mass:131.29, cat:"Noble Gas",          period:5, group:18, p:54, n:77, e:54},
  {z:55, sym:"Cs", name:"Cesium",     mass:132.91, cat:"Alkali Metal",       period:6, group:1,  p:55, n:78, e:55},
  {z:56, sym:"Ba", name:"Barium",     mass:137.33, cat:"Alkaline Earth Metal",period:6,group:2,  p:56, n:81, e:56},
  {z:74, sym:"W",  name:"Tungsten",   mass:183.84, cat:"Transition Metal",   period:6, group:6,  p:74, n:110,e:74},
  {z:78, sym:"Pt", name:"Platinum",   mass:195.08, cat:"Transition Metal",   period:6, group:10, p:78, n:117,e:78},
  {z:79, sym:"Au", name:"Gold",       mass:196.97, cat:"Transition Metal",   period:6, group:11, p:79, n:118,e:79},
  {z:80, sym:"Hg", name:"Mercury",    mass:200.59, cat:"Transition Metal",   period:6, group:12, p:80, n:121,e:80},
  {z:82, sym:"Pb", name:"Lead",       mass:207.20, cat:"Post-Transition Metal",period:6,group:14,p:82, n:125,e:82},
  {z:86, sym:"Rn", name:"Radon",      mass:222,    cat:"Noble Gas",          period:6, group:18, p:86, n:136,e:86},
  {z:88, sym:"Ra", name:"Radium",     mass:226,    cat:"Alkaline Earth Metal",period:7,group:2,  p:88, n:138,e:88},
  {z:92, sym:"U",  name:"Uranium",    mass:238.03, cat:"Actinide",           period:7, group:3,  p:92, n:146,e:92},
];

/* ── Full 18-group layout for Hunt grid (sparse) ── */
// [period, group] → element sym
const GRID_MAP = {};
const GRID_ELEMENTS = [
  {z:1, sym:"H",  period:1, group:1},
  {z:2, sym:"He", period:1, group:18},
  {z:3, sym:"Li", period:2, group:1},
  {z:4, sym:"Be", period:2, group:2},
  {z:5, sym:"B",  period:2, group:13},
  {z:6, sym:"C",  period:2, group:14},
  {z:7, sym:"N",  period:2, group:15},
  {z:8, sym:"O",  period:2, group:16},
  {z:9, sym:"F",  period:2, group:17},
  {z:10,sym:"Ne", period:2, group:18},
  {z:11,sym:"Na", period:3, group:1},
  {z:12,sym:"Mg", period:3, group:2},
  {z:13,sym:"Al", period:3, group:13},
  {z:14,sym:"Si", period:3, group:14},
  {z:15,sym:"P",  period:3, group:15},
  {z:16,sym:"S",  period:3, group:16},
  {z:17,sym:"Cl", period:3, group:17},
  {z:18,sym:"Ar", period:3, group:18},
  {z:19,sym:"K",  period:4, group:1},
  {z:20,sym:"Ca", period:4, group:2},
  {z:21,sym:"Sc", period:4, group:3},
  {z:22,sym:"Ti", period:4, group:4},
  {z:23,sym:"V",  period:4, group:5},
  {z:24,sym:"Cr", period:4, group:6},
  {z:25,sym:"Mn", period:4, group:7},
  {z:26,sym:"Fe", period:4, group:8},
  {z:27,sym:"Co", period:4, group:9},
  {z:28,sym:"Ni", period:4, group:10},
  {z:29,sym:"Cu", period:4, group:11},
  {z:30,sym:"Zn", period:4, group:12},
  {z:31,sym:"Ga", period:4, group:13},
  {z:32,sym:"Ge", period:4, group:14},
  {z:33,sym:"As", period:4, group:15},
  {z:34,sym:"Se", period:4, group:16},
  {z:35,sym:"Br", period:4, group:17},
  {z:36,sym:"Kr", period:4, group:18},
  {z:37,sym:"Rb", period:5, group:1},
  {z:38,sym:"Sr", period:5, group:2},
  {z:47,sym:"Ag", period:5, group:11},
  {z:50,sym:"Sn", period:5, group:14},
  {z:53,sym:"I",  period:5, group:17},
  {z:54,sym:"Xe", period:5, group:18},
  {z:55,sym:"Cs", period:6, group:1},
  {z:56,sym:"Ba", period:6, group:2},
  {z:74,sym:"W",  period:6, group:6},
  {z:78,sym:"Pt", period:6, group:10},
  {z:79,sym:"Au", period:6, group:11},
  {z:80,sym:"Hg", period:6, group:12},
  {z:82,sym:"Pb", period:6, group:14},
  {z:86,sym:"Rn", period:6, group:18},
  {z:88,sym:"Ra", period:7, group:2},
  {z:92,sym:"U",  period:7, group:3},
];

/* Category → CSS class */
const CAT_CLASS = {
  "Alkali Metal":          "cat-alkali",
  "Alkaline Earth Metal":  "cat-alkaline",
  "Transition Metal":      "cat-transition",
  "Nonmetal":              "cat-nonmetal",
  "Noble Gas":             "cat-noble",
  "Metalloid":             "cat-metalloid",
  "Halogen":               "cat-halogen",
  "Post-Transition Metal": "cat-post",
  "Lanthanide":            "cat-lanthanide",
  "Actinide":              "cat-actinide",
};

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   2. COMPOUNDS (Forge mode)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const COMPOUNDS = [
  { name:"Water",           formula:"H₂O",  recipe:{H:2,O:1},  hint:"2 Hydrogen + 1 Oxygen",            fun:"Covers 71% of Earth's surface!" },
  { name:"Table Salt",      formula:"NaCl", recipe:{Na:1,Cl:1}, hint:"1 Sodium + 1 Chlorine",            fun:"Essential for human life & cooking." },
  { name:"Carbon Dioxide",  formula:"CO₂",  recipe:{C:1,O:2},  hint:"1 Carbon + 2 Oxygen",              fun:"Plants breathe this in!" },
  { name:"Ammonia",         formula:"NH₃",  recipe:{N:1,H:3},  hint:"1 Nitrogen + 3 Hydrogen",          fun:"Used in fertilisers worldwide." },
  { name:"Rust",            formula:"Fe₂O₃",recipe:{Fe:2,O:3}, hint:"2 Iron + 3 Oxygen",                fun:"Iron oxidising — metals hate water!" },
  { name:"Methane",         formula:"CH₄",  recipe:{C:1,H:4},  hint:"1 Carbon + 4 Hydrogen",            fun:"Main component of natural gas." },
  { name:"Hydrochloric Acid",formula:"HCl", recipe:{H:1,Cl:1}, hint:"1 Hydrogen + 1 Chlorine",          fun:"Your stomach makes this acid!" },
  { name:"Magnesium Oxide", formula:"MgO",  recipe:{Mg:1,O:1}, hint:"1 Magnesium + 1 Oxygen",           fun:"Burns with brilliant white light." },
  { name:"Sodium Hydroxide",formula:"NaOH", recipe:{Na:1,O:1,H:1},hint:"1 Sodium + 1 Oxygen + 1 Hydrogen",fun:"Used in soap manufacturing." },
  { name:"Sulfuric Acid",   formula:"H₂SO₄",recipe:{H:2,S:1,O:4},hint:"2 Hydrogen + 1 Sulfur + 4 Oxygen",fun:"Most produced industrial chemical!" },
  { name:"Calcium Carbonate",formula:"CaCO₃",recipe:{Ca:1,C:1,O:3},hint:"1 Ca + 1 C + 3 Oxygen",       fun:"Makes up limestone & chalk." },
  { name:"Glucose",         formula:"C₆H₁₂O₆",recipe:{C:6,H:12,O:6},hint:"6C + 12H + 6O",             fun:"Primary fuel for your brain!" },
];

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   3. HUNT CLUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const CLUES = [
  { clue:"I am the lightest element in the universe and make up stars.", sym:"H" },
  { clue:"I am a noble gas used in party balloons — I make your voice squeaky!", sym:"He" },
  { clue:"I am the most electronegative element — very reactive halogen.", sym:"F" },
  { clue:"I am the element of life — found in all organic molecules.", sym:"C" },
  { clue:"I am an alkali metal that explodes in water dramatically.", sym:"Na" },
  { clue:"I am the most abundant gas in Earth's atmosphere (~78%).", sym:"N" },
  { clue:"I am essential for breathing and make up 21% of air.", sym:"O" },
  { clue:"I am a yellow non-metal with a strong smell, found in volcanoes.", sym:"S" },
  { clue:"I am a transition metal known as the king of conductors — jewelry too!", sym:"Au" },
  { clue:"I am used in computer chips and solar panels — a metalloid.", sym:"Si" },
  { clue:"I am a liquid metal at room temperature, once used in thermometers.", sym:"Hg" },
  { clue:"I am the element with atomic number 26 — the core of Earth.", sym:"Fe" },
  { clue:"I am a radioactive element used in nuclear power plants.", sym:"U" },
  { clue:"I am the halogen in table salt and ocean water.", sym:"Cl" },
  { clue:"I am a noble gas that glows orange-red in neon signs.", sym:"Ne" },
  { clue:"I am used to make stainless steel and gives chromium its shine.", sym:"Cr" },
  { clue:"I am a silvery alkali metal used in batteries & psychiatric medicine.", sym:"Li" },
  { clue:"I am essential for strong bones and teeth — found in milk!", sym:"Ca" },
  { clue:"I am the densest natural element and incredibly hard to melt.", sym:"W" },
  { clue:"I am the noble gas used in welding and laser technology.", sym:"Ar" },
  { clue:"I am a precious metal used in catalytic converters.", sym:"Pt" },
  { clue:"I am the only liquid non-metal at room temperature.", sym:"Br" },
  { clue:"I am a metalloid semiconductor used in transistors.", sym:"Ge" },
  { clue:"I am an alkali metal that reacts explosively with water — used in fireworks.", sym:"K" },
];

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   4. ATOM BUILDER LEVELS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const ATOM_LEVELS = [
  { name:"Hydrogen",  sym:"H",  p:1,  n:0,  e:1,  hint:"Simplest atom: 1 proton, 0 neutrons, 1 electron." },
  { name:"Helium",    sym:"He", p:2,  n:2,  e:2,  hint:"Noble gas: 2 protons, 2 neutrons, 2 electrons." },
  { name:"Lithium",   sym:"Li", p:3,  n:4,  e:3,  hint:"Alkali metal: 3 protons, 4 neutrons, 3 electrons." },
  { name:"Carbon",    sym:"C",  p:6,  n:6,  e:6,  hint:"Life element: 6 protons, 6 neutrons, 6 electrons." },
  { name:"Oxygen",    sym:"O",  p:8,  n:8,  e:8,  hint:"8 protons, 8 neutrons, 8 electrons." },
  { name:"Sodium",    sym:"Na", p:11, n:12, e:11, hint:"11 protons, 12 neutrons, 11 electrons." },
  { name:"Chlorine",  sym:"Cl", p:17, n:18, e:17, hint:"17 protons, 18 neutrons, 17 electrons." },
  { name:"Iron",      sym:"Fe", p:26, n:30, e:26, hint:"26 protons, 30 neutrons, 26 electrons." },
];

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   5. AUDIO ENGINE (Web Audio API – no files needed)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const AudioCtx = window.AudioContext || window.webkitAudioContext;
let audioCtx = null;
let soundEnabled = true;

function getCtx() {
  if (!audioCtx) audioCtx = new AudioCtx();
  if (audioCtx.state === "suspended") audioCtx.resume();
  return audioCtx;
}

function playTone(freq, type = "sine", dur = 0.15, vol = 0.25, delay = 0) {
  if (!soundEnabled) return;
  try {
    const ctx = getCtx();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain); gain.connect(ctx.destination);
    osc.type = type;
    osc.frequency.setValueAtTime(freq, ctx.currentTime + delay);
    gain.gain.setValueAtTime(vol, ctx.currentTime + delay);
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + delay + dur);
    osc.start(ctx.currentTime + delay);
    osc.stop(ctx.currentTime + delay + dur);
  } catch(e) {}
}

function sfx_success() {
  playTone(523.25, "sine", 0.12, 0.3);
  playTone(659.25, "sine", 0.12, 0.3, 0.12);
  playTone(783.99, "sine", 0.18, 0.3, 0.24);
}
function sfx_error() {
  playTone(220, "sawtooth", 0.18, 0.25);
  playTone(196, "sawtooth", 0.12, 0.2, 0.14);
}
function sfx_click() { playTone(880, "sine", 0.07, 0.15); }
function sfx_drop()  { playTone(440, "triangle", 0.1, 0.2); }
function sfx_level() {
  [523,587,659,698,784].forEach((f,i) => playTone(f,"sine",0.15,0.3,i*0.12));
}
function sfx_tick()  { playTone(1200, "square", 0.05, 0.1); }
function sfx_win() {
  const notes = [523,659,784,880,1047];
  notes.forEach((f,i) => {
    playTone(f, "sine", 0.18, 0.3, i*0.15);
    playTone(f*1.5, "sine", 0.12, 0.2, i*0.15 + 0.08);
  });
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   6. GLOBAL STATE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const STATE = {
  playerName: "Scientist",
  totalScore:  0,
  lives:       3,
  currentMode: null,
};

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   7. SCREEN ROUTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function showScreen(id) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  const el = document.getElementById(id);
  if (el) el.classList.add("active");
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   8. HUD HELPERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function updateHUD() {
  const n = document.getElementById("hud-name");
  const s = document.getElementById("hud-score");
  const l = document.getElementById("hud-lives");
  if (n) n.textContent = STATE.playerName;
  if (s) s.textContent = STATE.totalScore;
  if (l) l.textContent = STATE.lives;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   9. TOAST HELPER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
let toastTimers = {};
function showToast(id, msg, type = "info", dur = 2200) {
  const el = document.getElementById(id);
  if (!el) return;
  clearTimeout(toastTimers[id]);
  el.textContent = msg;
  el.className = `feedback-toast show ${type}`;
  toastTimers[id] = setTimeout(() => el.classList.remove("show"), dur);
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   10. ELEMENT TILE FACTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function catClass(cat) {
  return CAT_CLASS[cat] || "cat-transition";
}

function makeTile(el, opts = {}) {
  const div = document.createElement("div");
  div.className = `el-tile ${catClass(el.cat)}${opts.small ? " el-tile-sm" : ""}`;
  div.dataset.sym = el.sym;
  div.dataset.cat = el.cat;
  if (opts.draggable !== false) div.draggable = true;
  div.innerHTML = `
    <span class="el-num">${el.z}</span>
    <span class="el-sym">${el.sym}</span>
    <span class="el-name">${el.name}</span>`;
  if (opts.onClick) div.addEventListener("click", () => opts.onClick(el, div));
  return div;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   11. ── COMPOUND FORGE ─────────────────────────────────────
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const FORGE = {
  score:    0,
  level:    0,
  timer:    30,
  timerInt: null,
  forgeContents: {}, // sym → count
};

function forgeInit() {
  FORGE.score = 0;
  FORGE.level = 0;
  FORGE.forgeContents = {};
  renderForgePalette();
  forgeLoadLevel();
  forgeClearContents();
  document.getElementById("cmp-score").textContent = 0;
}

/* Element palette at bottom */
function renderForgePalette() {
  const palette = document.getElementById("element-palette");
  palette.innerHTML = "";
  // Show a curated subset
  const shown = ELEMENTS.filter(e => [
    "H","O","C","N","Na","Cl","Fe","Mg","S","Ca","Si","P","K","Al","He"
  ].includes(e.sym));
  shown.forEach(el => {
    const tile = makeTile(el);
    tile.addEventListener("dragstart", e => {
      e.dataTransfer.setData("sym", el.sym);
      tile.classList.add("dragging");
    });
    tile.addEventListener("dragend", () => tile.classList.remove("dragging"));
    tile.addEventListener("click", () => {
      sfx_click();
      addToForge(el.sym);
    });
    palette.appendChild(tile);
  });
}

function forgeLoadLevel() {
  const compound = COMPOUNDS[FORGE.level % COMPOUNDS.length];
  FORGE.currentCompound = compound;
  FORGE.timer = 30;
  clearInterval(FORGE.timerInt);
  FORGE.timerInt = setInterval(forgeTimerTick, 1000);

  document.getElementById("cmp-target-name").textContent    = compound.name;
  document.getElementById("cmp-target-formula").textContent = compound.formula;
  document.getElementById("cmp-target-hint").textContent    = "Hint: " + compound.hint;
  document.getElementById("cmp-level").textContent          = FORGE.level + 1;
  document.getElementById("cmp-timer").textContent          = FORGE.timer;
}

function forgeTimerTick() {
  FORGE.timer--;
  document.getElementById("cmp-timer").textContent = FORGE.timer;
  if (FORGE.timer <= 5) sfx_tick();
  if (FORGE.timer <= 0) {
    clearInterval(FORGE.timerInt);
    sfx_error();
    showToast("cmp-feedback", "⏰ Time's up! Try the next one.", "error");
    forgeClearContents();
    FORGE.level++;
    setTimeout(() => { forgeLoadLevel(); }, 1500);
  }
}

function addToForge(sym) {
  FORGE.forgeContents[sym] = (FORGE.forgeContents[sym] || 0) + 1;
  renderForgeContents();
  sfx_drop();
}

function renderForgeContents() {
  const container = document.getElementById("forge-elements");
  const label     = document.querySelector(".forge-label");
  container.innerHTML = "";
  if (Object.keys(FORGE.forgeContents).length === 0) {
    label.style.display = "block";
  } else {
    label.style.display = "none";
    Object.entries(FORGE.forgeContents).forEach(([sym, cnt]) => {
      const el = ELEMENTS.find(e => e.sym === sym);
      if (!el) return;
      for (let i = 0; i < cnt; i++) {
        const span = document.createElement("span");
        span.className = `el-tile-sm ${catClass(el.cat)}`;
        span.textContent = sym;
        container.appendChild(span);
      }
    });
  }
}

function forgeClearContents() {
  FORGE.forgeContents = {};
  renderForgeContents();
  const label = document.querySelector(".forge-label");
  if (label) label.style.display = "block";
}

function forgeSynthesise() {
  const comp   = FORGE.currentCompound;
  const recipe = comp.recipe;
  const got    = FORGE.forgeContents;

  // Check match
  const recipeKeys  = Object.keys(recipe);
  const gotKeys     = Object.keys(got);
  let match = recipeKeys.length === gotKeys.length;
  if (match) {
    for (const sym of recipeKeys) {
      if ((got[sym] || 0) !== recipe[sym]) { match = false; break; }
    }
  }

  if (match) {
    sfx_success();
    const pts = 50 + FORGE.timer * 2;
    FORGE.score += pts;
    STATE.totalScore += pts;
    updateHUD();
    document.getElementById("cmp-score").textContent = FORGE.score;
    showToast("cmp-feedback", `✅ Correct! +${pts} pts — ${comp.fun}`, "success", 3000);
    forgeClearContents();
    clearInterval(FORGE.timerInt);
    FORGE.level++;
    setTimeout(() => {
      if (FORGE.level >= COMPOUNDS.length) {
        endGame("compound", FORGE.score);
      } else {
        sfx_level();
        forgeLoadLevel();
      }
    }, 2200);
  } else {
    sfx_error();
    showToast("cmp-feedback", `❌ Wrong formula! Hint: ${comp.hint}`, "error", 2500);
    forgeClearContents();
  }
}

/* Drag-and-drop for forge drop zone */
function initForgeDropZone() {
  const zone = document.getElementById("forge-drop");
  zone.addEventListener("dragover", e => { e.preventDefault(); zone.classList.add("dragover"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("dragover"));
  zone.addEventListener("drop", e => {
    e.preventDefault();
    zone.classList.remove("dragover");
    const sym = e.dataTransfer.getData("sym");
    if (sym) addToForge(sym);
  });
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   12. ── ELEMENT HUNT ───────────────────────────────────────
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const HUNT = {
  score:    0,
  round:    0,
  timer:    20,
  timerInt: null,
  queue:    [],
  answer:   null,
};

function huntInit() {
  HUNT.score  = 0;
  HUNT.round  = 0;
  HUNT.queue  = shuffle([...CLUES]).slice(0, 10);
  document.getElementById("hunt-score").textContent = 0;
  buildPeriodicGrid();
  huntLoadRound();
}

function buildPeriodicGrid() {
  const grid = document.getElementById("periodic-grid");
  grid.innerHTML = "";

  // 7 rows × 18 cols
  const cells = [];
  for (let r = 1; r <= 7; r++) {
    for (let g = 1; g <= 18; g++) cells.push({ r, g });
  }

  const elMap = {};
  GRID_ELEMENTS.forEach(e => {
    const el = ELEMENTS.find(x => x.sym === e.sym);
    if (el) elMap[`${e.period}-${e.group}`] = el;
  });

  cells.forEach(({ r, g }) => {
    const el = elMap[`${r}-${g}`];
    const cell = document.createElement("div");
    if (el) {
      cell.className = `el-tile ${catClass(el.cat)}`;
      cell.dataset.sym = el.sym;
      cell.innerHTML = `
        <div class="el-inner">
          <span class="el-num">${el.z}</span>
          <span class="el-sym">${el.sym}</span>
          <span class="el-name">${el.name}</span>
        </div>`;
      cell.style.cursor = "pointer";
      cell.addEventListener("click", () => huntGuess(el.sym, cell));
    } else {
      cell.style.background = "transparent";
      cell.style.border = "none";
    }
    grid.appendChild(cell);
  });
}

function huntLoadRound() {
  if (HUNT.round >= HUNT.queue.length) { endGame("hunt", HUNT.score); return; }
  const item = HUNT.queue[HUNT.round];
  HUNT.answer = item.sym;
  HUNT.timer  = 20;
  clearInterval(HUNT.timerInt);
  HUNT.timerInt = setInterval(huntTimerTick, 1000);

  document.getElementById("hunt-clue").textContent   = item.clue;
  document.getElementById("hunt-round").textContent  = HUNT.round + 1;
  document.getElementById("hunt-timer").textContent  = HUNT.timer;
}

function huntTimerTick() {
  HUNT.timer--;
  document.getElementById("hunt-timer").textContent = HUNT.timer;
  if (HUNT.timer <= 5) sfx_tick();
  if (HUNT.timer <= 0) {
    clearInterval(HUNT.timerInt);
    sfx_error();
    highlightAnswer("wrong");
    showToast("hunt-feedback", `⏰ Time up! Answer: ${HUNT.answer}`, "error", 2000);
    HUNT.round++;
    setTimeout(huntLoadRound, 2200);
  }
}

function huntGuess(sym, cell) {
  clearInterval(HUNT.timerInt);
  if (sym === HUNT.answer) {
    sfx_success();
    const pts = 30 + HUNT.timer * 3;
    HUNT.score += pts;
    STATE.totalScore += pts;
    updateHUD();
    document.getElementById("hunt-score").textContent = HUNT.score;
    cell.classList.add("correct-flash");
    showToast("hunt-feedback", `✅ Correct! +${pts} pts`, "success");
    setTimeout(() => cell.classList.remove("correct-flash"), 600);
  } else {
    sfx_error();
    cell.classList.add("wrong-flash");
    highlightAnswer("correct");
    showToast("hunt-feedback", `❌ Wrong! It was ${HUNT.answer}`, "error", 2000);
    setTimeout(() => cell.classList.remove("wrong-flash"), 600);
  }
  HUNT.round++;
  setTimeout(huntLoadRound, 2000);
}

function highlightAnswer(type) {
  const cells = document.querySelectorAll(`#periodic-grid .el-tile`);
  cells.forEach(c => {
    if (c.dataset.sym === HUNT.answer) {
      c.classList.add(type === "correct" ? "correct-flash" : "wrong-flash");
      setTimeout(() => c.classList.remove("correct-flash", "wrong-flash"), 800);
    }
  });
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   13. ── CATEGORY SORTER ────────────────────────────────────
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const SORT = {
  score:    0,
  total:    0,
  correct:  0,
  wrong:    0,
};

const SORT_CATS = ["Alkali Metal","Alkaline Earth Metal","Transition Metal","Nonmetal","Noble Gas","Metalloid"];
const CAT_TO_BIN = {
  "Alkali Metal":"bin-alkali",
  "Alkaline Earth Metal":"bin-alkaline",
  "Transition Metal":"bin-transition",
  "Nonmetal":"bin-nonmetal",
  "Noble Gas":"bin-noble",
  "Metalloid":"bin-metalloid",
};

function sortInit() {
  SORT.score   = 0;
  SORT.correct = 0;
  SORT.wrong   = 0;

  // Clear all bins
  Object.values(CAT_TO_BIN).forEach(id => {
    const el = document.getElementById(id);
    if (el) el.innerHTML = "";
  });

  // Pick elements from those categories
  const pool = ELEMENTS.filter(e => SORT_CATS.includes(e.cat));
  const chosen = shuffle(pool).slice(0, 20);
  SORT.total = chosen.length;
  document.getElementById("sort-left").textContent = SORT.total;
  document.getElementById("sort-score").textContent = 0;

  const source = document.getElementById("sort-source");
  source.innerHTML = "";
  chosen.forEach(el => {
    const tile = makeTile(el);
    tile.id = `sort-tile-${el.sym}`;
    tile.dataset.correctCat = el.cat;
    tile.addEventListener("dragstart", e => {
      e.dataTransfer.setData("sortSym", el.sym);
      e.dataTransfer.setData("sortCat", el.cat);
      tile.classList.add("dragging");
    });
    tile.addEventListener("dragend", () => tile.classList.remove("dragging"));
    tile.addEventListener("click", () => sfx_click());
    source.appendChild(tile);
  });

  // Setup bin drop zones
  document.querySelectorAll(".bin-drop").forEach(bin => {
    bin.addEventListener("dragover", e => { e.preventDefault(); bin.classList.add("dragover"); });
    bin.addEventListener("dragleave", () => bin.classList.remove("dragover"));
    bin.addEventListener("drop", e => {
      e.preventDefault();
      bin.classList.remove("dragover");
      const sym = e.dataTransfer.getData("sortSym");
      const cat = e.dataTransfer.getData("sortCat");
      const binCat = bin.closest(".sort-bin").dataset.cat;
      sortHandleDrop(sym, cat, binCat, bin);
    });
  });
}

function sortHandleDrop(sym, cat, binCat, bin) {
  const tile = document.getElementById(`sort-tile-${sym}`);
  if (!tile) return;
  sfx_drop();

  if (cat === binCat) {
    sfx_success();
    SORT.correct++;
    SORT.score += 20;
    STATE.totalScore += 20;
    updateHUD();
    tile.style.border = `2px solid var(--green)`;
    tile.style.boxShadow = `0 0 12px rgba(0,255,136,.4)`;
    bin.appendChild(tile);
    tile.draggable = false;
    document.getElementById("sort-score").textContent = SORT.score;
    showToast("sort-feedback", `✅ Correct! ${sym} is a ${cat}`, "success");
  } else {
    sfx_error();
    SORT.wrong++;
    tile.style.animation = "flashRed .4s ease";
    setTimeout(() => tile.style.animation = "", 500);
    showToast("sort-feedback", `❌ ${sym} is NOT a ${binCat}!`, "error");
  }

  const left = SORT.total - SORT.correct - SORT.wrong;
  document.getElementById("sort-left").textContent = Math.max(0, left);

  if (SORT.correct + SORT.wrong >= SORT.total) {
    clearTimeout(SORT._endTimer);
    SORT._endTimer = setTimeout(() => endGame("sort", SORT.score), 1500);
  }
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   14. ── ATOM BUILDER ───────────────────────────────────────
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
const ATOM_STATE = {
  level: 0,
  score: 0,
  p: 0, n: 0, e: 0,
  animFrame: null,
};

function atomInit() {
  ATOM_STATE.level = 0;
  ATOM_STATE.score = 0;
  ATOM_STATE.p = 0; ATOM_STATE.n = 0; ATOM_STATE.e = 0;
  document.getElementById("atom-score").textContent = 0;
  atomLoadLevel();
}

function atomLoadLevel() {
  const lvl = ATOM_LEVELS[ATOM_STATE.level % ATOM_LEVELS.length];
  ATOM_STATE.target = lvl;
  ATOM_STATE.p = 0; ATOM_STATE.n = 0; ATOM_STATE.e = 0;
  document.getElementById("atom-target-name").textContent    = lvl.name;
  document.getElementById("atom-target-symbol").textContent  = lvl.sym;
  document.getElementById("atom-target-props").textContent   = `Protons: ${lvl.p}  |  Neutrons: ${lvl.n}  |  Electrons: ${lvl.e}`;
  document.getElementById("atom-hint-box").textContent       = "💡 " + lvl.hint;
  document.getElementById("atom-level").textContent          = ATOM_STATE.level + 1;
  updateAtomCounts();
  atomDraw();
}

function updateAtomCounts() {
  document.getElementById("atom-p-count").textContent = ATOM_STATE.p;
  document.getElementById("atom-n-count").textContent = ATOM_STATE.n;
  document.getElementById("atom-e-count").textContent = ATOM_STATE.e;
}

function atomAdjust(particle, delta) {
  ATOM_STATE[particle] = Math.max(0, ATOM_STATE[particle] + delta);
  updateAtomCounts();
  sfx_click();
  atomDraw();
}

function atomCheck() {
  const t = ATOM_STATE.target;
  if (ATOM_STATE.p === t.p && ATOM_STATE.n === t.n && ATOM_STATE.e === t.e) {
    sfx_success();
    const pts = 60;
    ATOM_STATE.score += pts;
    STATE.totalScore += pts;
    updateHUD();
    document.getElementById("atom-score").textContent = ATOM_STATE.score;
    showToast("atom-feedback", `⚛️ Perfect atom! +${pts} pts`, "success");
    ATOM_STATE.level++;
    setTimeout(() => {
      if (ATOM_STATE.level >= ATOM_LEVELS.length) endGame("atom", ATOM_STATE.score);
      else { sfx_level(); atomLoadLevel(); }
    }, 1800);
  } else {
    sfx_error();
    let msg = "❌ Not quite. Check: ";
    if (ATOM_STATE.p !== t.p) msg += `protons should be ${t.p}. `;
    if (ATOM_STATE.n !== t.n) msg += `neutrons should be ${t.n}. `;
    if (ATOM_STATE.e !== t.e) msg += `electrons should be ${t.e}.`;
    showToast("atom-feedback", msg, "error", 3000);
  }
}

/* Canvas Atom Visualisation */
function atomDraw() {
  const canvas = document.getElementById("atom-canvas");
  if (!canvas) return;
  const ctx  = canvas.getContext("2d");
  const W    = canvas.width;
  const H    = canvas.height;
  const cx   = W / 2;
  const cy   = H / 2;
  const now  = Date.now() / 1000;

  ctx.clearRect(0, 0, W, H);

  // Glow background
  const bg = ctx.createRadialGradient(cx, cy, 0, cx, cy, W/2);
  bg.addColorStop(0, "rgba(0,229,255,0.04)");
  bg.addColorStop(1, "transparent");
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  // Nucleus
  const nucR = Math.min(24, 8 + ATOM_STATE.p * 0.9 + ATOM_STATE.n * 0.5);
  drawGlowCircle(ctx, cx, cy, nucR, "#ff6b6b", "rgba(255,107,107,0.5)");

  // Proton labels
  ctx.fillStyle = "#ff6b6b";
  ctx.font = "bold 11px Exo 2";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  if (ATOM_STATE.p > 0) ctx.fillText(`${ATOM_STATE.p}p`, cx, cy - 4);
  if (ATOM_STATE.n > 0) {
    ctx.fillStyle = "#aaa";
    ctx.fillText(`${ATOM_STATE.n}n`, cx, cy + 7);
  }

  // Electron shells
  const shellCap = [2, 8, 18, 32];
  let remE = ATOM_STATE.e;
  let shellIdx = 0;
  const radii = [55, 85, 115, 145];

  while (remE > 0 && shellIdx < shellCap.length) {
    const cap  = shellCap[shellIdx];
    const cnt  = Math.min(remE, cap);
    const r    = radii[shellIdx];
    const speed= 0.4 + shellIdx * 0.15;

    // Draw orbit ring
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(0,229,255,0.18)";
    ctx.lineWidth   = 1;
    ctx.stroke();

    // Draw electrons
    for (let i = 0; i < cnt; i++) {
      const angle = (i / cnt) * Math.PI * 2 + now * speed;
      const ex = cx + r * Math.cos(angle);
      const ey = cy + r * Math.sin(angle);
      drawGlowCircle(ctx, ex, ey, 5, "#00e5ff", "rgba(0,229,255,0.5)");
    }

    remE -= cnt;
    shellIdx++;
  }

  // Legend
  ctx.font      = "10px Exo 2";
  ctx.textAlign = "right";
  ctx.fillStyle = "rgba(255,107,107,0.8)";  ctx.fillText("● Proton",  W - 8, H - 42);
  ctx.fillStyle = "rgba(200,200,200,0.8)";  ctx.fillText("● Neutron", W - 8, H - 28);
  ctx.fillStyle = "rgba(0,229,255,0.8)";    ctx.fillText("● Electron",W - 8, H - 14);

  // Animate
  if (ATOM_STATE.e > 0 || ATOM_STATE.p > 0) {
    cancelAnimationFrame(ATOM_STATE.animFrame);
    ATOM_STATE.animFrame = requestAnimationFrame(atomDraw);
  }
}

function drawGlowCircle(ctx, x, y, r, color, glowColor) {
  ctx.save();
  ctx.shadowBlur  = 14;
  ctx.shadowColor = glowColor;
  ctx.fillStyle   = color;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   15. END GAME / RESULTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function endGame(mode, modeScore) {
  sfx_win();
  STATE.currentMode = mode;

  const titles = {
    compound: "⚗️ Forge Complete!",
    hunt:     "🔍 Hunt Complete!",
    sort:     "🧲 Sorted!",
    atom:     "⚛️ Atom Mastered!",
  };
  document.getElementById("results-title").textContent = titles[mode] || "Complete!";
  document.getElementById("results-score").textContent = modeScore;
  document.getElementById("results-breakdown").innerHTML =
    `<p>Total Adventure Score: <b style="color:var(--neon)">${STATE.totalScore}</b></p>`;

  showScreen("screen-results");
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   16. UTILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   17. WIRING – EVENT LISTENERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
document.addEventListener("DOMContentLoaded", () => {

  /* ── Landing → Hub ── */
  document.getElementById("btn-start").addEventListener("click", () => {
    sfx_level();
    const name = document.getElementById("player-name").value.trim();
    STATE.playerName = name || "Scientist";
    STATE.totalScore = 0;
    STATE.lives      = 3;
    updateHUD();
    showScreen("screen-hub");
  });

  /* ── Hub → Game ── */
  document.querySelectorAll(".btn-mission").forEach(btn => {
    btn.addEventListener("click", () => {
      sfx_click();
      const mode = btn.closest(".mission-card").dataset.mode;
      launchMode(mode);
    });
  });

  /* ── Back Buttons ── */
  ["compound","hunt","sort","atom"].forEach(mode => {
    const btn = document.getElementById(`back-${mode}`);
    if (btn) btn.addEventListener("click", () => {
      sfx_click();
      cleanupMode(mode);
      showScreen("screen-hub");
    });
  });

  /* ── Compound Forge ── */
  document.getElementById("btn-combine").addEventListener("click", () => {
    sfx_click();
    forgeSynthesise();
  });
  document.getElementById("btn-clear-forge").addEventListener("click", () => {
    sfx_click();
    forgeClearContents();
  });
  initForgeDropZone();

  /* ── Atom Builder ── */
  document.getElementById("btn-p-add").addEventListener("click", () => atomAdjust("p",  1));
  document.getElementById("btn-p-rem").addEventListener("click", () => atomAdjust("p", -1));
  document.getElementById("btn-n-add").addEventListener("click", () => atomAdjust("n",  1));
  document.getElementById("btn-n-rem").addEventListener("click", () => atomAdjust("n", -1));
  document.getElementById("btn-e-add").addEventListener("click", () => atomAdjust("e",  1));
  document.getElementById("btn-e-rem").addEventListener("click", () => atomAdjust("e", -1));
  document.getElementById("btn-check-atom").addEventListener("click", () => atomCheck());

  /* ── Sound Toggle ── */
  document.getElementById("btn-sound").addEventListener("click", () => {
    soundEnabled = !soundEnabled;
    document.getElementById("btn-sound").textContent = soundEnabled ? "🔊" : "🔇";
    sfx_click();
  });

  /* ── Results ── */
  document.getElementById("btn-play-again").addEventListener("click", () => {
    sfx_click();
    launchMode(STATE.currentMode);
  });
  document.getElementById("btn-hub-from-results").addEventListener("click", () => {
    sfx_click();
    showScreen("screen-hub");
  });
});

/* ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   18. MODE LAUNCH & CLEANUP
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ */
function launchMode(mode) {
  STATE.currentMode = mode;
  switch (mode) {
    case "compound":
      forgeInit();
      showScreen("screen-compound");
      break;
    case "hunt":
      huntInit();
      showScreen("screen-hunt");
      break;
    case "sort":
      sortInit();
      showScreen("screen-sort");
      break;
    case "atom":
      atomInit();
      showScreen("screen-atom");
      break;
  }
}

function cleanupMode(mode) {
  if (mode === "compound") clearInterval(FORGE.timerInt);
  if (mode === "hunt")     clearInterval(HUNT.timerInt);
  if (mode === "atom")     cancelAnimationFrame(ATOM_STATE.animFrame);
}
