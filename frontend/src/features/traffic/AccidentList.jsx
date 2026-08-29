import { Card, CardContent, CardHeader, CardTitle } from "@components/common/Card";
import { Badge } from "@components/common/Badge";
import { useTraffic } from "@hooks/useTraffic";
import { AlertTriangle, Clock } from "lucide-react";

const severityColors = {
  low: "bg-emerald-100 text-emerald-800",
  medium: "bg-amber-100 text-amber-800",
  high: "bg-red-100 text-red-800",
};

export function AccidentList() {
  const { incidents } = useTraffic();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <AlertTriangle className="h-5 w-5 text-amber-500" />
          حوادث
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-2 max-h-64 overflow-y-auto">
        {incidents.map((incident) => (
          <div
            key={incident.id}
            className="rounded-lg border p-2 text-sm space-y-1"
          >
            <div className="flex items-center justify-between">
              <span className="font-medium truncate">{incident.roadName}</span>
              <Badge
                variant="outline"
                className={`text-xs ${severityColors[incident.severity] || ""}`}
              >
                {incident.severity}
              </Badge>
            </div>
            <p className="text-xs text-muted-foreground truncate">
              {incident.description}
            </p>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Clock className="h-3 w-3" />
              <span>{new Date(incident.startTime).toLocaleTimeString("fa-IR")}</span>
            </div>
          </div>
        ))}
        {incidents.length === 0 && (
          <p className="text-xs text-muted-foreground text-center py-4">
            حادثه فعالی وجود ندارد
          </p>
        )}
      </CardContent>
    </Card>
  );
}
