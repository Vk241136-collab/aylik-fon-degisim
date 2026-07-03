"use client";

export default function ErrorPage({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <main className="flex min-h-screen items-center justify-center p-6">
      <div className="w-full max-w-xl rounded-md border border-border bg-white p-5 dark:bg-zinc-950">
        <h1 className="text-lg font-semibold">Veri alınamadı</h1>
        <p className="mt-2 text-sm text-zinc-600 dark:text-zinc-400">{error.message}</p>
        <button className="mt-4 rounded-md bg-teal-700 px-3 py-2 text-sm font-medium text-white" onClick={reset}>Tekrar dene</button>
      </div>
    </main>
  );
}
