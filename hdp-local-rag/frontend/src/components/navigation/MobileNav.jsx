import { Link, useLocation } from "react-router-dom";
import { cn } from "@utils/cn";
import {
  Home,
  MapPin,
  TrafficCone,
  MessageCircle,
  Mic,
} from "lucide-react";

const mobileItems = [
  { path: "/", label: "خانه", icon: Home },
  { path: "/map", label: "نقشه", icon: MapPin },
  { path: "/traffic", label: "ترافیک", icon: TrafficCone },
  { path: "/chat", label: "چت", icon: MessageCircle },
  { path: "/voice", label: "صوت", icon: Mic },
];

export function MobileNav() {
  const location = useLocation();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 border-t bg-background lg:hidden">
      <div className="flex items-center justify-around">
        {mobileItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                "flex flex-1 flex-col items-center gap-0.5 py-2 text-xs font-medium transition-colors",
                isActive
                  ? "text-teal-600"
                  : "text-muted-foreground"
              )}
            >
              <Icon className={cn("h-5 w-5", isActive && "fill-teal-100")} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
