// Commit City — a night-time New York built from a GitHub contribution graph.
// One building per day (height = commits), parks on empty days, weekdays are
// avenues, months are cross streets, the weekend lives across the river.
// Rendered to frames by scripts/render.py, assembled into an animated image.

import * as THREE from 'three';
import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js';
import { mergeGeometries } from 'three/addons/utils/BufferGeometryUtils.js';

// ---------- knobs ----------
const LOT = 10, AV = 8, ST = 7, FLOOR = 3.2, RIVER = 36, DEPTH = 9;
const ROAD_AV = 5.2, ROAD_ST = 4.6;
const LOOP = 12;                      // seconds per loop
const ORDER = [1, 2, 3, 4, 5, 6, 0];  // Mon..Sun as display rows (GitHub day index)
const DAYN = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN'];
const q = new URLSearchParams(location.search);
const WIDTH = +q.get('w') || 1248, HEIGHT = +q.get('h') || 648;

// ---------- deterministic randomness ----------
let seed = 20261029;
const rnd = () => { seed = (seed + 0x6D2B79F5) | 0; let t = Math.imul(seed ^ (seed >>> 15), 1 | seed); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
const pick = a => a[Math.floor(rnd() * a.length)];
const lerp = (a, b, t) => a + (b - a) * t;

// ---------- renderer ----------
const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(1);
renderer.setSize(WIDTH, HEIGHT);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
scene.background = new THREE.Color(0x070a12);
scene.fog = new THREE.FogExp2(0x0b1020, 0.00085);
const camera = new THREE.PerspectiveCamera(40, WIDTH / HEIGHT, 1, 4000);

// ---------- shared textures / materials ----------
function radialTexture(inner, outer) {
  const c = document.createElement('canvas'); c.width = c.height = 128;
  const g = c.getContext('2d');
  const grad = g.createRadialGradient(64, 64, 2, 64, 64, 64);
  grad.addColorStop(0, inner); grad.addColorStop(1, outer);
  g.fillStyle = grad; g.fillRect(0, 0, 128, 128);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const poolTex = radialTexture('rgba(255,214,150,0.9)', 'rgba(255,214,150,0)');
const beamTex = (() => {
  const c = document.createElement('canvas'); c.width = 128; c.height = 64;
  const g = c.getContext('2d');
  const grad = g.createLinearGradient(0, 0, 128, 0);
  grad.addColorStop(0, 'rgba(255,245,210,0.75)'); grad.addColorStop(1, 'rgba(255,245,210,0)');
  g.fillStyle = grad; g.beginPath(); g.moveTo(0, 22); g.lineTo(128, 0); g.lineTo(128, 64); g.lineTo(0, 42); g.closePath(); g.fill();
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
})();
const poolMat = new THREE.MeshBasicMaterial({ map: poolTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.22 });
const beamMat = new THREE.MeshBasicMaterial({ map: beamTex, transparent: true, blending: THREE.AdditiveBlending, depthWrite: false, opacity: 0.5 });
const poleMat = new THREE.MeshStandardMaterial({ color: 0x3c4149, roughness: 0.7, metalness: 0.4 });
const lampMat = new THREE.MeshStandardMaterial({ color: 0xffe2b0, emissive: 0xffc77a, emissiveIntensity: 2.4 });
const darkMetal = new THREE.MeshStandardMaterial({ color: 0x2a2d33, roughness: 0.6, metalness: 0.5 });
const hvacMat = new THREE.MeshStandardMaterial({ color: 0x8e949c, roughness: 0.8, metalness: 0.3 });
const hvacDark = new THREE.MeshStandardMaterial({ color: 0x5e636b, roughness: 0.8, metalness: 0.3 });
const woodMat = new THREE.MeshStandardMaterial({ color: 0x6b4a2e, roughness: 0.95 });
const woodDark = new THREE.MeshStandardMaterial({ color: 0x4a3220, roughness: 0.95 });
const tarMat = new THREE.MeshStandardMaterial({ color: 0x303238, roughness: 1 });
const redLight = new THREE.MeshStandardMaterial({ color: 0xff2a2a, emissive: 0xff1f1f, emissiveIntensity: 3 });
const beaconMat = redLight.clone();
const whiteLight = new THREE.MeshStandardMaterial({ color: 0xffffff, emissive: 0xfff4d6, emissiveIntensity: 4 });
const amberLight = new THREE.MeshStandardMaterial({ color: 0xffc14d, emissive: 0xffb02e, emissiveIntensity: 2.5 });
const greenLight = new THREE.MeshStandardMaterial({ color: 0x5bff7a, emissive: 0x2dff5a, emissiveIntensity: 2.5 });
const trunkMat = new THREE.MeshStandardMaterial({ color: 0x4a3524, roughness: 1 });
const canopyMats = [0x2f6b3a, 0x3b7f45, 0x27592f, 0x4d8a3f].map(c => new THREE.MeshStandardMaterial({ color: c, roughness: 0.95 }));
const grassMat = new THREE.MeshStandardMaterial({ color: 0x25452b, roughness: 1 });
const waterMat = new THREE.MeshPhongMaterial({ color: 0x08162a, emissive: 0x030a14, specular: 0x24416a, shininess: 22, transparent: true, opacity: 0.72 });
const stoneMat = new THREE.MeshStandardMaterial({ color: 0x6f6a62, roughness: 0.9 });
const cableMat = new THREE.MeshStandardMaterial({ color: 0x9aa3ad, roughness: 0.5, metalness: 0.6 });
const bulbMat = new THREE.MeshStandardMaterial({ color: 0xfff1c4, emissive: 0xffd48a, emissiveIntensity: 3 });
const taxiSign = new THREE.MeshStandardMaterial({ color: 0xfff6c8, emissive: 0xfff0b0, emissiveIntensity: 2 });

const unitBox = new THREE.BoxGeometry(1, 1, 1);
const box = (w, h, d, mat, x, y, z, parent) => { const m = new THREE.Mesh(unitBox, mat); m.scale.set(w, h, d); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; (parent || scene).add(m); return m; };

// ---------- facade textures ----------
const WALL = {
  brick: ['#5a3326', '#63402c', '#4e2f22', '#704a30', '#5c3a2e', '#4a342c'],
  stone: ['#8f8672', '#847a66', '#9a8e78', '#7a7264', '#8d7f6a'],
  concrete: ['#6a6f78', '#5f646c', '#767a82', '#565a62'],
  glass: ['#1a2436', '#14202f', '#1f2a3d', '#102033', '#1a2a2e']
};
function facadeTexture(type, cols, floors, litP, opts) {
  const CW = 14, CH = 20;
  const mk = () => { const c = document.createElement('canvas'); c.width = cols * CW; c.height = floors * CH; return [c, c.getContext('2d')]; };
  const [ca, g] = mk(), [ce, e] = mk();
  const wall = opts.wall;
  g.fillStyle = wall; g.fillRect(0, 0, ca.width, ca.height);
  e.fillStyle = '#000000'; e.fillRect(0, 0, ce.width, ce.height);
  if (type === 'brick') {
    for (let y = 0; y < ca.height; y += 3) for (let x = -3; x < ca.width; x += 6) {
      const o = (y / 3) % 2 ? 3 : 0;
      g.fillStyle = `rgba(0,0,0,${0.06 + rnd() * 0.14})`; g.fillRect(x + o, y, 5, 2);
      if (rnd() < 0.08) { g.fillStyle = 'rgba(255,255,255,0.05)'; g.fillRect(x + o, y, 5, 2); }
    }
  } else if (type === 'stone' || type === 'concrete') {
    for (let y = 0; y < ca.height; y += 5) { g.fillStyle = 'rgba(0,0,0,0.10)'; g.fillRect(0, y, ca.width, 1); }
    for (let i = 0; i < ca.width * ca.height / 60; i++) { g.fillStyle = `rgba(0,0,0,${rnd() * 0.1})`; g.fillRect(rnd() * ca.width, rnd() * ca.height, 2, 2); }
    for (let x = 0; x < ca.width; x += CW * 2) { g.fillStyle = 'rgba(0,0,0,0.12)'; g.fillRect(x, 0, 1, ca.height); }
  } else if (type === 'glass') {
    g.fillStyle = wall; g.fillRect(0, 0, ca.width, ca.height);
  }
  const warm = ['#ffd27a', '#ffc766', '#ffe0a3', '#ffb85c', '#ffcf8a'];
  const cool = ['#cfe0ff', '#dfe9ff', '#b9d3ff'];
  const dimC = ['#6b5a3a', '#5a4e40', '#5c5340'];
  for (let f = 0; f < floors; f++) {
    const y0 = ca.height - (f + 1) * CH;
    const floorLit = type === 'glass' ? (rnd() < litP ? 1 : 0) : 1;
    // floor line / spandrel
    if (type === 'glass') { g.fillStyle = 'rgba(0,0,0,0.55)'; g.fillRect(0, y0 + CH - 4, ca.width, 4); g.fillStyle = 'rgba(255,255,255,0.06)'; g.fillRect(0, y0 + CH - 5, ca.width, 1); }
    else { g.fillStyle = 'rgba(0,0,0,0.18)'; g.fillRect(0, y0 + CH - 1, ca.width, 1); }
    for (let k = 0; k < cols; k++) {
      const x0 = k * CW;
      if (f === 0 && opts.storefront) {
        g.fillStyle = opts.awning; g.fillRect(x0, y0 + 2, CW, 4);
        g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(x0, y0 + 6, CW, 1);
        const lit = rnd() < 0.85;
        const col = lit ? (rnd() < 0.8 ? pick(warm) : pick(cool)) : '#1a1d24';
        g.fillStyle = '#15161a'; g.fillRect(x0 + 1, y0 + 7, CW - 2, CH - 8);
        g.fillStyle = col; g.fillRect(x0 + 2, y0 + 8, CW - 4, CH - 10);
        if (lit) { e.fillStyle = col; e.fillRect(x0 + 2, y0 + 8, CW - 4, CH - 10); }
        if (k === Math.floor(cols / 2)) { g.fillStyle = '#1c1a18'; g.fillRect(x0 + 5, y0 + 10, 5, CH - 10); e.fillStyle = '#000'; e.fillRect(x0 + 5, y0 + 10, 5, CH - 10); }
        continue;
      }
      let lit;
      if (type === 'glass') lit = floorLit ? (rnd() < 0.85 ? 1 : 0.25) : (rnd() < 0.07 ? 1 : 0);
      else lit = rnd() < litP ? 1 : (rnd() < 0.18 ? 0.3 : 0);
      const wx = type === 'glass' ? x0 + 1 : x0 + 4, wy = type === 'glass' ? y0 + 1 : y0 + 5;
      const ww = type === 'glass' ? CW - 2 : 6, wh = type === 'glass' ? CH - 6 : 10;
      // lintel / sill
      if (type !== 'glass') { g.fillStyle = 'rgba(0,0,0,0.35)'; g.fillRect(wx - 1, wy - 2, ww + 2, 1); g.fillStyle = 'rgba(255,255,255,0.14)'; g.fillRect(wx - 1, wy + wh + 1, ww + 2, 1); }
      g.fillStyle = type === 'glass' ? '#0d1119' : '#111317'; g.fillRect(wx - 1, wy - 1, ww + 2, wh + 2);
      let col;
      if (lit === 1) col = rnd() < 0.78 ? pick(warm) : pick(cool);
      else if (lit > 0) col = pick(dimC);
      else col = type === 'glass' ? '#121b28' : '#0d121a';
      g.fillStyle = col; g.fillRect(wx, wy, ww, wh);
      if (lit > 0) { e.fillStyle = col; e.fillRect(wx, wy, ww, wh); }
      if (lit === 1 && type !== 'glass' && rnd() < 0.4) { const sh = Math.floor(wh * (0.3 + rnd() * 0.45)); g.fillStyle = 'rgba(35,28,22,0.8)'; g.fillRect(wx, wy, ww, sh); e.fillStyle = 'rgba(0,0,0,0.75)'; e.fillRect(wx, wy, ww, sh); }
      if (type !== 'glass') { g.fillStyle = 'rgba(0,0,0,0.55)'; g.fillRect(wx + 3, wy, 1, wh); g.fillRect(wx, wy + 4, ww, 1); e.fillStyle = 'rgba(0,0,0,0.5)'; e.fillRect(wx + 3, wy, 1, wh); e.fillRect(wx, wy + 4, ww, 1); }
      else { g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(x0 + CW / 2, wy, 1, wh); e.fillStyle = 'rgba(0,0,0,0.5)'; e.fillRect(x0 + CW / 2, wy, 1, wh); if (lit === 0 && rnd() < 0.5) { g.fillStyle = 'rgba(120,150,200,0.12)'; g.fillRect(wx, wy, ww, Math.floor(wh * 0.4)); } }
    }
  }
  if (opts.cornice) { g.fillStyle = 'rgba(0,0,0,0.5)'; g.fillRect(0, 0, ca.width, 4); g.fillStyle = 'rgba(255,255,255,0.12)'; g.fillRect(0, 4, ca.width, 2); g.fillStyle = 'rgba(0,0,0,0.25)'; g.fillRect(0, 6, ca.width, 1); }
  const tex = t => { const x = new THREE.CanvasTexture(t); x.colorSpace = THREE.SRGBColorSpace; x.minFilter = THREE.LinearMipmapLinearFilter; x.anisotropy = 4; return x; };
  return { map: tex(ca), emissive: tex(ce) };
}
function facadeMaterial(t, type) {
  const glass = type === 'glass';
  return new THREE.MeshStandardMaterial({ map: t.map, emissiveMap: t.emissive, emissive: 0xffffff, emissiveIntensity: glass ? 1.0 : 1.15, roughness: glass ? 0.3 : 0.9, metalness: glass ? 0.35 : 0.0 });
}

// ---------- layout helpers ----------
let DATA, W, D, weekX, rowZ, boundaries, bridges;
function layout(data) {
  const starts = data.months.filter(m => m.w > 0).map(m => m.w);
  boundaries = starts;
  weekX = w => ST + w * LOT + starts.filter(s => s <= w).length * ST;
  W = weekX(52) + LOT + ST;
  rowZ = i => AV + i * (LOT + AV) + (i >= 5 ? RIVER : 0);
  D = rowZ(6) + LOT + AV;
  bridges = starts.filter((s, i) => i % 2 === 1);
}
const riverZ0 = () => rowZ(4) + LOT + AV, riverZ1 = () => rowZ(5) - AV;

// ---------- ground ----------
function buildGround(data) {
  const SX = 4096 / W, SZ = 1024 / D;
  const c = document.createElement('canvas'); c.width = 4096; c.height = 1024;
  const g = c.getContext('2d');
  const R = (x, z, w, d, col) => { g.fillStyle = col; g.fillRect(x * SX, z * SZ, w * SX, d * SZ); };
  R(0, 0, W, D, '#1b1d23');
  // sidewalks around every block
  const blockEdges = [];
  let bx = ST;
  for (let w = 0; w < 53; w++) {
    const x = weekX(w);
    if (w === 0) bx = x;
    const next = w < 52 ? weekX(w + 1) : null;
    if (next === null || next - x > LOT) { blockEdges.push([bx, x + LOT]); bx = next; }
  }
  for (let i = 0; i < 7; i++) {
    const z = rowZ(i);
    blockEdges.forEach(([x0, x1]) => R(x0 - 1.2, z - 1.4, x1 - x0 + 2.4, LOT + 2.8, '#3a3d45'));
  }
  // river
  R(0, riverZ0(), W, riverZ1() - riverZ0(), '#0b1a33');
  R(0, riverZ0(), W, 1.2, '#5e5a52'); R(0, riverZ1() - 1.2, W, 1.2, '#5e5a52');
  for (let i = 0; i < 260; i++) { g.fillStyle = `rgba(120,160,220,${0.04 + rnd() * 0.08})`; g.fillRect(rnd() * W * SX, (riverZ0() + 2 + rnd() * (RIVER - 4)) * SZ, (6 + rnd() * 30) * SX, 0.4 * SZ); }
  // parks
  for (let w = 0; w < 53; w++) for (let i = 0; i < 7; i++) {
    const cell = data.weeks[w][ORDER[i]];
    if (cell.count === 0) {
      R(weekX(w), rowZ(i), LOT, LOT, '#23402a');
      g.fillStyle = '#b9ab8d'; g.fillRect((weekX(w) + 4.2) * SX, rowZ(i) * SZ, 1.6 * SX, LOT * SZ);
    }
  }
  // lane markings: avenues (yellow dashes)
  const avCenters = [AV / 2];
  for (let i = 0; i < 7; i++) avCenters.push(rowZ(i) + LOT + AV / 2);
  avCenters.forEach(zc => { for (let x = 0; x < W; x += 4.5) R(x, zc - 0.14, 2.4, 0.28, '#c9a94a'); });
  // cross streets (white dashes), including the two edge streets
  const stCenters = [ST / 2, W - ST / 2].concat(boundaries.map(s => weekX(s) - ST / 2));
  stCenters.forEach(xc => { for (let z = 0; z < D; z += 4.5) R(xc - 0.12, z, 0.24, 2.4, '#d8d8d8'); });
  // crosswalks
  stCenters.forEach(xc => avCenters.forEach(zc => {
    for (let k = -2; k <= 2; k++) { R(xc - ROAD_ST / 2 - 1.3, zc + k * 1.05 - 0.3, 1.0, 0.6, '#e8e8e8'); R(xc + ROAD_ST / 2 + 0.3, zc + k * 1.05 - 0.3, 1.0, 0.6, '#e8e8e8'); }
    for (let k = -2; k <= 2; k++) { R(xc + k * 1.05 - 0.3, zc - ROAD_AV / 2 - 1.3, 0.6, 1.0, '#e8e8e8'); R(xc + k * 1.05 - 0.3, zc + ROAD_AV / 2 + 0.3, 0.6, 1.0, '#e8e8e8'); }
  }));
  // manholes and grime
  for (let i = 0; i < 90; i++) { const zc = pick(avCenters) + (rnd() - 0.5) * 3; const x = rnd() * W; g.fillStyle = '#121419'; g.beginPath(); g.arc(x * SX, zc * SZ, 0.55 * SX, 0, 6.3); g.fill(); }
  for (let i = 0; i < 400; i++) { g.fillStyle = `rgba(0,0,0,${rnd() * 0.25})`; g.fillRect(rnd() * 4096, rnd() * 1024, 6 + rnd() * 40, 2 + rnd() * 6); }
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 8;
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(W, D), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.95 }));
  ground.rotation.x = -Math.PI / 2; ground.position.set(W / 2, 0, D / 2); ground.receiveShadow = true;
  scene.add(ground);
  // outskirts
  const far = new THREE.Mesh(new THREE.PlaneGeometry(6000, 6000), new THREE.MeshStandardMaterial({ color: 0x0d0f15, roughness: 1 }));
  far.rotation.x = -Math.PI / 2; far.position.set(W / 2, -0.05, D / 2); scene.add(far);
  // water as its own glossy plane so the moon catches it
  const water = new THREE.Mesh(new THREE.PlaneGeometry(W + 400, riverZ1() - riverZ0() - 2.2), waterMat);
  water.rotation.x = -Math.PI / 2; water.position.set(W / 2, 0.06, (riverZ0() + riverZ1()) / 2); scene.add(water);
}

