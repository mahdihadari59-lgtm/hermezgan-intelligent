#!/usr/bin/env python3
# ============================================================
# patch_redux_round2.py
# رفع تداخل star export در store/index.js + اضافه‌کردن addToast و setMapMode
# ============================================================
import os

# ---------- 1. store/index.js: به‌جای star export از هر slice، از features/index.js بخون ----------
store_index_path = "src/store/index.js"
store_index_new = """// src/store/index.js
// Barrel: exports the configured store + all slice actions (aliased) from features/index.js
export { default } from './store';
export * from '../features';
"""
with open(store_index_path, "w", encoding="utf-8") as f:
    f.write(store_index_new)
print(f"✅ بازنویسی شد: {store_index_path}")


# ---------- 2. uiSlice: اضافه‌کردن toasts + addToast ----------
ui_path = "src/features/ui/uiSlice.js"
with open(ui_path, "r", encoding="utf-8") as f:
    ui_content = f.read()

if "addToast" not in ui_content:
    ui_content = ui_content.replace(
        "  notifications: [],\n",
        "  notifications: [],\n  toasts: [],\n"
    )
    ui_content = ui_content.replace(
        "    addNotification: (state, action) => {",
        """    addToast: (state, action) => {
      state.toasts.push({
        id: Date.now(),
        ...action.payload,
      });
    },
    removeToast: (state, action) => {
      state.toasts = state.toasts.filter(t => t.id !== action.payload);
    },
    addNotification: (state, action) => {"""
    )
    ui_content = ui_content.replace(
        "export const {\n  toggleSidebar,",
        "export const {\n  addToast,\n  removeToast,\n  toggleSidebar,"
    )
    with open(ui_path, "w", encoding="utf-8") as f:
        f.write(ui_content)
    print(f"✅ اضافه شد: {ui_path} (addToast, removeToast)")
else:
    print(f"⚠️ addToast از قبل در {ui_path} وجود دارد")


# ---------- 3. mapSlice: اضافه‌کردن mapMode + setMapMode ----------
map_path = "src/features/map/mapSlice.js"
with open(map_path, "r", encoding="utf-8") as f:
    map_content = f.read()

if "setMapMode" not in map_content:
    map_content = map_content.replace(
        "  serviceTypeFilter: null,\n",
        "  serviceTypeFilter: null,\n  mapMode: 'street',\n"
    )
    map_content = map_content.replace(
        "    setServiceTypeFilter: (state, action) => {",
        """    setMapMode: (state, action) => {
      state.mapMode = action.payload;
    },
    setServiceTypeFilter: (state, action) => {"""
    )
    map_content = map_content.replace(
        "export const {\n  setMapCenter,",
        "export const {\n  setMapMode,\n  setMapCenter,"
    )
    with open(map_path, "w", encoding="utf-8") as f:
        f.write(map_content)
    print(f"✅ اضافه شد: {map_path} (setMapMode)")
else:
    print(f"⚠️ setMapMode از قبل در {map_path} وجود دارد")


# ---------- 4. features/index.js: اضافه‌کردن export برای addToast, removeToast, setMapMode ----------
features_index_path = "src/features/index.js"
with open(features_index_path, "r", encoding="utf-8") as f:
    fi_content = f.read()

if "addToast" not in fi_content:
    fi_content = fi_content.replace(
        "export {\n  toggleSidebar,\n  setTheme,\n  setNotification,\n} from './ui/uiSlice';",
        "export {\n  toggleSidebar,\n  setTheme,\n  setNotification,\n  addToast,\n  removeToast,\n} from './ui/uiSlice';"
    )
    fi_content = fi_content.replace(
        "  setServiceTypeFilter,\n} from './map/mapSlice';",
        "  setServiceTypeFilter,\n  setMapMode,\n} from './map/mapSlice';"
    )
    with open(features_index_path, "w", encoding="utf-8") as f:
        f.write(fi_content)
    print(f"✅ اضافه شد: {features_index_path} (addToast, removeToast, setMapMode)")
else:
    print(f"⚠️ addToast از قبل در {features_index_path} وجود دارد")

print("\n🎉 پچ دور دوم کامل شد.")
