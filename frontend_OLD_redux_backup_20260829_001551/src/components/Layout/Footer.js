import React from "react";
import "./Footer.css";

const Footer = () => {
  const year = new Date().getFullYear();
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-content">
          <div className="footer-section">
            <h3>درباره ما</h3>
            <p>هرمزگان هوشمند یک سیستم دانش‌گراف هوشمند برای شهر بندرعباس</p>
          </div>
          <div className="footer-section">
            <h3>تماس</h3>
            <p>📧 info@hermezgan.com</p>
            <p>📱 +98 (912) 345-6789</p>
          </div>
          <div className="footer-section">
            <h3>شبکه‌های اجتماعی</h3>
            <div className="social-links">
              <a href="#">📱</a>
              <a href="#">🐦</a>
              <a href="#">📷</a>
            </div>
          </div>
        </div>
        <div className="footer-bottom">
          <p>© {year} هرمزگان هوشمند. تمام حقوق محفوظ است.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