// ---------- buildings ----------
const beacons = [];
function waterTower(x, y, z, parent) {
  const g = new THREE.Group();
  const legs = new THREE.Mesh(mergeGeometries([0, 1, 2, 3].map(i => { const b = new THREE.BoxGeometry(0.18, 2.2, 0.18); b.translate(i < 2 ? -0.8 : 0.8, 1.1, i % 2 ? -0.8 : 0.8); return b; })), woodDark);
  g.add(legs);
  const tank = new THREE.Mesh(new THREE.CylinderGeometry(1.15, 1.25, 2.4, 14), woodMat); tank.position.y = 3.4; g.add(tank);
  const cap = new THREE.Mesh(new THREE.ConeGeometry(1.35, 0.9, 14), woodDark); cap.position.y = 5.05; g.add(cap);
  const hoop = new THREE.Mesh(new THREE.TorusGeometry(1.22, 0.05, 6, 16), darkMetal); hoop.rotation.x = Math.PI / 2; hoop.position.y = 3.0; g.add(hoop);
  g.position.set(x, y, z); g.traverse(m => { m.castShadow = true; }); parent.add(g);
}
function hvac(x, y, z, parent, big) {
  const w = big ? 2.4 : 1.5, d = big ? 1.4 : 1.0, h = big ? 1.4 : 1.0;
  box(w, h, d, hvacMat, x, y + h / 2, z, parent);
  box(w * 0.8, 0.08, d * 0.8, hvacDark, x, y + h + 0.04, z, parent);
  for (let i = 0; i < 3; i++) box(w * 0.9, 0.06, 0.06, hvacDark, x, y + h * (0.3 + i * 0.22), z + d / 2 + 0.01, parent);
}
function parapet(x, y, z, w, d, parent, h, t) {
  const hh = h || 0.5, tt = t || 0.35, mat = tarMat;
  box(w, hh, tt, mat, x, y + hh / 2, z - d / 2 + tt / 2, parent);
  box(w, hh, tt, mat, x, y + hh / 2, z + d / 2 - tt / 2, parent);
  box(tt, hh, d, mat, x - w / 2 + tt / 2, y + hh / 2, z, parent);
  box(tt, hh, d, mat, x + w / 2 - tt / 2, y + hh / 2, z, parent);
}
function tier(cx, cz, w, h, d, yBase, type, opts, parent) {
  const floors = Math.max(1, Math.round(h / FLOOR));
  const colsF = Math.max(2, Math.round(w / 1.45)), colsS = Math.max(2, Math.round(d / 1.45));
  const texF = facadeTexture(type, colsF, floors, opts.litP, opts);
  const texS = facadeTexture(type, colsS, floors, opts.litP, Object.assign({}, opts, { storefront: false }));
  const mF = facadeMaterial(texF, type), mS = facadeMaterial(texS, type);
  const roofMat = type === 'glass' ? new THREE.MeshStandardMaterial({ color: 0x2b3038, roughness: 0.7, metalness: 0.3 }) : tarMat;
  const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), [mS, mS, roofMat, tarMat, mF, mF]);
  mesh.position.set(cx, yBase + h / 2, cz); mesh.castShadow = true; mesh.receiveShadow = true; parent.add(mesh);
  return mesh;
}
function fireEscape(cx, cz, w, h, d, parent) {
  const floors = Math.round(h / FLOOR);
  const z = cz + d / 2 + 0.35;
  const fw = Math.min(4.5, w * 0.5);
  for (let f = 1; f < floors; f++) {
    const y = f * FLOOR + 0.1;
    box(fw, 0.1, 0.7, darkMetal, cx, y, z, parent);
    box(fw, 0.06, 0.06, darkMetal, cx, y + 0.9, z + 0.33, parent);
    box(0.06, 0.9, 0.06, darkMetal, cx - fw / 2, y + 0.45, z + 0.33, parent);
    box(0.06, 0.9, 0.06, darkMetal, cx + fw / 2, y + 0.45, z + 0.33, parent);
    const stair = box(0.12, FLOOR * 1.05, 0.5, darkMetal, cx + (f % 2 ? 1 : -1) * fw * 0.3, y - FLOOR / 2 + 0.1, z, parent);
    stair.rotation.z = (f % 2 ? 1 : -1) * 0.5;
  }
}
function building(x, z, count, rank, nTotal) {
  const g = new THREE.Group();
  const floors = Math.min(64, Math.max(2, Math.round(count * 1.45)));
  let type = count <= 4 ? 'brick' : count <= 11 ? (rnd() < 0.6 ? 'stone' : 'concrete') : (rnd() < 0.8 ? 'glass' : 'concrete');
  const landmark = rank < 2;
  const litP = count <= 4 ? 0.26 : count <= 11 ? 0.32 : 0.5;
  const opts = { wall: pick(WALL[type]), litP, storefront: type !== 'glass' && rnd() < 0.75, awning: pick(['#8b2d2d', '#2d5a8b', '#2f7a4a', '#7a2f7a', '#b06d1a']), cornice: type === 'brick' || type === 'stone' };
  const cx0 = x + LOT / 2, cz = z + DEPTH / 2 + 0.5;
  const gap = pick([0, 0, 0, 0.8, 1.4, 2.0]);
  let w = LOT - gap, d = DEPTH - pick([0, 0, 0.6, 1.2]), H = floors * FLOOR, top, tw = w, td = d;
  if (type === 'glass') { w = Math.min(w, LOT - 1); d = Math.min(d, DEPTH - 0.6); }
  const align = pick([-1, 0, 1]);
  const cx = cx0 + align * (LOT - w) / 2;
  if (landmark) {
    const h1 = H * 0.5, h2 = H * 0.3, h3 = H * 0.2;
    tier(cx, cz, w, h1, d, 0, type, opts, g);
    tier(cx, cz, w * 0.72, h2, d * 0.72, h1, type, opts, g);
    tier(cx, cz, w * 0.46, h3, d * 0.46, h1 + h2, type, opts, g);
    top = H; tw = w * 0.46; td = d * 0.46;
    parapet(cx, h1, cz, w, d, g, 0.6, 0.4); parapet(cx, h1 + h2, cz, w * 0.72, d * 0.72, g, 0.5, 0.35);
    const spire = new THREE.Mesh(new THREE.ConeGeometry(0.9, 14, 8), cableMat); spire.position.set(cx, H + 7, cz); g.add(spire);
    const b = new THREE.Mesh(new THREE.SphereGeometry(0.3, 8, 8), beaconMat); b.position.set(cx, H + 14.2, cz); g.add(b); beacons.push(b);
    for (let k = 0; k < 6; k++) { const s = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 6), bulbMat); s.position.set(cx, H + 1 + k * 2.1, cz); g.add(s); }
  } else if (type === 'glass' && floors > 18 && rnd() < 0.5) {
    const h1 = H * 0.72;
    tier(cx, cz, w, h1, d, 0, type, opts, g);
    tier(cx, cz, w * 0.78, H - h1, d * 0.78, h1, type, opts, g);
    top = H; tw = w * 0.78; td = d * 0.78;
    parapet(cx, h1, cz, w, d, g, 0.5, 0.3);
  } else if ((type === 'stone' || type === 'concrete') && floors > 8) {
    const h1 = H * 0.66;
    tier(cx, cz, w, h1, d, 0, type, opts, g);
    tier(cx, cz, w * 0.7, H - h1, d * 0.7, h1, type, opts, g);
    top = H; tw = w * 0.7; td = d * 0.7;
    parapet(cx, h1, cz, w, d, g, 0.6, 0.35);
    if (rnd() < 0.7) waterTower(cx + w * 0.3, h1, cz - d * 0.25, g);
  } else {
    tier(cx, cz, w, H, d, 0, type, opts, g);
    top = H;
  }
  // roof furniture on the top tier
  parapet(cx, top, cz, tw, td, g, type === 'glass' ? 0.35 : 0.55, 0.3);
  if (type === 'brick') {
    if (rnd() < 0.65) waterTower(cx + (rnd() - 0.5) * tw * 0.4, top, cz + (rnd() - 0.5) * td * 0.4, g);
    if (rnd() < 0.6) hvac(cx - tw * 0.3, top, cz + td * 0.2, g, false);
    box(2.2, 2.1, 1.9, new THREE.MeshStandardMaterial({ color: opts.wall, roughness: 0.9 }), cx - tw * 0.28, top + 1.05, cz - td * 0.25, g);
    if (rnd() < 0.8) fireEscape(cx, cz, w, H, d, g);
    if (rnd() < 0.22 && floors >= 3) neonSign(cx, cz, w, d, H, g);
  } else if (type === 'stone' || type === 'concrete') {
    box(2.6, 2.4, 2.2, new THREE.MeshStandardMaterial({ color: opts.wall, roughness: 0.9 }), cx + tw * 0.2, top + 1.2, cz - td * 0.2, g);
    hvac(cx - tw * 0.25, top, cz + td * 0.22, g, true);
    if (rnd() < 0.5) hvac(cx + tw * 0.28, top, cz + td * 0.25, g, false);
    if (!landmark && rnd() < 0.45) waterTower(cx - tw * 0.28, top, cz - td * 0.25, g);
    if (rnd() < 0.15) neonSign(cx, cz, w, d, H, g);
    if (billboardsLeft > 0 && floors >= 8 && floors <= 14 && rnd() < 0.5) { billboardsLeft--; billboard(cx, cz, tw, td, top, g, [DATA.login || 'commit city', 'COMMIT CITY', String(DATA.total || '') + ' COMMITS'][billboardsLeft]); }
  } else if (type === 'glass') {
    box(tw * 0.5, 2.2, td * 0.5, darkMetal, cx, top + 1.1, cz, g);
    hvac(cx - tw * 0.3, top, cz + td * 0.3, g, true);
    if (rnd() < 0.6) hvac(cx + tw * 0.3, top, cz - td * 0.3, g, false);
    if (!landmark && rnd() < 0.55) {
      const ant = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.14, 7, 6), cableMat); ant.position.set(cx + tw * 0.2, top + 2.2 + 3.5, cz - td * 0.2); g.add(ant);
      const b = new THREE.Mesh(new THREE.SphereGeometry(0.3, 6, 6), beaconMat); b.position.set(cx + tw * 0.2, top + 2.2 + 7.1, cz - td * 0.2); g.add(b); beacons.push(b);
    }
  }
  scene.add(g);
}

