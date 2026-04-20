interface Props {
  label: string;
  value: string | number;
  icon?: string;
  subValue?: string;
}

export function StatCard({ label, value, icon, subValue }: Props) {
  return (
    <div className="stat-card">
      {icon && <span className="stat-icon">{icon}</span>}
      <div className="stat-content">
        <span className="stat-label">{label}</span>
        <span className="stat-value">{value}</span>
        {subValue && <span className="stat-sub">{subValue}</span>}
      </div>
    </div>
  );
}
