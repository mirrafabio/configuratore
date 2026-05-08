import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { AlertTriangle, CheckCheck, Check } from "lucide-react";
import { format } from "date-fns";
import { it } from "date-fns/locale";
import { Header } from "@/components/Layout/Header";
import { api } from "@/services/api";
import type { AlertType } from "@/types";

const TYPE_LABELS: Record<AlertType, string> = {
  speeding: "Eccesso velocità",
  geofence_exit: "Uscita geofence",
  geofence_enter: "Entrata geofence",
  ignition_on: "Accensione",
  ignition_off: "Spegnimento",
  low_battery: "Batteria scarica",
  harsh_braking: "Frenata brusca",
  harsh_acceleration: "Accelerazione brusca",
  device_offline: "Dispositivo offline",
};

const TYPE_VARIANT: Record<AlertType, string> = {
  speeding: "danger",
  geofence_exit: "warning",
  geofence_enter: "info",
  ignition_on: "success",
  ignition_off: "default",
  low_battery: "danger",
  harsh_braking: "warning",
  harsh_acceleration: "warning",
  device_offline: "danger",
};

export function AlertsPage() {
  const qc = useQueryClient();
  const [unackOnly, setUnackOnly] = useState(false);

  const { data: vehicles = [] } = useQuery({
    queryKey: ["vehicles"],
    queryFn: api.getVehicles,
  });
  const { data: alerts = [], isLoading } = useQuery({
    queryKey: ["alerts", unackOnly],
    queryFn: () => api.getAlerts(unackOnly, 200),
    refetchInterval: 15_000,
  });

  const ackMut = useMutation({
    mutationFn: api.acknowledgeAlert,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["alerts"] }),
  });
  const ackAllMut = useMutation({
    mutationFn: api.acknowledgeAll,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["alerts"] });
      qc.invalidateQueries({ queryKey: ["stats"] });
    },
  });

  const vehicleMap = new Map(vehicles.map((v) => [v.id, v]));

  return (
    <div className="page">
      <Header title="Avvisi" />
      <div className="page-content">
        <div className="toolbar">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={unackOnly}
              onChange={(e) => setUnackOnly(e.target.checked)}
            />
            Solo non letti
          </label>
          <button
            className="btn btn-ghost"
            onClick={() => ackAllMut.mutate()}
            disabled={ackAllMut.isPending}
          >
            <CheckCheck size={16} /> Segna tutti come letti
          </button>
        </div>

        {isLoading ? (
          <div className="loading">Caricamento...</div>
        ) : alerts.length === 0 ? (
          <div className="empty-state">Nessun avviso trovato.</div>
        ) : (
          <div className="alerts-table-wrap">
            <table className="alerts-table">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Veicolo</th>
                  <th>Messaggio</th>
                  <th>Data/Ora</th>
                  <th>Velocità</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {alerts.map((a) => {
                  const vehicle = vehicleMap.get(a.vehicle_id);
                  return (
                    <tr key={a.id} className={a.acknowledged ? "row-ack" : ""}>
                      <td>
                        <span className={`badge badge--${TYPE_VARIANT[a.type]}`}>
                          {TYPE_LABELS[a.type]}
                        </span>
                      </td>
                      <td>{vehicle?.name ?? `#${a.vehicle_id}`}</td>
                      <td>{a.message}</td>
                      <td className="mono">
                        {format(new Date(a.created_at), "dd/MM/yy HH:mm", { locale: it })}
                      </td>
                      <td>{a.speed ? `${a.speed} km/h` : "–"}</td>
                      <td>
                        {!a.acknowledged && (
                          <button
                            className="icon-btn"
                            onClick={() => ackMut.mutate(a.id)}
                            title="Segna come letto"
                          >
                            <Check size={15} />
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
