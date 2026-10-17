import React from 'react';
import { LucideIcon } from 'lucide-react';

interface KpiCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  badge?: string;
  badgeColor?: 'green' | 'blue' | 'amber' | 'red';
}

export const KpiCard: React.FC<KpiCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  badge,
  badgeColor = 'blue'
}) => {
  const badgeClasses = {
    green: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
    amber: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    red: 'bg-rose-500/10 text-rose-400 border-rose-500/20',
  }[badgeColor];

  return (
    <div className="bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg relative overflow-hidden transition-all duration-200 hover:border-[#48CAE4]/50 hover:shadow-cyan-500/5">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm font-medium text-slate-400 uppercase tracking-wider">{title}</span>
        {Icon && (
          <div className="p-2 rounded-lg bg-[#0B132B]/60 text-[#48CAE4]">
            <Icon size={18} />
          </div>
        )}
      </div>
      <div className="flex items-baseline space-x-2">
        <span className="text-2xl font-bold tracking-tight text-white">{value}</span>
        {badge && (
          <span className={`text-xs px-2 py-0.5 rounded-full border ${badgeClasses}`}>
            {badge}
          </span>
        )}
      </div>
      {subtitle && <p className="text-xs text-slate-400 mt-1">{subtitle}</p>}
    </div>
  );
};
