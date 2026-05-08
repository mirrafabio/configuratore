import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { Header } from "@/components/Layout/Header";
import { FleetMap } from "@/components/Map/FleetMap";
import { VehicleCard } from "@/components/Vehicles/VehicleCard";
import { api } from "@/services/api";
import { useWebSocket } from "@/hooks/useWebSocket";
import type { Vehicle } from "@/types";

export function TrackingPage() {
  useWebSocket();
  const [selected, setSelected] = useState<Vehicle | null>(null);

  const { data: vehicles = [] } = useQuery({
    queryKey: ["vehicles"],
    queryFn: api.getVehicles,
    refetchInterval: 30_000,
  });

  const { data: latest = [] } = useQuery({
    queryKey: ["positions", "latest"],
    queryFn: api.getLatestPositions,
    refetchInterval: 10_000,
  });

  const { data: trail = [] } = useQuery({
    queryKey: ["positions", "trail", selected?.id],
    queryFn: () =>
      selected ? api.getPositions(selected.id, 200) : Promise.resolve([]),
    enabled: !!selected,
    refetchInterval: 10_000,
  });

  return (
    <div className="page page--tracking">
      <Header title="Tracking in tempo reale" />
      <div className="tracking-layout">
        <aside className="tracking-sidebar">
          <div className="tracking-sidebar-inner">
            <p className="tracking-count">{vehicles.length} veicoli</p>
            {vehicles.map((v) => (
              <VehicleCard
                key={v.id}
                vehicle={v}
                selected={selected?.id === v.id}
                onClick={() => setSelected((prev) => (prev?.id === v.id ? null : v))}
              />
            ))}
          </div>
        </aside>
        <div className="tracking-map">
          <FleetMap
            vehicles={vehicles}
            positions={latest}
            selectedVehicle={selected}
            trail={selected ? trail : undefined}
            onVehicleClick={(v) =>
              setSelected((prev) => (prev?.id === v.id ? null : v))
            }
          />
        </div>
      </div>
    </div>
  );
}
