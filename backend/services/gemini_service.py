"""
Service for interacting with the Google Gemini API.
"""

from flask import current_app
from google import genai
from google.genai import types
from services.tool_registry import TOOL_SCHEMAS


class GeminiService:
    """Handle communication with the Gemini API."""

    def __init__(self) -> None:
        """
        Initialize the Gemini client using Flask configuration.
        """
        api_key = current_app.config.get("GEMINI_API_KEY")
        model = current_app.config.get(
            "GEMINI_MODEL",
            "gemini-3.5-flash",
        )

        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(api_key=api_key)
        self.model = model




    def _build_tools(self):
        """Convert TOOL_SCHEMAS into Gemini FunctionDeclarations."""

        declarations = []

        for name, schema in TOOL_SCHEMAS.items():
            declarations.append(
                types.FunctionDeclaration(
                    name=name,
                    description=schema["description"],
                    parameters={
                        "type": "OBJECT",
                        "properties": schema["parameters"],
                        "required": schema.get("required", []),
                    },
                )
            )

        return [
            types.Tool(
                function_declarations=declarations
            )
        ]

    def generate_first_response(
            self,
            prompt: str,
    ) -> tuple[types.Content, object]:
        """
        Send the initial prompt to Gemini with the available tools.

        Args:
            prompt: The user's prompt.

        Returns:
            A tuple containing:
            - The user Content object.
            - The raw Gemini response.

        Raises:
            ValueError: If the prompt is empty.
        """

        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        user_content = types.Content(
            role="user",
            parts=[
                types.Part.from_text(
                    text=prompt.strip(),
                )
            ],
        )

        response = self.client.models.generate_content(
            model=self.model,
            contents=[user_content],
            config=types.GenerateContentConfig(
                tools=self._build_tools(),
            ),
        )

        return user_content, response

    def generate_final_response(self, contents: list[types.Content],) -> str:
        """
        Generate the final response after tool execution.

        Args:
            conversation: Conversation including tool responses.

        Returns:
            Final natural-language response.
        """

        response = self.client.models.generate_content(
            model=self.model,
            contents=contents,
        )

        return response.text