// ---------- signs ----------
function textTexture(text, pw, ph, color, vertical) {
  const c = document.createElement('canvas'); c.width = pw; c.height = ph;
  const g = c.getContext('2d');
  g.fillStyle = '#0c0c10'; g.fillRect(0, 0, pw, ph);
  g.fillStyle = color; g.textAlign = 'center'; g.textBaseline = 'middle';
  if (vertical) {
    const n = text.length, cell = ph / n;
    g.font = `bold ${Math.floor(cell * 0.78)}px Arial Black, Arial, sans-serif`;
    for (let i = 0; i < n; i++) g.fillText(text[i], pw / 2, cell * (i + 0.5));
  } else {
    let size = Math.floor(ph * 0.62);
    g.font = `bold ${size}px Arial Black, Arial, sans-serif`;
    while (g.measureText(text).width > pw * 0.88 && size > 12) { size -= 2; g.font = `bold ${size}px Arial Black, Arial, sans-serif`; }
    g.fillText(text, pw / 2, ph / 2 + 2);
  }
  g.strokeStyle = color; g.lineWidth = 3; g.strokeRect(3, 3, pw - 6, ph - 6);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t;
}
const NEON = ['HOTEL', 'DINER', 'BAR', 'JAZZ', 'PIZZA', 'LIVE', 'DELI', 'CAFE', 'RADIO', 'MOTEL', 'BOOKS', 'NOODLE'];
const NEONC = ['#ff3b6b', '#36f0ff', '#ffd23f', '#7cff5a', '#ff8a3b', '#c56bff'];
function neonSign(cx, cz, w, d, H, parent) {
  const word = pick(NEON), col = pick(NEONC);
  const h = Math.min(H - 4, word.length * 1.25), wdt = 1.3;
  const tex = textTexture(word, 64, 64 * word.length, col, true);
  const mat = new THREE.MeshStandardMaterial({ map: tex, emissiveMap: tex, emissive: 0xffffff, emissiveIntensity: 1.6, side: THREE.DoubleSide, roughness: 0.6 });
  const m = new THREE.Mesh(new THREE.PlaneGeometry(wdt, h), mat);
  m.position.set(cx + w / 2 - 0.9, 3.5 + h / 2, cz + d / 2 + 0.75); m.rotation.y = Math.PI / 2; parent.add(m);
  box(0.12, 0.12, 1.3, darkMetal, cx + w / 2 - 0.9, 3.5 + h - 0.3, cz + d / 2 + 0.1, parent);
  box(0.12, 0.12, 1.3, darkMetal, cx + w / 2 - 0.9, 3.8, cz + d / 2 + 0.1, parent);
}
let billboardsLeft = 3;
function billboard(cx, cz, w, d, top, parent, text) {
  const tex = textTexture(text, 512, 192, pick(['#ffd23f', '#36f0ff', '#ff6b9a']), false);
  const mat = new THREE.MeshStandardMaterial({ map: tex, emissiveMap: tex, emissive: 0xffffff, emissiveIntensity: 1.5, roughness: 0.6 });
  const bw = Math.min(w, 8.5), bh = bw * 0.375;
  const m = new THREE.Mesh(new THREE.PlaneGeometry(bw, bh), mat);
  m.position.set(cx, top + 2.2 + bh / 2, cz + d / 2 - 0.4); parent.add(m);
  [-bw * 0.35, bw * 0.35].forEach(dx => box(0.16, 2.3, 0.16, darkMetal, cx + dx, top + 1.15, cz + d / 2 - 0.5, parent));
  box(bw + 0.4, 0.2, 0.2, darkMetal, cx, top + 2.2 + bh + 0.1, cz + d / 2 - 0.4, parent);
  [-bw * 0.3, bw * 0.3].forEach(dx => box(0.4, 0.2, 0.3, lampMat, cx + dx, top + 2.2 + bh + 0.3, cz + d / 2 + 0.2, parent));
}

