import type { Vehicle, Position, Trip, Alert, DashboardStats } from "@/types";

const BASE = "/api";

async function req<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, options);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json();
}

export const api = {
  // Vehicles
  getVehicles: () => req<Vehicle[]>("/vehicles/"),
  getVehicle: (id: number) => req<Vehicle>(`/vehicles/${id}`),
  createVehicle: (data: Partial<Vehicle>) =>
    req<Vehicle>("/vehicles/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  updateVehicle: (id: number, data: Partial<Vehicle>) =>
    req<Vehicle>(`/vehicles/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }),
  deleteVehicle: (id: number) =>
    fetch(`${BASE}/vehicles/${id}`, { method: "DELETE" }),

  // Positions
  getLatestPositions: () => req<Position[]>("/positions/latest"),
  getPositions: (vehicleId?: number, limit = 200) =>
    req<Position[]>(
      `/positions/?limit=${limit}${vehicleId ? `&vehicle_id=${vehicleId}` : ""}`
    ),

  // Trips
  getTrips: (vehicleId?: number, limit = 50) =>
    req<Trip[]>(`/trips/?limit=${limit}${vehicleId ? `&vehicle_id=${vehicleId}` : ""}`),

  // Alerts
  getAlerts: (unacknowledgedOnly = false, limit = 100) =>
    req<Alert[]>(`/alerts/?limit=${limit}&unacknowledged_only=${unacknowledgedOnly}`),
  acknowledgeAlert: (id: number) =>
    req<Alert>(`/alerts/${id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ acknowledged: true }),
    }),
  acknowledgeAll: () =>
    fetch(`${BASE}/alerts/acknowledge-all`, { method: "POST" }),

  // Dashboard
  getStats: () => req<DashboardStats>("/dashboard/stats"),
};
