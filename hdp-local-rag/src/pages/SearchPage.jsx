
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './SearchPage.css';

const SearchPage = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = 'Search - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="searchpage-page">
      <h1>SearchPage</h1>
      <p>محتوای صفحه SearchPage</p>
    </div>
  );
};

export default SearchPage;
