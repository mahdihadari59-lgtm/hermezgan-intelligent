import { Link } from "react-router-dom";
import { MapPin, TrafficCone, Palmtree, MessageCircle, Mic, BarChart3 } from "lucide-react";
import { Card, CardContent } from "@components/common/Card";

const features = [
  { to: "/map", icon: MapPin, title: "نقشه", desc: "خدمات، دوربین‌ها و نقاط حادثه‌خیز" },
  { to: "/traffic", icon: TrafficCone, title: "ترافیک", desc: "وضعیت لحظه‌ای جاده‌ها" },
  { to: "/tourism", icon: Palmtree, title: "گردشگری", desc: "جاذبه‌های استان هرمزگان" },
  { to: "/chat", icon: MessageCircle, title: "چت هوشمند", desc: "پرسش و پاسخ با دستیار" },
  { to: "/voice", icon: Mic, title: "دستیار صوتی", desc: "گفتگوی صوتی با سیستم" },
  { to: "/analytics", icon: BarChart3, title: "تحلیل‌ها", desc: "آمار و گزارش‌های استان" },
];

export default function Home() {
  return (
    <div className="space-y-8 p-4">
      <div className="text-center space-y-2 py-8">
        <h1 className="text-3xl font-bold">هرمزگان هوشمند</h1>
        <p className="text-muted-foreground">
          سامانه یکپارچه نقشه، ترافیک، گردشگری و دستیار هوشمند استان هرمزگان
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {features.map(({ to, icon: Icon, title, desc }) => (
          <Link key={to} to={to}>
            <Card className="h-full transition-colors hover:bg-slate-50">
              <CardContent className="p-5 space-y-2">
                <Icon className="h-6 w-6 text-teal-500" />
                <h3 className="font-semibold">{title}</h3>
                <p className="text-sm text-muted-foreground">{desc}</p>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
