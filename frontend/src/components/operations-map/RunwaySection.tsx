import { Route } from "lucide-react";

import type { Runway } from "../../types/api";

function isClosed(runway: Runway): boolean {
  return runway.status.toLowerCase() === "closed";
}

export default function RunwaySection({ runways }: { runways: Runway[] }) {
  return (
    <section className="mt-5 rounded-3xl border border-white/10 bg-white/[0.035] p-4 backdrop-blur-xl sm:p-6">
      <div className="flex items-center gap-3">
        <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet/10 text-violet">
          <Route className="h-4 w-4" />
        </span>
        <div>
          <h2 className="font-semibold text-white">Runway operations</h2>
          <p className="text-xs text-muted">{runways.length} configured runways</p>
        </div>
      </div>

      {runways.length === 0 ? (
        <div className="mt-5 rounded-2xl border border-dashed border-white/10 px-5 py-10 text-center">
          <p className="text-sm font-medium text-white">No runways to display</p>
          <p className="mt-1 text-xs text-muted">
            Runways will appear here once configured.
          </p>
        </div>
      ) : (
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {runways.map((runway) => {
            const closed = isClosed(runway);

            return (
              <article
                key={runway.id}
                className={`relative overflow-hidden rounded-2xl border p-5 ${
                  closed
                    ? "border-alert/25 bg-alert/[0.06]"
                    : "border-clear/25 bg-clear/[0.055]"
                }`}
              >
                <div className="absolute inset-x-5 top-1/2 border-t border-dashed border-white/20" />
                <div className="relative flex items-center justify-between gap-4">
                  <div className="rounded-lg bg-paper/85 px-3 py-2 backdrop-blur-xl">
                    <p className="text-xs text-muted">Runway</p>
                    <p className="mt-0.5 font-mono text-lg font-semibold text-white">
                      {runway.runway_code}
                    </p>
                  </div>
                  <div className="rounded-lg bg-paper/85 px-3 py-2 text-right backdrop-blur-xl">
                    <p className="flex items-center justify-end gap-1.5 text-sm font-medium text-white">
                      <span
                        className={`h-2 w-2 rounded-full ${
                          closed ? "bg-alert" : "bg-clear"
                        }`}
                      />
                      {closed ? "Closed" : "Open"}
                    </p>
                    <p className="mt-0.5 font-mono text-xs text-muted">
                      {runway.length.toLocaleString()} m
                    </p>
                  </div>
                </div>

                {closed && runway.closure_reason && (
                  <p className="relative mt-4 rounded-lg bg-paper/75 px-3 py-2 text-xs text-alert">
                    {runway.closure_reason}
                  </p>
                )}
              </article>
            );
          })}
        </div>
      )}
    </section>
  );
}
