// src/map/utils/popupContent.js
//
// Fix for issue #8 (Popup uses onclick="..." strings, which is not safe or
// idiomatic in React — it relies on global scope and breaks CSP).
//
// Instead we build a real DOM node with document.createElement and attach
// listeners with addEventListener. Leaflet's bindPopup() accepts an
// HTMLElement directly, so this works without needing ReactDOM portals.

/**
 * Build a popup DOM node from a simple declarative description.
 * @param {Object} opts
 * @param {string} opts.title
 * @param {Array<{label:string,value:string}>} opts.rows
 * @param {Array<{label:string,onClick:Function,tone?:'danger'|'primary'}>} [opts.actions]
 * @param {string} [opts.footer]
 */
export function buildPopup({ title, rows = [], actions = [], footer }) {
  const root = document.createElement('div');
  root.style.cssText = 'text-align:right;min-width:200px;padding:4px;';

  const h = document.createElement('h4');
  h.style.margin = '0 0 8px 0';
  h.textContent = title;
  root.appendChild(h);

  const list = document.createElement('div');
  list.style.cssText = 'display:flex;flex-direction:column;gap:4px;font-size:13px;';
  rows.forEach(({ label, value }) => {
    const row = document.createElement('span');
    row.textContent = value !== undefined ? `${label}: ${value}` : label;
    list.appendChild(row);
  });
  root.appendChild(list);

  if (actions.length) {
    const actionRow = document.createElement('div');
    actionRow.style.cssText = 'margin-top:8px;display:flex;gap:8px;';
    actions.forEach(({ label, onClick, tone }) => {
      const btn = document.createElement('button');
      btn.textContent = label;
      btn.style.cssText = `padding:4px 12px;border:none;border-radius:4px;cursor:pointer;color:white;background:${
        tone === 'danger' ? '#ff4757' : '#667eea'
      };`;
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        onClick?.();
      });
      actionRow.appendChild(btn);
    });
    root.appendChild(actionRow);
  }

  if (footer) {
    const f = document.createElement('div');
    f.style.cssText =
      'margin-top:8px;padding:4px 8px;background:#66666620;border-radius:4px;font-size:12px;';
    f.textContent = footer;
    root.appendChild(f);
  }

  return root;
}
