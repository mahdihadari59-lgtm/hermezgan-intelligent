import { Link, useLocation } from "react-router-dom";
import { useAppStore } from "@stores/app.store";
import { cn } from "@utils/cn";
import {
  Home,
  MapPin,
  TrafficCone,
  Palmtree,
  MapPinned,
  MessageCircle,
  Mic,
  Car,
  BarChart3,
} from "lucide-react";

const navItems = [
  { path: "/", label: "صفحه اصلی", icon: Home },
  { path: "/map", label: "نقشه", icon: MapPin },
  { path: "/traffic", label: "ترافیک", icon: TrafficCone },
  { path: "/tourism", label: "گردشگری", icon: Palmtree },
  { path: "/places", label: "مراکز", icon: MapPinned },
  { path: "/chat", label: "دستیار", icon: MessageCircle },
  { path: "/voice", label: "صوت", icon: Mic },
  { path: "/driver", label: "رانندگان", icon: Car },
  { path: "/analytics", label: "تحلیل‌ها", icon: BarChart3 },
];

export function Sidebar() {
  const location = useLocation();
  const { sidebarOpen, closeSidebar } = useAppStore();

  return (
    <>
      {/* Mobile overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={closeSidebar}
        />
      )}

      {/* Sidebar */}
      <aside
        className={cn(
          "fixed right-0 top-16 z-50 h-[calc(100vh-4rem)] w-64 border-l bg-background transition-transform duration-300 lg:static lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "translate-x-full lg:translate-x-0"
        )}
      >
        <nav className="flex flex-col gap-1 p-3">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                onClick={closeSidebar}
                className={cn(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-teal-50 text-teal-700 dark:bg-teal-950/30 dark:text-teal-400"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground"
                )}
              >
                <Icon className="h-4 w-4" />
                {item.label}
              </Link>
            );
          })}
        </nav>
      </aside>
    </>
  );
}
