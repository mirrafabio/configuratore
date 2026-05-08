import { useQuery } from "@tanstack/react-query";
import {
  Truck,
  Activity,
  AlertTriangle,
  Navigation,
  WifiOff,
  Route,
  Gauge,
} from "lucide-react";
import { Header } from "@/components/Layout/Header";
import { StatsCard } from "@/components/Dashboard/StatsCard";
import { api } from "@/services/api";

export function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ["stats"],
    queryFn: api.getStats,
    refetchInterval: 15_000,
  });

  const { data: alerts } = useQuery({
    queryKey: ["alerts", "recent"],
    queryFn: () => api.getAlerts(false, 5),
    refetchInterval: 15_000,
  });

  return (
    <div className="page">
      <Header title="Dashboard" />
      <div className="page-content">
        {isLoading ? (
          <div className="loading">Caricamento...</div>
        ) : (
          <>
            <div className="stats-grid">
              <StatsCard
                label="Veicoli totali"
                value={stats?.total_vehicles ?? 0}
                icon={<Truck size={22} />}
                variant="default"
              />
              <StatsCard
                label="In movimento"
                value={stats?.moving_vehicles ?? 0}
                icon={<Navigation size={22} />}
                variant="success"
              />
              <StatsCard
                label="Fermi (accesi)"
                value={stats?.idle_vehicles ?? 0}
                icon={<Activity size={22} />}
                variant="warning"
              />
              <StatsCard
                label="Offline"
                value={stats?.offline_vehicles ?? 0}
                icon={<WifiOff size={22} />}
                variant="danger"
              />
              <StatsCard
                label="Percorsi attivi"
                value={stats?.active_trips ?? 0}
                icon={<Route size={22} />}
                variant="info"
              />
              <StatsCard
                label="Avvisi non letti"
                value={stats?.unacknowledged_alerts ?? 0}
                icon={<AlertTriangle size={22} />}
                variant={
                  (stats?.unacknowledged_alerts ?? 0) > 0 ? "danger" : "default"
                }
              />
              <StatsCard
                label="km percorsi oggi"
                value={`${stats?.total_distance_today_km ?? 0} km`}
                icon={<Gauge size={22} />}
                variant="info"
              />
            </div>

            <div className="section">
              <h2 className="section-title">Ultimi avvisi</h2>
              {alerts?.length === 0 && (
                <div className="empty-state">Nessun avviso recente</div>
              )}
              <div className="alert-list">
                {alerts?.map((alert) => (
                  <div
                    key={alert.id}
                    className={`alert-item alert-item--${alert.acknowledged ? "ack" : "unack"}`}
                  >
                    <AlertTriangle size={16} />
                    <div className="alert-item-body">
                      <span className="alert-message">{alert.message}</span>
                      <span className="alert-time">
                        {new Date(alert.created_at).toLocaleString("it-IT")}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
