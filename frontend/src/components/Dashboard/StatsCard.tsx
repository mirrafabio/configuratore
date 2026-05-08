import clsx from "clsx";

interface Props {
  label: string;
  value: number | string;
  icon: React.ReactNode;
  variant?: "default" | "success" | "warning" | "danger" | "info";
}

export function StatsCard({ label, value, icon, variant = "default" }: Props) {
  return (
    <div className={clsx("stats-card", `stats-card--${variant}`)}>
      <div className="stats-icon">{icon}</div>
      <div className="stats-body">
        <div className="stats-value">{value}</div>
        <div className="stats-label">{label}</div>
      </div>
    </div>
  );
}
