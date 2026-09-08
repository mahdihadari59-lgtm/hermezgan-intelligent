import { createBrowserRouter, RouterProvider, Outlet } from "react-router-dom";
import { Suspense, lazy } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

// Layout
import { AppLayout } from "@components/layout/AppLayout";
import { PageLoader } from "@components/loading/PageLoader";

// Eager-loaded pages
import HomePage from "@pages/Home";

// Lazy-loaded pages
const MapPage = lazy(() => import("@pages/Map"));
const TrafficPage = lazy(() => import("@pages/Traffic"));
const TourismPage = lazy(() => import("@pages/Tourism"));
const PlacesPage = lazy(() => import("@pages/Places"));
const ChatPage = lazy(() => import("@pages/Chat"));
const VoicePage = lazy(() => import("@pages/Voice"));
const DriverPage = lazy(() => import("@pages/Driver"));
const AnalyticsPage = lazy(() => import("@pages/Analytics"));
const NotFoundPage = lazy(() => import("@pages/NotFound"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppLayout>
        <Suspense fallback={<PageLoader />}>
          <Outlet />
        </Suspense>
      </AppLayout>
      <Toaster
        position="top-left"
        richColors
        closeButton
        dir="rtl"
        toastOptions={{
          style: { fontFamily: "Vazirmatn, system-ui, sans-serif" },
        }}
      />
    </QueryClientProvider>
  );
}

export const router = createBrowserRouter([
  {
    path: "/",
    element: <RootLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "map", element: <MapPage /> },
      { path: "traffic", element: <TrafficPage /> },
      { path: "tourism", element: <TourismPage /> },
      { path: "places", element: <PlacesPage /> },
      { path: "chat", element: <ChatPage /> },
      { path: "voice", element: <VoicePage /> },
      { path: "driver", element: <DriverPage /> },
      { path: "analytics", element: <AnalyticsPage /> },
      { path: "*", element: <NotFoundPage /> },
    ],
  },
]);

export function AppRouter() {
  return <RouterProvider router={router} />;
}
