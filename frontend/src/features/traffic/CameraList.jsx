import { Card, CardContent, CardHeader, CardTitle } from "@components/common/Card";
import { Badge } from "@components/common/Badge";
import { useTraffic } from "@hooks/useTraffic";
import { Camera, Eye } from "lucide-react";

export function CameraList() {
  const { cameras } = useTraffic();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <Camera className="h-5 w-5 text-red-500" />
          دوربین‌ها
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 max-h-64 overflow-y-auto">
        {cameras.slice(0, 10).map((camera) => (
          <div
            key={camera.id}
            className="flex items-center justify-between rounded-lg border p-2 text-sm"
          >
            <div className="flex items-center gap-2">
              <Eye className="h-3 w-3 text-muted-foreground" />
              <span className="truncate">{camera.name || camera.road_name}</span>
            </div>
            <Badge
              variant={camera.status === "active" ? "success" : "secondary"}
              className="text-xs"
            >
              {camera.status === "active" ? "فعال" : "غیرفعال"}
            </Badge>
          </div>
        ))}
        {cameras.length === 0 && (
          <p className="text-xs text-muted-foreground text-center py-4">
            دوربینی ثبت نشده
          </p>
        )}
      </CardContent>
    </Card>
  );
}
