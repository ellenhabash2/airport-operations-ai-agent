"""
Service for executing AI function tools by name.
"""

from services.tool_registry import TOOLS


class ToolExecutor:
    """Executes registered AI function tools."""

    @staticmethod
    def execute(tool_name: str, **kwargs):
        """
        Execute a registered tool.

        Args:
            tool_name: Name of the tool to execute.
            **kwargs: Arguments passed to the tool.

        Returns:
            The tool result.

        Raises:
            ValueError: If the tool does not exist.
        """
        tool = TOOLS.get(tool_name)

        if tool is None:
            raise ValueError(f"Unknown tool: {tool_name}")

        return tool(**kwargs)