export function formatPercent(value: string | number | null | undefined, suffix = "%") {
  if (value === null || value === undefined) return "-";
  const numeric = Number(value);
  const sign = numeric > 0 ? "+" : "";
  return `${sign}${numeric.toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}${suffix}`;
}

export function formatMoney(value: string | number | null | undefined) {
  if (value === null || value === undefined) return "-";
  return Number(value).toLocaleString("tr-TR", { style: "currency", currency: "TRY", maximumFractionDigits: 0 });
}

export function formatNumber(value: string | number | null | undefined) {
  if (value === null || value === undefined) return "-";
  return Number(value).toLocaleString("tr-TR", { maximumFractionDigits: 2 });
}
