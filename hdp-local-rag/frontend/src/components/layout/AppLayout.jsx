import { useEffect } from "react";
import { useAppStore } from "@stores/app.store";
import { Navbar } from "@components/navigation/Navbar";
import { Sidebar } from "@components/navigation/Sidebar";
import { MobileNav } from "@components/navigation/MobileNav";

export function AppLayout({ children }) {
  const { theme } = useAppStore();

  useEffect(() => {
    const root = document.documentElement;
    const isDark =
      theme === "dark" ||
      (theme === "system" &&
        window.matchMedia("(prefers-color-scheme: dark)").matches);
    root.classList.toggle("dark", isDark);
  }, [theme]);

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <Navbar />
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 overflow-auto">
          <div className="container mx-auto px-4 py-6">
            {children}
          </div>
        </main>
      </div>
      <MobileNav />
    </div>
  );
}
