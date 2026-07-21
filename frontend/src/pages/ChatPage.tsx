import { useCallback, useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import {
  ArrowLeft,
  Bot,
  Check,
  MessageSquarePlus,
  Send,
  Trash2,
  Wrench,
  X,
} from "lucide-react";

import { api, ApiError } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type {
  AgentAnswer,
  ConversationDetail,
  ConversationSummary,
  ItemResponse,
  ListResponse,
  ToolCall,
} from "../types/api";

interface ChatTurn {
  key: string;
  role: "user" | "assistant";
  text: string;
  toolCalls?: ToolCall[];
}

const SUGGESTIONS = [
  "Which flights are delayed right now?",
  "Are there any available gates in Terminal 1?",
  "Show me the runways that are closed.",
  "What is the latest weather report?",
];

/** Renders the tools the agent ran to produce an answer. */
function ToolCallList({ toolCalls }: { toolCalls: ToolCall[] }) {
  if (toolCalls.length === 0) {
    return null;
  }

  return (
    <div className="mb-3 space-y-1.5">
      <p className="flex items-center gap-1.5 text-xs text-muted">
        <Wrench className="h-3 w-3" />
        {toolCalls.length === 1
          ? "1 tool used"
          : `${toolCalls.length} tools used`}
      </p>

      {toolCalls.map((call, index) => (
        <div
          key={`${call.tool}-${index}`}
          className={`flex flex-wrap items-center gap-2 rounded-lg border px-2.5 py-1.5 ${
            call.failed
              ? "border-alert/25 bg-alert/10"
              : "border-cyan/20 bg-cyan/[0.06]"
          }`}
        >
          {call.failed ? (
            <X className="h-3 w-3 shrink-0 text-alert" />
          ) : (
            <Check className="h-3 w-3 shrink-0 text-cyan" />
          )}

          <span
            className={`font-mono text-xs font-medium ${
              call.failed ? "text-alert" : "text-cyan"
            }`}
          >
            {call.tool}
          </span>

          {Object.entries(call.arguments).map(([name, value]) => (
            <span
              key={name}
              className="rounded bg-black/25 px-1.5 py-0.5 font-mono text-xs text-muted-light"
            >
              {name}: {String(value)}
            </span>
          ))}
        </div>
      ))}
    </div>
  );
}

export default function ChatPage() {
  const { user } = useAuth();

  const [conversations, setConversations] = useState<ConversationSummary[]>([]);
  const [conversationId, setConversationId] = useState<number | null>(null);
  const [turns, setTurns] = useState<ChatTurn[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  const loadConversations = useCallback(async () => {
    try {
      const result =
        await api.get<ListResponse<ConversationSummary>>("/agent/conversations");
      setConversations(result.data);
    } catch {
      // The sidebar is secondary; a failure here should not block chatting.
    }
  }, []);

  useEffect(() => {
    void loadConversations();
  }, [loadConversations]);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [turns, sending]);

  async function openConversation(id: number) {
    setError(null);

    try {
      const result = await api.get<ItemResponse<ConversationDetail>>(
        `/agent/conversations/${id}`,
      );

      // Turns with no text are tool calls and tool results, not chat.
      const restored: ChatTurn[] = result.data.messages
        .filter((message) => message.text)
        .map((message) => ({
          key: `stored-${message.id}`,
          role: message.role === "model" ? "assistant" : "user",
          text: message.text as string,
        }));

      setConversationId(id);
      setTurns(restored);
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Could not open that conversation.",
      );
    }
  }

  async function deleteConversation(id: number) {
    try {
      await api.delete(`/agent/conversations/${id}`);
      setConversations((current) => current.filter((item) => item.id !== id));

      if (conversationId === id) {
        startNewConversation();
      }
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "Could not delete that conversation.",
      );
    }
  }

  function startNewConversation() {
    setConversationId(null);
    setTurns([]);
    setError(null);
  }

  async function sendMessage(message: string) {
    const trimmed = message.trim();

    if (!trimmed || sending) {
      return;
    }

    setDraft("");
    setError(null);
    setTurns((current) => [
      ...current,
      { key: `user-${Date.now()}`, role: "user", text: trimmed },
    ]);
    setSending(true);

    try {
      const result = await api.post<ItemResponse<AgentAnswer>>("/agent/query", {
        message: trimmed,
        conversation_id: conversationId,
      });

      setTurns((current) => [
        ...current,
        {
          key: `agent-${Date.now()}`,
          role: "assistant",
          text: result.data.answer,
          toolCalls: result.data.tool_calls,
        },
      ]);

      setConversationId(result.data.conversation_id);
      void loadConversations();
    } catch (caught) {
      setError(
        caught instanceof ApiError
          ? caught.message
          : "The agent did not respond. Try again.",
      );
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="min-h-screen px-3 py-3 sm:px-5 sm:py-5">
      <div className="glass-panel mx-auto flex h-[calc(100vh-1.5rem)] max-w-[1540px] overflow-hidden rounded-[28px] sm:h-[calc(100vh-2.5rem)]">
        <aside className="hidden w-[275px] shrink-0 flex-col border-r border-white/10 bg-black/15 lg:flex">
          <div className="border-b border-white/10 px-4 py-4">
            <Link
              to="/"
              className="mb-4 flex items-center gap-2 text-xs text-muted transition-colors hover:text-white"
            >
              <ArrowLeft className="h-3.5 w-3.5" />
              Back to overview
            </Link>

            <button
              type="button"
              onClick={startNewConversation}
              className="flex w-full items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-accent-strong via-accent to-cyan py-2.5 text-sm font-semibold text-white shadow-[0_12px_30px_rgba(47,128,255,0.25)] transition-all hover:-translate-y-0.5"
            >
              <MessageSquarePlus className="h-4 w-4" />
              New conversation
            </button>
          </div>

          <div className="flex-1 space-y-1 overflow-y-auto px-3 py-4">
            {conversations.length === 0 ? (
              <p className="px-2 py-6 text-center text-xs text-muted">
                Your conversations will appear here.
              </p>
            ) : (
              conversations.map((conversation) => (
                <div
                  key={conversation.id}
                  className={`group flex items-center gap-2 rounded-xl px-3 py-2.5 transition-all ${
                    conversationId === conversation.id
                      ? "border border-accent/15 bg-gradient-to-r from-accent-strong/25 to-violet/10"
                      : "border border-transparent hover:bg-white/[0.045]"
                  }`}
                >
                  <button
                    type="button"
                    onClick={() => void openConversation(conversation.id)}
                    className="min-w-0 flex-1 text-left"
                  >
                    <p className="truncate text-sm text-white">
                      {conversation.title}
                    </p>
                    <p className="mt-0.5 text-xs text-muted">
                      {conversation.message_count} messages
                    </p>
                  </button>

                  <button
                    type="button"
                    aria-label={`Delete ${conversation.title}`}
                    onClick={() => void deleteConversation(conversation.id)}
                    className="shrink-0 text-muted opacity-0 transition-all hover:text-alert group-hover:opacity-100"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between gap-4 border-b border-white/10 px-4 py-4 sm:px-6">
            <div className="flex items-center gap-3">
              <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-cyan to-accent text-white shadow-[0_0_20px_rgba(29,214,245,0.35)]">
                <Bot className="h-5 w-5" />
              </span>

              <div>
                <p className="font-semibold tracking-tight text-white">
                  AI Assistant
                </p>
                <p className="text-xs text-muted">
                  Ask about flights, gates, runways, incidents and weather
                </p>
              </div>
            </div>

            <Link
              to="/"
              className="rounded-xl border border-white/10 bg-white/[0.035] px-3 py-2 text-xs font-medium text-muted transition-all hover:border-cyan/25 hover:text-cyan lg:hidden"
            >
              Overview
            </Link>
          </header>

          <div className="flex-1 overflow-y-auto px-4 py-6 sm:px-6">
            {turns.length === 0 ? (
              <div className="mx-auto max-w-2xl py-10 text-center">
                <h1 className="text-2xl font-bold tracking-[-0.03em] text-white">
                  What do you need to know, {user?.username}?
                </h1>
                <p className="mt-2 text-sm text-muted">
                  The assistant reads live airport data to answer.
                </p>

                <div className="mt-8 grid gap-3 sm:grid-cols-2">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      onClick={() => void sendMessage(suggestion)}
                      className="rounded-2xl border border-white/10 bg-white/[0.04] p-4 text-left text-sm text-muted-light backdrop-blur-xl transition-all hover:-translate-y-0.5 hover:border-cyan/20 hover:text-white"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="mx-auto max-w-3xl space-y-5">
                {turns.map((turn) =>
                  turn.role === "user" ? (
                    <div key={turn.key} className="flex justify-end">
                      <p className="max-w-[80%] whitespace-pre-wrap rounded-2xl rounded-br-md bg-gradient-to-r from-accent-strong to-accent px-4 py-3 text-sm text-white shadow-[0_12px_30px_rgba(47,128,255,0.2)]">
                        {turn.text}
                      </p>
                    </div>
                  ) : (
                    <div key={turn.key} className="flex gap-3">
                      <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan to-accent text-white">
                        <Bot className="h-4 w-4" />
                      </span>

                      <div className="min-w-0 flex-1 rounded-2xl rounded-tl-md border border-white/10 bg-white/[0.04] p-4 backdrop-blur-xl">
                        {turn.toolCalls && (
                          <ToolCallList toolCalls={turn.toolCalls} />
                        )}

                        <p className="whitespace-pre-wrap text-sm leading-6 text-muted-light">
                          {turn.text}
                        </p>
                      </div>
                    </div>
                  ),
                )}

                {sending && (
                  <div className="flex gap-3">
                    <span className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-cyan to-accent text-white">
                      <Bot className="h-4 w-4" />
                    </span>

                    <div className="flex items-center gap-1.5 rounded-2xl rounded-tl-md border border-white/10 bg-white/[0.04] px-4 py-4">
                      <span className="h-2 w-2 animate-pulse rounded-full bg-cyan" />
                      <span className="h-2 w-2 animate-pulse rounded-full bg-cyan [animation-delay:150ms]" />
                      <span className="h-2 w-2 animate-pulse rounded-full bg-cyan [animation-delay:300ms]" />
                    </div>
                  </div>
                )}

                <div ref={endOfMessagesRef} />
              </div>
            )}
          </div>

          <div className="border-t border-white/10 px-4 py-4 sm:px-6">
            <div className="mx-auto max-w-3xl">
              {error && (
                <p className="mb-3 rounded-xl border border-alert/25 bg-alert/10 px-3.5 py-2.5 text-xs text-alert">
                  {error}
                </p>
              )}

              <div className="flex items-end gap-3">
                <textarea
                  value={draft}
                  onChange={(event) => setDraft(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.shiftKey) {
                      event.preventDefault();
                      void sendMessage(draft);
                    }
                  }}
                  rows={1}
                  placeholder="Ask about delayed flights, gates or incidents…"
                  className="max-h-40 min-h-[48px] flex-1 resize-none rounded-xl border border-white/10 bg-black/15 px-4 py-3 text-sm text-white outline-none transition-all placeholder:text-muted/55 focus:border-cyan/60 focus:shadow-[0_0_0_4px_rgba(29,214,245,0.07)]"
                />

                <button
                  type="button"
                  onClick={() => void sendMessage(draft)}
                  disabled={sending || draft.trim().length === 0}
                  aria-label="Send message"
                  className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-gradient-to-r from-accent-strong via-accent to-cyan text-white shadow-[0_12px_30px_rgba(47,128,255,0.25)] transition-all hover:-translate-y-0.5 disabled:translate-y-0 disabled:opacity-40"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>

              <p className="mt-2 text-center text-xs text-muted">
                Enter to send, Shift + Enter for a new line
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}