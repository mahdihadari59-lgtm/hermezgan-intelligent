import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import StatCards from './StatCards';
import Charts from './Charts';
import ReportTable from './ReportTable';
import { setStats, setLoading, setError } from '../../features/dashboard/dashboardSlice';
import './DashboardLayout.css';

const DashboardLayout = () => {
  const dispatch = useDispatch();
  const { stats, isLoading } = useSelector((state) => state.dashboard);
  const [dateRange, setDateRange] = useState('week');

  // Load dashboard data
  useEffect(() => {
    dispatch(setLoading(true));
    // Simulate API call
    setTimeout(() => {
      dispatch(setStats({
        totalUsers: 1234,
        activeUsers: 856,
        totalServices: 567,
        totalChats: 3421
      }));
      dispatch(setLoading(false));
    }, 1000);
  }, [dispatch]);

  return (
    <div className="dashboard-layout">
      <div className="dashboard-header">
        <div className="header-title">
          <h1>📊 داشبورد تحلیلی</h1>
          <p>نمای کلی عملکرد سیستم هرمزگان هوشمند</p>
        </div>
        <div className="header-actions">
          <select 
            className="date-filter"
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value)}
          >
            <option value="day">امروز</option>
            <option value="week">این هفته</option>
            <option value="month">این ماه</option>
            <option value="year">این سال</option>
          </select>
          <button className="refresh-btn" onClick={() => window.location.reload()}>
            🔄 به‌روزرسانی
          </button>
        </div>
      </div>

      {isLoading ? (
        <div className="loading-state">⏳ در حال بارگذاری...</div>
      ) : (
        <>
          <StatCards stats={stats} />
          <div className="dashboard-section">
            <Charts />
          </div>
          <div className="dashboard-section">
            <h2 className="section-title">📋 فعالیت‌های اخیر</h2>
            <ReportTable />
          </div>
        </>
      )}
    </div>
  );
};

export default DashboardLayout;
