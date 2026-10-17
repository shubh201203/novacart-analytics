import React from 'react';
import { OverviewData } from '../types/analytics';
import { KpiCard } from '../components/KpiCard';
import { formatCompactINR, formatINR } from '../services/api';
import {
  TrendingUp,
  DollarSign,
  Users,
  ShoppingBag,
  RotateCcw,
  Percent
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  LineChart,
  Line,
  CartesianGrid,
  PieChart,
  Pie,
  Cell
} from 'recharts';

interface Props {
  data: OverviewData | null;
  loading: boolean;
}

const STATUS_COLORS: Record<string, string> = {
  Completed: '#00B4D8',
  Shipped: '#0077B6',
  Returned: '#F77F00',
  Cancelled: '#D62828',
  Processing: '#7209B7'
};

export const ExecutiveOverview: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#48CAE4]"></div>
      </div>
    );
  }

  if (!data) return null;

  const { kpis, revenue_by_region, profit_by_category, order_status_breakdown, revenue_trend } = data;

  return (
    <div className="space-y-6">
      {/* 6 Executive KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
        <KpiCard
          title="Post-Return Revenue"
          value={formatCompactINR(kpis.post_return_revenue)}
          subtitle="Realized Less Returns"
          icon={DollarSign}
          badgeColor="blue"
        />
        <KpiCard
          title="Realized Profit"
          value={formatCompactINR(kpis.realized_profit)}
          subtitle="Completed + Shipped"
          icon={TrendingUp}
          badgeColor="green"
        />
        <KpiCard
          title="Realized Margin"
          value={`${kpis.realized_margin}%`}
          subtitle="Operating Margin"
          icon={Percent}
          badgeColor="green"
        />
        <KpiCard
          title="Active Customers"
          value={kpis.active_customers.toLocaleString()}
          subtitle="Completed Order Accounts"
          icon={Users}
          badgeColor="blue"
        />
        <KpiCard
          title="Average Order Value"
          value={formatINR(kpis.average_order_value)}
          subtitle="Realized Orders AOV"
          icon={ShoppingBag}
          badgeColor="blue"
        />
        <KpiCard
          title="Return Rate"
          value={`${kpis.return_rate}%`}
          subtitle="Units Returned Ratio"
          icon={RotateCcw}
          badgeColor="amber"
        />
      </div>

      {/* Row 2: Region Bars, Category Bars, Order Status Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Realized Revenue by Region */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Realized Revenue by Region
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revenue_by_region} layout="vertical" margin={{ left: 10, right: 30 }}>
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

        {/* Profit by Product Category */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Profit by Product Category
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={profit_by_category} layout="vertical" margin={{ left: 20, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="category" stroke="#94A3B8" width={95} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Profit']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_profit" fill="#0077B6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Order Status Breakdown Donut */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
            Order Status Breakdown
          </h3>
          <div className="h-48">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={order_status_breakdown}
                  dataKey="distinct_orders"
                  nameKey="order_status"
                  cx="50%"
                  cy="50%"
                  innerRadius={45}
                  outerRadius={70}
                  paddingAngle={3}
                >
                  {order_status_breakdown.map((entry) => (
                    <Cell key={entry.order_status} fill={STATUS_COLORS[entry.order_status] || '#94A3B8'} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(val: any, name: any) => [`${Number(val).toLocaleString()} orders`, name]}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {/* Legend */}
          <div className="flex flex-wrap justify-center gap-2 mt-2">
            {order_status_breakdown.map((s) => (
              <div key={s.order_status} className="flex items-center space-x-1.5 text-xs text-slate-300">
                <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: STATUS_COLORS[s.order_status] || '#94A3B8' }} />
                <span>{s.order_status}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Row 3: Monthly Realized Revenue Trend Line */}
      <div className="bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
          Realized Revenue Monthly Trend (2022–2026)
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={revenue_trend} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#253252" vertical={false} />
              <XAxis dataKey="period" stroke="#94A3B8" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" height={50} />
              <YAxis stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
              <Tooltip
                formatter={(val: any) => [formatINR(Number(val)), 'Realized Revenue']}
                contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
              />
              <Line
                type="monotone"
                dataKey="realized_revenue"
                stroke="#00B4D8"
                strokeWidth={3}
                dot={{ r: 3, fill: '#00B4D8' }}
                activeDot={{ r: 6 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
