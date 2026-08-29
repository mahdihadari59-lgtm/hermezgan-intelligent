const API_BASE = process.env.REACT_APP_HDP_COPILOT_API_BASE || 'http://127.0.0.1:8000/api/copilot';

export async function askCopilot(query, context = {}) {
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, context }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.detail || data?.error || 'copilot_request_failed');
  }
  return data;
}

export async function getCopilotSources(q, limit = 5) {
  const url = new URL(`${API_BASE}/sources`);
  url.searchParams.set('q', q);
  url.searchParams.set('limit', String(limit));

  const response = await fetch(url.toString());
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.detail || data?.error || 'copilot_sources_failed');
  }
  return data;
}

export async function getCopilotHealth() {
  const response = await fetch(`${API_BASE}/health`);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data?.detail || data?.error || 'copilot_health_failed');
  }
  return data;
}
