import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  LineChart,
  Users,
  Package,
  MapPin,
  CalendarDays,
  Sparkles
} from 'lucide-react';
import {
  FilterState,
  FilterOptions,
  OverviewData,
  SalesData,
  CustomersData,
  ProductsData,
  RegionalData,
  RetentionData
} from './types/analytics';
import {
  fetchFilters,
  fetchOverview,
  fetchSales,
  fetchCustomers,
  fetchProducts,
  fetchRegional,
  fetchRetention
} from './services/api';
import { FilterBar } from './components/FilterBar';
import { ExecutiveOverview } from './pages/ExecutiveOverview';
import { SalesProfitability } from './pages/SalesProfitability';
import { CustomerIntelligence } from './pages/CustomerIntelligence';
import { ProductAnalytics } from './pages/ProductAnalytics';
import { RegionalOperations } from './pages/RegionalOperations';
import { RetentionRFM } from './pages/RetentionRFM';

type Tab = 'overview' | 'sales' | 'customers' | 'products' | 'regional' | 'retention';

export function App() {
  const [activeTab, setActiveTab] = useState<Tab>('overview');
  const [filters, setFilters] = useState<FilterState>({});
  const [filterOptions, setFilterOptions] = useState<FilterOptions | null>(null);

  // Page States
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const [overviewData, setOverviewData] = useState<OverviewData | null>(null);
  const [salesData, setSalesData] = useState<SalesData | null>(null);
  const [customersData, setCustomersData] = useState<CustomersData | null>(null);
  const [productsData, setProductsData] = useState<ProductsData | null>(null);
  const [regionalData, setRegionalData] = useState<RegionalData | null>(null);
  const [retentionData, setRetentionData] = useState<RetentionData | null>(null);

  // Load Filter Options Once
  useEffect(() => {
    fetchFilters()
      .then(setFilterOptions)
      .catch((err) => console.error('Filter options load error:', err));
  }, []);

  // Fetch Active Tab Data on Filter or Tab Change
  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    setError(null);

    const loadData = async () => {
      try {
        switch (activeTab) {
          case 'overview': {
            const data = await fetchOverview(filters);
            if (isMounted) setOverviewData(data);
            break;
          }
          case 'sales': {
            const data = await fetchSales(filters);
            if (isMounted) setSalesData(data);
            break;
          }
          case 'customers': {
            const data = await fetchCustomers(filters);
            if (isMounted) setCustomersData(data);
            break;
          }
          case 'products': {
            const data = await fetchProducts(filters);
            if (isMounted) setProductsData(data);
            break;
          }
          case 'regional': {
            const data = await fetchRegional(filters);
            if (isMounted) setRegionalData(data);
            break;
          }
          case 'retention': {
            const data = await fetchRetention(filters);
            if (isMounted) setRetentionData(data);
            break;
          }
        }
      } catch (err: any) {
        if (isMounted) setError(err.message || 'Error fetching data from PostgreSQL API');
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    loadData();
    return () => {
      isMounted = false;
    };
  }, [activeTab, filters]);

  const tabs = [
    { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
    { id: 'sales', label: 'Sales & Profitability', icon: LineChart },
    { id: 'customers', label: 'Customer Intelligence', icon: Users },
    { id: 'products', label: 'Product Analytics', icon: Package },
    { id: 'regional', label: 'Regional Operations', icon: MapPin },
    { id: 'retention', label: 'Customer Retention & RFM', icon: CalendarDays }
  ];

  return (
    <div className="min-h-screen bg-[#0B132B] text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="bg-[#1C2541] border-b border-[#3A506B]/50 px-4 sm:px-6 lg:px-8 py-4 sticky top-0 z-50 shadow-md">
        <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-[#0077B6] to-[#48CAE4] flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <Sparkles className="text-white" size={20} />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h1 className="text-lg font-bold text-white tracking-tight">NovaCart Analytics</h1>
                <span className="text-[10px] bg-[#00B4D8]/10 text-[#48CAE4] px-2 py-0.5 rounded-full border border-[#00B4D8]/20 font-semibold uppercase tracking-wider">
                  PostgreSQL 18 Live
                </span>
              </div>
              <p className="text-xs text-slate-400">
                End-to-End E-Commerce Sales & Customer Analytics Platform | India Market
              </p>
            </div>
          </div>

          {/* Synthetic Data Disclaimer Pill */}
          <div className="text-[11px] text-slate-400 bg-[#0B132B]/80 px-3 py-1.5 rounded-lg border border-[#3A506B]/40 max-w-sm">
            <span className="font-semibold text-amber-400">Notice:</span> Synthetic e-commerce analytics demonstration.
          </div>
        </div>
      </header>

      {/* Main Body */}
      <main className="flex-1 max-w-[1600px] mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {/* Navigation Tabs */}
        <div className="flex space-x-1 border-b border-[#3A506B]/40 mb-6 overflow-x-auto pb-1 scrollbar-none">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as Tab)}
                className={`flex items-center space-x-2 px-4 py-2.5 rounded-t-lg font-medium text-xs sm:text-sm whitespace-nowrap transition-all cursor-pointer ${
                  isActive
                    ? 'bg-[#1C2541] text-[#48CAE4] border-t-2 border-x-2 border-[#00B4D8] border-b-transparent shadow-md'
                    : 'text-slate-400 hover:text-white hover:bg-[#1C2541]/40'
                }`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Global Slicer Bar */}
        <FilterBar
          filters={filters}
          options={filterOptions}
          onChange={setFilters}
          onReset={() => setFilters({})}
        />

        {/* Error Notice */}
        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-300 p-4 rounded-xl mb-6 text-sm flex items-center justify-between">
            <span>{error}</span>
            <button
              onClick={() => setFilters({ ...filters })}
              className="text-xs underline font-semibold"
            >
              Retry
            </button>
          </div>
        )}

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <ExecutiveOverview data={overviewData} loading={loading} />
        )}
        {activeTab === 'sales' && (
          <SalesProfitability data={salesData} loading={loading} />
        )}
        {activeTab === 'customers' && (
          <CustomerIntelligence data={customersData} loading={loading} />
        )}
        {activeTab === 'products' && (
          <ProductAnalytics data={productsData} loading={loading} />
        )}
        {activeTab === 'regional' && (
          <RegionalOperations data={regionalData} loading={loading} />
        )}
        {activeTab === 'retention' && (
          <RetentionRFM data={retentionData} loading={loading} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-[#1C2541]/80 border-t border-[#3A506B]/30 px-6 py-4 text-center text-xs text-slate-500">
        <p>NovaCart Analytics Platform &copy; 2026. Built with PostgreSQL 18, FastAPI, React 18, TypeScript & Tailwind CSS.</p>
      </footer>
    </div>
  );
}

export default App;
