# Testing Documentation

## Overview

This document describes the testing infrastructure and practices for the Azure Pricing MCP Server project.

## Test Structure

```
tests/
├── __init__.py
├── test_pricing_server.py    # Core server functionality tests
└── (future test files)
```

## Running Tests

### Install Test Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run All Tests

```bash
# Run all tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_pricing_server.py

# Run specific test
pytest tests/test_pricing_server.py::TestAzurePricingServer::test_search_azure_prices_with_filters
```

### Test Coverage

```bash
# Generate coverage report
pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Code Quality Tools

### Linting with flake8

```bash
# Check all Python files
flake8 .

# Check specific file
flake8 azure_pricing_server.py
```

### Code Formatting with black

```bash
# Check formatting
black --check .

# Auto-format code
black .

# Format specific file
black azure_pricing_server.py
```

### Type Checking with mypy

```bash
# Type check all files
mypy .

# Type check specific file
mypy azure_pricing_server.py
```

### Linting with pylint

```bash
# Lint all files
pylint azure_pricing_server.py

# Lint with specific rcfile
pylint --rcfile=pyproject.toml azure_pricing_server.py
```

## Test Categories

### Unit Tests
- Test individual functions and methods in isolation
- Use mocking to avoid external dependencies
- Fast execution
- Located in `tests/test_*.py`

### Integration Tests (Future)
- Test interaction with actual Azure API
- Require network connectivity
- Slower execution
- Mark with `@pytest.mark.integration`

## Writing Tests

### Test Naming Convention
- Test files: `test_*.py`
- Test classes: `Test*`
- Test functions: `test_*`

### Example Test Structure

```python
import pytest
from unittest.mock import AsyncMock, patch

class TestMyFeature:
    """Test cases for my feature."""
    
    @pytest.mark.asyncio
    async def test_my_async_function(self):
        """Test description."""
        # Arrange
        expected = "result"
        
        # Act
        result = await my_async_function()
        
        # Assert
        assert result == expected
```

### Mocking Guidelines

1. **Mock External Dependencies**: Always mock HTTP requests to Azure API
2. **Use AsyncMock for Async Functions**: Use `AsyncMock` for async functions
3. **Patch at Usage Point**: Patch where the function is used, not where it's defined

Example:
```python
with patch.object(server, '_make_request', return_value=mock_data):
    result = await server.search_azure_prices()
```

## Coverage Goals

- **Overall Coverage**: Aim for >80% code coverage
- **Critical Paths**: 100% coverage for core functionality
- **Error Handling**: All error paths should be tested

## Continuous Integration

Tests are automatically run on:
- Every push to any branch
- Every pull request
- Before merging to main branch

## Test Fixtures

### Available Fixtures

- `pricing_server`: Creates an AzurePricingServer instance
- `mock_api_response`: Sample Azure API response with pricing data
- `mock_empty_response`: Empty API response for testing edge cases

### Creating New Fixtures

Add to `tests/conftest.py` (to be created) for shared fixtures:

```python
@pytest.fixture
def my_fixture():
    """Fixture description."""
    return "fixture_value"
```

## Common Testing Patterns

### Testing Async Functions

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await async_function()
    assert result is not None
```

### Testing Exceptions

```python
@pytest.mark.asyncio
async def test_exception_handling():
    with pytest.raises(ValueError):
        await function_that_raises()
```

### Testing with Mocked HTTP Responses

```python
@pytest.mark.asyncio
async def test_api_call(pricing_server):
    async with pricing_server:
        with patch.object(pricing_server, '_make_request') as mock_request:
            mock_request.return_value = {"data": "value"}
            result = await pricing_server.some_method()
            assert result["data"] == "value"
```

## Troubleshooting

### Tests Failing Due to Network Issues
- Ensure all external API calls are mocked
- Check that fixtures are properly initialized

### Coverage Not Updating
- Delete `.coverage` file and `htmlcov/` directory
- Run `pytest --cov=. --cov-report=html` again

### Type Checking Errors
- Add `# type: ignore` for known issues
- Update type stubs: `pip install -U types-*`

## Best Practices

1. **Write Tests First**: Consider TDD (Test-Driven Development)
2. **Keep Tests Independent**: Each test should be runnable in isolation
3. **Use Descriptive Names**: Test names should describe what they test
4. **Test Edge Cases**: Include tests for boundary conditions
5. **Mock External Dependencies**: Never rely on external services in unit tests
6. **Keep Tests Fast**: Unit tests should complete in milliseconds
7. **Maintain Test Code**: Refactor tests as you refactor code

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
