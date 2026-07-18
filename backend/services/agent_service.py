"""
Main AI agent orchestration service.
"""

from services.gemini_service import GeminiService

from google.genai import types
from services.tool_executor import ToolExecutor


SYSTEM_PROMPT = """
You are AeroMind, an AI assistant for airport operations.

Your role is to assist airport staff with operational questions about
flights, gates, terminals, runways, weather, and incidents.

Always provide clear, accurate, and professional answers.

Do not invent or assume information. If the required information is
not available, clearly say so.

When function tools are available, use them to retrieve airport data
instead of making assumptions.

If a user's request cannot be fulfilled with the available information
or tools, explain the limitation politely.
"""


class AgentService:
    """Main AI agent service."""

    def __init__(self):
        """Initialize the AI agent."""
        self.gemini_service = GeminiService()




    def chat(self, user_message: str) -> dict:
        """
        Process a user message using Gemini and available function tools.
        """

        if not user_message or not user_message.strip():
            raise ValueError("User message cannot be empty.")

        prompt = f"""
        {SYSTEM_PROMPT}
    
        User:
        {user_message}
    
        Assistant:
        """

        user_content,response = self.gemini_service.generate_first_response(prompt)

        if response.function_calls:
            return self._handle_function_call(
                user_content,
                response,
            )

        return {
            "response": response.text,
        }



    def _handle_function_call(
        self,
        user_content: types.Content,
        response,
    ) -> dict:
        """
        Execute a Gemini-requested function call and return the final response.

        Args:
            user_content: The original user message as a Content object.
            response: The initial Gemini response containing the function call.

        Returns:
            A dictionary containing the final assistant response.
        """

        function_call = response.function_calls[0]

        tool_result = ToolExecutor.execute(
            function_call.name,
            **dict(function_call.args),
        )

        function_response_part = types.Part.from_function_response(
            name=function_call.name,
            response={
                "result": tool_result,
            },

        )

        function_response_content = types.Content(
            role="tool",
            parts=[function_response_part],
        )

        contents = [
            user_content,
            response.candidates[0].content,
            function_response_content,
        ]

        final_response = self.gemini_service.generate_final_response(
            contents
        )

        return {
            "response": final_response,
        }

