import { ArrowLeft, Bot, Map, RefreshCw } from "lucide-react";
import { Link } from "react-router-dom";

export default function OperationsMapPage() {
  return (
    <div className="min-h-screen px-3 py-3 sm:px-5 sm:py-5">
      <div className="glass-panel mx-auto min-h-[calc(100vh-1.5rem)] max-w-[1540px] overflow-hidden rounded-[28px] sm:min-h-[calc(100vh-2.5rem)]">
        <header className="sticky top-0 z-30 border-b border-white/10 bg-paper/80 backdrop-blur-2xl">
          <div className="flex flex-wrap items-center justify-between gap-4 px-4 py-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan to-accent text-white shadow-[0_0_24px_rgba(29,214,245,0.25)]">
                <Map className="h-5 w-5" />
              </span>
              <div>
                <p className="font-semibold text-white">Airport Operations Map</p>
                <p className="text-xs text-muted">Live airside layout</p>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Link
                to="/"
                className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.035] px-3.5 py-2 text-xs font-medium text-muted transition-all hover:border-cyan/25 hover:text-cyan"
              >
                <ArrowLeft className="h-3.5 w-3.5" />
                Overview
              </Link>
              <Link
                to="/chat"
                className="flex items-center gap-2 rounded-xl border border-accent/20 bg-accent/10 px-3.5 py-2 text-xs font-medium text-cyan transition-all hover:bg-accent/20"
              >
                <Bot className="h-3.5 w-3.5" />
                AI Assistant
              </Link>
              <button
                type="button"
                className="flex items-center gap-2 rounded-xl border border-white/10 bg-white/[0.035] px-3.5 py-2 text-xs font-medium text-muted transition-all hover:border-cyan/25 hover:text-cyan"
              >
                <RefreshCw className="h-3.5 w-3.5" />
                Refresh
              </button>
            </div>
          </div>
        </header>

        <main className="px-4 py-6 sm:px-6 lg:px-8 lg:py-8">
          <section>
            <p className="label">Operations center</p>
            <h1 className="mt-2 text-2xl font-bold tracking-[-0.03em] text-white sm:text-3xl">
              Airport Operations Map
            </h1>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-muted">
              A live visual overview of terminal gates, assigned flights, and
              runway availability.
            </p>
          </section>

          <section className="soft-grid mt-6 min-h-96 rounded-3xl border border-white/10 bg-black/10 p-5 sm:p-7">
            <div className="flex min-h-80 items-center justify-center rounded-2xl border border-dashed border-white/10">
              <p className="text-sm text-muted">Loading airport layout…</p>
            </div>
          </section>
        </main>
      </div>
    </div>
  );
}
