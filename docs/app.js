// Kanto Nuzlocke Tracker — Pokémon FireRed/LeafGreen design system

const BADGE_NAMES = [
  "Boulder","Cascade","Thunder","Rainbow",
  "Soul","Marsh","Volcano","Earth",
];

const TRAINER_COLORS = [
  "#3060c0","#c03028","#28a040","#9050c8",
  "#e87820","#18a8a0","#d050a0","#a09028",
];

const spriteUrl = (dex) =>
  dex ? `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${dex}.png` : "";

const $ = (s) => document.querySelector(s);
const el = (tag, cls) => { const e = document.createElement(tag); if (cls) e.className = cls; return e; };
const txt = (t) => document.createTextNode(t);

const hasCustomNick = (mon) =>
  mon.nickname && mon.nickname.toLowerCase() !== mon.species.toLowerCase();

// ── face helper (lead sprite or initial) ─────────────────────────────────────
function makeFace(player, extraClass = "") {
  const lead = player.party?.[0];
  if (lead?.dex) {
    const d = el("div", `face${extraClass ? " " + extraClass : ""}`);
    d.style.backgroundImage = `url(${spriteUrl(lead.dex)})`;
    d.title = hasCustomNick(lead) ? `${lead.nickname} (${lead.species})` : lead.species;
    return d;
  }
  const d = el("div", `face face-init${extraClass ? " " + extraClass : ""}`);
  d.style.backgroundColor = player._color;
  d.textContent = player.trainer.charAt(0).toUpperCase();
  // try custom photo
  const img = new Image();
  img.onload = () => { d.style.backgroundImage = `url(faces/${player.id}.png)`; d.textContent = ""; };
  img.src = `faces/${player.id}.png`;
  return d;
}

// ── HP bar ────────────────────────────────────────────────────────────────────
function makeHpBar(hp, maxHp) {
  const pct = maxHp ? Math.max(0, Math.min(100, (hp / maxHp) * 100)) : 0;
  const cls = pct > 50 ? "hp-full" : pct > 20 ? "hp-mid" : "hp-low";
  const row = el("div", "hp-row");

  const lbl = el("span", "hp-label"); lbl.textContent = "HP";
  const track = el("div", "hp-track");
  const fill = el("div", `hp-fill ${cls}`);
  fill.style.width = pct + "%";
  track.append(fill);

  const nums = el("div", "hp-nums");
  nums.textContent = `${hp}/${maxHp}`;

  row.append(lbl, track);
  const wrap = el("div"); wrap.append(row, nums);
  return wrap;
}

// ── Pokemon card (party) ──────────────────────────────────────────────────────
function monCard(mon) {
  const card = el("div", `mon-card${mon.dead ? " mon-dead" : ""}`);

  const img = el("img");
  img.src = spriteUrl(mon.dex);
  img.alt = mon.species;
  img.onerror = () => { img.style.visibility = "hidden"; };
  card.append(img);

  const info = el("div", "mon-info");

  // nickname / species
  const nameEl = el("div", "mon-name");
  nameEl.textContent = hasCustomNick(mon) ? mon.nickname : mon.species;
  if (mon.shiny) {
    const star = el("span", "shiny-star"); star.textContent = " ★";
    nameEl.append(star);
  }
  info.append(nameEl);

  if (hasCustomNick(mon)) {
    const nick = el("div", "mon-nick"); nick.textContent = mon.species;
    info.append(nick);
  }

  if (mon.level != null) {
    const lvl = el("div", "mon-lvl"); lvl.textContent = `Lv. ${mon.level}`;
    info.append(lvl);
  }

  if (mon.hp != null && mon.maxHp != null) {
    info.append(makeHpBar(mon.hp, mon.maxHp));
  }

  card.append(info);
  return card;
}

// ── Pokemon box tile ──────────────────────────────────────────────────────────
function boxTile(mon) {
  const tile = el("div", `box-mon${mon.dead ? " mon-dead" : ""}`);

  const img = el("img");
  img.src = spriteUrl(mon.dex);
  img.alt = mon.species;
  img.onerror = () => { img.style.visibility = "hidden"; };
  tile.append(img);

  const name = el("div", "bm-name");
  name.textContent = hasCustomNick(mon) ? mon.nickname : mon.species;
  if (mon.shiny) {
    const star = el("span", "shiny-star"); star.textContent = "★";
    name.append(star);
  }
  tile.append(name);

  const boxLbl = el("div", "bm-box");
  boxLbl.textContent = `BOX ${mon.box}`;
  tile.append(boxLbl);

  return tile;
}

