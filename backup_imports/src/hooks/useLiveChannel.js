// src/services/useLiveChannel.js
//
// FIX #16: no live-data mechanism existed for traffic/GPS/taxi/driver/
// accident/police/weather updates. This hook opens a single shared
// WebSocket to HDP's realtime endpoint, subscribes to a named channel, and
// invokes a callback per message. Reconnects with backoff on drop.

import { useEffect, useRef } from 'react';

const WS_URL = process.env.REACT_APP_REALTIME_WS_URL || 'wss://realtime.hormozgandriver.ir/ws';

let sharedSocket = null;
let sharedListeners = new Map(); // channel -> Set<callback>
let reconnectAttempt = 0;
let reconnectTimer = null;

function ensureSocket() {
  if (sharedSocket && sharedSocket.readyState <= WebSocket.OPEN) return sharedSocket;

  const socket = new WebSocket(WS_URL);
  sharedSocket = socket;

  socket.onmessage = (event) => {
    try {
      const msg = JSON.parse(event.data);
      const callbacks = sharedListeners.get(msg.channel);
      callbacks?.forEach((cb) => cb(msg.payload));
    } catch (err) {
      console.error('[useLiveChannel] bad message', err);
    }
  };

  socket.onclose = () => {
    reconnectAttempt += 1;
    const delay = Math.min(30000, 1000 * 2 ** reconnectAttempt);
    reconnectTimer = setTimeout(() => {
      if (sharedListeners.size > 0) ensureSocket();
    }, delay);
  };

  socket.onopen = () => {
    reconnectAttempt = 0;
  };

  return socket;
}

/**
 * Subscribe to a live-update channel, e.g. 'traffic', 'gps', 'taxi',
 * 'driver', 'accident', 'police', 'weather'.
 */
export function useLiveChannel(channel, onMessage) {
  const cbRef = useRef(onMessage);
  cbRef.current = onMessage;

  useEffect(() => {
    const wrapped = (payload) => cbRef.current(payload);

    if (!sharedListeners.has(channel)) sharedListeners.set(channel, new Set());
    sharedListeners.get(channel).add(wrapped);
    ensureSocket();

    return () => {
      const set = sharedListeners.get(channel);
      set?.delete(wrapped);
      if (set && set.size === 0) sharedListeners.delete(channel);
      if (sharedListeners.size === 0) {
        clearTimeout(reconnectTimer);
        sharedSocket?.close();
        sharedSocket = null;
      }
    };
  }, [channel]);
}
