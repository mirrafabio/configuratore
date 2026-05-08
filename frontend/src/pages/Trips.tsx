import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Route, Clock, Gauge, Navigation } from "lucide-react";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import { Header } from "@/components/Layout/Header";
import { api } from "@/services/api";

export function TripsPage() {
  const [vehicleFilter, setVehicleFilter] = useState<string>("");

  const { data: vehicles = [] } = useQuery({
    queryKey: ["vehicles"],
    queryFn: api.getVehicles,
  });

  const selectedVehicleId = vehicleFilter ? parseInt(vehicleFilter) : undefined;

  const { data: trips = [], isLoading } = useQuery({
    queryKey: ["trips", selectedVehicleId],
    queryFn: () => api.getTrips(selectedVehicleId, 100),
    refetchInterval: 30_000,
  });

  const vehicleMap = new Map(vehicles.map((v) => [v.id, v]));

  return (
    <div className="page">
      <Header title="Percorsi" />
      <div className="page-content">
        <div className="toolbar">
          <select
            className="form-select"
            value={vehicleFilter}
            onChange={(e) => setVehicleFilter(e.target.value)}
          >
            <option value="">Tutti i veicoli</option>
            {vehicles.map((v) => (
              <option key={v.id} value={v.id}>
                {v.name} – {v.plate}
              </option>
            ))}
          </select>
        </div>

        {isLoading ? (
          <div className="loading">Caricamento...</div>
        ) : trips.length === 0 ? (
          <div className="empty-state">Nessun percorso trovato.</div>
        ) : (
          <div className="trips-list">
            {trips.map((trip) => {
              const vehicle = vehicleMap.get(trip.vehicle_id);
              const duration = trip.duration_sec
                ? `${Math.floor(trip.duration_sec / 3600)}h ${Math.floor((trip.duration_sec % 3600) / 60)}m`
                : "–";
              return (
                <div key={trip.id} className="trip-card">
                  <div className="trip-header">
                    <div className="trip-vehicle">
                      <Navigation size={16} />
                      <strong>{vehicle?.name ?? `#${trip.vehicle_id}`}</strong>
                      {vehicle && <span className="muted">({vehicle.plate})</span>}
                    </div>
                    <span className={`trip-status ${trip.end_time ? "" : "trip-status--active"}`}>
                      {trip.end_time ? "Completato" : "In corso"}
                    </span>
                  </div>
                  <div className="trip-meta">
                    <span>
                      <Clock size={13} />
                      {format(new Date(trip.start_time), "dd/MM/yyyy HH:mm", { locale: it })}
                      {trip.end_time && ` → ${format(new Date(trip.end_time), "HH:mm")}`}
                    </span>
                    <span>
                      <Route size={13} />
                      {trip.distance_km.toFixed(1)} km
                    </span>
                    <span>
                      <Gauge size={13} />
                      Max {trip.max_speed} km/h · Media {trip.avg_speed.toFixed(0)} km/h
                    </span>
                    <span>
                      <Clock size={13} />
                      {duration}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
