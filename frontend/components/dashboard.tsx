"use client";

import { ArrowDownRight, ArrowUpRight, Download, Filter, Search, ShieldCheck } from "lucide-react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  Treemap,
  XAxis,
  YAxis,
} from "recharts";

import type { Charts, ComparisonAsset, Fund, KapStatus, Report, Summary } from "@/types/api";
import { PUBLIC_API_BASE } from "@/lib/api";
import { formatMoney, formatNumber, formatPercent } from "@/lib/format";

type Props = {
  fund: Fund;
  funds: Fund[];
  kapStatus: KapStatus;
  reports: Report[];
  summary: Summary | null;
  assets: ComparisonAsset[];
  charts: Charts | null;
  comparisonId: string | null;
};

export function Dashboard({ fund, funds, kapStatus, reports, summary, assets, charts, comparisonId }: Props) {
  if (!summary || !charts || !comparisonId) {
    return (
      <Shell fund={fund} funds={funds} kapStatus={kapStatus}>
        <section className="p-6">
          <Panel title="Rapor bekleniyor">
            <p className="text-sm text-zinc-600 dark:text-zinc-400">Bu fon için karşılaştırma yapabilmek adına en az iki aylık portföy dağılım raporu yüklenmeli.</p>
          </Panel>
        </section>
      </Shell>
    );
  }
  const equityAssets = assets.filter((asset) => asset.asset_type === "Hisse senedi");
  const rows = assets.slice().sort((a, b) => Number(b.current_weight ?? 0) - Number(a.current_weight ?? 0));

  return (
    <Shell fund={fund} funds={funds} kapStatus={kapStatus}>
      <header className="border-b border-border bg-white/80 px-6 py-4 backdrop-blur dark:bg-zinc-950/80">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="text-sm text-zinc-600 dark:text-zinc-400">{summary.company_name}</p>
            <h1 className="text-2xl font-semibold">{summary.fund_code} · {summary.fund_name}</h1>
            <p className="mt-1 text-sm text-zinc-500">{funds.length} fon katalogda, {reports.length} rapor bu fonda kayıtlı</p>
            {fund.fund_type ? <div className="mt-2 inline-flex rounded border border-border px-2 py-1 text-xs text-zinc-600 dark:text-zinc-300">{fund.fund_type}</div> : null}
          </div>
          <div className="flex items-center gap-2">
            <button className="inline-flex h-9 items-center gap-2 rounded-md border border-border px-3 text-sm">
              <Filter size={16} /> {summary.previous_period} / {summary.current_period}
            </button>
            <a
              className="inline-flex h-9 items-center gap-2 rounded-md bg-teal-700 px-3 text-sm font-medium text-white"
              href={`${PUBLIC_API_BASE}/comparisons/${comparisonId}/export?format=csv`}
            >
              <Download size={16} /> CSV
            </a>
          </div>
        </div>
      </header>

      <section className="grid gap-4 px-6 py-5 lg:grid-cols-5">
        <Metric title="Güncel fon değeri" value={formatMoney(summary.current_total_value)} sub={formatMoney(summary.total_value_delta)} positive={Number(summary.total_value_delta) >= 0} />
        <Metric title="Hisse oranı" value={formatPercent(summary.equity_weight_current)} sub={`${formatPercent(summary.equity_weight_delta_pp, " yp")} değişim`} positive={Number(summary.equity_weight_delta_pp) >= 0} />
        <Metric title="Yeni varlık" value={String(summary.new_count)} sub={summary.largest_new_position ?? "Yeni pozisyon yok"} />
        <Metric title="Çıkan varlık" value={String(summary.exited_count)} sub="Tamamen kapanan pozisyon" positive={false} />
        <Metric title="Yoğunlaşma HHI" value={formatNumber(summary.concentration_hhi_current)} sub={`${formatNumber(summary.concentration_hhi_previous)} önceki`} />
      </section>

      <section className="px-6 pb-5">
        <div className="border-y border-border bg-white px-4 py-3 text-sm leading-6 dark:bg-zinc-950">
          <div className="mb-2 inline-flex items-center gap-2 font-medium"><ShieldCheck size={16} /> Kurallı analiz özeti</div>
          <p className="max-w-6xl text-zinc-700 dark:text-zinc-300">{summary.analysis_text}</p>
        </div>
      </section>

      <section className="grid gap-5 px-6 pb-5 xl:grid-cols-3">
        <Panel title="Varlık sınıfı dağılımı" className="xl:col-span-2">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={charts.asset_class_distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="asset_type" tick={{ fontSize: 12 }} />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip formatter={(value) => formatPercent(String(value))} />
              <Legend />
              <Bar dataKey="previous" name="Önceki" fill="#64748b" radius={[4, 4, 0, 0]} />
              <Bar dataKey="current" name="Güncel" fill="#0f766e" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </Panel>
        <Panel title="Güncel ilk 10 pozisyon">
          <ResponsiveContainer width="100%" height={280}>
            <Treemap data={charts.top_assets.map((item) => ({ name: item.name, size: Number(item.weight) }))} dataKey="size" nameKey="name" aspectRatio={4 / 3} stroke="#fff" fill="#0f766e" />
          </ResponsiveContainer>
        </Panel>
      </section>

      <section className="grid gap-5 px-6 pb-5 xl:grid-cols-2">
        <ChangeList title="En fazla ağırlık artırılanlar" items={charts.weight_increases} positive />
        <ChangeList title="En fazla ağırlık azaltılanlar" items={charts.weight_decreases} />
      </section>

      <section className="px-6 pb-8">
        <Panel title="Tüm varlıklar">
          <div className="mb-3 flex items-center gap-2">
            <div className="flex h-9 min-w-72 items-center gap-2 rounded-md border border-border px-3 text-sm text-zinc-500">
              <Search size={16} /> Varlık, kod veya statü ara
            </div>
            <span className="text-sm text-zinc-500">{equityAssets.length} hisse, {assets.length} toplam varlık</span>
          </div>
          <div className="max-h-[520px] overflow-auto">
            <table className="w-full border-collapse text-sm">
              <thead className="sticky top-0 bg-zinc-100 text-left dark:bg-zinc-900">
                <tr>
                  {["Varlık", "Tür", "Statü", "Adet farkı", "Piyasa değeri farkı", "Ağırlık farkı", "İşlem/Fiyat etkisi"].map((head) => (
                    <th className="border-b border-border px-3 py-2 font-medium" key={head}>{head}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {rows.map((asset) => (
                  <tr className="border-b border-border/70 hover:bg-zinc-50 dark:hover:bg-zinc-900" key={asset.asset_key}>
                    <td className="px-3 py-2 font-medium">{asset.asset_name}</td>
                    <td className="px-3 py-2">{asset.asset_type}</td>
                    <td className="px-3 py-2">
                      <div className="flex flex-wrap gap-1">{asset.status_labels.map((label) => <span className="rounded border border-border px-2 py-0.5 text-xs" key={label}>{label}</span>)}</div>
                    </td>
                    <td className="px-3 py-2">{formatNumber(asset.quantity_delta)}</td>
                    <td className="px-3 py-2">{formatMoney(asset.market_value_delta)}</td>
                    <td className={Number(asset.weight_delta_pp ?? 0) >= 0 ? "px-3 py-2 text-positive" : "px-3 py-2 text-negative"}>{formatPercent(asset.weight_delta_pp, " yp")}</td>
                    <td className="px-3 py-2">{formatMoney(asset.transaction_effect)} / {formatMoney(asset.price_effect)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </section>
    </Shell>
  );
}

function Shell({ fund, funds, kapStatus, children }: { fund: Fund; funds: Fund[]; kapStatus: KapStatus; children: React.ReactNode }) {
  return (
    <main className="grid min-h-screen bg-background lg:grid-cols-[300px_1fr]">
      <aside className="border-r border-border bg-white dark:bg-zinc-950">
        <div className="border-b border-border p-4">
          <div className="text-lg font-semibold">Aylık Fon Değişim</div>
          <div className="mt-1 text-sm text-zinc-500">aylıkfondeğişim.com için KAP kaynaklı fon analiz sitesi</div>
          <div className="mt-3 rounded-md border border-border bg-zinc-50 p-3 text-xs dark:bg-zinc-900">
            <div className="font-medium">KAP veri hattı</div>
            <div className="mt-1 text-zinc-500">{kapStatus.enabled ? "Canlı senkronizasyon açık" : "Canlı senkronizasyon hazırlık modunda"}</div>
            <div className="mt-2 text-zinc-500">Son durum: {kapStatus.last_status}</div>
          </div>
        </div>
        <div className="p-3">
          <div className="mb-3 flex h-9 items-center gap-2 rounded-md border border-border px-3 text-sm text-zinc-500">
            <Search size={16} /> Fon kodu veya adı ara
          </div>
          <nav className="max-h-[calc(100vh-150px)] space-y-1 overflow-auto">
            {funds.map((item) => {
              const active = item.id === fund.id;
              return (
                <a
                  className={`block rounded-md border px-3 py-2 text-sm ${active ? "border-teal-700 bg-teal-50 text-teal-900 dark:bg-teal-950 dark:text-teal-50" : "border-transparent hover:border-border hover:bg-zinc-50 dark:hover:bg-zinc-900"}`}
                  href={`/?fund=${item.id}`}
                  key={item.id}
                >
                  <span className="block font-semibold">{item.code}</span>
                  <span className="line-clamp-2 text-xs text-zinc-500">{item.name}</span>
                  {item.fund_type ? <span className="mt-1 block truncate text-[11px] text-teal-700 dark:text-teal-300">{item.fund_type}</span> : null}
                </a>
              );
            })}
          </nav>
        </div>
      </aside>
      <div className="min-w-0">{children}</div>
    </main>
  );
}

function Metric({ title, value, sub, positive = true }: { title: string; value: string; sub: string; positive?: boolean }) {
  const Icon = positive ? ArrowUpRight : ArrowDownRight;
  return (
    <div className="rounded-md border border-border bg-white p-4 dark:bg-zinc-950">
      <div className="mb-2 flex items-center justify-between text-sm text-zinc-500"><span>{title}</span><Icon size={16} className={positive ? "text-positive" : "text-negative"} /></div>
      <div className="text-xl font-semibold">{value}</div>
      <div className="mt-1 truncate text-sm text-zinc-500">{sub}</div>
    </div>
  );
}

function Panel({ title, children, className = "" }: { title: string; children: React.ReactNode; className?: string }) {
  return <div className={`rounded-md border border-border bg-white p-4 dark:bg-zinc-950 ${className}`}><h2 className="mb-3 text-sm font-semibold">{title}</h2>{children}</div>;
}

function ChangeList({ title, items, positive = false }: { title: string; items: Array<{ name: string; delta: string; current: string | null }>; positive?: boolean }) {
  return (
    <Panel title={title}>
      <div className="space-y-2">
        {items.map((item) => (
          <div className="flex items-center justify-between gap-4 border-b border-border pb-2 last:border-0" key={`${title}-${item.name}`}>
            <span className="truncate text-sm font-medium">{item.name}</span>
            <span className={positive ? "text-sm font-semibold text-positive" : "text-sm font-semibold text-negative"}>{formatPercent(item.delta, " yp")}</span>
          </div>
        ))}
      </div>
    </Panel>
  );
}
