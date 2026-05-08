import { BrowserRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Sidebar } from "@/components/Layout/Sidebar";
import { DashboardPage } from "@/pages/Dashboard";
import { FleetPage } from "@/pages/Fleet";
import { TrackingPage } from "@/pages/Tracking";
import { TripsPage } from "@/pages/Trips";
import { AlertsPage } from "@/pages/Alerts";
import "./styles/main.css";

const qc = new QueryClient({
  defaultOptions: { queries: { retry: 1 } },
});

export default function App() {
  return (
    <QueryClientProvider client={qc}>
      <BrowserRouter>
        <div className="app-layout">
          <Sidebar />
          <main className="app-main">
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/fleet" element={<FleetPage />} />
              <Route path="/tracking" element={<TrackingPage />} />
              <Route path="/trips" element={<TripsPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
