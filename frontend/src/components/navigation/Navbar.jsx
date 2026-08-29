import { Link, useLocation } from "react-router-dom";
import { useAppStore } from "@stores/app.store";
import { Button } from "@components/common/Button";
import {
  MapPin,
  Sun,
  Moon,
  Menu,
  Bell,
  Search,
} from "lucide-react";

export function Navbar() {
  const location = useLocation();
  const { theme, toggleTheme, toggleSidebar } = useAppStore();

  const pageTitle = {
    "/": "صفحه اصلی",
    "/map": "نقشه",
    "/traffic": "ترافیک",
    "/tourism": "گردشگری",
    "/places": "مراکز",
    "/chat": "دستیار هوشمند",
    "/voice": "دستیار صوتی",
    "/driver": "رانندگان",
    "/analytics": "تحلیل‌ها",
  }[location.pathname] || "هرمزگان هوشمند";

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="lg:hidden"
          >
            <Menu className="h-5 w-5" />
          </Button>
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-teal-500 to-teal-700">
              <MapPin className="h-5 w-5 text-white" />
            </div>
            <span className="hidden text-lg font-bold sm:inline-block">
              هرمزگان هوشمند
            </span>
          </Link>
        </div>

        <div className="flex items-center gap-1 text-sm font-medium text-muted-foreground">
          {pageTitle}
        </div>

        <div className="flex items-center gap-2">
          <Button variant="ghost" size="icon" className="hidden sm:flex">
            <Search className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" className="hidden sm:flex">
            <Bell className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={toggleTheme}>
            {theme === "dark" ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
    </header>
  );
}