// ── Detail panel ──────────────────────────────────────────────────────────────
function openPanel(player) {
  const body = $(".summary-body");
  body.innerHTML = "";

  // -- HEADER --
  const hdr = el("div", "sum-header");
  const spr = makeFace(player, "trainer-sprite");
  hdr.append(spr);
  const info = el("div", "trainer-info");
  const nameEl = el("div", "trainer-name");
  nameEl.textContent = player.trainer;
  const sub = el("div", "trainer-sub");
  const pt = player.playTime;
  sub.innerHTML =
    `${player.gender === "F" ? "♀" : "♂"}  ID: ${player.trainerId}<br>` +
    `TIME: ${pt.h}h ${String(pt.m).padStart(2,"0")}m ${String(pt.s).padStart(2,"0")}s<br>` +
    `LOCATION: ${player.location.area}`;
  info.append(nameEl, sub);
  hdr.append(info);
  body.append(hdr);

  // -- TRAINER INFO --
  const infoSec = el("div", "sum-section");
  const infoTitle = el("div", "sum-section-title"); infoTitle.textContent = "TRAINER";
  const infoBody = el("div", "sum-section-body");
  const rows = [
    ["BADGES", `${player.badges} / 8`],
    ["LOCATION", player.location.area],
    ["PLAY TIME", `${pt.h}H ${String(pt.m).padStart(2,"0")}M`],
  ];
  rows.forEach(([k, v]) => {
    const row = el("div", "kv");
    const kEl = el("span", "k"); kEl.textContent = k;
    const vEl = el("span", "v"); vEl.textContent = v;
    row.append(kEl, vEl);
    infoBody.append(row);
  });
  infoSec.append(infoTitle, infoBody);
  body.append(infoSec);

  // -- BADGES --
  const badgeSec = el("div", "sum-section");
  const badgeTitle = el("div", "sum-section-title"); badgeTitle.textContent = "GYM BADGES";
  const badgeGrid = el("div", "badges-grid");
  player.badgeList.forEach((earned, i) => {
    const slot = el("div", `badge-slot${earned ? " earned" : ""}`);
    const num = el("div", "badge-num"); num.textContent = i + 1;
    const name = el("div", "badge-name"); name.textContent = BADGE_NAMES[i].toUpperCase();
    slot.append(num, name);
    slot.title = BADGE_NAMES[i] + " Badge";
    badgeGrid.append(slot);
  });
  badgeSec.append(badgeTitle, badgeGrid);
  body.append(badgeSec);

  // -- PARTY --
  const partySec = el("div", "sum-section");
  const partyTitle = el("div", "sum-section-title");
  partyTitle.textContent = `PARTY  (${player.party.length})`;
  partySec.append(partyTitle);
  if (player.party.length) {
    const grid = el("div", "party-grid");
    player.party.forEach(m => grid.append(monCard(m)));
    partySec.append(grid);
  } else {
    const empty = el("div", "empty-box"); empty.textContent = "NO POKEMON";
    partySec.append(empty);
  }
  body.append(partySec);

  // -- PC BOXES --
  const alive = player.boxes.filter(m => !m.dead);
  const dead  = player.boxes.filter(m => m.dead);

  if (alive.length) {
    const sec = el("div", "sum-section");
    const t = el("div", "sum-section-title"); t.textContent = `IN PC  (${alive.length})`;
    sec.append(t);
    const grid = el("div", "box-grid");
    alive.forEach(m => grid.append(boxTile(m)));
    sec.append(grid);
    body.append(sec);
  }

  if (dead.length) {
    const sec = el("div", "sum-section");
    const t = el("div", "sum-section-title");
    t.textContent = `FALLEN  (${dead.length})`;
    t.style.background = "#901820";
    sec.append(t);
    const grid = el("div", "box-grid");
    dead.forEach(m => grid.append(boxTile(m)));
    sec.append(grid);
    body.append(sec);
  }

  if (!player.boxes.length) {
    const empty = el("div", "empty-box"); empty.textContent = "PC IS EMPTY";
    body.append(empty);
  }

  // show
  $(".summary-panel").classList.add("show");
  $(".summary-panel").setAttribute("aria-hidden", "false");
  $(".scrim").classList.add("show");
}

function closePanel() {
  $(".summary-panel").classList.remove("show");
  $(".summary-panel").setAttribute("aria-hidden", "true");
  $(".scrim").classList.remove("show");
}

$("#panelClose").onclick  = closePanel;
$("#scrim").onclick       = closePanel;
document.addEventListener("keydown", e => e.key === "Escape" && closePanel());

// ── Map markers ───────────────────────────────────────────────────────────────
function renderMarkers(players) {
  const wrap = $("#markers");
  wrap.innerHTML = "";
  players.forEach(p => {
    const m = el("div", "marker");
    m.style.left = p.location.x + "%";
    m.style.top  = p.location.y + "%";

    const face = makeFace(p);
    m.append(face);

    if (p.badges > 0) {
      const bb = el("div", "badge-bubble"); bb.textContent = p.badges;
      m.append(bb);
    }

    const tag = el("div", "tag"); tag.textContent = p.trainer;
    m.append(tag);

    m.onclick = () => openPanel(p);
    wrap.append(m);
  });
}

// ── Legend / trainer chips ────────────────────────────────────────────────────
function renderLegend(players) {
  const nav = $("#legend");
  nav.innerHTML = "";
  players.forEach(p => {
    const chip = el("button", "trainer-chip");
    chip.style.borderColor = p._color;
    const dot = el("span", "chip-dot"); dot.style.background = p._color;
    chip.append(dot, txt(`${p.trainer} · ${p.location.area}`));
    chip.onclick = () => openPanel(p);
    nav.append(chip);
  });
}

// ── Init ──────────────────────────────────────────────────────────────────────
async function init() {
  let DATA = { players: [] };
  try {
    const res = await fetch("data.json", { cache: "no-store" });
    DATA = await res.json();
  } catch {
    $("#markers").innerHTML =
      `<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;color:#fff;font-family:'Press Start 2P',monospace;font-size:8px;text-align:center;padding:16px">
        RUN<br>python parse_saves.py<br>FIRST
      </div>`;
    return;
  }
  DATA.players.forEach((p, i) => p._color = TRAINER_COLORS[i % TRAINER_COLORS.length]);
  renderLegend(DATA.players);
  renderMarkers(DATA.players);
}

init();
