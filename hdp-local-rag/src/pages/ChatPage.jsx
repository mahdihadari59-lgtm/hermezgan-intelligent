
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './ChatPage.css';

const ChatPage = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = 'Chat - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="chatpage-page">
      <h1>ChatPage</h1>
      <p>محتوای صفحه ChatPage</p>
    </div>
  );
};

export default ChatPage;