// ---------- parks, lamps, lights ----------
function park(x, z) {
  const g = new THREE.Group();
  const n = 2 + Math.floor(rnd() * 2);
  for (let i = 0; i < n; i++) {
    const tx = x + 1.8 + rnd() * (LOT - 3.6), tz = z + 1.8 + rnd() * (LOT - 3.6);
    if (Math.abs(tx - (x + 5)) < 1.4) continue;
    const r = 1.4 + rnd() * 1.1;
    const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.3, 2.2, 6), trunkMat); trunk.position.set(tx, 1.1, tz); trunk.castShadow = true; g.add(trunk);
    const can = new THREE.Mesh(new THREE.SphereGeometry(r, 9, 7), pick(canopyMats)); can.position.set(tx, 2.2 + r * 0.8, tz); can.scale.y = 0.85; can.castShadow = true; g.add(can);
  }
  // a bench and a park lamp
  box(1.6, 0.1, 0.5, woodMat, x + 7.2, 0.55, z + 2.2, g); box(1.6, 0.5, 0.08, woodMat, x + 7.2, 0.85, z + 2.0, g);
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 3.2, 6), poleMat); pole.position.set(x + 2.6, 1.6, z + 7.4); g.add(pole);
  const head = new THREE.Mesh(new THREE.SphereGeometry(0.35, 8, 8), lampMat); head.position.set(x + 2.6, 3.4, z + 7.4); g.add(head);
  const pool = new THREE.Mesh(new THREE.PlaneGeometry(6, 6), poolMat); pool.rotation.x = -Math.PI / 2; pool.position.set(x + 2.6, 0.08, z + 7.4); g.add(pool);
  scene.add(g);
}
function streetLamp(x, z, side) {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.1, 0.14, 5.6, 6), poleMat); pole.position.set(x, 2.8, z); g.add(pole);
  const arm = box(0.14, 0.14, 1.6, poleMat, x, 5.5, z + side * 0.8, g);
  const head = box(0.5, 0.22, 0.7, lampMat, x, 5.45, z + side * 1.6, g);
  const pool = new THREE.Mesh(new THREE.PlaneGeometry(9, 9), poolMat); pool.rotation.x = -Math.PI / 2; pool.position.set(x, 0.07, z + side * 2.4); g.add(pool);
  scene.add(g);
}
const signals = [];
function trafficLight(x, z, rot) {
  const g = new THREE.Group();
  const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.12, 4.4, 6), poleMat); pole.position.set(0, 2.2, 0); g.add(pole);
  box(0.16, 0.16, 2.6, poleMat, 0, 4.3, 1.3, g);
  box(0.5, 1.3, 0.5, darkMetal, 0, 3.9, 2.4, g);
  const r = new THREE.Mesh(new THREE.SphereGeometry(0.16, 6, 6), redLight.clone()); r.position.set(0, 4.35, 2.68); g.add(r);
  const a = new THREE.Mesh(new THREE.SphereGeometry(0.16, 6, 6), amberLight.clone()); a.position.set(0, 3.9, 2.68); g.add(a);
  const gr = new THREE.Mesh(new THREE.SphereGeometry(0.16, 6, 6), greenLight.clone()); gr.position.set(0, 3.45, 2.68); g.add(gr);
  g.position.set(x, 0, z); g.rotation.y = rot; scene.add(g);
  signals.push({ r, a, gr, phase: rnd() });
}

