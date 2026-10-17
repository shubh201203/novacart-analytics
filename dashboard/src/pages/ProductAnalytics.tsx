import React from 'react';
import { ProductsData } from '../types/analytics';
import { KpiCard } from '../components/KpiCard';
import { formatCompactINR, formatINR } from '../services/api';
import { DollarSign, TrendingUp, Percent, Tag } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ScatterChart,
  Scatter,
  ZAxis
} from 'recharts';

interface Props {
  data: ProductsData | null;
  loading: boolean;
}

export const ProductAnalytics: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#48CAE4]"></div>
      </div>
    );
  }

  if (!data) return null;

  const { kpis, category_performance, top_products } = data;

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Realized Revenue"
          value={formatCompactINR(kpis.realized_revenue)}
          subtitle="Catalog Gross Fulfillment"
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
          title="Realized Margin"
          value={`${kpis.realized_margin}%`}
          subtitle="Overall Catalog Margin"
          icon={Percent}
          badgeColor="green"
        />
        <KpiCard
          title="Average Discount %"
          value={`${kpis.discount_pct}%`}
          subtitle="Markdown Depth"
          icon={Tag}
          badgeColor="amber"
        />
      </div>

      {/* Row 2: Category Profit, Category Revenue, Discount vs Margin Scatter */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Realized Profit by Category */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Realized Profit by Category
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={category_performance} layout="vertical" margin={{ left: 15, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="category" stroke="#94A3B8" width={95} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Profit']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_profit" fill="#00B4D8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Realized Revenue by Category */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Realized Revenue by Category
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={category_performance} margin={{ top: 10, right: 10, left: 10, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" vertical={false} />
                <XAxis dataKey="category" stroke="#94A3B8" tick={{ fontSize: 10 }} angle={-25} textAnchor="end" height={45} />
                <YAxis stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Revenue']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_revenue" fill="#0077B6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Discount % vs Profit Margin Scatter Plot */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Discount % vs. Profit Margin
            </h3>
            <span className="text-[10px] text-slate-400 font-mono">By Category</span>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 15, right: 25, bottom: 25, left: 15 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" />
                <XAxis
                  type="number"
                  dataKey="discount_pct"
                  name="Discount %"
                  unit="%"
                  stroke="#94A3B8"
                  domain={['dataMin - 0.2', 'dataMax + 0.2']}
                  tick={{ fontSize: 10 }}
                  label={{ value: 'Promotional Discount %', position: 'insideBottom', offset: -12, fill: '#94A3B8', fontSize: 10 }}
                />
                <YAxis
                  type="number"
                  dataKey="realized_margin"
                  name="Profit Margin"
                  unit="%"
                  stroke="#94A3B8"
                  domain={[10, 70]}
                  tick={{ fontSize: 10 }}
                  label={{ value: 'Realized Margin %', angle: -90, position: 'insideLeft', offset: 0, fill: '#94A3B8', fontSize: 10, style: { textAnchor: 'middle' } }}
                />
                <ZAxis range={[100, 100]} />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  content={({ active, payload }: any) => {
                    if (active && payload && payload.length) {
                      const item = payload[0].payload;
                      return (
                        <div className="bg-[#0B132B] border border-[#3A506B] p-3 rounded-lg shadow-xl text-xs space-y-1">
                          <p className="font-bold text-[#48CAE4] text-sm">{item.category}</p>
                          <div className="text-slate-300">
                            <p><span className="text-slate-400">Discount:</span> <span className="font-mono text-amber-400">{item.discount_pct}%</span></p>
                            <p><span className="text-slate-400">Profit Margin:</span> <span className="font-mono text-emerald-400">{item.realized_margin}%</span></p>
                            <p><span className="text-slate-400">Realized Revenue:</span> <span className="font-mono text-white">{formatINR(item.realized_revenue)}</span></p>
                            <p><span className="text-slate-400">Realized Profit:</span> <span className="font-mono text-emerald-400">{formatINR(item.realized_profit)}</span></p>
                          </div>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Scatter name="Categories" data={category_performance} fill="#48CAE4" />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 3: Category Profitability Matrix & Top Products */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top 10 Products by Realized Profit */}
        <div className="lg:col-span-6 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
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
                <Bar dataKey="realized_profit" fill="#00B4D8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Performance Data Matrix Table */}
        <div className="lg:col-span-6 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg overflow-x-auto">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Category Profitability Matrix
          </h3>
          <table className="w-full text-left text-xs">
            <thead className="bg-[#0B132B] text-slate-400 uppercase tracking-wider border-b border-[#3A506B]/50">
              <tr>
                <th className="py-2.5 px-3">Category</th>
                <th className="py-2.5 px-3 text-right">Revenue</th>
                <th className="py-2.5 px-3 text-right">Profit</th>
                <th className="py-2.5 px-3 text-right">Margin %</th>
                <th className="py-2.5 px-3 text-right">Discount %</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#3A506B]/30 text-slate-200">
              {category_performance.map((c) => (
                <tr key={c.category} className="hover:bg-[#253252]/40 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-white">{c.category}</td>
                  <td className="py-2.5 px-3 text-right">{formatINR(c.realized_revenue)}</td>
                  <td className="py-2.5 px-3 text-right text-emerald-400 font-medium">{formatINR(c.realized_profit)}</td>
                  <td className="py-2.5 px-3 text-right font-bold text-[#48CAE4]">{c.realized_margin}%</td>
                  <td className="py-2.5 px-3 text-right text-amber-400">{c.discount_pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
