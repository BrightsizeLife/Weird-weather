# Component patterns

Copy-paste building blocks. Each one assumes the CSS tokens from
[`DESIGN-SYSTEM.md`](./DESIGN-SYSTEM.md) are in scope.

## Stat card

```html
<div class="stat-card">
  <div class="label">Hottest city</div>
  <div class="value color-red">Denver</div>
  <div class="detail">+11.1°F vs normal · z = +2.70</div>
</div>
```

```css
.stat-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 1.2rem;
}
.stat-card .label {
  color: var(--muted);
  font-size: .75rem;
  text-transform: uppercase;
  letter-spacing: .05em;
  margin-bottom: .4rem;
}
.stat-card .value { font-size: 1.8rem; font-weight: 700; line-height: 1.2; }
.stat-card .detail { color: var(--muted); font-size: .8rem; margin-top: .3rem; }
```

## Stat-card grid

```css
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
  max-width: 1200px;
  margin: 0 auto;
}
```

## Editable code block

```html
<div class="code-card">
  <div class="code-card-header">
    <span class="file-name">analysis.R <span class="dim">· model fit</span></span>
    <div class="code-card-actions">
      <button class="code-card-btn" data-copy>Copy</button>
      <button class="code-card-btn" data-reset>Reset</button>
    </div>
  </div>
  <textarea class="code-editable" spellcheck="false">…your code…</textarea>
</div>
```

## Math card

```html
<div class="math-card">
  <div class="math-label">Per-unit z-score</div>
  <div class="math-formula">
    <span class="var">z</span><sub>c, t</sub>
    <span class="op">=</span>
    ( <span class="var">y</span><sub>c, t</sub>
      <span class="op">−</span>
      <span class="var">ŷ</span><sub>c, t</sub> ) / <span class="var">σ</span><sub>c</sub>
  </div>
  <div class="math-note">σ is per-unit, so 2σ means something domain-relevant.</div>
</div>
```

```css
.math-card {
  background: linear-gradient(135deg, var(--card-deep), var(--bg));
  border: 1px solid #2a2a2a;
  border-radius: 8px;
  padding: 1.5rem 1.6rem 1.3rem;
}
.math-card .math-label {
  color: var(--muted); font-size: .7rem;
  letter-spacing: .14em; text-transform: uppercase; margin-bottom: .8rem;
}
.math-card .math-formula {
  font-family: 'Cambria Math', 'STIX Two Math', 'Times New Roman', serif;
  font-size: 1.45rem; color: var(--text); line-height: 1.6;
}
.math-card .math-formula .var { color: var(--blue); font-style: italic; }
.math-card .math-formula .op  { color: var(--red); }
.math-card .math-formula .fn  { color: var(--yellow); font-style: italic; }
.math-card .math-note { color: var(--muted); font-size: .8rem; margin-top: .7rem; }
```

## Recipe step

```html
<div class="recipe-step">
  <span class="step-num">1</span>
  <span class="step-text">Normalize each metric to <code>[0, 1]</code>.</span>
</div>
```

```css
.recipe-step {
  display: flex; gap: 1rem; align-items: flex-start;
  padding: .9rem 0; border-bottom: 1px dashed var(--border);
}
.recipe-step .step-num {
  flex: 0 0 auto;
  width: 28px; height: 28px;
  border-radius: 50%;
  background: var(--card); border: 1px solid var(--border);
  color: var(--red); font-weight: 700;
  display: flex; align-items: center; justify-content: center;
}
.recipe-step .step-text { flex: 1; line-height: 1.55; color: var(--text); }
```

## Annotated parameter list

```html
<ul class="annotated-list">
  <li>
    <span class="anno-key">spline_k</span>
    <span class="anno-val">Upper bound on basis dimension. REML chooses the effective df below this.</span>
  </li>
</ul>
```

```css
.annotated-list { list-style: none; padding: 0; }
.annotated-list li {
  display: grid; grid-template-columns: 200px 1fr; gap: 1.4rem;
  padding: .9rem 0; border-bottom: 1px dashed var(--border);
}
.annotated-list .anno-key {
  font-family: 'SF Mono', monospace; color: var(--yellow);
  font-size: .85rem;
}
.annotated-list .anno-val { color: var(--text); font-size: .9rem; line-height: 1.6; }

@media (max-width: 700px) {
  .annotated-list li { grid-template-columns: 1fr; }
}
```

## Pill row

```html
<div class="pill-row">
  <span class="pill blue">numpy</span>
  <span class="pill yellow">scipy</span>
  <span class="pill red">least squares</span>
</div>
```

