const fs = require('fs');
const path = require('path');

const CONFIG = {
  rootDir: path.join(__dirname, '..'),
  srcDir: path.join(__dirname, '..', 'src'),
  modules: {
    store: {
      path: 'store',
      slices: [
        { name: 'ui', actions: ['toggleSidebar', 'setTheme', 'addNotification'] },
        { name: 'auth', actions: ['login', 'logout', 'register'] },
        { name: 'chat', actions: ['addMessage', 'setTyping', 'clearMessages'] },
        { name: 'map', actions: ['setMapCenter', 'setZoom', 'setMarkers'] },
        { name: 'hotspot', actions: ['setHotspots', 'selectHotspot'] },
        { name: 'camera', actions: ['setCameras', 'selectCamera'] },
        { name: 'dashboard', actions: ['setStats', 'setUserGrowth'] }
      ]
    },
    components: {
      path: 'components',
      modules: [
        { name: 'Chat', files: ['ChatBox.jsx', 'MessageList.jsx', 'MessageInput.jsx', 'ChatBubble.jsx', 'TypingIndicator.jsx'] },
        { name: 'Map', files: ['MapContainer.jsx', 'MapMarkers.jsx', 'MapSearch.jsx', 'MapPopup.jsx'] },
        { name: 'Hotspots', files: ['HotspotFilter.jsx', 'HotspotList.jsx'] },
        { name: 'Camera', files: ['CameraFilter.jsx', 'CameraList.jsx', 'CameraInfo.jsx'] },
        { name: 'Dashboard', files: ['DashboardLayout.jsx', 'StatCards.jsx', 'Charts.jsx'] },
        { name: 'Layout', files: ['Header.jsx', 'Sidebar.jsx', 'Footer.jsx'] },
        { name: 'Common', files: ['Button.jsx', 'Card.jsx', 'Loading.jsx', 'Modal.jsx', 'Toast.jsx'] }
      ]
    },
    pages: {
      path: 'pages',
      files: ['HomePage.jsx', 'ChatPage.jsx', 'MapPage.jsx', 'DashboardPage.jsx', 'SearchPage.jsx', 'ProfilePage.jsx', 'SettingsPage.jsx']
    },
    services: {
      path: 'services',
      files: ['api.js', 'chatService.js', 'mapService.js', 'hotspotService.js', 'cameraService.js', 'analyticsService.js']
    },
    hooks: {
      path: 'hooks',
      files: ['useAuth.js', 'useMap.js', 'useChat.js', 'useHotspot.js', 'useCamera.js', 'useToast.js', 'useLocalStorage.js']
    },
    utils: {
      path: 'utils',
      files: ['helpers.js', 'validators.js', 'constants.js', 'formatters.js']
    },
    assets: {
      path: 'assets',
      subdirs: ['icons', 'images', 'fonts', 'styles']
    }
  }
};

