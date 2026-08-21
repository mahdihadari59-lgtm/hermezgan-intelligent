import React, { useState } from 'react';
import { askOrchestrator, getOrchestratorHealth } from '../../services/orchestratorService';

export default function OrchestratorPanel() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([{ role: 'assistant', text: 'HDP Orchestrator v2 آماده است.' }]);
  const [health, setHealth] = useState(null);

  const context = {
    conversationId: 'frontend-demo',
    userId: 'frontend-user',
    location: { city: 'بندرعباس', latitude: 27.1832, longitude: 56.2666 },
    mode: 'text',
  };

  const send = async () => {
    const q = query.trim();
    if (!q) return;
    setMessages(prev => [...prev, { role: 'user', text: q }]);
    try {
      const res = await askOrchestrator(q, context);
      setMessages(prev => [...prev, { role: 'assistant', text: res.answer || res.text || 'پاسخ دریافت نشد.' }]);
    } catch (e) {
      setMessages(prev => [...prev, { role: 'assistant', text: `خطا: ${e.message}` }]);
    }
  };

  const check = async () => {
    try { setHealth(await getOrchestratorHealth()); }
    catch (e) { setHealth({ ok: false, error: e.message }); }
  };

  return (
    <div dir="rtl" style={{ minHeight: '100vh', background: '#0f172a', color: '#e2e8f0', padding: 24, fontFamily: 'system-ui, sans-serif' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', background: '#111827', border: '1px solid #334155', borderRadius: 20, padding: 20 }}>
        <h1 style={{ marginTop: 0 }}>HDP Orchestrator v2</h1>
        <p style={{ opacity: 0.9, lineHeight: 1.9 }}>
          یک نقطه ورود واحد برای Bandari، Vosk، Intent، Expert Dispatcher و Hybrid/RAG.
        </p>

        <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
          <button onClick={check} style={btn}>Health</button>
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
                placeholder="سوال خود را بنویسید..."
                style={input}
              />
              <button onClick={send} style={btnPrimary}>ارسال</button>
            </div>
          </div>

          <div>
            <div style={{ background: '#0b1220', border: '1px solid #334155', borderRadius: 16, padding: 16 }}>
              <h3 style={{ marginTop: 0 }}>وضعیت</h3>
              <pre style={pre}>{JSON.stringify(health, null, 2)}</pre>
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
const pre = { whiteSpace: 'pre-wrap', background: '#0b1220', border: '1px solid #334155', borderRadius: 12, padding: 12, fontSize: 12 };
