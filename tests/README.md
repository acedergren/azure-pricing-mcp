# Test Suite for Azure Pricing MCP Server

This directory contains the comprehensive test suite for the Azure Pricing MCP Server.

## Test Structure

```
tests/
├── __init__.py              # Test package initialization
├── conftest.py              # Pytest fixtures and configuration
├── test_azure_pricing_server.py   # Core server functionality tests
├── test_mcp_tools.py        # MCP tool handler tests
└── test_fuzzy_matching.py   # Fuzzy matching and service discovery tests
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements.txt
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest tests/test_azure_pricing_server.py
```

### Run Tests with Coverage

```bash
pytest --cov=azure_pricing_server --cov-report=html
```

This will generate an HTML coverage report in `htmlcov/index.html`.

### Run Tests Verbosely

```bash
pytest -v
```

### Run Specific Test

```bash
pytest tests/test_azure_pricing_server.py::TestAzurePricingServer::test_context_manager
```

## Test Categories

### Core Functionality Tests (`test_azure_pricing_server.py`)

Tests for the main `AzurePricingServer` class:

- **Context Manager**: Tests async context manager functionality
- **API Requests**: Tests HTTP request handling with retry logic
- **Rate Limiting**: Tests 429 response handling and retries
- **Price Search**: Tests basic and advanced price searching
- **Discount Application**: Tests discount calculation and application
- **SKU Validation**: Tests SKU validation and suggestions
- **Price Comparison**: Tests multi-region price comparisons
- **Cost Estimation**: Tests cost calculation logic
- **SKU Discovery**: Tests SKU enumeration

### MCP Tool Tests (`test_mcp_tools.py`)

Tests for MCP tool handlers:

- **azure_price_search**: Tests price search tool with various parameters
- **azure_price_compare**: Tests price comparison tool
- **azure_cost_estimate**: Tests cost estimation tool
- **azure_discover_skus**: Tests SKU discovery tool
- **azure_sku_discovery**: Tests intelligent SKU discovery with fuzzy matching
- **get_customer_discount**: Tests customer discount retrieval
- **Error Handling**: Tests invalid tool names and missing parameters

### Fuzzy Matching Tests (`test_fuzzy_matching.py`)

Tests for intelligent service discovery:

- **Service Mapping**: Tests exact service name mappings (e.g., "vm" → "Virtual Machines")
- **Alias Recognition**: Tests various service aliases (e.g., "app service", "web app")
- **SKU Suggestions**: Tests partial SKU matching and suggestions
- **Suggestion Limits**: Tests that suggestions are limited to a reasonable number
- **Clarification Messages**: Tests user-friendly messages for ambiguous queries

## Fixtures

### Available Fixtures (defined in `conftest.py`)

- `mock_vm_pricing_response`: Mock VM pricing data
- `mock_storage_pricing_response`: Mock storage pricing data
- `mock_empty_response`: Mock empty API response
- `mock_paginated_response`: Mock response with pagination
- `mock_multi_region_response`: Mock multi-region pricing data

## Test Coverage

The test suite aims for comprehensive coverage of:

- ✅ Core server functionality
- ✅ All MCP tools
- ✅ Retry and error handling logic
- ✅ Discount application
- ✅ SKU validation and suggestions
- ✅ Fuzzy matching and service discovery
- ✅ Edge cases and error conditions

## Mocking Strategy

Since the Azure Pricing API requires internet access, all tests use mocks:

- **HTTP Requests**: Mocked using `unittest.mock.AsyncMock`
- **API Responses**: Defined as fixtures in `conftest.py`
- **Async Operations**: Use `pytest-asyncio` for async test support

## Writing New Tests

When adding new tests:

1. Use appropriate fixtures from `conftest.py`
2. Mock external dependencies (HTTP requests, API calls)
3. Test both success and error paths
4. Include edge cases
5. Follow existing naming conventions
6. Add docstrings explaining what each test validates

Example:

```python
@pytest.mark.asyncio
async def test_new_feature(mock_vm_pricing_response):
    """Test description here."""
    async with AzurePricingServer() as server:
        with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_vm_pricing_response
            
            result = await server.new_feature()
            
            assert result is not None
            # More assertions...
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines without requiring:

- Internet access
- Azure credentials
- External services

All dependencies are mocked for fast, reliable test execution.

## Troubleshooting

### Tests Fail with "No module named 'azure_pricing_server'"

Ensure you're running pytest from the repository root:

```bash
cd /path/to/azure-pricing-mcp
pytest
```

### Async Test Failures

Ensure `pytest-asyncio` is installed:

```bash
pip install pytest-asyncio
```

### Import Errors

Ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```