const log = (msg, color) => {
  const colors = { green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m', red: '\x1b[31m', reset: '\x1b[0m' };
  console.log(`${colors[color] || ''}${msg}${colors.reset}`);
};

const createDir = (dirPath) => {
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    log(`ایجاد پوشه: ${dirPath}`, 'blue');
    return true;
  }
  return false;
};

const createFile = (filePath, content) => {
  if (!fs.existsSync(filePath)) {
    fs.writeFileSync(filePath, content, 'utf8');
    log(`ایجاد فایل: ${filePath}`, 'green');
    return true;
  }
  log(`فایل موجود است: ${filePath}`, 'yellow');
  return false;
};

const TEMPLATES = {
  sliceTemplate: (name, actions) => `
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  loading: false,
  error: null,
  data: [],
};

const ${name}Slice = createSlice({
  name: '${name}',
  initialState,
  reducers: {
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
    ${actions.map(a => `${a}: (state, action) => { state.${a} = action.payload; }`).join(',\n    ')}
  },
});

export const { setLoading, setError, clearError, ${actions.join(', ')} } = ${name}Slice.actions;
export default ${name}Slice.reducer;
`,
  componentTemplate: (name) => `
import React from 'react';
import './${name}.css';

const ${name} = ({ children, className, ...props }) => {
  return (
    <div className={\`${name.toLowerCase()}-container \${className || ''}\`} {...props}>
      {children}
    </div>
  );
};

export default ${name};
`,
  pageTemplate: (name) => `
import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import './${name}.css';

const ${name} = () => {
  const dispatch = useDispatch();
  const { loading, error } = useSelector(state => state.ui);

  useEffect(() => {
    document.title = '${name.replace('Page', '')} - هرمزگان هوشمند';
  }, []);

  if (loading) return <div>در حال بارگذاری...</div>;
  if (error) return <div>خطا: {error}</div>;

  return (
    <div className="${name.toLowerCase()}-page">
      <h1>${name}</h1>
      <p>محتوای صفحه ${name}</p>
    </div>
  );
};

export default ${name};
`,
  serviceTemplate: (name) => `
import api from './api';

const ${name}Service = {
  getAll: async () => {
    try {
      const response = await api.get('/${name.toLowerCase()}');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  getById: async (id) => {
    try {
      const response = await api.get(\`/${name.toLowerCase()}/\${id}\`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  create: async (data) => {
    try {
      const response = await api.post('/${name.toLowerCase()}', data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  update: async (id, data) => {
    try {
      const response = await api.put(\`/${name.toLowerCase()}/\${id}\`, data);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
  delete: async (id) => {
    try {
      const response = await api.delete(\`/${name.toLowerCase()}/\${id}\`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export default ${name}Service;
`,
  hookTemplate: (name) => `
import { useState, useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import ${name}Service from '../services/${name.toLowerCase()}Service';

export const use${name} = () => {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const data = useSelector(state => state.${name.toLowerCase()});

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await ${name}Service.getAll();
      return result;
    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, fetchData };
};
`,
  helpersTemplate: () => `
export const generateId = () => Date.now().toString(36) + Math.random().toString(36).substr(2);
export const formatTime = (timestamp) => new Date(timestamp).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' });
export const formatPersianDate = (timestamp) => new Date(timestamp).toLocaleDateString('fa-IR', { year: 'numeric', month: 'long', day: 'numeric' });
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
  const R = 6371;
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
};
export const timeAgo = (timestamp) => {
  const now = Date.now();
  const diff = now - timestamp;
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  if (minutes < 1) return 'لحظاتی پیش';
  if (minutes < 60) return minutes + ' دقیقه پیش';
  if (hours < 24) return hours + ' ساعت پیش';
  if (days < 7) return days + ' روز پیش';
  return formatPersianDate(timestamp);
};
export const isValidEmail = (email) => /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email);
export const isValidPhone = (phone) => /^09[0-9]{9}$/.test(phone);
export const slugify = (text) => text.toLowerCase().replace(/[^\\w\\s-]/g, '').replace(/[\\s_-]+/g, '-').replace(/^-+|-+$/g, '');
export const groupBy = (array, key) => array.reduce((result, item) => {
  const groupKey = item[key];
  if (!result[groupKey]) result[groupKey] = [];
  result[groupKey].push(item);
  return result;
}, {});
export const getDefaultLocation = () => ({ lat: 27.2158, lng: 56.2808, name: 'بندرعباس' });
`,
  storeIndexTemplate: (slices) => `
import { configureStore } from '@reduxjs/toolkit';
${slices.map(s => `import ${s.name}Reducer from './slices/${s.name}Slice';`).join('\n')}

const store = configureStore({
  reducer: {
    ${slices.map(s => `${s.name}: ${s.name}Reducer`).join(',\n    ')}
  },
  devTools: process.env.NODE_ENV !== 'production',
});

export default store;
`
};

function createFolders() {
  log('\n📁 ایجاد پوشه‌های پروژه...', 'blue');
  const folders = [
    CONFIG.srcDir,
    path.join(CONFIG.srcDir, CONFIG.modules.store.path, 'slices'),
    path.join(CONFIG.srcDir, CONFIG.modules.components.path),
    path.join(CONFIG.srcDir, CONFIG.modules.pages.path),
    path.join(CONFIG.srcDir, CONFIG.modules.services.path),
    path.join(CONFIG.srcDir, CONFIG.modules.hooks.path),
    path.join(CONFIG.srcDir, CONFIG.modules.utils.path),
    path.join(CONFIG.srcDir, CONFIG.modules.assets.path),
    ...CONFIG.modules.assets.subdirs.map(d => path.join(CONFIG.srcDir, CONFIG.modules.assets.path, d)),
  ];
  CONFIG.modules.components.modules.forEach(m => folders.push(path.join(CONFIG.srcDir, CONFIG.modules.components.path, m.name)));
  folders.forEach(createDir);
}

function generateStore() {
  log('\n📦 ایجاد فایل‌های Store...', 'blue');
  const { store } = CONFIG.modules;
  store.slices.forEach(slice => {
    const filePath = path.join(CONFIG.srcDir, store.path, 'slices', slice.name + 'Slice.js');
    createFile(filePath, TEMPLATES.sliceTemplate(slice.name, slice.actions));
  });
  const indexPath = path.join(CONFIG.srcDir, store.path, 'index.js');
  createFile(indexPath, TEMPLATES.storeIndexTemplate(store.slices));
}

function generateComponents() {
  log('\n🧩 ایجاد کامپوننت‌ها...', 'blue');
  CONFIG.modules.components.modules.forEach(module => {
    module.files.forEach(file => {
      const filePath = path.join(CONFIG.srcDir, CONFIG.modules.components.path, module.name, file);
      const name = file.replace('.jsx', '');
      createFile(filePath, TEMPLATES.componentTemplate(name));
      const cssPath = filePath.replace('.jsx', '.css');
      createFile(cssPath, '/* ' + name + ' Styles */\n.' + name.toLowerCase() + '-container { }\n');
    });
  });
}

function generatePages() {
  log('\n📄 ایجاد صفحات...', 'blue');
  CONFIG.modules.pages.files.forEach(file => {
    const filePath = path.join(CONFIG.srcDir, CONFIG.modules.pages.path, file);
    const name = file.replace('.jsx', '');
    createFile(filePath, TEMPLATES.pageTemplate(name));
    const cssPath = filePath.replace('.jsx', '.css');
    createFile(cssPath, '/* ' + name + ' Styles */\n.' + name.toLowerCase() + '-page { padding: 2rem; }\n');
  });
}

function generateServices() {
  log('\n🔌 ایجاد سرویس‌ها...', 'blue');
  CONFIG.modules.services.files.forEach(file => {
    const filePath = path.join(CONFIG.srcDir, CONFIG.modules.services.path, file);
    const name = file.replace('Service.js', '');
    createFile(filePath, TEMPLATES.serviceTemplate(name));
  });
}

function generateHooks() {
  log('\n🪝 ایجاد Hooks...', 'blue');
  CONFIG.modules.hooks.files.forEach(file => {
    const filePath = path.join(CONFIG.srcDir, CONFIG.modules.hooks.path, file);
    const name = file.replace('.js', '').replace('use', '');
    createFile(filePath, TEMPLATES.hookTemplate(name));
  });
}

function generateUtils() {
  log('\n🛠️ ایجاد Utilities...', 'blue');
  const helpersPath = path.join(CONFIG.srcDir, CONFIG.modules.utils.path, 'helpers.js');
  createFile(helpersPath, TEMPLATES.helpersTemplate());
  ['validators.js', 'constants.js', 'formatters.js'].forEach(f => {
    const p = path.join(CONFIG.srcDir, CONFIG.modules.utils.path, f);
    createFile(p, '// src/utils/' + f + '\nexport default {};\n');
  });
}

function generateStyles() {
  log('\n🎨 ایجاد فایل‌های استایل...', 'blue');
  const stylesPath = path.join(CONFIG.srcDir, CONFIG.modules.assets.path, 'styles');
  const indexCssPath = path.join(CONFIG.srcDir, 'index.css');
  createFile(indexCssPath, '@import "./assets/styles/variables.css";\n@import "./assets/styles/globals.css";\n');
  createFile(path.join(stylesPath, 'variables.css'), ':root { --primary: #667eea; --primary-dark: #764ba2; }\n');
  createFile(path.join(stylesPath, 'globals.css'), '.container { max-width: 1200px; margin: 0 auto; padding: 0 1rem; }\n');
}

function generatePackageJson() {
  log('\n📦 ایجاد package.json...', 'blue');
  const packagePath = path.join(CONFIG.rootDir, 'package.json');
  if (!fs.existsSync(packagePath)) {
    const pkg = {
      name: "hermezgan-intelligent",
      version: "3.0.0",
      private: true,
      scripts: { start: "react-scripts start", build: "react-scripts build", test: "react-scripts test", eject: "react-scripts eject", generate: "node scripts/generate.js" },
      dependencies: { "react": "^18.2.0", "react-dom": "^18.2.0", "react-scripts": "5.0.1", "react-redux": "^8.1.1", "@reduxjs/toolkit": "^1.9.5", "react-router-dom": "^6.14.2", "axios": "^1.4.0", "leaflet": "^1.9.4", "react-leaflet": "^4.2.1", "react-leaflet-cluster": "^3.1.0", "leaflet.markercluster": "^1.5.3", "leaflet.heat": "^1.0.0", "leaflet-draw": "^1.0.4", "leaflet-velocity": "^1.0.0", "leaflet-vectorgrid": "^1.3.0", "geotiff": "^2.0.7", "proj4": "^2.9.2", "idb": "^7.1.1", "lodash": "^4.17.21" }
    };
    fs.writeFileSync(packagePath, JSON.stringify(pkg, null, 2), 'utf8');
    log('ایجاد: ' + packagePath, 'green');
  }
}

function main() {
  console.log('\n🚀 شروع ساخت پروژه هرمزگان هوشمند...\n');
  try {
    createFolders();
    generateStore();
    generateComponents();
    generatePages();
    generateServices();
    generateHooks();
    generateUtils();
    generateStyles();
    generatePackageJson();
    console.log('\n✅ پروژه با موفقیت ساخته شد!\n');
    console.log('📋 مراحل بعدی:');
    console.log('  1. npm install');
    console.log('  2. npm start\n');
  } catch (error) {
    console.error('\n❌ خطا:', error.message);
    process.exit(1);
  }
}

main();
