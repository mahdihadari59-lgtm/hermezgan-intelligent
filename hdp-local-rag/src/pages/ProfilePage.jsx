
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './ProfilePage.css';

const ProfilePage = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = 'Profile - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="profilepage-page">
      <h1>ProfilePage</h1>
      <p>محتوای صفحه ProfilePage</p>
    </div>
  );
};

export default ProfilePage;
