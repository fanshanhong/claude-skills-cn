#!/usr/bin/env node
// Generate public/og-default.png via the local CDP Proxy + Canvas API.
// Prereq: web-access CDP Proxy running on http://localhost:3456 with a Chromium browser attached.
// Usage:  node scripts/gen-og.mjs

import { writeFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const PROXY = process.env.CDP_PROXY ?? 'http://localhost:3456';
const OUT = resolve(dirname(fileURLToPath(import.meta.url)), '..', 'public', 'og-default.png');

const drawJs = `(function(){
  const c=document.createElement('canvas');c.width=1200;c.height=630;
  const x=c.getContext('2d');
  const g=x.createLinearGradient(0,0,1200,630);
  g.addColorStop(0,'#0f172a');g.addColorStop(1,'#1e3a8a');
  x.fillStyle=g;x.fillRect(0,0,1200,630);
  x.fillStyle='#fbbf24';
  x.font='bold 60px -apple-system,"PingFang SC","Hiragino Sans GB",sans-serif';
  x.fillText('Claude Skills',80,240);
  x.fillStyle='#ffffff';
  x.font='bold 100px -apple-system,"PingFang SC","Hiragino Sans GB",sans-serif';
  x.fillText('中文市集',80,380);
  x.fillStyle='#cbd5e1';
  x.font='32px -apple-system,"PingFang SC","Hiragino Sans GB",sans-serif';
  x.fillText('每个 Claude Skill 一篇深度长文教程',80,470);
  x.fillStyle='#94a3b8';
  x.font='24px -apple-system,"PingFang SC","Hiragino Sans GB",sans-serif';
  x.fillText('claudeskill.me  ·  Anthropic / Superpowers / 社区精选',80,540);
  x.strokeStyle='#fbbf24';x.lineWidth=6;
  x.beginPath();x.moveTo(80,410);x.lineTo(280,410);x.stroke();
  return c.toDataURL('image/png').slice(22);
})()`;

async function main() {
  const newResp = await fetch(`${PROXY}/new`, { method: 'POST', body: 'about:blank' });
  if (!newResp.ok) throw new Error(`CDP /new failed: ${newResp.status}`);
  const { targetId } = await newResp.json();
  try {
    const evalResp = await fetch(`${PROXY}/eval?target=${targetId}`, {
      method: 'POST',
      body: drawJs,
    });
    const data = await evalResp.json();
    if (!data.value) throw new Error(`CDP eval returned no value: ${JSON.stringify(data)}`);
    writeFileSync(OUT, Buffer.from(data.value, 'base64'));
    console.log(`✓ Wrote ${OUT}`);
  } finally {
    await fetch(`${PROXY}/close?target=${targetId}`).catch(() => {});
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
