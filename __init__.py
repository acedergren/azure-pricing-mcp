"""Azure Pricing MCP Server

A Model Context Protocol server for querying Azure retail pricing information.
"""

import azure_pricing_server

__version__ = "1.0.0"

# Re-export main function for convenience
main = azure_pricing_server.main
__all__ = ["main"]
