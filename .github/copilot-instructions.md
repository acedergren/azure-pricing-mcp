# GitHub Copilot Instructions for Azure Pricing MCP Server

This document provides guidelines for GitHub Copilot and AI assistants when working with the Azure Pricing MCP Server project.

## Project Overview

The Azure Pricing MCP Server is a Model Context Protocol (MCP) server that provides tools for querying Azure retail pricing information. The project follows Spec-Driven Development (SDD) methodology and emphasizes code quality, testing, and comprehensive documentation.

## Core Technologies

- **Language**: Python 3.8+
- **Framework**: Model Context Protocol (MCP)
- **API**: Azure Retail Prices API
- **Key Libraries**: `mcp`, `requests`, `aiohttp`, `pydantic`

## Project Structure

```
azure-pricing-mcp/
├── .github/               # GitHub-specific files
├── azure_pricing_server.py # Main MCP server implementation
├── __main__.py            # Entry point for module execution
├── __init__.py            # Package initialization
├── setup.py               # Cross-platform setup script
├── setup.ps1              # Windows PowerShell setup script
├── requirements.txt       # Python dependencies
├── test_*.py              # Test files
├── debug_*.py             # Debug utilities
├── README.md              # Main documentation
├── QUICK_START.md         # Getting started guide
└── USAGE_EXAMPLES.md      # Usage examples
```

## Development Guidelines

### Code Style

1. **Follow PEP 8**: Use Python's standard style guide
2. **Type Hints**: Add type hints to all function signatures
3. **Docstrings**: Use Google-style docstrings for all public functions
4. **Error Handling**: Always include comprehensive error handling with meaningful messages
5. **Logging**: Use appropriate logging levels (DEBUG, INFO, WARNING, ERROR)

### MCP Tool Development

When creating or modifying MCP tools:

1. **Tool Definition**: Each tool should have clear `name`, `description`, and `inputSchema`
2. **Input Validation**: Validate all inputs using Pydantic models where applicable
3. **Error Messages**: Provide user-friendly error messages
4. **Documentation**: Include usage examples in docstrings
5. **Testing**: Create corresponding test cases for each tool

Example tool structure:
```python
@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Handle tool calls with validation and error handling."""
    try:
        if name == "tool_name":
            # Validate inputs
            # Process request
            # Return structured response
            pass
    except Exception as e:
        logger.error(f"Error in {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]
```

### Azure API Integration

1. **API Version**: Use `2023-01-01-preview` for savings plan support
2. **Base URL**: `https://prices.azure.com/api/retail/prices`
3. **Pagination**: Handle `nextLink` for paginated responses
4. **Rate Limiting**: Implement retry logic with exponential backoff
5. **Error Handling**: Handle HTTP errors gracefully (404, 429, 500, etc.)

### Testing

1. **Test Files**: Create test files with `test_` prefix
2. **Coverage**: Aim for >80% code coverage
3. **Mocking**: Mock Azure API calls in unit tests
4. **Integration Tests**: Test actual API calls separately
5. **Edge Cases**: Test error conditions and edge cases

### Documentation

1. **Code Comments**: Explain "why" not "what"
2. **README Updates**: Update README.md for new features
3. **Examples**: Add usage examples to USAGE_EXAMPLES.md
4. **Changelog**: Document changes in commit messages
5. **API Docs**: Keep tool descriptions up to date

## Common Patterns

### Error Handling Pattern

```python
try:
    # Operation
    result = await some_operation()
    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
except requests.exceptions.RequestException as e:
    logger.error(f"API request failed: {str(e)}")
    return [types.TextContent(type="text", text=f"API Error: {str(e)}")]
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return [types.TextContent(type="text", text=f"Error: {str(e)}")]
```

### API Request Pattern

```python
def make_api_request(filters: str, max_results: int = 100) -> dict:
    """Make request to Azure Retail Prices API with retry logic."""
    url = f"{BASE_URL}?api-version={API_VERSION}&$filter={filters}"
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise
            time.sleep(2 ** attempt)
```

### SKU Discovery Pattern

```python
def discover_skus(service_hint: str) -> list[dict]:
    """Discover SKUs with fuzzy matching and intelligent suggestions."""
    # 1. Try exact match
    # 2. Try partial match
    # 3. Try fuzzy match
    # 4. Return suggestions with confidence scores
```

## Task Workflow

When working on tasks from COPILOT_AGENT_TASKS.md:

1. **Read Task Description**: Understand objectives and requirements
2. **Check Dependencies**: Ensure prerequisite tasks are complete
3. **Plan Changes**: Consider minimal changes needed
4. **Write Tests First**: Follow TDD when appropriate
5. **Implement Feature**: Make surgical, focused changes
6. **Test Thoroughly**: Run all tests and manual validation
7. **Update Documentation**: Keep docs in sync with code
8. **Update Task Status**: Mark items as complete in COPILOT_AGENT_TASKS.md

## Security Considerations

1. **No Secrets**: Never commit API keys or credentials
2. **Input Validation**: Sanitize all user inputs
3. **Dependencies**: Keep dependencies up to date
4. **Error Messages**: Don't leak sensitive information in errors
5. **API Usage**: Respect Azure API terms of service

## Performance Guidelines

1. **Pagination**: Use pagination for large result sets
2. **Caching**: Cache frequently requested data
3. **Async Operations**: Use async/await for I/O operations
4. **Resource Cleanup**: Always clean up resources (connections, files)
5. **Memory Management**: Be mindful of memory usage with large datasets

## Debugging

1. **Debug Scripts**: Use provided debug_*.py scripts
2. **Logging**: Enable DEBUG level logging for troubleshooting
3. **Test Isolation**: Use test scripts for isolated testing
4. **API Testing**: Test API calls independently before integration

## Before Committing

- [ ] Run all tests
- [ ] Check code style (PEP 8)
- [ ] Update documentation
- [ ] Add meaningful commit message
- [ ] Update COPILOT_AGENT_TASKS.md if completing a task
- [ ] Review changes for security issues

## Useful Commands

```bash
# Setup
python setup.py

# Run server
python -m azure_pricing_server

# Run tests
python test_mcp_server.py

# Debug
python debug_handler_return.py
python debug_suggestions.py

# Test specific functionality
python find_app_service.py
python simulate_mcp_call.py
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io/)
- [Azure Retail Prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)

## Questions or Issues?

- Check existing documentation in README.md and USAGE_EXAMPLES.md
- Review test files for examples
- Check COPILOT_AGENT_TASKS.md for known issues
- Open an issue for new bugs or feature requests

---

*Last Updated: 2025-10-31*
