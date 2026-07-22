import { act, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api, ApiError } from "../api/client";
import { mockConversation, mockToolCalls } from "../test/fixtures";
import { renderWithProviders } from "../test/render";
import type {
  AgentAnswer,
  ConversationDetail,
  ConversationSummary,
  ItemResponse,
  ListResponse,
} from "../types/api";
import ChatPage from "./ChatPage";

const getMock = vi.mocked(api.get);
const postMock = vi.mocked(api.post);

function conversationList(): ListResponse<ConversationSummary> {
  return {
    data: [
      {
        id: mockConversation.id,
        title: mockConversation.title,
        message_count: mockConversation.message_count,
        created_at: mockConversation.created_at,
        updated_at: mockConversation.updated_at,
      },
    ],
  };
}

function answer(
  overrides: Partial<AgentAnswer> = {},
): ItemResponse<AgentAnswer> {
  return {
    data: {
      answer: "PW2018 is delayed by airport operations.",
      tool_calls: mockToolCalls,
      conversation_id: 12,
      ...overrides,
    },
  };
}

function mockConversationApi(detail: ConversationDetail = mockConversation) {
  getMock.mockImplementation((path) => {
    if (path === "/agent/conversations") {
      return Promise.resolve(conversationList()) as never;
    }

    if (path === `/agent/conversations/${detail.id}`) {
      return Promise.resolve({ data: detail }) as never;
    }

    return Promise.reject(new Error(`Unexpected GET ${path}`));
  });
}

async function openMockConversation() {
  const user = userEvent.setup();
  const conversationButton = await screen.findByRole("button", {
    name: new RegExp(`^${mockConversation.title}`),
  });
  await user.click(conversationButton);
  return user;
}

describe("ChatPage conversation rendering", () => {
  beforeEach(() => {
    getMock.mockResolvedValue({ data: [] } as never);
    postMock.mockResolvedValue(answer() as never);
  });

  it("renders user and assistant messages in stored order", async () => {
    mockConversationApi();
    renderWithProviders(<ChatPage />, { route: "/chat" });

    await openMockConversation();

    const messages = screen.getAllByText(
      /Check flight PW2018|PW2018 is delayed|This is an older message/,
    );
    expect(messages).toHaveLength(3);
    expect(messages[0]).toHaveTextContent("Check flight PW2018");
    expect(messages[1]).toHaveTextContent(
      "PW2018 is delayed. Gate staff have been notified.",
    );
  });

  it("renders persisted tool calls in execution order", async () => {
    mockConversationApi();
    renderWithProviders(<ChatPage />, { route: "/chat" });

    await openMockConversation();

    const toolStatuses = screen.getAllByRole("status");
    expect(toolStatuses).toHaveLength(2);
    expect(toolStatuses[0]).toHaveAccessibleName("Tool succeeded");
    expect(toolStatuses[1]).toHaveAccessibleName("Tool failed");
    expect(within(toolStatuses[0]).getByText("get_flight_by_number")).toBeVisible();
    expect(within(toolStatuses[1]).getByText("get_available_gates")).toBeVisible();
    expect(within(toolStatuses[1]).getByText("Gate service unavailable")).toBeVisible();
  });

  it("renders legacy messages with missing tool calls without an empty section", async () => {
    mockConversationApi();
    renderWithProviders(<ChatPage />, { route: "/chat" });

    await openMockConversation();

    expect(screen.getByText("This is an older message.")).toBeVisible();
    expect(screen.queryByText("0 tools used")).not.toBeInTheDocument();
  });
});

describe("ChatPage submission", () => {
  beforeEach(() => {
    getMock.mockResolvedValue({ data: [] } as never);
    postMock.mockResolvedValue(answer() as never);
  });

  it("submits the exact prompt and renders the assistant response", async () => {
    const user = userEvent.setup();
    renderWithProviders(<ChatPage />, { route: "/chat" });
    const prompt = "Explain the status of PW2018";

    await user.type(screen.getByPlaceholderText(/Ask about delayed flights/), prompt);
    await user.click(screen.getByRole("button", { name: "Send message" }));

    expect(postMock).toHaveBeenCalledWith("/agent/query", {
      message: prompt,
      conversation_id: null,
    });
    expect(await screen.findByText("PW2018 is delayed by airport operations.")).toBeVisible();
    expect(screen.getByText("get_flight_by_number")).toBeVisible();
  });

  it("passes the active conversation identifier", async () => {
    mockConversationApi();
    const user = userEvent.setup();
    renderWithProviders(<ChatPage />, { route: "/chat" });
    await openMockConversation();

    await user.type(screen.getByPlaceholderText(/Ask about delayed flights/), "Any update?");
    await user.click(screen.getByRole("button", { name: "Send message" }));

    expect(postMock).toHaveBeenCalledWith("/agent/query", {
      message: "Any update?",
      conversation_id: 12,
    });
  });

  it("disables sending and prevents duplicate requests while pending", async () => {
    let resolveRequest!: (value: ItemResponse<AgentAnswer>) => void;
    postMock.mockReturnValue(
      new Promise((resolve) => {
        resolveRequest = resolve;
      }) as never,
    );
    const user = userEvent.setup();
    renderWithProviders(<ChatPage />, { route: "/chat" });

    await user.type(screen.getByPlaceholderText(/Ask about delayed flights/), "Check PW2018");
    const sendButton = screen.getByRole("button", { name: "Send message" });
    await user.click(sendButton);

    expect(sendButton).toBeDisabled();
    await user.click(sendButton);
    expect(postMock).toHaveBeenCalledTimes(1);

    await act(async () => resolveRequest(answer()));
    expect(await screen.findByText("PW2018 is delayed by airport operations.")).toBeVisible();
  });

  it("shows a readable API error and remains usable", async () => {
    postMock.mockRejectedValueOnce(new ApiError("AI service unavailable", 503));
    const user = userEvent.setup();
    renderWithProviders(<ChatPage />, { route: "/chat" });

    const input = screen.getByPlaceholderText(/Ask about delayed flights/);
    await user.type(input, "Check PW2018");
    await user.click(screen.getByRole("button", { name: "Send message" }));

    expect(await screen.findByText("AI service unavailable")).toBeVisible();
    expect(screen.queryByText("[object Object]")).not.toBeInTheDocument();
    await user.type(input, "Try another question");
    expect(screen.getByRole("button", { name: "Send message" })).toBeEnabled();
  });

  it("prefills a quick-action prompt without submitting it", async () => {
    renderWithProviders(<ChatPage />, {
      route: "/chat?prompt=Explain%20flight%20PW2018.",
    });

    expect(screen.getByPlaceholderText(/Ask about delayed flights/)).toHaveValue(
      "Explain flight PW2018.",
    );
    await waitFor(() => expect(getMock).toHaveBeenCalled());
    expect(postMock).not.toHaveBeenCalled();
  });
});
