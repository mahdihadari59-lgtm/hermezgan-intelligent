import React, { useMemo, useState } from 'react';
import { askCopilot, getCopilotHealth, getCopilotSources } from '../../services/copilotService';

export default function CopilotPanel() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'HDP Copilot آماده است. سوال خود را وارد کنید.' }
  ]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState(null);
  const [sources, setSources] = useState([]);
  const [error, setError] = useState('');

  const context = useMemo(() => ({
    conversationId: 'frontend-demo',
    userId: 'frontend-user',
    location: { city: 'بندرعباس', latitude: 27.1832, longitude: 56.2666 }
  }), []);

  const send = async () => {
    const q = query.trim();
    if (!q || loading) return;
    setLoading(true);
    setError('');
    setMessages(prev => [...prev, { role: 'user', text: q }]);

    try {
      const result = await askCopilot(q, context);
      setMessages(prev => [...prev, { role: 'assistant', text: result.answer || 'پاسخی دریافت نشد.' }]);
      setSources(result.sources || []);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', text: `خطا: ${e.message}` }]);
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const healthCheck = async () => {
    try {
      const h = await getCopilotHealth();
      setHealth(h);
    } catch (e) {
      setHealth({ ok: false, error: e.message });
    }
  };

  const loadSources = async () => {
    const q = query.trim();
    if (!q) return;
    try {
      const result = await getCopilotSources(q, 5);
      const merged = [...(result.items || []), ...(result.relations || [])];
      setSources(merged);
    } catch (e) {
      setError(e.message);
    }
  };

  return (
    <div dir="rtl" style={{ minHeight: '100vh', background: '#0f172a', color: '#e2e8f0', padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', background: '#111827', border: '1px solid #334155', borderRadius: 20, padding: 20 }}>
        <h1 style={{ marginTop: 0 }}>HDP Copilot</h1>
        <p style={{ lineHeight: 1.9, opacity: 0.9 }}>
          اتصال مستقیم به Hybrid/RAG موجود پروژه با پایگاه داده مرجع backend/data/hdp_v2.db.
        </p>

        <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 16 }}>
          <button onClick={healthCheck} style={btn}>Health</button>
          <button onClick={loadSources} style={btn}>Sources</button>
          <button onClick={() => setMessages([{ role: 'assistant', text: 'گفتگو پاک شد.' }])} style={btn}>Clear</button>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: 16 }}>
          <div>
            <div style={{ height: 420, overflowY: 'auto', background: '#0b1220', border: '1px solid #334155', borderRadius: 16, padding: 16 }}>
              {messages.map((m, i) => (
                <div key={i} style={{ marginBottom: 12, textAlign: m.role === 'user' ? 'right' : 'left' }}>
                  <div style={{ display: 'inline-block', maxWidth: '92%', padding: '10px 12px', borderRadius: 14, background: m.role === 'user' ? '#1d4ed8' : '#0f766e', whiteSpace: 'pre-wrap', lineHeight: 1.9 }}>
                    {m.text}
                  </div>
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => { if (e.key === 'Enter') send(); }}
                placeholder="مثال: بندرعباس را معرفی کن"
                style={input}
              />
              <button onClick={send} disabled={loading} style={btnPrimary}>{loading ? '...' : 'ارسال'}</button>
            </div>

            {error ? <div style={{ marginTop: 10, color: '#fca5a5' }}>{error}</div> : null}
            {health ? <pre style={pre}>{JSON.stringify(health, null, 2)}</pre> : null}
          </div>

          <div>
            <div style={{ background: '#0b1220', border: '1px solid #334155', borderRadius: 16, padding: 16, marginBottom: 16 }}>
              <h3 style={{ marginTop: 0 }}>Sources</h3>
              {sources.length ? sources.slice(0, 8).map((s, i) => (
                <div key={i} style={{ marginBottom: 10, paddingBottom: 10, borderBottom: '1px solid #1f2937' }}>
                  <div><b>{s.title || s.relation || 'source'}</b></div>
                  <div style={{ fontSize: 13, opacity: 0.85 }}>{s.table || 'unknown'} | score: {String(s.score ?? '')}</div>
                  {s.content ? <div style={{ marginTop: 4, fontSize: 13, lineHeight: 1.8 }}>{String(s.content).slice(0, 180)}</div> : null}
                </div>
              )) : <div style={{ opacity: 0.75 }}>خالی</div>}
            </div>

            <div style={{ background: '#0b1220', border: '1px solid #334155', borderRadius: 16, padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>راهنما</h3>
              <ul style={{ lineHeight: 2, margin: 0, paddingInlineStart: 20 }}>
                <li>Hybrid/RAG داخلی پروژه</li>
                <li>SQLite مرجع: hdp_v2.db</li>
                <li>llama.cpp محلی</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

const btn = { background: '#334155', color: '#e2e8f0', border: '1px solid #475569', borderRadius: 12, padding: '8px 12px', cursor: 'pointer' };
const btnPrimary = { background: '#38bdf8', color: '#082f49', border: 'none', borderRadius: 12, padding: '10px 18px', cursor: 'pointer', fontWeight: 700 };
const input = { flex: 1, borderRadius: 12, border: '1px solid #475569', background: '#0b1220', color: '#e2e8f0', padding: '12px 14px', outline: 'none' };
const pre = { marginTop: 12, whiteSpace: 'pre-wrap', background: '#0b1220', border: '1px solid #334155', borderRadius: 12, padding: 12, fontSize: 12 };
