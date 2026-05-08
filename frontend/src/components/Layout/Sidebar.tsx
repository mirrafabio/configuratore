import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Truck,
  MapPin,
  Route,
  Bell,
  Settings,
} from "lucide-react";
import clsx from "clsx";

const links = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard" },
  { to: "/fleet", icon: Truck, label: "Flotta" },
  { to: "/tracking", icon: MapPin, label: "Tracking" },
  { to: "/trips", icon: Route, label: "Percorsi" },
  { to: "/alerts", icon: Bell, label: "Avvisi" },
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <Truck size={24} className="logo-icon" />
        <span>Fleet Manager</span>
      </div>
      <nav className="sidebar-nav">
        {links.map(({ to, icon: Icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              clsx("nav-link", { "nav-link--active": isActive })
            }
          >
            <Icon size={18} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <span className="teltonika-badge">Teltonika Ready</span>
      </div>
    </aside>
  );
}
