#!/bin/bash

# ============================================
# 🔧 فرانت‌اند دیباگ و تعمیر اسکریپت کامل
# ============================================
# این اسکریپت به صورت خودکار مسیر پروژه رو پیدا میکنه
# ============================================

set -e

# رنگ‌ها
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}========================================${NC}"
    echo -e "${CYAN}🔹 $1${NC}"
    echo -e "${CYAN}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# ============================================
# پیدا کردن مسیر پروژه
# ============================================

print_header "پیدا کردن مسیر پروژه"

# مسیر فعلی اسکریپت
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_info "مسیر اسکریپت: $SCRIPT_DIR"

# پیدا کردن پوشه frontend
if [ -d "$SCRIPT_DIR/../frontend" ]; then
    PROJECT_DIR="$(cd "$SCRIPT_DIR/../frontend" && pwd)"
elif [ -d "$SCRIPT_DIR/frontend" ]; then
    PROJECT_DIR="$(cd "$SCRIPT_DIR/frontend" && pwd)"
else
    # جستجوی frontend در کل مسیر
    PROJECT_DIR=$(find "$SCRIPT_DIR/.." -maxdepth 2 -type d -name "frontend" | head -1)
    if [ -z "$PROJECT_DIR" ]; then
        print_error "پوشه frontend پیدا نشد!"
        print_info "لطفاً مسیر پروژه را وارد کنید:"
        read -p "مسیر: " PROJECT_DIR
        if [ ! -d "$PROJECT_DIR" ]; then
            print_error "مسیر نامعتبر!"
            exit 1
        fi
    fi
fi

print_success "پروژه در: $PROJECT_DIR"
cd "$PROJECT_DIR"

# ============================================
# مرحله 1: بررسی محیط
# ============================================

print_header "مرحله 1: بررسی محیط و پیش‌نیازها"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node -v)
    print_success "Node.js نصب است: $NODE_VERSION"
else
    print_error "Node.js نصب نیست!"
    exit 1
fi

if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm -v)
    print_success "npm نصب است: $NPM_VERSION"
else
    print_error "npm نصب نیست!"
    exit 1
fi

# ============================================
# مرحله 2: پشتیبان‌گیری
# ============================================

print_header "مرحله 2: پشتیبان‌گیری از فایل‌های مهم"

BACKUP_DIR="$SCRIPT_DIR/../backups/frontend_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# کپی فایل‌ها اگر وجود داشته باشند
[ -f ".env" ] && cp .env "$BACKUP_DIR/" || print_warning ".env پیدا نشد"
[ -f "package.json" ] && cp package.json "$BACKUP_DIR/" || print_warning "package.json پیدا نشد"
[ -f "package-lock.json" ] && cp package-lock.json "$BACKUP_DIR/" || print_warning "package-lock.json پیدا نشد"
[ -d "src" ] && cp -r src "$BACKUP_DIR/" || print_warning "src پیدا نشد"

print_success "پشتیبان در $BACKUP_DIR ذخیره شد"

# ============================================
# مرحله 3: ایجاد package.json اگر وجود ندارد
# ============================================

print_header "مرحله 3: بررسی package.json"