// ---------- bridges ----------
function bridge(xc) {
  const z0 = riverZ0(), z1 = riverZ1(), zm = (z0 + z1) / 2;
  const deckY = 3.2, towerH = 30;
  const g = new THREE.Group();
  box(7.5, 0.9, z1 - z0 + 16, new THREE.MeshStandardMaterial({ color: 0x3b3e46, roughness: 0.9 }), xc, deckY, zm, g);
  for (let z = z0 - 8; z <= z1 + 8; z += 2.6) { box(7.5, 0.08, 0.18, new THREE.MeshStandardMaterial({ color: 0x4a4d55 }), xc, deckY + 0.5, z, g); }
  [z0 + 2, z1 - 2].forEach(zt => {
    [-3.2, 3.2].forEach(dx => box(1.6, towerH, 1.6, stoneMat, xc + dx, towerH / 2, zt, g));
    box(8.2, 1.6, 1.8, stoneMat, xc, towerH - 0.8, zt, g);
    box(8.2, 1.2, 1.8, stoneMat, xc, towerH * 0.55, zt, g);
    const r1 = new THREE.Mesh(new THREE.SphereGeometry(0.2, 6, 6), beaconMat); r1.position.set(xc - 3.2, towerH + 0.4, zt); g.add(r1); beacons.push(r1);
    const r2 = new THREE.Mesh(new THREE.SphereGeometry(0.2, 6, 6), beaconMat); r2.position.set(xc + 3.2, towerH + 0.4, zt); g.add(r2); beacons.push(r2);
  });
  [-3.4, 3.4].forEach(dx => {
    const p0 = new THREE.Vector3(xc + dx, towerH, z0 + 2), p1 = new THREE.Vector3(xc + dx, deckY + 1.2, zm), p2 = new THREE.Vector3(xc + dx, towerH, z1 - 2);
    const curve = new THREE.QuadraticBezierCurve3(p0, new THREE.Vector3(xc + dx, deckY - 8, zm), p2);
    const tube = new THREE.Mesh(new THREE.TubeGeometry(curve, 24, 0.14, 6, false), cableMat); g.add(tube);
    const back0 = new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(p0, new THREE.Vector3(xc + dx, deckY, z0 - 14)), 1, 0.12, 6, false), cableMat); g.add(back0);
    const back1 = new THREE.Mesh(new THREE.TubeGeometry(new THREE.LineCurve3(p2, new THREE.Vector3(xc + dx, deckY, z1 + 14)), 1, 0.12, 6, false), cableMat); g.add(back1);
    for (let t = 0.04; t < 0.97; t += 0.045) {
      const p = curve.getPoint(t);
      box(0.06, p.y - deckY, 0.06, cableMat, p.x, (p.y + deckY) / 2, p.z, g);
      const bulb = new THREE.Mesh(new THREE.SphereGeometry(0.2, 6, 6), bulbMat); bulb.position.copy(p); g.add(bulb);
    }
  });
  for (let z = z0 - 6; z <= z1 + 6; z += 7) [-3.2, 3.2].forEach(dx => { const h = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 6), lampMat); h.position.set(xc + dx, deckY + 3.4, z); g.add(h); box(0.1, 3, 0.1, poleMat, xc + dx, deckY + 2, z, g); });
  scene.add(g);
}

