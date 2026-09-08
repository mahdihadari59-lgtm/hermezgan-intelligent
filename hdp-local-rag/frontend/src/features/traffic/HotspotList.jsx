import { Card, CardContent, CardHeader, CardTitle } from "@components/common/Card";
import { Badge } from "@components/common/Badge";
import { useTraffic } from "@hooks/useTraffic";
import { Flame, TrendingUp } from "lucide-react";

export function HotspotList() {
  const { hotspots } = useTraffic();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Flame className="h-5 w-5 text-orange-500" />
          نقاط داغ
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 max-h-64 overflow-y-auto">
        {hotspots.slice(0, 10).map((hotspot) => (
          <div
            key={hotspot.id}
            className="flex items-center justify-between rounded-lg border p-2 text-sm"
          >
            <div>
              <p className="font-medium">{hotspot.name || "نقطه داغ"}</p>
              <p className="text-xs text-muted-foreground">
                {hotspot.incident_count || 0} حادثه
              </p>
            </div>
            <TrendingUp className="h-4 w-4 text-orange-500" />
          </div>
        ))}
        {hotspots.length === 0 && (
          <p className="text-xs text-muted-foreground text-center py-4">
            نقطه داغی ثبت نشده
          </p>
        )}
      </CardContent>
    </Card>
  );
}
