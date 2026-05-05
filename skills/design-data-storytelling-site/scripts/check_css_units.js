#!/usr/bin/env node
// check_css_units.js
//
// Scan markdown files in the design-data-storytelling-site skill for
// CSS unit literals with invalid internal whitespace inside fenced
// code blocks. The LLM imitates these blocks; if they drift to
// `1 px`, `220 px`, `1 fr`, or `90 deg`, the generated CSS will be
// invalid.
//
// Usage:
//   node check_css_units.js path/to/skill_dir [more_paths...]
//
// Exit codes:
//   0  no offenses
//   1  offenses found
//   2  could not access input

const fs   = require('fs');
const path = require('path');

const args = process.argv.slice(2);
if (args.length === 0) {
  console.error('Usage: node check_css_units.js path/to/skill_dir [...]');
  process.exit(2);
}

const findMarkdown = (root) => {
  const out = [];
  const stack = [root];
  while (stack.length) {
    const cur = stack.pop();
    let stat;
    try { stat = fs.statSync(cur); } catch { continue; }
    if (stat.isDirectory()) {
      for (const entry of fs.readdirSync(cur)) {
        if (entry.startsWith('._')) continue;
        stack.push(path.join(cur, entry));
      }
    } else if (cur.endsWith('.md')) {
      out.push(cur);
    }
  }
  return out;
};

const files = [];
for (const a of args) {
  if (!fs.existsSync(a)) {
    console.error(`FAIL: input not found: ${a}`);
    process.exit(2);
  }
  const stat = fs.statSync(a);
  if (stat.isDirectory()) files.push(...findMarkdown(a));
  else if (a.endsWith('.md')) files.push(a);
}

// Match a digit followed by whitespace followed by a CSS unit, e.g.
// `1 px`, `220 px`, `1 fr`, `90 deg`, `.75 rem`, `0.5 em`.
const BAD_RE = /(\d|\.\d)\s+(px|rem|em|fr|vh|vw|deg|%)\b/g;

const offenses = [];
for (const file of files) {
  const text = fs.readFileSync(file, 'utf8');
  const lines = text.split(/\r?\n/);
  let inFence = false;
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    if (/^\s*```/.test(line)) { inFence = !inFence; continue; }
    if (!inFence) continue;
    let m;
    BAD_RE.lastIndex = 0;
    while ((m = BAD_RE.exec(line)) !== null) {
      offenses.push({ file, line: i + 1, snippet: line.trim(), match: m[0] });
    }
  }
}

if (offenses.length === 0) {
  console.log(`OK: scanned ${files.length} markdown file(s); no invalid CSS unit spacing in fenced code blocks.`);
  process.exit(0);
} else {
  console.error(`FAIL: ${offenses.length} CSS unit offense(s) in fenced code blocks:`);
  for (const o of offenses) {
    console.error(`  ${o.file}:${o.line}  "${o.match}"  →  ${o.snippet}`);
  }
  process.exit(1);
}
