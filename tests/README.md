# Tests

This directory contains the test suite for the Azure Pricing MCP Server.

## Test Structure

- `conftest.py` - Shared pytest fixtures and configuration
- `test_server.py` - Unit tests for core server functionality
- `test_integration.py` - Integration tests (requires network access)

## Running Tests

### Run all unit tests
```bash
pytest tests/
```

### Run with coverage
```bash
pytest tests/ --cov=azure_pricing_server --cov-report=html
```

### Run specific test file
```bash
pytest tests/test_server.py -v
```

### Run integration tests (requires network)
```bash
pytest tests/ -m integration
```

### Skip integration tests
```bash
pytest tests/ -m "not integration"
```

## Test Categories

- **Unit tests**: Fast, isolated tests with mocked dependencies
- **Integration tests**: Tests that make real API calls (marked with `@pytest.mark.integration`)

## Writing Tests

### Unit Test Example
```python
@pytest.mark.asyncio
async def test_something(mock_aiohttp_session):
    server = AzurePricingServer()
    server.session = mock_aiohttp_session
    result = await server.some_method()
    assert result is not None
```

### Integration Test Example
```python
@pytest.mark.integration
@pytest.mark.asyncio
async def test_real_api():
    async with AzurePricingServer() as server:
        result = await server.search_azure_prices(...)
        assert result is not None
```
