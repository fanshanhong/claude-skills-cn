// Theme toggle — runs as early as possible to avoid FOUC
(function initTheme() {
  const stored = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = stored ?? (prefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', theme);
})();

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector<HTMLButtonElement>('.theme-toggle');
  if (!toggle) return;

  toggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
    // re-render mermaid with new theme if present
    window.dispatchEvent(new CustomEvent('theme-changed', { detail: next }));
  });
});
