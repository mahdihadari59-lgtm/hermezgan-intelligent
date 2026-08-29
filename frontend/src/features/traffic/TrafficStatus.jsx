import { Card, CardContent, CardHeader, CardTitle } from "@components/common/Card";
import { useTraffic } from "@hooks/useTraffic";
import { Activity } from "lucide-react";

export function TrafficStatus() {
  const { stats } = useTraffic();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Activity className="h-5 w-5 text-teal-500" />
          خلاصه ترافیک
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>جاده‌های شلوغ</span>
            <span className="font-medium">
              {stats?.congestedRoads || 0} از {stats?.totalRoads || 0}
            </span>
          </div>
          <div className="h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-teal-500 transition-all"
              style={{
                width: `${stats?.totalRoads ? (stats.congestedRoads / stats.totalRoads) * 100 : 0}%`,
              }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
