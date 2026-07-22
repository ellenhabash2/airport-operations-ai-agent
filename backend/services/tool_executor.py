"""
Service for executing AI function tools by name.
"""

import logging

from database import db
from services.tool_registry import TOOLS, TOOL_SCHEMAS

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Executes registered AI function tools."""

    @staticmethod
    def execute(tool_name: str, arguments: dict | None = None):
        """
        Execute a registered tool and always return a serializable result.

        Errors are returned to the model as data instead of being raised,
        so a single failing tool cannot break the whole agent loop.

        Args:
            tool_name: Name of the tool to execute.
            arguments: Arguments requested by the model.

        Returns:
            The tool result, or a dictionary containing an "error" key.
        """
        tool = TOOLS.get(tool_name)

        if tool is None:
            return {"error": f"Unknown tool: {tool_name}"}

        arguments = ToolExecutor._coerce_arguments(tool_name, arguments or {})

        try:
            return tool(**arguments)
        except TypeError as error:
            db.session.rollback()
            return {
                "error": f"Invalid arguments for '{tool_name}': {error}"
            }
        except Exception:  # noqa: BLE001 - isolate tool failures
            db.session.rollback()
            logger.exception("Tool execution failed: %s", tool_name)
            return {"error": f"Tool '{tool_name}' could not be completed."}

    @staticmethod
    def _coerce_arguments(tool_name: str, arguments: dict) -> dict:
        """
        Convert model-supplied arguments to the types declared in the schema.

        Gemini returns every number as a float, so an ID declared as an
        integer arrives as 3.0 and breaks the database lookup.
        """
        schema = TOOL_SCHEMAS.get(tool_name, {})
        properties = schema.get("parameters") or {}
        coerced = {}

        for key, value in arguments.items():
            expected_type = (properties.get(key) or {}).get("type")

            try:
                if value is None:
                    coerced[key] = value
                elif expected_type == "integer":
                    coerced[key] = int(value)
                elif expected_type == "number":
                    coerced[key] = float(value)
                elif expected_type == "string" and not isinstance(value, str):
                    coerced[key] = str(value)
                else:
                    coerced[key] = value
            except (TypeError, ValueError):
                coerced[key] = value

        return coerced
