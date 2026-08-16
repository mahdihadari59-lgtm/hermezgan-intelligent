// src/map/OfflineManager.jsx
// Updated to match offlineCache's real downloadArea(bounds, zoom, onProgress)
// signature (see services/offlineCache.js, FIX #5) and to add a cancel button.

import React, { useState, useEffect } from 'react';
import { openDB } from 'idb';
import { Download, Wifi, Database, X } from 'lucide-react';
import { offlineCache } from '../services/offlineCache';

const OfflineManager = ({ isOffline, onToggle, onDownload }) => {
  const [progress, setProgress] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const [tileCount, setTileCount] = useState(0);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const db = await openDB('offline_tiles', 1);
        const count = await db.count('tiles');
        if (!cancelled) setTileCount(count);
      } catch (error) {
        console.error('Error loading tile count:', error);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [isDownloading]);

  const handleDownload = async () => {
    setIsDownloading(true);
    setProgress(0);
    try {
      await onDownload((fraction) => setProgress(fraction * 100));
      const stats = await offlineCache.getStats();
      setTileCount(stats.count);
    } catch (error) {
      console.error('Download error:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleCancel = () => {
    offlineCache.cancelDownload();
    setIsDownloading(false);
  };

  return (
    <div className="offline-manager">
      <div className="offline-controls">
        <button className={`offline-toggle ${isOffline ? 'active' : ''}`} onClick={onToggle}>
          {isOffline ? <Wifi size={18} /> : <Database size={18} />}
          <span>{isOffline ? 'آفلاین' : 'آنلاین'}</span>
        </button>

        {!isOffline && !isDownloading && (
          <button className="download-btn" onClick={handleDownload}>
            <Download size={18} />
            <span>دانلود منطقه</span>
          </button>
        )}

        {isDownloading && (
          <button className="download-btn" onClick={handleCancel}>
            <X size={18} />
            <span>{Math.round(progress)}% — لغو</span>
          </button>
        )}
      </div>

      {isOffline && tileCount > 0 && (
        <div className="offline-status">
          <span>📦 {tileCount} کاشی ذخیره شده</span>
        </div>
      )}
    </div>
  );
};

export default OfflineManager;
