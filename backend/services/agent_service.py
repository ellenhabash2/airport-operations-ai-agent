"""
Main AI agent orchestration service.
"""

from google.genai import types

from services.gemini_service import GeminiService
from services.tool_executor import ToolExecutor


SYSTEM_PROMPT = """
You are AeroMind, an AI assistant for airport operations.

Your role is to assist airport staff with operational questions about
flights, gates, terminals, runways, weather, and incidents.

Always provide clear, accurate, and professional answers.

Do not invent or assume information. If the required information is
not available, clearly say so.

Use the available function tools to retrieve airport data instead of
making assumptions. When a question requires several pieces of data,
call the tools one after another until you have everything you need
before writing the final answer.

If a tool returns an error, explain the problem to the user instead of
guessing the answer.
"""

MAX_TOOL_ITERATIONS = 5


class AgentService:
    """Main AI agent service."""

    def __init__(self) -> None:
        """Initialize the AI agent."""
        self.gemini_service = GeminiService()

    def chat(
        self,
        user_message: str,
        history: list[types.Content] | None = None,
    ) -> dict:
        """
        Process a user message through the agentic loop.

        The loop runs: model -> tool calls -> tool results -> model,
        repeating until the model answers without requesting more tools
        or until MAX_TOOL_ITERATIONS is reached.

        Args:
            user_message: The message sent by the user.
            history: Optional previous conversation turns.

        Returns:
            A dictionary with the final answer and the executed tool calls.

        Raises:
            ValueError: If the user message is empty.
        """
        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty.")

        contents: list[types.Content] = list(history or [])
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message.strip())],
            )
        )

        tool_calls: list[dict] = []

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.gemini_service.generate(
                contents,
                system_instruction=SYSTEM_PROMPT,
            )

            model_content = self._extract_model_content(response)

            if model_content is not None:
                contents.append(model_content)

            function_calls = response.function_calls or []

            if not function_calls:
                return {
                    "response": response.text,
                    "tool_calls": tool_calls,
                    "history": contents,
                }

            contents.append(
                self._run_function_calls(function_calls, tool_calls)
            )

        # The model kept requesting tools: force a final answer without them.
        final_response = self.gemini_service.generate(
            contents,
            system_instruction=SYSTEM_PROMPT,
            use_tools=False,
        )

        return {
            "response": final_response.text,
            "tool_calls": tool_calls,
            "history": contents,
            "truncated": True,
        }

    @staticmethod
    def _extract_model_content(
        response: types.GenerateContentResponse,
    ) -> types.Content | None:
        """
        Return the model turn from a Gemini response, if present.
        """
        if not response.candidates:
            return None

        return response.candidates[0].content

    @staticmethod
    def _run_function_calls(
        function_calls: list[types.FunctionCall],
        tool_calls: list[dict],
    ) -> types.Content:
        """
        Execute every function call requested by the model.

        All results are returned in a single Content turn, so parallel
        function calls are preserved instead of being dropped.

        Args:
            function_calls: Function calls requested by the model.
            tool_calls: Accumulator recording the executed calls.

        Returns:
            A Content object holding the function responses.
        """
        parts = []

        for function_call in function_calls:
            arguments = dict(function_call.args or {})
            result = ToolExecutor.execute(function_call.name, arguments)

            tool_calls.append(
                {
                    "tool": function_call.name,
                    "arguments": arguments,
                    "failed": isinstance(result, dict) and "error" in result,
                }
            )

            parts.append(
                types.Part.from_function_response(
                    name=function_call.name,
                    response={"result": result},
                )
            )

        # Gemini only accepts the roles "user" and "model".
        # Function results are sent back as a user turn.
        return types.Content(role="user", parts=parts)