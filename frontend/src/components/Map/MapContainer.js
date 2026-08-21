import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { MapContainer as LeafletMap, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import { setMarkers, setCenter, setUserLocation, selectMarker } from '../store/slices/mapSlice';
import mapService from '../../services/mapService';
import 'leaflet/dist/leaflet.css';

// Fix marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapUpdater = ({ center, zoom }) => {
  const map = useMap();
  useEffect(() => {
    if (center?.lat && center?.lng) {
      map.setView([center.lat, center.lng], zoom);
    }
  }, [center, zoom, map]);
  return null;
};

const MapContainer = () => {
  const dispatch = useDispatch();
  const { center, zoom, markers, selectedMarker } = useSelector((state) => state.map);
  const [showPopup, setShowPopup] = useState(false);

  useEffect(() => {
    mapService.getUserLocation()
      .then((location) => {
        dispatch(setUserLocation(location));
        dispatch(setCenter(location));
      })
      .catch(() => {
        dispatch(setCenter({ lat: 27.2158, lng: 56.2808 }));
      });

    mapService.getNearest(27.2158, 56.2808, 10)
      .then((data) => dispatch(setMarkers(data || [])))
      .catch(() => {});
  }, [dispatch]);

  return (
    <div className="map-container" style={{ height: '500px', borderRadius: '12px', overflow: 'hidden' }}>
      <LeafletMap center={[center.lat, center.lng]} zoom={zoom} style={{ height: '100%', width: '100%' }}>
        <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution='&copy; OpenStreetMap' />
        <MapUpdater center={center} zoom={zoom} />
        {markers.map((m) => (
          <Marker
            key={m.id}
            position={[m.lat, m.lng]}
            eventHandlers={{ click: () => { dispatch(selectMarker(m)); setShowPopup(true); } }}
          >
            <Popup>
              <strong>{m.name}</strong><br />
              {m.type && <>📂 {m.type}<br /></>}
              {m.distance && <>📏 {m.distance} کیلومتر</>}
            </Popup>
          </Marker>
        ))}
      </LeafletMap>
    </div>
  );
};

export default MapContainer;
