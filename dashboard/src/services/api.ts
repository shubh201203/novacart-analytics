import {
  FilterState,
  FilterOptions,
  OverviewData,
  SalesData,
  CustomersData,
  ProductsData,
  RegionalData,
  RetentionData
} from '../types/analytics';

const API_ORIGIN = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');
const BASE_URL = API_ORIGIN ? `${API_ORIGIN}/api` : '/api';

function buildQuery(filters: FilterState): string {
  const params = new URLSearchParams();
  if (filters.year) params.append('year', filters.year.toString());
  if (filters.month) params.append('month', filters.month.toString());
  if (filters.region && filters.region !== 'All') params.append('region', filters.region);
  if (filters.category && filters.category !== 'All') params.append('category', filters.category);
  const q = params.toString();
  return q ? `?${q}` : '';
}

export async function fetchFilters(): Promise<FilterOptions> {
  const res = await fetch(`${BASE_URL}/filters`);
  if (!res.ok) throw new Error('Failed to fetch filter options');
  return res.json();
}

export async function fetchOverview(filters: FilterState): Promise<OverviewData> {
  const res = await fetch(`${BASE_URL}/overview${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Failed to fetch overview analytics');
  return res.json();
}

export async function fetchSales(filters: FilterState): Promise<SalesData> {
  const res = await fetch(`${BASE_URL}/sales${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Failed to fetch sales analytics');
  return res.json();
}

export async function fetchCustomers(filters: FilterState): Promise<CustomersData> {
  const res = await fetch(`${BASE_URL}/customers${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Failed to fetch customer analytics');
  return res.json();
}

export async function fetchProducts(filters: FilterState): Promise<ProductsData> {
  const res = await fetch(`${BASE_URL}/products${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Failed to fetch product analytics');
  return res.json();
}

export async function fetchRegional(filters: FilterState): Promise<RegionalData> {
  const res = await fetch(`${BASE_URL}/regional${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Failed to fetch regional analytics');
  return res.json();
}

export async function fetchRetention(filters: FilterState): Promise<RetentionData> {
  const res = await fetch(`${BASE_URL}/retention${buildQuery(filters)}`);
  if (!res.ok) throw new Error('Failed to fetch retention analytics');
  return res.json();
}

export function formatINR(val: number): string {
  if (val >= 10000000) {
    return `₹${(val / 10000000).toFixed(2)} Cr`;
  }
  if (val >= 100000) {
    return `₹${(val / 100000).toFixed(2)} L`;
  }
  if (val >= 1000) {
    return `₹${(val / 1000).toFixed(1)} K`;
  }
  return `₹${val.toLocaleString('en-IN')}`;
}

export function formatCompactINR(val: number): string {
  if (val >= 1000000000) {
    return `₹${(val / 1000000000).toFixed(2)}bn`;
  }
  if (val >= 1000000) {
    return `₹${(val / 1000000).toFixed(2)}M`;
  }
  if (val >= 1000) {
    return `₹${(val / 1000).toFixed(1)}K`;
  }
  return `₹${val.toFixed(2)}`;
}
