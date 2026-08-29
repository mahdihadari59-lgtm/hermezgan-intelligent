import React from "react";
import { useDispatch } from "react-redux";
import { toggleSidebar } from "../../store/slices/uiSlice";
import "./Header.css";

const Header = () => {
  const dispatch = useDispatch();

  return (
    <header className="header">
      <div className="header-container">
        <div className="header-left">
          <button className="menu-toggle" onClick={() => dispatch(toggleSidebar())}>
            ☰
          </button>
          <div className="logo-section">
            <h1 className="logo-text">🌊 هرمزگان هوشمند</h1>
            <p className="logo-subtitle">سیستم دانش‌گراف شهر بندرعباس</p>
          </div>
        </div>
        <div className="header-center">
          <input type="text" placeholder="جستجو..." className="search-input" />
        </div>
        <div className="header-right">
          <button className="header-icon-btn">🔔</button>
          <div className="user-profile">
            <img src="https://ui-avatars.com/api/?name=User&background=667eea&color=fff" alt="پروفایل" className="user-avatar" />
            <div className="user-info">
              <p className="user-name">کاربر</p>
              <p className="user-status">فعال</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
