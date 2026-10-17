export interface FilterState {
  year?: number;
  month?: number;
  region?: string;
  category?: string;
}

export interface FilterOptions {
  years: number[];
  months: { num: number; name: string }[];
  regions: string[];
  categories: string[];
}

export interface OverviewKPIs {
  post_return_revenue: number;
  realized_profit: number;
  realized_margin: number;
  active_customers: number;
  average_order_value: number;
  return_rate: number;
  placed_net_revenue: number;
  realized_net_revenue: number;
  returned_revenue: number;
  ordered_quantity: number;
  returned_quantity: number;
  realized_orders: number;
}

export interface RegionRevenue {
  region: string;
  realized_revenue: number;
}

export interface CategoryProfit {
  category: string;
  realized_profit: number;
}

export interface OrderStatusBreakdown {
  order_status: string;
  distinct_orders: number;
  net_revenue: number;
}

export interface RevenueTrendItem {
  period: string;
  year: number;
  month_num: number;
  realized_revenue: number;
  realized_profit: number;
}

export interface OverviewData {
  kpis: OverviewKPIs;
  revenue_by_region: RegionRevenue[];
  profit_by_category: CategoryProfit[];
  order_status_breakdown: OrderStatusBreakdown[];
  revenue_trend: RevenueTrendItem[];
}

export interface SalesKPIs {
  gross_sales: number;
  discount_amount: number;
  total_placed_revenue: number;
  realized_profit: number;
  realized_margin: number;
}

export interface MonthlyPerformanceItem {
  period: string;
  realized_revenue: number;
  realized_profit: number;
  discount_amount: number;
  discount_pct: number;
}

export interface StatusRevenueItem {
  order_status: string;
  placed_net_revenue: number;
  distinct_orders: number;
}

export interface TopProductItem {
  product_name: string;
  category?: string;
  realized_profit: number;
  realized_revenue: number;
}

export interface SalesData {
  kpis: SalesKPIs;
  monthly_performance: MonthlyPerformanceItem[];
  revenue_by_status: StatusRevenueItem[];
  top_products: TopProductItem[];
}

export interface CustomerKPIs {
  active_customers: number;
  repeat_customers: number;
  onetime_customers: number;
  repeat_customer_share: number;
  revenue_per_active_customer: number;
}

export interface TopCustomerItem {
  customer_name: string;
  customer_id: string;
  customer_segment: string;
  realized_orders: number;
  realized_revenue: number;
  realized_profit: number;
}

export interface CustomersData {
  kpis: CustomerKPIs;
  top_customers: TopCustomerItem[];
  top_customers_by_frequency: TopCustomerItem[];
  revenue_by_region: RegionRevenue[];
}

export interface ProductKPIs {
  realized_revenue: number;
  realized_profit: number;
  realized_margin: number;
  discount_pct: number;
}

export interface CategoryPerformanceItem {
  category: string;
  realized_revenue: number;
  realized_profit: number;
  realized_margin: number;
  discount_pct: number;
  units_sold: number;
}

export interface ProductsData {
  kpis: ProductKPIs;
  category_performance: CategoryPerformanceItem[];
  top_products: TopProductItem[];
}

export interface RegionalKPIs {
  realized_revenue: number;
  realized_profit: number;
  realized_orders: number;
  return_rate: number;
}

export interface RegionalSummaryItem {
  region: string;
  realized_revenue: number;
  realized_profit: number;
  realized_orders: number;
}

export interface TopStateItem {
  state: string;
  realized_revenue: number;
}

export interface RegionalMatrixItem {
  region: string;
  total: number;
  [category: string]: any;
}

export interface RegionalData {
  kpis: RegionalKPIs;
  regional_summary: RegionalSummaryItem[];
  top_states: TopStateItem[];
  regional_matrix: RegionalMatrixItem[];
}

export interface RetentionKPIs {
  active_customers: number;
  repeat_customers: number;
  onetime_customers: number;
  repeat_customer_share: number;
}

export interface SegmentDistributionItem {
  customer_segment: string;
  customer_count: number;
  realized_revenue: number;
}

export interface CustomerValueItem {
  customer_id: string;
  customer_segment: string;
  realized_revenue: number;
  realized_profit: number;
  realized_orders: number;
}

export interface CohortMatrixItem {
  cohort_month: string;
  month_offset: number;
  cohort_customers: number;
  retained_customers: number;
  retention_rate: number;
}

export interface RetentionData {
  kpis: RetentionKPIs;
  segment_distribution: SegmentDistributionItem[];
  customer_value_table: CustomerValueItem[];
  cohort_matrix: CohortMatrixItem[];
}
