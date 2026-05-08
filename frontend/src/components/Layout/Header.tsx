import { Bell } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { api } from "@/services/api";

interface Props {
  title: string;
}

export function Header({ title }: Props) {
  const { data: stats } = useQuery({
    queryKey: ["stats"],
    queryFn: api.getStats,
    refetchInterval: 15_000,
  });

  const unread = stats?.unacknowledged_alerts ?? 0;

  return (
    <header className="page-header">
      <h1 className="page-title">{title}</h1>
      <div className="header-actions">
        <div className="alert-bell">
          <Bell size={20} />
          {unread > 0 && <span className="alert-badge">{unread}</span>}
        </div>
      </div>
    </header>
  );
}
