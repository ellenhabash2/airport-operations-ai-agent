"""
Service for interacting with the Google Gemini API.
"""

import time
from functools import lru_cache

from flask import current_app
from google import genai
from google.genai import errors, types

from services.tool_registry import TOOL_SCHEMAS


DEFAULT_MODEL = "gemini-3.5-flash"

# Status codes worth retrying: rate limiting and transient server errors.
TRANSIENT_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

MAX_ATTEMPTS = 3
RETRY_BACKOFF_SECONDS = 1.0


class GeminiUnavailableError(RuntimeError):
    """Raised when Gemini is still unavailable after retrying."""


@lru_cache(maxsize=4)
def _get_client(api_key: str) -> genai.Client:
    """
    Return a cached Gemini client for the given API key.

    The client is reused across requests instead of being rebuilt
    on every incoming call.
    """
    return genai.Client(api_key=api_key)


class GeminiService:
    """Handle communication with the Gemini API."""

    def __init__(self) -> None:
        """
        Initialize the Gemini client using Flask configuration.

        Raises:
            RuntimeError: If GEMINI_API_KEY is not configured.
        """
        api_key = current_app.config.get("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured.")

        self.client = _get_client(api_key)
        self.model = current_app.config.get("GEMINI_MODEL", DEFAULT_MODEL)
        self.tools = self._build_tools()

    @staticmethod
    def _build_tools() -> list[types.Tool]:
        """
        Convert TOOL_SCHEMAS into Gemini FunctionDeclarations.

        Tools without parameters are declared without a `parameters`
        field: the Gemini API rejects an OBJECT schema with an empty
        `properties` map.
        """
        declarations = []

        for name, schema in TOOL_SCHEMAS.items():
            properties = schema.get("parameters") or {}

            declaration = types.FunctionDeclaration(
                name=name,
                description=schema["description"],
            )

            if properties:
                declaration.parameters = types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        key: types.Schema(**value)
                        for key, value in properties.items()
                    },
                    required=schema.get("required", []),
                )

            declarations.append(declaration)

        return [types.Tool(function_declarations=declarations)]

    def generate(
        self,
        contents: list[types.Content],
        system_instruction: str | None = None,
        use_tools: bool = True,
    ) -> types.GenerateContentResponse:
        """
        Send a conversation to Gemini.

        Args:
            contents: Full conversation history sent to the model.
            system_instruction: System prompt applied to the call.
            use_tools: Whether the function tools are exposed to the model.

        Returns:
            The raw Gemini response.

        Raises:
            ValueError: If the conversation is empty.
            GeminiUnavailableError: If Gemini keeps returning a transient
                error after every attempt.
        """
        if not contents:
            raise ValueError("Conversation cannot be empty.")

        config = types.GenerateContentConfig(
            system_instruction=system_instruction,
            tools=self.tools if use_tools else None,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True,
            ),
        )

        return self._generate_with_retry(contents, config)

    def _generate_with_retry(
        self,
        contents: list[types.Content],
        config: types.GenerateContentConfig,
    ) -> types.GenerateContentResponse:
        """
        Call Gemini, retrying transient failures with a growing delay.

        Rate limiting and server overload are common on the free tier and
        usually clear within seconds, so they are retried instead of being
        reported to the user as a failed request.
        """
        last_error = None

        for attempt in range(MAX_ATTEMPTS):
            try:
                return self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
            except errors.APIError as error:
                if error.code not in TRANSIENT_STATUS_CODES:
                    raise

                last_error = error

                if attempt < MAX_ATTEMPTS - 1:
                    time.sleep(RETRY_BACKOFF_SECONDS * (2 ** attempt))

        raise GeminiUnavailableError(
            "The AI service is temporarily unavailable. "
            f"Gemini returned {last_error.code} on {MAX_ATTEMPTS} attempts."
        ) from last_error