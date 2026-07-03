import { Dashboard } from "@/components/dashboard";
import { loadDashboard } from "@/lib/api";

export default async function Home({ searchParams }: { searchParams: Promise<{ fund?: string }> }) {
  const params = await searchParams;
  const data = await loadDashboard(params.fund);
  return <Dashboard {...data} />;
}
