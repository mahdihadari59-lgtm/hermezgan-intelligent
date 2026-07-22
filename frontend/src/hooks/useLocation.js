import { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';

const useLocation = () => {
  const dispatch = useDispatch();
  const [location, setLocation] = useState(null);
  const [isGeolocating, setIsGeolocating] = useState(false);
  const [error, setError] = useState(null);

  const getLocation = () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject('Geolocation is not supported');
        return;
      }
      setIsGeolocating(true);
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const loc = { lat: position.coords.latitude, lng: position.coords.longitude, accuracy: position.coords.accuracy };
          setLocation(loc);
          setIsGeolocating(false);
          resolve(loc);
        },
        (error) => {
          setError(error.message);
          setIsGeolocating(false);
          reject(error);
        },
        { enableHighAccuracy: true, timeout: 15000, maximumAge: 10000 }
      );
    });
  };

  const calculateDistance = (lat1, lng1, lat2, lng2) => {
    const toRad = (value) => (value * Math.PI) / 180;
    const R = 6371;
    const dLat = toRad(lat2 - lat1);
    const dLng = toRad(lng2 - lng1);
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLng / 2) * Math.sin(dLng / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  return { location, isGeolocating, error, getLocation, calculateDistance };
};

export default useLocation;
