export type Fund = {
  id: string;
  code: string;
  name: string;
  company_id: string;
};

export type Report = {
  id: string;
  fund_id: string;
  period: string;
  report_date: string;
  file_name: string;
  file_type: string;
  total_value: string | null;
  parsed_row_count: number;
  error_count: number;
  parse_status: string;
};

export type Summary = {
  fund_code: string;
  fund_name: string;
  company_name: string;
  previous_period: string;
  current_period: string;
  previous_total_value: string | null;
  current_total_value: string | null;
  total_value_delta: string | null;
  equity_weight_previous: string;
  equity_weight_current: string;
  equity_weight_delta_pp: string;
  new_count: number;
  exited_count: number;
  increased_count: number;
  decreased_count: number;
  largest_position: string | null;
  largest_new_position: string | null;
  top_increased_position: string | null;
  top_decreased_position: string | null;
  concentration_hhi_previous: string;
  concentration_hhi_current: string;
  analysis_text: string;
};

export type ComparisonAsset = {
  asset_key: string;
  asset_name: string;
  asset_type: string;
  status_labels: string[];
  previous_quantity: string | null;
  current_quantity: string | null;
  quantity_delta: string | null;
  previous_market_value: string | null;
  current_market_value: string | null;
  market_value_delta: string | null;
  previous_weight: string | null;
  current_weight: string | null;
  weight_delta_pp: string | null;
  weight_change_pct: string | null;
  transaction_effect: string | null;
  price_effect: string | null;
  unit_price_is_estimated: boolean;
};

export type Charts = {
  asset_class_distribution: Array<{ asset_type: string; previous: string; current: string }>;
  top_assets: Array<{ name: string; weight: string; type: string }>;
  weight_increases: Array<{ name: string; delta: string; current: string | null }>;
  weight_decreases: Array<{ name: string; delta: string; current: string | null }>;
  currency_distribution: Array<{ currency: string; weight: string }>;
};

export type KapStatus = {
  enabled: boolean;
  last_started_at: string | null;
  last_finished_at: string | null;
  last_status: string;
  last_message: string | null;
  discovered_funds: number;
  discovered_disclosures: number;
  downloaded_reports: number;
  parse_jobs_created: number;
  errors: string[];
};
