import React from 'react';
import { SalesData } from '../types/analytics';
import { KpiCard } from '../components/KpiCard';
import { formatCompactINR, formatINR } from '../services/api';
import { DollarSign, Tag, TrendingUp, Percent } from 'lucide-react';
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
  Legend
} from 'recharts';

interface Props {
  data: SalesData | null;
  loading: boolean;
}

export const SalesProfitability: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#48CAE4]"></div>
      </div>
    );
  }

  if (!data) return null;

  const { kpis, monthly_performance, revenue_by_status, top_products } = data;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          title="Gross Sales"
          value={formatCompactINR(kpis.gross_sales)}
          subtitle="Pre-Discount Demand"
          icon={DollarSign}
        />
        <KpiCard
          title="Discount Amount"
          value={formatCompactINR(kpis.discount_amount)}
          subtitle="Promotional Markdowns"
          icon={Tag}
          badgeColor="amber"
        />
        <KpiCard
          title="Total Placed Revenue"
          value={formatCompactINR(kpis.total_placed_revenue)}
          subtitle="All 104,852 Order Lines"
          icon={TrendingUp}
          badgeColor="blue"
        />
        <KpiCard
          title="Realized Profit"
          value={formatCompactINR(kpis.realized_profit)}
          subtitle="Operating Profit"
          icon={TrendingUp}
          badgeColor="green"
        />
        <KpiCard
          title="Realized Margin"
          value={`${kpis.realized_margin}%`}
          subtitle="Realized Margin Ratio"
          icon={Percent}
          badgeColor="green"
        />
      </div>

      {/* Row 2: Monthly Realized Revenue vs Profit Combo Chart */}
      <div className="bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
          Monthly Realized Revenue vs. Profit
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={monthly_performance} margin={{ top: 10, right: 30, left: 20, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#253252" vertical={false} />
              <XAxis dataKey="period" stroke="#94A3B8" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" height={50} />
              <YAxis stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
              <Tooltip
                formatter={(val: any, name: any) => [formatINR(Number(val)), name === 'realized_revenue' ? 'Realized Revenue' : 'Realized Profit']}
                contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
              />
              <Legend verticalAlign="top" wrapperStyle={{ paddingBottom: 10 }} />
              <Bar dataKey="realized_revenue" name="Realized Revenue" fill="#00B4D8" radius={[4, 4, 0, 0]} />
              <Bar dataKey="realized_profit" name="Realized Profit" fill="#1A5D1A" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Row 3: Status Breakdown & Monthly Discount Depth */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Placed Revenue by Order Status */}
        <div className="lg:col-span-6 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Placed Revenue by Order Status
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={revenue_by_status} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="order_status" stroke="#94A3B8" width={80} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Placed Revenue']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="placed_net_revenue" fill="#0077B6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Monthly Discount Impact */}
        <div className="lg:col-span-6 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Monthly Discount Depth (% of Gross Demand)
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={monthly_performance} margin={{ top: 10, right: 30, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" vertical={false} />
                <XAxis dataKey="period" stroke="#94A3B8" tick={{ fontSize: 11 }} angle={-35} textAnchor="end" height={45} />
                <YAxis stroke="#94A3B8" tickFormatter={(v) => `${v}%`} />
                <Tooltip
                  formatter={(val: any) => [`${Number(val).toFixed(2)}%`, 'Discount %']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Line
                  type="monotone"
                  dataKey="discount_pct"
                  stroke="#F77F00"
                  strokeWidth={2.5}
                  dot={{ r: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 4: Top 10 Products by Realized Profit */}
      <div className="bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
          Top 10 Products by Realized Profit
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={top_products} layout="vertical" margin={{ left: 10, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
              <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
              <YAxis type="category" dataKey="product_name" stroke="#94A3B8" width={150} tick={{ fontSize: 11 }} />
              <Tooltip
                formatter={(val: any) => [formatINR(Number(val)), 'Realized Profit']}
                contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
              />
              <Bar dataKey="realized_profit" fill="#48CAE4" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
