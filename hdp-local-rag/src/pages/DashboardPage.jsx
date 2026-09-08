
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './DashboardPage.css';

const DashboardPage = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = 'Dashboard - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="dashboardpage-page">
      <h1>DashboardPage</h1>
      <p>محتوای صفحه DashboardPage</p>
    </div>
  );
};

export default DashboardPage;
