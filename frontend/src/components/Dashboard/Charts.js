import React from 'react';
import './Charts.css';

const Charts = () => {
  // داده‌های نمونه برای نمودار
  const data = [
    { day: 'شنبه', users: 120, queries: 240 },
    { day: 'یکشنبه', users: 150, queries: 280 },
    { day: 'دوشنبه', users: 130, queries: 220 },
    { day: 'سه‌شنبه', users: 180, queries: 310 },
    { day: 'چهارشنبه', users: 160, queries: 290 },
    { day: 'پنجشنبه', users: 200, queries: 350 },
    { day: 'جمعه', users: 170, queries: 300 }
  ];

  const maxValue = Math.max(...data.map(d => Math.max(d.users, d.queries)));

  return (
    <div className="charts-container">
      <div className="chart-card">
        <h3 className="chart-title">📈 رشد کاربران و پرس‌وجوها</h3>
        <div className="chart-wrapper">
          <div className="chart-bars">
            {data.map((item, index) => (
              <div key={index} className="chart-bar-group">
                <div className="chart-bar">
                  <div 
                    className="bar-users" 
                    style={{ height: `${(item.users / maxValue) * 100}%` }}
                    title={`کاربران: ${item.users}`}
                  />
                  <div 
                    className="bar-queries" 
                    style={{ height: `${(item.queries / maxValue) * 100}%` }}
                    title={`پرس‌وجوها: ${item.queries}`}
                  />
                </div>
                <span className="bar-label">{item.day}</span>
              </div>
            ))}
          </div>
        </div>
        <div className="chart-legend">
          <span><span className="legend-dot users-dot"></span> کاربران</span>
          <span><span className="legend-dot queries-dot"></span> پرس‌وجوها</span>
        </div>
      </div>

      <div className="chart-card">
        <h3 className="chart-title">📊 توزیع خدمات</h3>
        <div className="pie-chart">
          <div className="pie-slice hospital">25%</div>
          <div className="pie-slice restaurant">20%</div>
          <div className="pie-slice taxi">35%</div>
          <div className="pie-slice pharmacy">15%</div>
          <div className="pie-slice school">5%</div>
        </div>
        <div className="pie-legend">
          <span><span className="pie-dot hospital-dot"></span> بیمارستان</span>
          <span><span className="pie-dot restaurant-dot"></span> رستوران</span>
          <span><span className="pie-dot taxi-dot"></span> تاکسی</span>
          <span><span className="pie-dot pharmacy-dot"></span> داروخانه</span>
          <span><span className="pie-dot school-dot"></span> مدرسه</span>
        </div>
      </div>
    </div>
  );
};

export default Charts;
