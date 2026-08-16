
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './SettingsPage.css';

const SettingsPage = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = 'Settings - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="settingspage-page">
      <h1>SettingsPage</h1>
      <p>محتوای صفحه SettingsPage</p>
    </div>
  );
};

export default SettingsPage;
