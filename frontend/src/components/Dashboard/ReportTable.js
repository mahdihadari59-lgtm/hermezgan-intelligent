import React from 'react';
import './ReportTable.css';

const ReportTable = () => {
  const reports = [
    { id: 1, user: 'علی محمدی', action: 'جستجوی بیمارستان', time: '۱۰ دقیقه پیش', status: 'موفق' },
    { id: 2, user: 'فاطمه احمدی', action: 'درخواست مسیریابی', time: '۲۵ دقیقه پیش', status: 'موفق' },
    { id: 3, user: 'محمد رضایی', action: 'جستجوی رستوران', time: '۴۵ دقیقه پیش', status: 'موفق' },
    { id: 4, user: 'زهرا کریمی', action: 'درخواست تاکسی', time: '۱ ساعت پیش', status: 'درحال انجام' },
    { id: 5, user: 'حسین نادری', action: 'مشاهده دوربین‌ها', time: '۲ ساعت پیش', status: 'موفق' }
  ];

  return (
    <div className="report-table-wrapper">
      <table className="report-table">
        <thead>
          <tr>
            <th>کاربر</th>
            <th>عملیات</th>
            <th>زمان</th>
            <th>وضعیت</th>
          </tr>
        </thead>
        <tbody>
          {reports.map((report) => (
            <tr key={report.id}>
              <td>
                <div className="table-user">
                  <span className="user-avatar">{report.user.charAt(0)}</span>
                  {report.user}
                </div>
              </td>
              <td>{report.action}</td>
              <td className="time-cell">{report.time}</td>
              <td>
                <span className={`status-badge ${report.status === 'موفق' ? 'success' : 'pending'}`}>
                  {report.status}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ReportTable;
