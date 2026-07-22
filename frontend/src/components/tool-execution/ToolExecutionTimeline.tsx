import { Check, ChevronDown, CircleX, Wrench } from "lucide-react";
import type { ToolCall } from "../../types/api";

const names: Record<string, string> = {
  get_flight_by_number: "Get flight by number", get_flight_by_id: "Get flight details",
  get_all_flights: "Review all flights", find_delayed_flights: "Find delayed flights", search_flights: "Search flights",
  get_available_gates: "Find available gates", assign_flight_to_gate: "Assign flight to gate",
  get_runway_status: "Check runway status", get_runway_by_code: "Get runway details", update_runway_status: "Update runway status",
  get_all_incidents: "Review incidents", get_latest_weather: "Check latest weather",
};
const sensitive = /token|secret|password|credential|api.?key|authorization/i;
const safeEntries = (value: Record<string, unknown>) => Object.entries(value).filter(([key]) => !sensitive.test(key));
const humanName = (tool: string) => names[tool] ?? tool.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());

export default function ToolExecutionTimeline({ toolCalls }: { toolCalls?: ToolCall[] | null }) {
  if (!toolCalls?.length) return null;
  return <details className="mb-4 rounded-xl border border-white/10 bg-black/15" open={toolCalls.length <= 2}>
    <summary className="flex cursor-pointer list-none items-center gap-2 p-3 text-xs text-muted-light"><Wrench className="h-3.5 w-3.5 text-cyan" /><span className="font-medium">Operational tools</span><span className="text-muted">{toolCalls.length} step{toolCalls.length === 1 ? "" : "s"}</span><ChevronDown className="ml-auto h-3.5 w-3.5" /></summary>
    <ol className="border-t border-white/10 px-3 py-2">{toolCalls.map((call, index) => <li key={`${call.tool}-${index}`} role="status" aria-label={call.failed ? "Tool failed" : "Tool succeeded"} className="relative flex gap-3 border-l border-white/10 pb-4 pl-5 last:pb-2">
      <span className={`absolute -left-2 top-1 flex h-4 w-4 items-center justify-center rounded-full ${call.failed ? "bg-alert" : "bg-clear"}`}>{call.failed ? <CircleX className="h-3 w-3 text-white" /> : <Check className="h-3 w-3 text-paper" />}</span>
      <div className="min-w-0 flex-1"><div className="flex flex-wrap items-center gap-2"><span className="text-xs text-muted">{index + 1}.</span><p className="text-sm font-medium text-white">{humanName(call.tool)}</p><span className={call.failed ? "text-xs text-alert" : "text-xs text-clear"}>{call.failed ? "Failed" : "Completed"}</span></div>
        {safeEntries(call.arguments || {}).length > 0 && <p className="mt-1 break-words text-xs text-muted">{safeEntries(call.arguments).map(([key, value]) => `${key.replaceAll("_", " ")}: ${String(value)}`).join(" · ")}</p>}
        {call.error && <p className="mt-1 text-xs text-alert">{call.error}</p>}
        <details className="mt-2" open={toolCalls.length <= 2}><summary className="cursor-pointer text-xs text-muted hover:text-white">Technical details</summary><p className="mt-1 font-mono text-xs text-muted">{call.tool}</p></details>
      </div>
    </li>)}</ol>
  </details>;
}
