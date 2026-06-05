// Kanto Nuzlocke Tracker — loads data.json and renders the map + detail panel.

const BADGE_NAMES = [
  "Boulder", "Cascade", "Thunder", "Rainbow",
  "Soul", "Marsh", "Volcano", "Earth",
];
const COLORS = ["#3b6cff","#ff5d5d","#5bd06a","#c86bff","#ff9f1c","#1fd1c4","#ff6fb5","#9aa7ff"];

// Pokemon sprite by National Dex number (PokeAPI sprite CDN).
const spriteUrl = (dex) =>
  dex ? `https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/${dex}.png` : "";

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, html) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (html != null) e.innerHTML = html;
  return e;
};

const initial = (name) => (name || "?").trim().charAt(0).toUpperCase() || "?";

// Did the player give this Pokemon a real nickname (vs. the default ALL-CAPS species name)?
const hasCustomNick = (mon) =>
  mon.nickname && mon.nickname.toLowerCase() !== mon.species.toLowerCase();

// A face element. Priority:
//   1. sprite of the lead (first) party Pokémon
//   2. a player photo at faces/<id>.png
//   3. a colored circle with the trainer's initial
function faceStyle(player, color) {
  const div = el("div", "face");
  div.style.backgroundColor = color;

  const lead = player.party && player.party[0];
  if (lead && lead.dex) {
    div.classList.add("face-mon");
    div.style.backgroundColor = "";  // let CSS decide (transparent on map)
    div.style.backgroundImage = `url(${spriteUrl(lead.dex)})`;
    div.title = hasCustomNick(lead)
      ? `${lead.nickname} (${lead.species})` : lead.species;
    return div;
  }

  div.textContent = initial(player.trainer);
  const img = new Image();
  img.onload = () => {
    div.style.backgroundImage = `url(faces/${player.id}.png)`;
    div.style.backgroundSize = "cover";
    div.textContent = "";
  };
  img.src = `faces/${player.id}.png`;
  return div;
}

let DATA = { players: [] };

async function init() {
  try {
    const res = await fetch("data.json", { cache: "no-store" });
    DATA = await res.json();
  } catch (e) {
    $("#markers").innerHTML =
      `<div style="position:absolute;inset:0;display:grid;place-items:center;color:#fff">
         Could not load data.json — run <code>python parse_saves.py</code> first.
       </div>`;
    return;
  }
  DATA.players.forEach((p, i) => (p._color = COLORS[i % COLORS.length]));
  renderLegend();
  renderMarkers();
}

function renderLegend() {
  const legend = $("#legend");
  legend.innerHTML = "";
  DATA.players.forEach((p) => {
    const chip = el("div", "chip");
    chip.append(Object.assign(el("span", "dot"), { style: `background:${p._color}` }));
    chip.append(document.createTextNode(`${p.trainer} · ${p.location.area}`));
    chip.onclick = () => openPanel(p);
    legend.append(chip);
  });
}

function renderMarkers() {
  const wrap = $("#markers");
  wrap.innerHTML = "";
  DATA.players.forEach((p) => {
    const m = el("div", "marker");
    m.style.left = p.location.x + "%";
    m.style.top = p.location.y + "%";

    const face = faceStyle(p, p._color);
    face.style.borderColor = p._color;
    if (p.badges > 0) face.append(el("span", "badgecount", String(p.badges)));
    m.append(face);
    m.append(el("div", "pin"));
    m.append(el("div", "tag", p.trainer));
    m.onclick = () => openPanel(p);
    wrap.append(m);
  });
}

function monCard(mon, withLevel) {
  const c = el("div", "mon");
  const img = el("img");
  img.src = spriteUrl(mon.dex);
  img.alt = mon.species;
  img.onerror = () => { img.style.visibility = "hidden"; };
  c.append(img);

  const info = el("div");
  const name = hasCustomNick(mon)
    ? `${mon.nickname} <span class="ml">(${mon.species})</span>`
    : mon.species;
  info.append(el("div", "mn", name + (mon.shiny ? ' <span class="shiny">★</span>' : "")));

  const bits = [];
  if (withLevel && mon.level != null) bits.push("Lv " + mon.level);
  if (mon.isEgg) bits.push("Egg");
  if (mon.box) bits.push("Box " + mon.box);
  if (bits.length) info.append(el("div", "ml", bits.join(" · ")));

  if (withLevel && mon.maxHp) {
    const pct = Math.max(0, Math.min(100, (mon.hp / mon.maxHp) * 100));
    const bar = el("div", "hpbar");
    const fill = el("span");
    fill.style.width = pct + "%";
    fill.style.background = pct < 25 ? "var(--bad)" : pct < 50 ? "var(--accent)" : "var(--good)";
    bar.append(fill);
    info.append(bar);
    info.append(el("div", "ml", `${mon.hp}/${mon.maxHp} HP`));
  }
  c.append(info);
  return c;
}

function openPanel(p) {
  const body = $("#panelBody");
  body.innerHTML = "";

  // header
  const head = el("div", "ph");
  const face = faceStyle(p, "#2a3b66");
  head.append(face);
  const who = el("div", "who");
  who.append(el("h2", null, p.trainer));
  who.append(el("div", "sub",
    `${p.gender === "F" ? "♀" : "♂"} · ID ${p.trainerId} · ${p.location.area}`));
  head.append(who);
  body.append(head);

  // play time + badges count
  const pt = p.playTime;
  const meta = el("div", "section");
  meta.append(el("h3", null, "Trainer"));
  const playStr = `${pt.h}h ${String(pt.m).padStart(2, "0")}m ${String(pt.s).padStart(2, "0")}s`;
  meta.innerHTML += `
    <div class="kv"><span class="k">Play time</span><span>${playStr}</span></div>
    <div class="kv"><span class="k">Badges</span><span>${p.badges} / 8</span></div>
    <div class="kv"><span class="k">Location</span><span>${p.location.area}</span></div>`;
  body.append(meta);

  // badges row
  const bsec = el("div", "section");
  bsec.append(el("h3", null, "Gym Badges"));
  const badges = el("div", "badges");
  p.badgeList.forEach((earned, i) => {
    const b = el("div", "badge" + (earned ? " earned" : ""), String(i + 1));
    b.title = BADGE_NAMES[i] + " Badge";
    badges.append(b);
  });
  bsec.append(badges);
  body.append(bsec);

  // party
  const party = el("div", "section");
  party.append(el("h3", null, `Party (${p.party.length})`));
  if (p.party.length) {
    const grid = el("div", "mons");
    p.party.forEach((m) => grid.append(monCard(m, true)));
    party.append(grid);
  } else {
    party.append(el("div", "empty", "No Pokémon in party yet."));
  }
  body.append(party);

  // boxes
  const boxes = el("div", "section");
  boxes.append(el("h3", null, `PC Boxes (${p.boxes.length})`));
  if (p.boxes.length) {
    const grid = el("div", "box-grid");
    p.boxes.forEach((m) => grid.append(monCard(m, false)));
    boxes.append(grid);
  } else {
    boxes.append(el("div", "empty", "No Pokémon stored in the PC."));
  }
  body.append(boxes);

  $("#panel").classList.add("show");
  $("#panel").setAttribute("aria-hidden", "false");
  $("#scrim").classList.add("show");
}

function closePanel() {
  $("#panel").classList.remove("show");
  $("#panel").setAttribute("aria-hidden", "true");
  $("#scrim").classList.remove("show");
}

$("#panelClose").onclick = closePanel;
$("#scrim").onclick = closePanel;
document.addEventListener("keydown", (e) => e.key === "Escape" && closePanel());

init();
