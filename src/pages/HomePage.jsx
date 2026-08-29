
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './HomePage.css';

const HomePage = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = 'Home - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="homepage-page">
      <h1>HomePage</h1>
      <p>محتوای صفحه HomePage</p>
    </div>
  );
};

export default HomePage;
