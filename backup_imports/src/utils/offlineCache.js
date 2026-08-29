// src/services/offlineCache.js
//
// FIX #5: downloadArea() was previously a `console.log` stub. This
// implements an actual tile downloader:
//   - enumerates tiles for the given bounds/zoom range
//   - downloads with a bounded concurrency queue
//   - retries failed tiles (exponential backoff, max 3 attempts)
//   - stores a schema `version` + `savedAt` per tile for cache-policy checks
//   - exposes progress callback and cancellation
//
// Storage remains IndexedDB via `idb`, matching the rest of the stack's
// stdlib/sqlite-first, no-heavy-backend-dependency preference.

import { openDB } from 'idb';

const DB_NAME = 'offline_tiles';
const DB_VERSION = 1;
const CACHE_SCHEMA_VERSION = 1;
const MAX_TILE_AGE_MS = 30 * 24 * 60 * 60 * 1000; // 30 days
const CONCURRENCY = 6;
const MAX_RETRIES = 3;

class OfflineCache {
  constructor() {
    this.db = null;
    this.isEnabled = false;
    this._cancelToken = null;
  }

  async init() {
    if (this.db) return this.db;
    this.db = await openDB(DB_NAME, DB_VERSION, {
      upgrade(db) {
        if (!db.objectStoreNames.contains('tiles')) {
          const store = db.createObjectStore('tiles', { keyPath: 'key' });
          store.createIndex('timestamp', 'timestamp');
        }
        if (!db.objectStoreNames.contains('metadata')) {
          db.createObjectStore('metadata', { keyPath: 'id' });
        }
      },
    });
    return this.db;
  }

  async enable() {
    await this.init();
    this.isEnabled = true;
  }

  async disable() {
    this.isEnabled = false;
  }

  _tileKey(z, x, y) {
    return `${z}/${x}/${y}`;
  }

  _tilesForBounds(bounds, zoom) {
    const lng2tile = (lng, z) => Math.floor(((lng + 180) / 360) * 2 ** z);
    const lat2tile = (lat, z) =>
      Math.floor(
        ((1 -
          Math.log(Math.tan((lat * Math.PI) / 180) + 1 / Math.cos((lat * Math.PI) / 180)) /
            Math.PI) /
          2) *
          2 ** z
      );

    const xMin = lng2tile(bounds.getWest(), zoom);
    const xMax = lng2tile(bounds.getEast(), zoom);
    const yMin = lat2tile(bounds.getNorth(), zoom);
    const yMax = lat2tile(bounds.getSouth(), zoom);

    const tiles = [];
    for (let x = xMin; x <= xMax; x += 1) {
      for (let y = yMin; y <= yMax; y += 1) {
        tiles.push({ z: zoom, x, y });
      }
    }
    return tiles;
  }

  /**
   * Downloads all tiles for `bounds` across zoom levels
   * [zoom, zoom + extraZoomLevels], with retry + progress reporting.
   * @returns {{cancel: Function}} handle to cancel an in-flight download
   */
  async downloadArea(bounds, zoom, onProgress, { extraZoomLevels = 2, tileUrlTemplate } = {}) {
    await this.init();
    const urlTemplate =
      tileUrlTemplate ||
      process.env.REACT_APP_OFFLINE_TILE_URL ||
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
    const subdomains = ['a', 'b', 'c'];

    let allTiles = [];
    for (let z = zoom; z <= zoom + extraZoomLevels; z += 1) {
      allTiles = allTiles.concat(this._tilesForBounds(bounds, z));
    }

    let cancelled = false;
    this._cancelToken = () => {
      cancelled = true;
    };

    let completed = 0;
    const total = allTiles.length;

    const downloadOne = async (tile, attempt = 1) => {
      if (cancelled) return;
      const s = subdomains[(tile.x + tile.y) % subdomains.length];
      const url = urlTemplate
        .replace('{s}', s)
        .replace('{z}', tile.z)
        .replace('{x}', tile.x)
        .replace('{y}', tile.y);

      try {
        const resp = await fetch(url);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const blob = await resp.blob();
        await this.saveTile(this._tileKey(tile.z, tile.x, tile.y), blob);
      } catch (err) {
        if (attempt < MAX_RETRIES && !cancelled) {
          const backoff = 300 * 2 ** attempt;
          await new Promise((r) => setTimeout(r, backoff));
          return downloadOne(tile, attempt + 1);
        }
        console.error('[offlineCache] failed to download tile', tile, err);
      } finally {
        completed += 1;
        onProgress?.(completed / total);
      }
      return undefined;
    };

    // Bounded-concurrency queue
    let index = 0;
    const workers = Array.from({ length: Math.min(CONCURRENCY, total || 1) }, async () => {
      while (index < allTiles.length && !cancelled) {
        const tile = allTiles[index];
        index += 1;
        await downloadOne(tile);
      }
    });

    await Promise.all(workers);

    await this.db.put('metadata', {
      id: 'lastDownload',
      version: CACHE_SCHEMA_VERSION,
      savedAt: Date.now(),
      tileCount: total,
      bounds: {
        north: bounds.getNorth(),
        south: bounds.getSouth(),
        east: bounds.getEast(),
        west: bounds.getWest(),
      },
    });

    return { cancelled, total, completed };
  }

  cancelDownload() {
    this._cancelToken?.();
  }

  async getTile(key) {
    await this.init();
    const tile = await this.db.get('tiles', key);
    if (!tile) return null;
    // Cache policy: drop stale tiles
    if (Date.now() - tile.timestamp > MAX_TILE_AGE_MS) {
      await this.db.delete('tiles', key);
      return null;
    }
    if (tile.version !== CACHE_SCHEMA_VERSION) {
      await this.db.delete('tiles', key);
      return null;
    }
    return tile;
  }

  async saveTile(key, blob) {
    await this.init();
    return this.db.put('tiles', {
      key,
      blob,
      version: CACHE_SCHEMA_VERSION,
      timestamp: Date.now(),
    });
  }

  async getStats() {
    await this.init();
    const count = await this.db.count('tiles');
    return { count };
  }

  async clear() {
    await this.init();
    await this.db.clear('tiles');
    await this.db.clear('metadata');
  }

  /** Removes tiles older than MAX_TILE_AGE_MS or from a previous schema version. */
  async pruneStale() {
    await this.init();
    const all = await this.db.getAll('tiles');
    const stale = all.filter(
      (t) => Date.now() - t.timestamp > MAX_TILE_AGE_MS || t.version !== CACHE_SCHEMA_VERSION
    );
    await Promise.all(stale.map((t) => this.db.delete('tiles', t.key)));
    return stale.length;
  }
}

export const offlineCache = new OfflineCache();
