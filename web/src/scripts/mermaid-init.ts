// Mermaid client-side rendering
// Lazy-loads mermaid.js only on pages that contain mermaid code blocks.

import type mermaid from 'mermaid';

let mermaidApi: typeof mermaid | null = null;

async function loadMermaid(): Promise<typeof mermaid> {
  if (mermaidApi) return mermaidApi;
  const mod = await import('mermaid');
  mermaidApi = mod.default;
  return mermaidApi;
}

function getCurrentTheme(): 'default' | 'dark' {
  const theme = document.documentElement.getAttribute('data-theme');
  return theme === 'dark' ? 'dark' : 'default';
}

async function renderAll() {
  const codeBlocks = document.querySelectorAll<HTMLElement>('pre[data-language="mermaid"] > code');
  if (codeBlocks.length === 0) return;

  const m = await loadMermaid();
  m.initialize({
    startOnLoad: false,
    theme: getCurrentTheme(),
    securityLevel: 'loose',
    flowchart: { htmlLabels: true, curve: 'basis' },
    themeVariables: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif',
    },
  });

  let i = 0;
  for (const code of Array.from(codeBlocks)) {
    const pre = code.parentElement!;
    const source = code.textContent ?? '';
    const id = `mermaid-${Date.now()}-${i++}`;
    try {
      const { svg } = await m.render(id, source);
      const wrapper = document.createElement('div');
      wrapper.className = 'mermaid-block';
      wrapper.innerHTML = svg;
      pre.replaceWith(wrapper);
    } catch (err) {
      console.error('Mermaid render error:', err);
      pre.style.display = '';
      pre.classList.add('mermaid-error');
    }
  }
}

async function rerenderForTheme() {
  // For theme changes: find rendered .mermaid-block, but to keep simple,
  // a hard reload is the cheapest path. Mermaid SVG colors are baked in.
  // Mark blocks so a soft re-render is possible if desired.
  const blocks = document.querySelectorAll('.mermaid-block');
  if (blocks.length === 0) return;
  // Soft approach: do nothing — accept slight color mismatch in dark mode.
  // Hard approach below: re-render from cached source.
  const m = await loadMermaid();
  m.initialize({
    startOnLoad: false,
    theme: getCurrentTheme(),
    securityLevel: 'loose',
    themeVariables: {
      fontFamily: '-apple-system, BlinkMacSystemFont, "PingFang SC", sans-serif',
    },
  });
  let i = 0;
  for (const block of Array.from(blocks)) {
    const source = (block as HTMLElement).dataset.source;
    if (!source) continue;
    const id = `mermaid-rerender-${Date.now()}-${i++}`;
    try {
      const { svg } = await m.render(id, source);
      block.innerHTML = svg;
    } catch (err) {
      console.error('Mermaid re-render error:', err);
    }
  }
}

// Stash source on each block for theme re-render
function stashSources() {
  document.querySelectorAll<HTMLElement>('pre[data-language="mermaid"] > code').forEach(code => {
    const pre = code.parentElement!;
    pre.dataset.source = code.textContent ?? '';
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  stashSources();
  // After render, .mermaid-block carries data-source from its replaced pre
  const codeBlocks = document.querySelectorAll<HTMLElement>('pre[data-language="mermaid"] > code');
  const sources: string[] = [];
  codeBlocks.forEach(code => sources.push(code.textContent ?? ''));

  await renderAll();

  // Attach source data to the rendered blocks (in DOM order)
  const blocks = document.querySelectorAll<HTMLElement>('.mermaid-block');
  blocks.forEach((block, idx) => {
    if (sources[idx]) block.dataset.source = sources[idx];
  });
});

window.addEventListener('theme-changed', () => {
  rerenderForTheme();
});
