import { useEffect } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import type { Vehicle, Position } from "@/types";

// Fix default icon issue with webpack/vite
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
});

function makeIcon(status: Vehicle["status"]) {
  const colors: Record<Vehicle["status"], string> = {
    moving: "#22c55e",
    idle: "#f59e0b",
    online: "#3b82f6",
    offline: "#6b7280",
  };
  const color = colors[status];
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
    <path d="M14 0C6.3 0 0 6.3 0 14c0 9.9 14 22 14 22S28 23.9 28 14C28 6.3 21.7 0 14 0z" fill="${color}" stroke="white" stroke-width="2"/>
    <circle cx="14" cy="14" r="5" fill="white"/>
  </svg>`;
  return L.divIcon({
    html: svg,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -36],
    className: "",
  });
}

interface Props {
  vehicles: Vehicle[];
  positions: Position[];
  trail?: Position[];
  onVehicleClick?: (v: Vehicle) => void;
}

function FitBounds({ positions }: { positions: Position[] }) {
  const map = useMap();
  useEffect(() => {
    if (positions.length > 0) {
      const bounds = L.latLngBounds(
        positions.map((p) => [p.latitude, p.longitude] as [number, number])
      );
      map.fitBounds(bounds, { padding: [40, 40], maxZoom: 14 });
    }
  }, [positions.length]);
  return null;
}

export function FleetMap({
  vehicles,
  positions,
  trail,
  onVehicleClick,
}: Props) {
  const posMap = new Map(positions.map((p) => [p.vehicle_id, p]));

  return (
    <MapContainer
      center={[41.9028, 12.4964]}
      zoom={6}
      className="leaflet-map"
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      {positions.length > 0 && <FitBounds positions={positions} />}

      {vehicles.map((v) => {
        const pos = posMap.get(v.id);
        if (!pos) return null;
        return (
          <Marker
            key={v.id}
            position={[pos.latitude, pos.longitude]}
            icon={makeIcon(v.status)}
            eventHandlers={{ click: () => onVehicleClick?.(v) }}
          >
            <Popup>
              <strong>{v.name}</strong>
              <br />
              Targa: {v.plate}
              <br />
              Velocità: {pos.speed} km/h
              <br />
              Ignizione: {pos.ignition ? "Sì" : "No"}
            </Popup>
          </Marker>
        );
      })}

      {trail && trail.length > 1 && (
        <Polyline
          positions={trail.map((p) => [p.latitude, p.longitude] as [number, number])}
          color="#3b82f6"
          weight={3}
          opacity={0.7}
        />
      )}
    </MapContainer>
  );
}