// ---------- vehicles ----------
const cars = [], boats = [];
const carColors = [0xf2c230, 0xf2c230, 0xf2c230, 0xffffff, 0x111111, 0xbfc5cc, 0xb8262a, 0x2a4b8d, 0x3a3a3a, 0x8e9aa6];
function carMesh(color, taxi) {
  const g = new THREE.Group();
  const paint = new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.5 });
  box(4.2, 1.1, 1.9, paint, 0, 0.85, 0, g);
  box(2.2, 0.85, 1.7, new THREE.MeshStandardMaterial({ color: 0x1a2230, roughness: 0.2, metalness: 0.6 }), -0.2, 1.8, 0, g);
  const wheels = new THREE.Mesh(mergeGeometries([[1.3, 0.95], [-1.3, 0.95], [1.3, -0.95], [-1.3, -0.95]].map(p => { const c = new THREE.CylinderGeometry(0.42, 0.42, 0.35, 10); c.rotateX(Math.PI / 2); c.translate(p[0], 0.42, p[1]); return c; })), new THREE.MeshStandardMaterial({ color: 0x0f1013, roughness: 0.9 }));
  g.add(wheels);
  box(0.12, 0.3, 0.45, whiteLight, 2.1, 0.95, 0.6, g); box(0.12, 0.3, 0.45, whiteLight, 2.1, 0.95, -0.6, g);
  box(0.12, 0.25, 0.5, redLight, -2.1, 0.95, 0.6, g); box(0.12, 0.25, 0.5, redLight, -2.1, 0.95, -0.6, g);
  if (taxi) box(1.1, 0.32, 0.35, taxiSign, -0.3, 2.4, 0, g);
  const beam = new THREE.Mesh(new THREE.PlaneGeometry(9, 4.5), beamMat); beam.rotation.x = -Math.PI / 2; beam.rotation.z = 0; beam.position.set(6.6, 0.1, 0); g.add(beam);
  g.traverse(m => { if (m.isMesh && m.material !== beamMat) m.castShadow = true; });
  return g;
}
function addCar(lane) {
  const taxi = rnd() < 0.3;
  const color = taxi ? 0xf2c230 : pick(carColors.slice(3));
  const m = carMesh(color, taxi);
  scene.add(m);
  cars.push({ m, lane, offset: rnd() * lane.len, speed: lane.speed * (0.8 + rnd() * 0.5) });
}
function placeCar(c, t) {
  const L = c.lane;
  const s = (c.offset + c.speed * t) % L.len;
  const p = L.at(s);
  c.m.position.set(p.x, p.y, p.z);
  c.m.rotation.y = L.heading;
}
function lanes() {
  const out = [];
  // avenues: east and west lanes
  const avCenters = [AV / 2];
  for (let i = 0; i < 7; i++) avCenters.push(rowZ(i) + LOT + AV / 2);
  avCenters.forEach(zc => {
    out.push({ len: W + 30, speed: 14, heading: 0, at: s => ({ x: s - 15, y: 0, z: zc + 1.35 }) });
    out.push({ len: W + 30, speed: 14, heading: Math.PI, at: s => ({ x: W + 15 - s, y: 0, z: zc - 1.35 }) });
  });
  // bridge streets run the whole depth, climbing the ramps
  const ramp = z => { const z0 = riverZ0(), z1 = riverZ1(), up = 3.2; if (z < z0 - 14 || z > z1 + 14) return 0; if (z < z0 - 6) return up * (z - (z0 - 14)) / 8; if (z > z1 + 6) return up * ((z1 + 14) - z) / 8; return up; };
  bridges.forEach(s => {
    const xc = weekX(s) - ST / 2;
    out.push({ len: D + 30, speed: 12, heading: -Math.PI / 2, at: t => ({ x: xc + 1.2, y: ramp(t - 15), z: t - 15 }) });
    out.push({ len: D + 30, speed: 12, heading: Math.PI / 2, at: t => ({ x: xc - 1.2, y: ramp(D + 15 - t), z: D + 15 - t }) });
  });
  // the other cross streets only on the Manhattan side
  const z0 = riverZ0();
  boundaries.filter(s => !bridges.includes(s)).concat([0]).forEach(s => {
    const xc = s === 0 ? ST / 2 : weekX(s) - ST / 2;
    out.push({ len: z0 + 20, speed: 11, heading: -Math.PI / 2, at: t => ({ x: xc + 1.2, y: 0, z: t - 20 }) });
    out.push({ len: z0 + 20, speed: 11, heading: Math.PI / 2, at: t => ({ x: xc - 1.2, y: 0, z: z0 - t }) });
  });
  return out;
}
function boat(x, z, dir) {
  const g = new THREE.Group();
  box(9, 1.4, 3.2, new THREE.MeshStandardMaterial({ color: 0xe9e4d8, roughness: 0.7 }), 0, 0.7, 0, g);
  box(5, 1.3, 2.4, new THREE.MeshStandardMaterial({ color: 0x3b4a5a, roughness: 0.6 }), -0.5, 2.0, 0, g);
  for (let i = -1.5; i <= 1.5; i += 0.75) box(0.4, 0.4, 0.05, bulbMat, i, 2.0, 1.22, g);
  box(0.4, 0.5, 0.4, greenLight, 3.5, 1.6, 1.2, g); box(0.4, 0.5, 0.4, redLight, 3.5, 1.6, -1.2, g);
  g.position.set(x, 0.1, z); g.rotation.y = dir > 0 ? 0 : Math.PI; scene.add(g);
  boats.push({ g, x, z, dir, speed: 4 + rnd() * 3 });
}

