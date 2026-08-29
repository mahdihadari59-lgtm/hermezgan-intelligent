import { cn } from "@utils/cn";

export function Badge({ className, variant = "default", ...props }) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        variant === "default" && "border-transparent bg-teal-600 text-white shadow",
        variant === "secondary" && "border-transparent bg-slate-100 text-slate-900",
        variant === "destructive" && "border-transparent bg-red-600 text-white",
        variant === "outline" && "text-foreground",
        variant === "success" && "border-transparent bg-emerald-100 text-emerald-800",
        variant === "warning" && "border-transparent bg-amber-100 text-amber-800",
        className
      )}
      {...props}
    />
  );
}
