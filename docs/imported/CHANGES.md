# HDP Map Engine — Bug Fix Pass

Fixes every item from the production-readiness review, file by file.

| # | Issue | Fix | File(s) |
|---|---|---|---|
| 1 | ClusterManager renders `<div>` children — react-leaflet-cluster can't read them | Real `<Marker>` children, canvas renderer | `ClusterManager.jsx` |
| 2 | Routing hardcoded to public OSRM demo server | Configurable via `REACT_APP_ROUTING_URL`, real waypoints, cleanup | `RoutingManager.jsx` |
| 3 | Vector tile URL (`tile.openstreetmap.org/.../{y}.pbf`) doesn't exist | Configurable `REACT_APP_VECTOR_TILE_URL`, no-op with a warning if unset | `VectorTileLayer.jsx` |
| 4 | GeoTIFF fetched a fake URL and displayed an unrelated hardcoded PNG | Fetches a real dataset, rasterizes actual pixel data onto canvas, uses real georeferenced bounds | `GeoTiffLayer.jsx` |
| 5 | `offlineCache.downloadArea()` was an empty stub | Real tile downloader: tile enumeration, bounded concurrency (6), retry w/ backoff, versioning, stale-cache pruning | `services/offlineCache.js` |
| 5b | (bonus) offline base layer pointed at a static path that download never wrote to | Custom `L.TileLayer` reading tiles back out of IndexedDB | `OfflineTileLayer.jsx` |
| 6 | Weather layer showed a hardcoded uniform wind grid | Fetches real wind data via `mapApi.getWindData`; renders nothing until data arrives | `WeatherLayer.jsx`, `mapApi.js` |
| 7 | All data layers hardcoded (Camera/Hospital/Fuel/Tourism/Traffic) | Fetch from `mapApi`, hardcoded arrays kept only as offline/dev fallback | `CameraLayer.jsx`, `HospitalLayer.jsx`, `FuelLayer.jsx`, `TourismLayer.jsx`, `TrafficLayer.jsx` |
| 8 | Popups used `onclick="alert(...)"` inline strings | `buildPopup()` helper builds real DOM nodes with `addEventListener` | `utils/popupContent.js`, all data layers |
| 9 | `MapLayers.jsx` built a second, duplicate `L.control.layers` | Removed entirely; `MapEngine`'s `<LayersControl>` is the single source | `MapEngine.jsx` (MapLayers deleted) |
| 10 | `MarkerManager` removed & recreated every marker on every render | Diff-based add/update/remove keyed by marker id | `MarkerManager.jsx` |
| 11 | `map.on(...)` never paired with `map.off(...)` → listener leaks | Named handlers stored in refs, removed on unmount, everywhere | `MapEngine.jsx`, `DrawTools.jsx`, `RoutingManager.jsx`, all layers |
| 12 | `useCallback(debounce(...))` recreated timers, never cancelled | `useMemo` for the debounced fn + `.cancel()` on unmount | `MapEngine.jsx` |
| 13 | Draw `edit.featureGroup` created but never added to map, created shapes never registered | `featureGroup` added to map; `CREATED` handler pushes shapes into it | `DrawTools.jsx` |
| 14 | All markers use `divIcon` → DOM-heavy, poor FPS at scale | Canvas renderer wired in for cluster/marker layers where possible; full fix requires server-side clustering/vector tiles — flagged, not fully solvable client-side | `ClusterManager.jsx`, `MarkerManager.jsx` |
| 15 | `leaflet.heat` installed but unused | New `HeatmapLayer.jsx`, wired into the "🔥" map mode | `HeatmapLayer.jsx`, `MapEngine.jsx` |
| 16 | No live updates (traffic/GPS/taxi/driver/accident/police/weather) | `useLiveChannel` WebSocket hook with reconnect/backoff; wired into `TrafficLayer` as an example | `services/useLiveChannel.js`, `TrafficLayer.jsx` |
| 17 | Won't scale to 100k+ POIs | Partially addressed (diffing, canvas renderer, chunked clustering). Full fix needs backend: PostGIS + supercluster/vector tiles + spatial index — out of scope for a frontend-only pass | — |

## Also fixed in passing
- `TourismLayer`: `background: '#ff6b6b';` inside a template literal put literal quote characters into the CSS value, so every tourism marker rendered with no background color.
- All layers now clean up their `useMap()` layer refs symmetrically on unmount (was inconsistent before).

## Required environment variables (new)
```
REACT_APP_ROUTING_URL=https://your-osrm-or-graphhopper-host/route/v1
REACT_APP_VECTOR_TILE_URL=https://your-tileserver/{z}/{x}/{y}.pbf
REACT_APP_VECTOR_TILE_KEY=            # if using a hosted provider like MapTiler
REACT_APP_OFFLINE_TILE_URL=https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png
REACT_APP_REALTIME_WS_URL=wss://your-realtime-host/ws
REACT_APP_DEM_URL=https://your-storage/hormozgan_dem.tif
REACT_APP_API_URL=http://localhost:8000/api/v1
```
None of these have working defaults pointing at third parties anymore — layers now either read from an explicit env var or render nothing with a console warning, rather than silently hitting a URL that doesn't do what the original code assumed.

## Still open (backend work, not fixable from the frontend alone)
- Real OSRM/GraphHopper/Valhalla deployment for `REACT_APP_ROUTING_URL`
- Real vector tile server (TileServer-GL / OpenMapTiles) for `REACT_APP_VECTOR_TILE_URL`
- `/api/v1/map/*` REST endpoints backed by the 8-database split (`geo.db`, `events.db`, etc.)
- WebSocket server publishing `{channel, payload}` messages for `useLiveChannel`
- Server-side clustering (supercluster) or vector-tile POI rendering for the 100k+ scale case (#17)
