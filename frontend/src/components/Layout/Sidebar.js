import React from "react";
import { useDispatch, useSelector } from "react-redux";
import { Link, useLocation } from "react-router-dom";
import { toggleSidebar } from "../../store/slices/uiSlice";
import "./Sidebar.css";

const Sidebar = () => {
  const dispatch = useDispatch();
  const { isSidebarOpen } = useSelector((state) => state.ui);
  const location = useLocation();

  const menuItems = [
    { id: 1, title: "خانه", icon: "🏠", path: "/" },
    { id: 2, title: "چت‌بات", icon: "💬", path: "/chat" },
    { id: 3, title: "نقشه", icon: "🗺️", path: "/map" },
    { id: 4, title: "داشبورد", icon: "📊", path: "/dashboard" },
  ];

  return (
    <>
      {isSidebarOpen && <div className="sidebar-overlay" onClick={() => dispatch(toggleSidebar())} />}
      <aside className={`sidebar ${isSidebarOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <h2 className="sidebar-title">📋 منو</h2>
          <button className="sidebar-close" onClick={() => dispatch(toggleSidebar())}>✕</button>
        </div>
        <nav className="sidebar-nav">
          {menuItems.map((item) => (
            <Link
              key={item.id}
              to={item.path}
              className={`menu-item ${location.pathname === item.path ? "active" : ""}`}
            >
              <span className="menu-icon">{item.icon}</span>
              <span className="menu-text">{item.title}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          <button className="logout-btn">🚪 خروج</button>
        </div>
      </aside>
    </>
  );
};

export default Sidebar;
