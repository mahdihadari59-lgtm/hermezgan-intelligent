import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="flex flex-col items-center justify-center gap-3 p-16 text-center">
      <h1 className="text-4xl font-bold">۴۰۴</h1>
      <p className="text-muted-foreground">صفحه مورد نظر پیدا نشد.</p>
      <Link to="/" className="text-teal-600 hover:underline">بازگشت به صفحه اصلی</Link>
    </div>
  );
}
