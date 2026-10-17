import React from 'react';
import { RetentionData } from '../types/analytics';
import { KpiCard } from '../components/KpiCard';
import { formatCompactINR, formatINR } from '../services/api';
import { Users, UserCheck, UserMinus, Percent } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface Props {
  data: RetentionData | null;
  loading: boolean;
}

export const RetentionRFM: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#48CAE4]"></div>
      </div>
    );
  }

  if (!data) return null;

  const { kpis, segment_distribution, customer_value_table, cohort_matrix } = data;

  const repeatDonutData = [
    { name: 'Repeat Customers', value: kpis.repeat_customers, color: '#00B4D8' },
    { name: 'One-Time Customers', value: kpis.onetime_customers, color: '#0F2C59' }
  ];

  // Pivot cohort matrix into { cohort_month, m0, m1, m2... }
  const cohortPivoted: Record<string, { cohort_month: string; cohort_size: number; [key: string]: any }> = {};
  cohort_matrix.forEach((item) => {
    if (!cohortPivoted[item.cohort_month]) {
      cohortPivoted[item.cohort_month] = {
        cohort_month: item.cohort_month,
        cohort_size: item.cohort_customers
      };
    }
    cohortPivoted[item.cohort_month][`m${item.month_offset}`] = item.retention_rate;
  });

  const cohortRows = Object.values(cohortPivoted).sort((a, b) => a.cohort_month.localeCompare(b.cohort_month));
  const maxOffsets = Math.min(18, Math.max(...cohort_matrix.map((c) => c.month_offset)));
  const offsetCols = Array.from({ length: maxOffsets + 1 }, (_, i) => i);

  const getHeatmapColor = (rate?: number) => {
    if (rate === undefined || rate === null) return 'bg-transparent text-transparent';
    if (rate >= 50) return 'bg-[#0077B6] text-white font-bold';
    if (rate >= 35) return 'bg-[#0096C7] text-white';
    if (rate >= 25) return 'bg-[#00B4D8] text-slate-900';
    if (rate >= 15) return 'bg-[#48CAE4] text-slate-900';
    if (rate > 0) return 'bg-[#90E0EF] text-slate-900';
    return 'bg-slate-800 text-slate-500';
  };

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Active Customers"
          value={kpis.active_customers.toLocaleString()}
          subtitle="Realized Accounts"
          icon={Users}
        />
        <KpiCard
          title="Repeat Customers"
          value={kpis.repeat_customers.toLocaleString()}
          subtitle="Multi-Order Buyers"
          icon={UserCheck}
          badgeColor="green"
        />
        <KpiCard
          title="One-Time Customers"
          value={kpis.onetime_customers.toLocaleString()}
          subtitle="Single Purchase Only"
          icon={UserMinus}
          badgeColor="amber"
        />
        <KpiCard
          title="Repeat Customer Share"
          value={`${kpis.repeat_customer_share}%`}
          subtitle="Retention Loyalty Benchmark"
          icon={Percent}
          badgeColor="green"
        />
      </div>

      {/* Row 2: Segment Revenue, Repeat Donut, Segment Accounts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Realized Revenue by Customer Segment */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Realized Revenue by Customer Segment
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={segment_distribution} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="customer_segment" stroke="#94A3B8" width={85} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Revenue']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_revenue" fill="#00B4D8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Repeat vs One-Time Donut */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
            Repeat vs. One-Time Customers
          </h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={repeatDonutData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={4}
                >
                  {repeatDonutData.map((entry) => (
                    <Cell key={entry.name} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any, name: any) => [`${Number(val).toLocaleString()} accounts`, name]}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex justify-center gap-4 text-xs text-slate-300">
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-[#00B4D8]" />
              <span>Repeat ({kpis.repeat_customer_share}%)</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded-full bg-[#0F2C59]" />
              <span>One-Time ({(100 - kpis.repeat_customer_share).toFixed(2)}%)</span>
            </div>
          </div>
        </div>

        {/* Customer Distribution by Segment */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Customer Distribution by Customer Segment
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={segment_distribution} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => `${(v / 1000).toFixed(1)}K`} />
                <YAxis type="category" dataKey="customer_segment" stroke="#94A3B8" width={85} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [`${Number(val).toLocaleString()} accounts`, 'Customer Accounts']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="customer_count" fill="#48CAE4" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 3: Customer Value Table & Monthly Cohort Heatmap */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Customer Value Table */}
        <div className="lg:col-span-5 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg overflow-x-auto">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Customer Value & Purchase Behavior
          </h3>
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0B132B] text-slate-400 uppercase tracking-wider border-b border-[#3A506B]/50">
              <tr>
                <th className="py-2.5 px-2">Customer ID</th>
                <th className="py-2.5 px-2 text-right">Revenue</th>
                <th className="py-2.5 px-2 text-right">Profit</th>
                <th className="py-2.5 px-2 text-right">Orders</th>
                <th className="py-2.5 px-2">Segment</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#3A506B]/30 text-slate-200">
              {customer_value_table.map((c) => (
                <tr key={c.customer_id} className="hover:bg-[#253252]/40 transition-colors">
                  <td className="py-2 px-2 font-mono text-[#48CAE4]">{c.customer_id}</td>
                  <td className="py-2 px-2 text-right font-medium">{formatINR(c.realized_revenue)}</td>
                  <td className="py-2 px-2 text-right text-emerald-400 font-medium">{formatINR(c.realized_profit)}</td>
                  <td className="py-2 px-2 text-right">{c.realized_orders}</td>
                  <td className="py-2 px-2 text-slate-400">{c.customer_segment}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Monthly Customer Cohort Retention Heatmap */}
        <div className="lg:col-span-7 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg overflow-x-auto">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Monthly Customer Cohort Retention (public.vw_cohort_retention)
            </h3>
            <span className="text-[10px] text-slate-400 bg-[#0B132B] px-2 py-1 rounded border border-[#3A506B]/30 font-mono">
              Month Offset: 0 to {maxOffsets}
            </span>
          </div>

          {/* Cohort Retention Color Scale Legend */}
          <div className="flex flex-wrap items-center gap-3 text-xs text-slate-300 mb-3 bg-[#0B132B]/60 p-2.5 rounded-lg border border-[#3A506B]/30">
            <span className="font-semibold text-slate-400">Retention Scale:</span>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-[#0077B6]" />
              <span>≥ 50%</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-[#0096C7]" />
              <span>35% – 49%</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-[#00B4D8]" />
              <span>25% – 34%</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-[#48CAE4]" />
              <span>15% – 24%</span>
            </div>
            <div className="flex items-center space-x-1.5">
              <span className="w-3 h-3 rounded bg-[#90E0EF]" />
              <span>&lt; 15%</span>
            </div>
          </div>

          <table className="w-full text-center text-[10px] border-collapse">
            <thead>
              <tr className="bg-[#0B132B] text-slate-400 border-b border-[#3A506B]/50">
                <th className="py-2 px-2 text-left">Cohort</th>
                <th className="py-2 px-1">Size</th>
                {offsetCols.map((m) => (
                  <th key={m} className="py-2 px-1 w-8">M{m}</th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[#3A506B]/20">
              {cohortRows.map((row) => (
                <tr key={row.cohort_month} className="hover:opacity-90">
                  <td className="py-1 px-2 text-left font-mono font-medium text-slate-300 whitespace-nowrap">
                    {row.cohort_month}
                  </td>
                  <td className="py-1 px-1 font-semibold text-white bg-[#0B132B]/50">
                    {row.cohort_size}
                  </td>
                  {offsetCols.map((m) => {
                    const rate = row[`m${m}`];
                    return (
                      <td
                        key={m}
                        className={`py-1 px-0.5 text-center transition-colors cursor-help ${getHeatmapColor(rate)}`}
                        title={rate !== undefined ? `Cohort: ${row.cohort_month} | Month +${m}\nRetention Rate: ${rate.toFixed(1)}%\nRetained Accounts: ${Math.round(row.cohort_size * (rate / 100))} of ${row.cohort_size}` : undefined}
                      >
                        {rate !== undefined ? `${Math.round(rate)}%` : ''}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
