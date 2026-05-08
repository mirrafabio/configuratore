import clsx from "clsx";
import { Truck, User, Cpu, Clock } from "lucide-react";
import { formatDistanceToNow } from "date-fns";
import { it } from "date-fns/locale";
import type { Vehicle } from "@/types";

const STATUS_LABELS: Record<Vehicle["status"], string> = {
  online: "Online",
  offline: "Offline",
  moving: "In movimento",
  idle: "Fermo (acceso)",
};

interface Props {
  vehicle: Vehicle;
  selected?: boolean;
  onClick?: () => void;
}

export function VehicleCard({ vehicle, selected, onClick }: Props) {
  return (
    <div
      className={clsx("vehicle-card", `vehicle-card--${vehicle.status}`, {
        "vehicle-card--selected": selected,
      })}
      onClick={onClick}
      role="button"
      tabIndex={0}
    >
      <div className="vehicle-card-header">
        <div className="vehicle-status-dot" />
        <span className="vehicle-name">{vehicle.name}</span>
        <span className={clsx("status-badge", `status-badge--${vehicle.status}`)}>
          {STATUS_LABELS[vehicle.status]}
        </span>
      </div>
      <div className="vehicle-card-body">
        <div className="vehicle-meta">
          <Truck size={14} />
          <span>{vehicle.plate}</span>
          {vehicle.model && <span className="muted">· {vehicle.model}</span>}
        </div>
        {vehicle.driver && (
          <div className="vehicle-meta">
            <User size={14} />
            <span>{vehicle.driver}</span>
          </div>
        )}
        {vehicle.imei && (
          <div className="vehicle-meta">
            <Cpu size={14} />
            <span className="mono">{vehicle.imei}</span>
          </div>
        )}
        {vehicle.last_seen && (
          <div className="vehicle-meta muted">
            <Clock size={14} />
            <span>
              {formatDistanceToNow(new Date(vehicle.last_seen), {
                addSuffix: true,
                locale: it,
              })}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
