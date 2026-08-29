import { MapPin } from "lucide-react";

export function PageLoader() {
  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4">
      <div className="relative">
        <div className="h-16 w-16 animate-spin rounded-full border-4 border-teal-200 border-t-teal-600" />
        <MapPin className="absolute left-1/2 top-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 text-teal-600" />
      </div>
      <p className="text-sm text-muted-foreground animate-pulse">
        در حال بارگذاری...
      </p>
    </div>
  );
}
