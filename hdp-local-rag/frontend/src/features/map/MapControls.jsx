import { useMapStore } from "@stores/map.store";
import { useMap } from "@hooks/useMap";
import { Button } from "@components/common/Button";
import { cn } from "@utils/cn";
import {
  Crosshair,
  Layers,
  Navigation,
  Camera,
  MapPin,
  Flame,
  Route,
  X,
} from "lucide-react";

const layerButtons = [
  { key: "traffic", label: "ترافیک", icon: Navigation },
  { key: "cameras", label: "دوربین", icon: Camera },
  { key: "pois", label: "مراکز", icon: MapPin },
  { key: "hotspots", label: "هات‌اسپات", icon: Flame },
  { key: "route", label: "مسیر", icon: Route },
];

export function MapControls() {
  const { layers, toggleLayer } = useMapStore();
  const { locateUser } = useMap();

  return (
    <div className="absolute left-4 top-4 z-[1000] flex flex-col gap-2">
      {/* Locate me */}
      <Button
        variant="secondary"
        size="icon"
        onClick={locateUser}
        className="h-10 w-10 rounded-lg shadow-lg bg-white/90 backdrop-blur"
        title="موقعیت من"
      >
        <Crosshair className="h-4 w-4" />
      </Button>

      {/* Layer toggles */}
      <div className="flex flex-col gap-1 rounded-lg bg-white/90 p-1 shadow-lg backdrop-blur">
        {layerButtons.map(({ key, label, icon: Icon }) => (
          <Button
            key={key}
            variant="ghost"
            size="icon"
            onClick={() => toggleLayer(key)}
            className={cn(
              "h-9 w-9 rounded-md transition-colors",
              layers[key]
                ? "bg-teal-100 text-teal-700 dark:bg-teal-900/30 dark:text-teal-400"
                : "text-slate-500 hover:text-slate-700"
            )}
            title={label}
          >
            <Icon className="h-4 w-4" />
          </Button>
        ))}
      </div>
    </div>
  );
}
