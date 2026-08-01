const API_BASE = process.env.REACT_APP_HDP_COPILOT_API_BASE || 'http://127.0.0.1:8000/api/v1/orchestrator';
export async function askOrchestrator(input, context = {}) {
  const query = typeof input === 'string' ? input : (input?.query || input?.message || input?.text || '');
  const response = await fetch(`${API_BASE}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query, ...context }),
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.detail || data?.error || 'orchestrator_request_failed');
  return data;
}
export async function getOrchestratorHealth() {
  const response = await fetch(`${API_BASE}/health`);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data?.detail || data?.error || 'orchestrator_health_failed');
  return data;
}
