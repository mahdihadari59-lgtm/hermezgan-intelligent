
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './MapPage.css';

const MapPage = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = 'Map - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="mappage-page">
      <h1>MapPage</h1>
      <p>محتوای صفحه MapPage</p>
    </div>
  );
};

export default MapPage;