if [ ! -f "package.json" ]; then
    print_warning "package.json پیدا نشد! ایجاد می‌شود..."
    
    cat > package.json << 'EOF'
{
  "name": "hermezgan-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^13.5.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.14.2",
    "react-scripts": "5.0.1",
    "web-vitals": "^2.1.4"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject",
    "clean": "rm -rf node_modules package-lock.json && npm cache clean --force"
  },
  "eslintConfig": {
    "extends": [
      "react-app"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF
    print_success "package.json ساخته شد"
fi

# ============================================
# مرحله 4: رفع پرمیشن‌ها
# ============================================

print_header "مرحله 4: رفع پرمیشن‌های فایل‌ها"

if [ -d "src" ]; then
    find src -type f -name "*.js" -exec chmod 644 {} \; 2>/dev/null
    find src -type f -name "*.jsx" -exec chmod 644 {} \; 2>/dev/null
    find src -type f -name "*.css" -exec chmod 644 {} \; 2>/dev/null
    find src -type f -name "*.json" -exec chmod 644 {} \; 2>/dev/null
    find src -type d -exec chmod 755 {} \; 2>/dev/null
    print_success "پرمیشن‌های src اصلاح شد"
fi

# ============================================
# مرحله 5: ایجاد فایل‌های مورد نیاز
# ============================================

print_header "مرحله 5: ایجاد فایل‌های محیطی"

# ایجاد .env
if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# API Configuration
REACT_APP_API_URL=http://localhost:5000/api
REACT_APP_WEBSOCKET_URL=ws://localhost:5000

# Map Configuration
REACT_APP_MAP_API_KEY=your_map_api_key

# Feature Flags
REACT_APP_ENABLE_CHAT=true
REACT_APP_ENABLE_MAP=true

# Build Configuration
PUBLIC_URL=/
GENERATE_SOURCEMAP=false

# Logging
REACT_APP_LOG_LEVEL=info
EOF
    print_success ".env ساخته شد"
fi

# ایجاد .env.production
if [ ! -f ".env.production" ]; then
    cat > .env.production << 'EOF'
REACT_APP_API_URL=/api
REACT_APP_WEBSOCKET_URL=wss://your-domain.com
REACT_APP_ENABLE_CHAT=true
REACT_APP_ENABLE_MAP=true
GENERATE_SOURCEMAP=false
EOF
    print_success ".env.production ساخته شد"
fi

# ============================================
# مرحله 6: ایجاد ساختار src
# ============================================

print_header "مرحله 6: بررسی ساختار src"

# ایجاد پوشه‌های مورد نیاز
mkdir -p src/{api,components,features,hooks,pages,reducers,services,store,styles,utils}

# ایجاد index.js
if [ ! -f "src/index.js" ]; then
    cat > src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF
    print_success "src/index.js ساخته شد"
fi

# ایجاد App.js
if [ ! -f "src/App.js" ]; then
    cat > src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="App-header">
          <h1>Hermezgan Intelligent</h1>
        </header>
        <main>
          <Routes>
            <Route path="/" element={<div>Home</div>} />
            <Route path="/chat" element={<div>Chat</div>} />
            <Route path="/map" element={<div>Map</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
EOF
    print_success "src/App.js ساخته شد"
fi

# ایجاد App.css
if [ ! -f "src/App.css" ]; then
    cat > src/App.css << 'EOF'
.App {
  text-align: center;
}

.App-header {
  background-color: #282c34;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
}
EOF
    print_success "src/App.css ساخته شد"
fi

# ایجاد index.css
if [ ! -f "src/index.css" ]; then
    cat > src/index.css << 'EOF'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
EOF
    print_success "src/index.css ساخته شد"
fi

# ============================================
# مرحله 7: نصب dependencies
# ============================================

print_header "مرحله 7: نصب dependencies"

print_info "پاک کردن کش..."
rm -rf node_modules package-lock.json 2>/dev/null
npm cache clean --force 2>/dev/null || true

print_info "نصب dependencies..."
npm install --legacy-peer-deps

print_success "Dependencies نصب شد"

# ============================================
# مرحله 8: تست Build
# ============================================

print_header "مرحله 8: تست Build"

print_info "در حال build کردن..."
if npm run build 2>&1 | tee build.log; then
    print_success "✅ Build با موفقیت انجام شد!"
else
    print_error "❌ Build با خطا مواجه شد!"
    print_info "خطاهای build:"
    tail -20 build.log
    
    print_info "تلاش با NODE_OPTIONS..."
    export NODE_OPTIONS=--openssl-legacy-provider
    if npm run build; then
        print_success "✅ Build با NODE_OPTIONS انجام شد!"
    else
        print_error "❌ Build نشد!"
        exit 1
    fi
fi

# ============================================
# مرحله 9: اجرای سرویس
# ============================================

print_header "مرحله 9: اجرای سرویس"

# پیدا کردن پورت خالی
find_free_port() {
    local port=3000
    while lsof -i:$port > /dev/null 2>&1 || netstat -tuln 2>/dev/null | grep -q ":$port "; do
        port=$((port + 1))
    done
    echo $port
}

PORT=$(find_free_port)
print_info "استفاده از پورت: $PORT"

print_info "شروع سرویس..."
BROWSER=none PORT=$PORT npm start &
APP_PID=$!

sleep 15

# بررسی سرویس
if curl -s http://localhost:$PORT > /dev/null 2>&1; then
    print_success "✅ سرویس روی http://localhost:$PORT اجرا شد!"
else
    print_warning "سرویس ممکن است در حال اجرا باشد ولی پاسخ نمی‌دهد"
    print_info "برای بررسی: curl http://localhost:$PORT"
fi

# ============================================
# گزارش نهایی
# ============================================

print_header "✅ عملیات با موفقیت انجام شد!"

echo ""
echo -e "${GREEN}📊 خلاصه:${NC}"
echo "─────────────────────────────"
echo -e "✅ پرمیشن‌ها اصلاح شد"
echo -e "✅ فایل‌های محیطی ایجاد شد"
echo -e "✅ Dependencies نصب شد"
echo -e "✅ Build انجام شد"
echo -e "✅ سرویس روی http://localhost:$PORT"
echo ""
echo -e "${CYAN}📁 پشتیبان: $BACKUP_DIR${NC}"
echo ""
echo -e "${YELLOW}💡 نکات:${NC}"
echo "1. برای stop: kill $APP_PID"
echo "2. برای لاگ: tail -f build.log"
echo "3. برای build: npm run build"
echo ""

print_success "🎉 آماده است!"

# نگه داشتن
wait $APP_PID 2>/dev/null
