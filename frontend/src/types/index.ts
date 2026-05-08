export type VehicleStatus = "online" | "offline" | "moving" | "idle";

export type AlertType =
  | "speeding"
  | "geofence_exit"
  | "geofence_enter"
  | "ignition_on"
  | "ignition_off"
  | "low_battery"
  | "harsh_braking"
  | "harsh_acceleration"
  | "device_offline";

export interface Vehicle {
  id: number;
  name: string;
  plate: string;
  model: string | null;
  driver: string | null;
  imei: string | null;
  status: VehicleStatus;
  last_seen: string | null;
  created_at: string;
}

export interface Position {
  id: number;
  vehicle_id: number;
  timestamp: string;
  latitude: number;
  longitude: number;
  altitude: number;
  angle: number;
  speed: number;
  satellites: number;
  ignition: boolean;
  movement: boolean;
  battery_voltage: number | null;
  gsm_signal: number | null;
  odometer: number | null;
}

export interface Trip {
  id: number;
  vehicle_id: number;
  start_time: string;
  end_time: string | null;
  start_lat: number;
  start_lng: number;
  end_lat: number | null;
  end_lng: number | null;
  start_address: string | null;
  end_address: string | null;
  distance_km: number;
  max_speed: number;
  avg_speed: number;
  duration_sec: number;
}

export interface Alert {
  id: number;
  vehicle_id: number;
  type: AlertType;
  message: string;
  latitude: number | null;
  longitude: number | null;
  speed: number | null;
  acknowledged: boolean;
  created_at: string;
}

export interface DashboardStats {
  total_vehicles: number;
  online_vehicles: number;
  moving_vehicles: number;
  idle_vehicles: number;
  offline_vehicles: number;
  active_trips: number;
  unacknowledged_alerts: number;
  total_distance_today_km: number;
}
