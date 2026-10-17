import React from 'react';
import { CustomersData } from '../types/analytics';
import { KpiCard } from '../components/KpiCard';
import { formatCompactINR, formatINR } from '../services/api';
import { Users, UserCheck, UserMinus, Percent, DollarSign } from 'lucide-react';
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
  data: CustomersData | null;
  loading: boolean;
}

export const CustomerIntelligence: React.FC<Props> = ({ data, loading }) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#48CAE4]"></div>
      </div>
    );
  }

  if (!data) return null;

  const { kpis, top_customers, top_customers_by_frequency, revenue_by_region } = data;

  const repeatDonutData = [
    { name: 'Repeat Customers', value: kpis.repeat_customers, color: '#00B4D8' },
    { name: 'One-Time Customers', value: kpis.onetime_customers, color: '#0F2C59' }
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <KpiCard
          title="Active Customers"
          value={kpis.active_customers.toLocaleString()}
          subtitle="Completed Order Accounts"
          icon={Users}
        />
        <KpiCard
          title="Repeat Customers"
          value={kpis.repeat_customers.toLocaleString()}
          subtitle="> 1 Realized Order"
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
          subtitle="Retention Loyalty Ratio"
          icon={Percent}
          badgeColor="green"
        />
        <KpiCard
          title="Revenue Per Active Customer"
          value={formatCompactINR(kpis.revenue_per_active_customer)}
          subtitle="Customer Lifetime Value"
          icon={DollarSign}
          badgeColor="blue"
        />
      </div>

      {/* Row 2: Customer Purchase Frequency & Repeat Donut */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Top 10 Customers by Realized Orders (Frequency) */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Customer Purchase Frequency
            </h3>
            <span className="text-xs text-[#94A3B8] font-mono">Top by Orders</span>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={top_customers_by_frequency || top_customers} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" />
                <YAxis type="category" dataKey="customer_name" stroke="#94A3B8" width={110} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [`${Number(val).toLocaleString()} orders`, 'Realized Orders']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_orders" fill="#00B4D8" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Repeat vs One-Time Donut */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg flex flex-col justify-between">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-2">
            Repeat vs. One-Time Customers
          </h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={repeatDonutData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
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

        {/* Top 10 Customers by Realized Revenue */}
        <div className="lg:col-span-4 bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
            Top 10 Customers by Realized Revenue
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={top_customers} layout="vertical" margin={{ left: 10, right: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
                <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
                <YAxis type="category" dataKey="customer_name" stroke="#94A3B8" width={110} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(val: any) => [formatINR(Number(val)), 'Realized Revenue']}
                  contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
                />
                <Bar dataKey="realized_revenue" fill="#0077B6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Row 3: Regional Customer Revenue */}
      <div className="bg-[#1C2541] border border-[#3A506B]/50 rounded-xl p-5 shadow-lg">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4">
          Realized Revenue by Region
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={revenue_by_region} layout="vertical" margin={{ left: 10, right: 30 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#253252" horizontal={false} />
              <XAxis type="number" stroke="#94A3B8" tickFormatter={(v) => formatCompactINR(v)} />
              <YAxis type="category" dataKey="region" stroke="#94A3B8" width={70} />
              <Tooltip
                formatter={(val: any) => [formatINR(Number(val)), 'Realized Revenue']}
                contentStyle={{ backgroundColor: '#0B132B', borderColor: '#3A506B' }}
              />
              <Bar dataKey="realized_revenue" fill="#00B4D8" radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
