const WS_BASE = process.env.REACT_APP_HDP_COPILOT_WS_BASE || 'ws://127.0.0.1:8000/api/v1/ws/chat';
export function createHdpSocket({ onMessage, onOpen, onClose, onError } = {}) {
  const ws = new WebSocket(WS_BASE);
  ws.onopen = () => onOpen?.();
  ws.onclose = () => onClose?.();
  ws.onerror = (e) => onError?.(e);
  ws.onmessage = (event) => {
    try { onMessage?.(JSON.parse(event.data)); }
    catch { onMessage?.({ type: 'raw', data: event.data }); }
  };
  return ws;
}
