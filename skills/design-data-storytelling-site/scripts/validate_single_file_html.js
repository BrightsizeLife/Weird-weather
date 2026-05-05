#!/usr/bin/env node
// validate_single_file_html.js
//
// Lightweight structural + accessibility validator for an
// index.html produced by the design-data-storytelling-site skill.
//
// Usage:
//   node validate_single_file_html.js path/to/index.html [--allow-cdn]
//
// Exit codes:
//   0  every check passed
//   1  one or more checks failed
//   2  could not read input

const fs = require('fs');

const args = process.argv.slice(2);
if (args.length === 0 || args[0].startsWith('-')) {
  console.error('Usage: node validate_single_file_html.js path/to/index.html [--allow-cdn]');
  process.exit(2);
}
const filePath = args[0];
const allowCdn = args.includes('--allow-cdn');

if (!fs.existsSync(filePath)) {
  console.error(`FAIL: file not found: ${filePath}`);
  process.exit(2);
}
const html = fs.readFileSync(filePath, 'utf8');

const errors = [];
const fail = (msg) => errors.push(msg);

// Tag counts
const count = (re) => (html.match(re) || []).length;
if (count(/<html\b/gi) !== 1) fail('expected exactly one <html> tag');
if (count(/<head\b/gi) !== 1) fail('expected exactly one <head> tag');
if (count(/<body\b/gi) !== 1) fail('expected exactly one <body> tag');

// Required head meta
if (!/<meta[^>]+charset/i.test(html)) fail('missing <meta charset>');
if (!/<meta[^>]+name=["']viewport["']/i.test(html)) fail('missing viewport meta');

// External CSS / JS
if (!allowCdn) {
  const externalLink = /<link[^>]+href=["']https?:\/\//gi.test(html);
  const externalScript = /<script[^>]+src=["']https?:\/\//gi.test(html);
  if (externalLink) fail('external <link href="https://..."> present but --allow-cdn was not passed');
  if (externalScript) fail('external <script src="https://..."> present but --allow-cdn was not passed');
}

// Tabs: every role="tab" button must reference a panel that exists
const tabBtnRe = /<button[^>]*\brole=["']tab["'][^>]*>/gi;
const idRe = /\bid=["']([^"']+)["']/i;
const ariaControlsRe = /\baria-controls=["']([^"']+)["']/i;
const tabBtnMatches = html.match(tabBtnRe) || [];
for (const tag of tabBtnMatches) {
  const ariaCtl = tag.match(ariaControlsRe);
  if (!ariaCtl) {
    fail(`tab button missing aria-controls: ${tag.slice(0, 80)}…`);
    continue;
  }
  const panelId = ariaCtl[1];
  const panelRe = new RegExp(`<[^>]+\\brole=["']tabpanel["'][^>]*\\bid=["']${panelId}["']`, 'i');
  const panelReAlt = new RegExp(`<[^>]+\\bid=["']${panelId}["'][^>]*\\brole=["']tabpanel["']`, 'i');
  if (!panelRe.test(html) && !panelReAlt.test(html)) {
    fail(`tab button aria-controls="${panelId}" has no matching role="tabpanel" element`);
  }
}

// Panels: every role="tabpanel" should have aria-labelledby pointing at a button id
const panelRe = /<[^>]*\brole=["']tabpanel["'][^>]*>/gi;
const panelMatches = html.match(panelRe) || [];
for (const tag of panelMatches) {
  const idM = tag.match(idRe);
  const labelM = tag.match(/\baria-labelledby=["']([^"']+)["']/i);
  if (!labelM) {
    fail(`tabpanel ${idM ? '#' + idM[1] : ''} missing aria-labelledby`);
    continue;
  }
  const btnRe = new RegExp(`<button[^>]*\\bid=["']${labelM[1]}["'][^>]*>`, 'i');
  if (!btnRe.test(html)) {
    fail(`tabpanel aria-labelledby="${labelM[1]}" has no matching <button id="${labelM[1]}">`);
  }
}

// Buttons: must have text content or aria-label
const buttonRe = /<button\b[^>]*>([\s\S]*?)<\/button>/gi;
let bm;
while ((bm = buttonRe.exec(html)) !== null) {
  const tag = bm[0];
  const inner = bm[1].replace(/<[^>]+>/g, '').replace(/\s+/g, '').trim();
  const hasLabel = /\baria-label=["'][^"']+["']/i.test(tag) ||
                   /\baria-labelledby=["'][^"']+["']/i.test(tag);
  if (!inner && !hasLabel) {
    fail(`<button> has neither text content nor aria-label: ${tag.slice(0, 80)}…`);
  }
}

// outline: none must be paired with :focus-visible rule
if (/outline:\s*none/i.test(html) && !/:focus-visible[^{]*\{[^}]*outline:/i.test(html)) {
  fail('outline:none found without a :focus-visible replacement');
}

// prefers-reduced-motion media query present
if (!/@media[^{]*prefers-reduced-motion[^{]*\{/i.test(html)) {
  fail('no prefers-reduced-motion media query found');
}

// Invalid CSS unit spacing inside <style> blocks
const styleBlocks = [...html.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/gi)].map(m => m[1]);
const inlineStyles = [...html.matchAll(/\bstyle=["']([^"']*)["']/gi)].map(m => m[1]);
const cssChunks = styleBlocks.concat(inlineStyles);
const BAD_UNIT_RE = /(\d|\.\d)\s+(px|rem|em|fr|vh|vw|deg|%)\b/g;
let unitOffenses = 0;
for (const css of cssChunks) {
  let m;
  BAD_UNIT_RE.lastIndex = 0;
  while ((m = BAD_UNIT_RE.exec(css)) !== null) unitOffenses++;
}
if (unitOffenses > 0) {
  fail(`${unitOffenses} invalid CSS unit literal(s) (digit + space + unit) inside <style> or style="…"`);
}

// "best" / "worst" / "amazing" / etc. language audit (light)
const banned = ['best', 'worst', 'winner', 'loser', 'amazing', 'incredible', 'shocking'];
const visibleText = html.replace(/<script[\s\S]*?<\/script>/gi, '')
                        .replace(/<style[\s\S]*?<\/style>/gi, '')
                        .replace(/<!--[\s\S]*?-->/g, '');
const matches = banned.filter(w => new RegExp(`\\b${w}\\b`, 'i').test(visibleText));
if (matches.length > 0) {
  fail(`banned editorial language found in visible text: ${matches.join(', ')}`);
}

if (errors.length === 0) {
  console.log('OK: validate_single_file_html.js passed.');
  process.exit(0);
} else {
  console.error('FAIL: validate_single_file_html.js found issues:');
  for (const e of errors) console.error('  - ' + e);
  process.exit(1);
}