```css
.pill {
  background: var(--card); border: 1px solid var(--border);
  color: var(--muted); padding: .35rem .8rem;
  border-radius: 999px; font-size: .75rem;
}
.pill.red    { border-color: var(--red);    color: var(--red); }
.pill.blue   { border-color: var(--blue);   color: var(--blue); }
.pill.yellow { border-color: var(--yellow); color: var(--yellow); }
```

## Callout box

```html
<div class="callout-box">
  <strong>What this model is and isn't.</strong> Descriptive, not causal.
  Read the residuals before you read the conclusions.
</div>
```

```css
.callout-box {
  background: var(--card-deep);
  border-left: 3px solid var(--yellow);
  border-radius: 0 6px 6px 0;
  padding: 1.2rem 1.5rem;
  margin: 1.5rem 0;
}
```

## Sortable data table

```html
<table class="data-table">
  <thead>
    <tr>
      <th data-sort="city">City <span class="sort-arrow">↕</span></th>
      <th data-sort="delta" class="num">Δ °F</th>
    </tr>
  </thead>
  <tbody>…</tbody>
</table>
```

```js
document.querySelectorAll('.data-table thead th[data-sort]').forEach(th => {
  th.addEventListener('click', () => {
    const key = th.dataset.sort;
    const asc = th.classList.toggle('asc');
    const tbody = th.closest('table').querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    rows.sort((a, b) => {
      const va = a.dataset[key], vb = b.dataset[key];
      const na = Number(va), nb = Number(vb);
      if (!isNaN(na) && !isNaN(nb)) return asc ? na - nb : nb - na;
      return asc ? va.localeCompare(vb) : vb.localeCompare(va);
    });
    rows.forEach(r => tbody.appendChild(r));
  });
});
```

## Time series small-multiple grid

```html
<div class="ts-grid">
  <div class="ts-cell"><svg id="ts-Denver"></svg><div class="ts-cap">Denver, CO</div></div>
  <!-- one cell per unit -->
</div>
```

```css
.ts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
}
.ts-cell {
  background: var(--card-deep);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: .8rem;
}
.ts-cap { color: var(--muted); font-size: .75rem; margin-top: .3rem; }
```

## Infographic poster

```html
<div class="poster-wrap">
  <div class="poster-header">
    <div class="poster-index">01 / 07</div>
    <div class="poster-meta">Where winter went · nearest-match cities</div>
    <button class="export-btn"
            data-target="poster-1" data-name="01-where-winter-went">Export PNG</button>
  </div>
  <div class="poster-stage">
    <div class="poster" id="poster-1">…content at 1200×1500 design size…</div>
  </div>
</div>
```

```css
.poster-stage {
  width: 100%; max-width: 1200px;
  aspect-ratio: 4 / 5;
  position: relative; overflow: hidden;
  border: 1px solid var(--border); background: var(--bg);
}
.poster {
  position: absolute; top: 0; left: 0;
  width: 1200px; height: 1500px;
  background: var(--bg); color: var(--text);
  padding: 56px 64px 0;
  transform-origin: top left;
}
```

```js
function rescalePosters() {
  document.querySelectorAll('.poster-stage').forEach(stage => {
    const poster = stage.querySelector('.poster');
    const w = stage.clientWidth;
    if (poster && w > 0) poster.style.transform = `scale(${w / 1200})`;
  });
}
window.addEventListener('resize', rescalePosters);
```

## Footer

```html
<footer>
  Data: <a href="https://open-meteo.com">Open-Meteo Archive API</a> ·
  Normals: 1991–2020 winter seasons (Dec–Feb) ·
  Model: weather ~ spline(year) + (year | city); σ ~ city
</footer>
```

```css
footer {
  text-align: center; color: var(--muted); font-size: .75rem;
  padding: 2rem 1rem; border-top: 1px solid var(--border);
}
footer a { color: var(--text); text-decoration: none; border-bottom: 1px dotted var(--muted); }
```

## Home link (header top-left)

```html
<a class="home-link" href="https://example.com" title="example.com">
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/>
  </svg>
  <span>example</span>
</a>
```

```css
.home-link {
  position: absolute; top: 50%; left: 1.2rem;
  transform: translateY(-50%);
  color: var(--muted); text-decoration: none;
  font-size: .72rem; letter-spacing: .05em;
  display: flex; align-items: center; gap: .35rem;
}
.home-link:hover { color: var(--red); }
.home-link svg { width: 14px; height: 14px; fill: currentColor; }
```
