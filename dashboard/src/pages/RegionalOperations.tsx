import React from 'react';
import { RegionalData } from '../types/analytics';
import { KpiCard } from '../components/KpiCard';
import { formatCompactINR, formatINR } from '../services/api';
import { DollarSign, TrendingUp, ShoppingBag, RotateCcw } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

interface Props {
  data: RegionalData | null;
  loading: boolean;
}

export const RegionalOperations: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#48CAE4]"></div>
      </div>
    );
  }

  if (!data) return null;

  const { kpis, regional_summary, top_states, regional_matrix } = data;

  const categories = ['Apparel', 'Beauty & Personal Care', 'Books & Media', 'Electronics', 'Home & Kitchen', 'Sports & Outdoors'];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Realized Revenue"
          value={formatCompactINR(kpis.realized_revenue)}
          subtitle="All Regional Deliveries"
          icon={DollarSign}
        />
        <KpiCard
          title="Realized Profit"
          value={formatCompactINR(kpis.realized_profit)}
          subtitle="Operating Profit"
          icon={TrendingUp}
          badgeColor="green"
        />
        <KpiCard
          title="Realized Orders"
          value={kpis.realized_orders.toLocaleString()}
          subtitle="Completed + Shipped"
          icon={ShoppingBag}
          badgeColor="blue"
        />
        <KpiCard
          title="Return Rate"
          value={`${kpis.return_rate}%`}
          subtitle="Uniform Regional Baseline"
          icon={RotateCcw}
          badgeColor="amber"
        />
      </div>

      {/* Row 2: Regional Revenue, Regional Profit, Top States */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Realized Revenue by Region */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Realized Revenue by Region
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regional_summary} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="region" stroke="#94A3B8" width={65} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Revenue']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_revenue" fill="#00B4D8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Realized Profit by Region */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Realized Profit by Region
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={regional_summary} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="region" stroke="#94A3B8" width={65} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Profit']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_profit" fill="#0077B6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top States by Realized Revenue */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Top Locations by Realized Revenue
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={top_states} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="state" stroke="#94A3B8" width={100} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Revenue']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_revenue" fill="#48CAE4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 3: Regional Cross-Tab Revenue Matrix Table */}
      <div className="bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg overflow-x-auto">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
          Regional Revenue by Category Matrix
        </h3>
        <table className="w-full text-left text-xs">
          <thead className="bg-[#0B132B] text-slate-400 uppercase tracking-wider border-b border-[#3A506B]/50">
            <tr>
              <th className="py-2.5 px-3">Region</th>
              {categories.map((cat) => (
                <th key={cat} className="py-2.5 px-3 text-right">{cat}</th>
              ))}
              <th className="py-2.5 px-3 text-right text-white font-bold">Total</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#3A506B]/30 text-slate-200">
            {regional_matrix.map((row) => (
              <tr key={row.region} className="hover:bg-[#253252]/40 transition-colors">
                <td className="py-2.5 px-3 font-semibold text-white">{row.region}</td>
                {categories.map((cat) => (
                  <td key={cat} className="py-2.5 px-3 text-right">
                    {formatINR(row[cat] || 0)}
                  </td>
                ))}
                <td className="py-2.5 px-3 text-right font-bold text-[#48CAE4]">
                  {formatINR(row.total)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