// ---------- sky ----------
function sky() {
  const n = 1800, pos = new Float32Array(n * 3);
  for (let i = 0; i < n; i++) { const th = rnd() * Math.PI * 2, ph = Math.acos(rnd() * 0.9 + 0.05); const r = 2600; pos[i * 3] = W / 2 + r * Math.sin(ph) * Math.cos(th); pos[i * 3 + 1] = r * Math.cos(ph) * 0.6 + 40; pos[i * 3 + 2] = D / 2 + r * Math.sin(ph) * Math.sin(th); }
  const geo = new THREE.BufferGeometry(); geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const pts = new THREE.Points(geo, new THREE.PointsMaterial({ color: 0xdfe8ff, size: 1.6, sizeAttenuation: false, fog: false, transparent: true, opacity: 0.8 }));
  scene.add(pts);
  const sc2 = document.createElement('canvas'); sc2.width = 4; sc2.height = 256;
  const sg = sc2.getContext('2d'); const grad = sg.createLinearGradient(0, 0, 0, 256);
  grad.addColorStop(0, '#05070e'); grad.addColorStop(0.55, '#0a0f1f'); grad.addColorStop(0.8, '#151c36'); grad.addColorStop(0.92, '#2a2636'); grad.addColorStop(1, '#3a2a24');
  sg.fillStyle = grad; sg.fillRect(0, 0, 4, 256);
  const skyTex = new THREE.CanvasTexture(sc2); skyTex.colorSpace = THREE.SRGBColorSpace;
  const dome = new THREE.Mesh(new THREE.SphereGeometry(3200, 24, 16, 0, Math.PI * 2, 0, Math.PI * 0.52), new THREE.MeshBasicMaterial({ map: skyTex, side: THREE.BackSide, fog: false }));
  dome.position.set(W / 2, -80, D / 2); scene.add(dome);
  const moon = new THREE.Mesh(new THREE.SphereGeometry(22, 16, 16), new THREE.MeshBasicMaterial({ color: 0xf1ecd8, fog: false }));
  moon.position.set(W / 2 - 900, 420, D / 2 - 1500); scene.add(moon);
  const hemi = new THREE.HemisphereLight(0x55689a, 0x14110f, 1.6); scene.add(hemi);
  const dir = new THREE.DirectionalLight(0xaebbe0, 2.1);
  dir.position.set(W / 2 - 300, 420, D / 2 - 500); dir.target.position.set(W / 2, 0, D / 2); scene.add(dir.target);
  dir.castShadow = true; dir.shadow.mapSize.set(4096, 4096);
  const sc = dir.shadow.camera; sc.left = -380; sc.right = 380; sc.top = 170; sc.bottom = -170; sc.near = 50; sc.far = 1400; dir.shadow.bias = -0.0008; dir.shadow.normalBias = 0.3;
  scene.add(dir);
  const warm = new THREE.PointLight(0xffb060, 1.0, 0, 2); warm.position.set(W / 2, 120, D / 2); // soft city glow
  scene.add(warm);
}

