import type { Charts, ComparisonAsset, Fund, KapStatus, Report, Summary } from "@/types/api";

const API_BASE = "https://aylik-fon-degisim-api.onrender.com/api";
export const PUBLIC_API_BASE = API_BASE.replace("http://backend:8000", "http://localhost:8000");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { ...init, cache: "no-store" });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json() as Promise<T>;
}

export async function loadDashboard(fundId?: string) {
  const [funds, kapStatus] = await Promise.all([request<Fund[]>("/funds"), request<KapStatus>("/kap/status")]);
  const fund = funds.find((item) => item.id === fundId) ?? funds[0];
  const reports = await request<Report[]>(`/funds/${fund.id}/reports`);
  const sorted = [...reports].sort((a, b) => a.period.localeCompare(b.period));
  if (sorted.length < 2) {
    return { fund, funds, kapStatus, reports: sorted, comparisonId: null, summary: null, assets: [], charts: null };
  }
  const comparison = await request<{ id: string }>("/comparisons", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      fund_id: fund.id,
      previous_report_id: sorted[0].id,
      current_report_id: sorted[1].id,
    }),
  });
  const [summary, assets, charts] = await Promise.all([
    request<Summary>(`/comparisons/${comparison.id}/summary`),
    request<ComparisonAsset[]>(`/comparisons/${comparison.id}/assets`),
    request<Charts>(`/comparisons/${comparison.id}/charts`),
  ]);
  return { fund, funds, kapStatus, reports: sorted, comparisonId: comparison.id, summary, assets, charts };
}
