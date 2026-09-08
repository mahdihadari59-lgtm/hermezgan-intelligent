import { motion } from "framer-motion";
import { useTraffic } from "@hooks/useTraffic";
import { Card, CardContent, CardHeader, CardTitle } from "@components/common/Card";
import { Badge } from "@components/common/Badge";
import { Button } from "@components/common/Button";
import { TrafficStatus } from "./TrafficStatus";
import { CameraList } from "./CameraList";
import { AccidentList } from "./AccidentList";
import { HotspotList } from "./HotspotList";
import {
  TrafficCone,
  Camera,
  AlertTriangle,
  Flame,
  TrendingUp,
  Activity,
} from "lucide-react";

const congestionLabels = {
  low: "خلوت",
  medium: "متوسط",
  high: "شلوغ",
  severe: "بسیار شلوغ",
};

const congestionColors = {
  low: "bg-emerald-500",
  medium: "bg-amber-500",
  high: "bg-orange-500",
  severe: "bg-red-500",
};

export function TrafficPanel() {
  const { trafficData, stats, loading } = useTraffic();

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[
          {
            title: "کل جاده‌ها",
            value: stats?.totalRoads || 0,
            icon: TrafficCone,
            color: "text-blue-500",
            bg: "bg-blue-50",
          },
          {
            title: "شلوغ",
            value: stats?.congestedRoads || 0,
            icon: AlertTriangle,
            color: "text-red-500",
            bg: "bg-red-50",
          },
          {
            title: "میانگین سرعت",
            value: `${stats?.averageSpeed || 0} km/h`,
            icon: TrendingUp,
            color: "text-amber-500",
            bg: "bg-amber-50",
          },
          {
            title: "حادثه فعال",
            value: stats?.activeIncidents || 0,
            icon: Activity,
            color: "text-purple-500",
            bg: "bg-purple-50",
          },
        ].map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title}>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-xs text-muted-foreground">{stat.title}</p>
                    <p className="mt-1 text-2xl font-bold">{stat.value}</p>
                  </div>
                  <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${stat.bg}`}>
                    <Icon className={`h-5 w-5 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Traffic List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-base">
            <TrafficCone className="h-5 w-5 text-teal-500" />
            وضعیت جاده‌ها
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          {trafficData.map((road) => (
            <motion.div
              key={road.id}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center justify-between rounded-lg border p-3 hover:bg-slate-50 transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${congestionColors[road.congestionLevel]}`} />
                <div>
                  <p className="font-medium text-sm">{road.roadName}</p>
                  <p className="text-xs text-muted-foreground">
                    {road.averageSpeed} km/h · {road.vehicleCount} خودرو
                  </p>
                </div>
              </div>
              <Badge variant={road.congestionLevel === "low" ? "success" : "warning"}>
                {congestionLabels[road.congestionLevel]}
              </Badge>
            </motion.div>
          ))}
          {trafficData.length === 0 && (
            <p className="text-center text-sm text-muted-foreground py-8">
              داده‌ای در دسترس نیست
            </p>
          )}
        </CardContent>
      </Card>

      {/* Sub-panels */}
      <div className="grid gap-6 lg:grid-cols-3">
        <CameraList />
        <AccidentList />
        <HotspotList />
      </div>
    </div>
  );
}