// ---------- camera path ----------
let camCurve;
function cameraPath() {
  const zA = rowZ(2) + LOT + AV / 2;
  const zR = riverZ0() + 19;
  const zm = (zA + zR) / 2;
  const P = [
    new THREE.Vector3(-70, 60, zA),
    new THREE.Vector3(W * 0.33, 56, zA),
    new THREE.Vector3(W * 0.66, 56, zA),
    new THREE.Vector3(W + 60, 60, zA),
    new THREE.Vector3(W + 125, 54, zm + 8),
    new THREE.Vector3(W + 60, 44, zR),
    new THREE.Vector3(W * 0.66, 40, zR + 4),
    new THREE.Vector3(W * 0.33, 40, zR + 4),
    new THREE.Vector3(-60, 44, zR),
    new THREE.Vector3(-125, 54, zm)
  ];
  camCurve = new THREE.CatmullRomCurve3(P, true, 'centripetal', 0.5);
}
const smooth = x => x * x * (3 - 2 * x);
function cameraAt(t) {
  const p = camCurve.getPointAt(t);
  const ahead = camCurve.getPointAt((t + 0.045) % 1); ahead.y = 24;
  const sky = new THREE.Vector3(W * 0.5, 26, riverZ0() - 64);
  let k;
  if (t < 0.33) k = 0; else if (t < 0.42) k = smooth((t - 0.33) / 0.09); else if (t < 0.93) k = 1; else k = 1 - smooth((t - 0.93) / 0.07);
  const target = ahead.lerp(sky, k);
  camera.position.copy(p);
  camera.lookAt(target);
}

// ---------- build ----------
let composer, laneList;
async function build() {
  const res = await fetch('./data.json'); DATA = await res.json();
  DATA.total = DATA.weeks.flat().reduce((acc, c) => acc + (c.count || 0), 0);
  layout(DATA);
  cameraPath();
  buildGround(DATA);
  sky();
  // rank buildings for landmarks
  const cells = [];
  for (let w = 0; w < 53; w++) for (let i = 0; i < 7; i++) { const c = DATA.weeks[w][ORDER[i]]; if (c.count > 0) cells.push({ w, i, count: c.count }); }
  const sorted = cells.slice().sort((a, b) => b.count - a.count);
  const rank = new Map(); sorted.forEach((c, k) => rank.set(c.w * 7 + c.i, k));
  for (let w = 0; w < 53; w++) for (let i = 0; i < 7; i++) {
    const c = DATA.weeks[w][ORDER[i]];
    if (c.count === null) continue;
    if (c.count === 0) park(weekX(w), rowZ(i));
    else building(weekX(w), rowZ(i), c.count, rank.get(w * 7 + i), cells.length);
  }
  // street lamps along avenues
  const avC = [AV / 2]; for (let i = 0; i < 7; i++) avC.push(rowZ(i) + LOT + AV / 2);
  avC.forEach(zc => { for (let x = 9; x < W; x += 16) { streetLamp(x, zc - ROAD_AV / 2 - 0.9, 1); streetLamp(x + 8, zc + ROAD_AV / 2 + 0.9, -1); } });
  // traffic lights at the cross streets
  const stC = [ST / 2].concat(boundaries.map(s => weekX(s) - ST / 2));
  stC.forEach(xc => avC.forEach((zc, i) => { if (zc > riverZ0() && zc < riverZ1()) return; if ((i + Math.round(xc)) % 2) trafficLight(xc - ROAD_ST / 2 - 0.8, zc + ROAD_AV / 2 + 0.8, Math.PI); else trafficLight(xc + ROAD_ST / 2 + 0.8, zc - ROAD_AV / 2 - 0.8, 0); }));
  bridges.forEach(s => bridge(weekX(s) - ST / 2));
  laneList = lanes();
  laneList.forEach(l => { const n = Math.max(3, Math.round(l.len / 34)); for (let k = 0; k < n; k++) addCar(l); });
  boat(120, (riverZ0() + riverZ1()) / 2 + 7, 1); boat(420, (riverZ0() + riverZ1()) / 2 - 8, -1);
  composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bloom = new UnrealBloomPass(new THREE.Vector2(WIDTH, HEIGHT), 0.55, 0.45, 0.82);
  composer.addPass(bloom);
  composer.addPass(new OutputPass());
}

function update(t) {
  const T = t * LOOP;
  cars.forEach(c => placeCar(c, T));
  boats.forEach(b => { const x = (b.x + b.dir * b.speed * T) % (W + 60); b.g.position.x = ((x + W + 60) % (W + 60)) - 30; });
  signals.forEach(s => { const ph = (T / 9 + s.phase) % 1; const red = ph < 0.47, amber = ph >= 0.47 && ph < 0.53; s.r.material.emissiveIntensity = red ? 3 : 0.05; s.a.material.emissiveIntensity = amber ? 3 : 0.05; s.gr.material.emissiveIntensity = (!red && !amber) ? 3 : 0.05; });
  const blink = (Math.sin(T * 2.6) > 0.2) ? 3 : 0.3;
  beaconMat.emissiveIntensity = blink;
  cameraAt(t);
}

window.cityRender = function (t) {
  update(t);
  composer.render();
  return renderer.domElement.toDataURL('image/png');
};
window.cityReady = build().then(() => { update(0); composer.render(); return true; });
