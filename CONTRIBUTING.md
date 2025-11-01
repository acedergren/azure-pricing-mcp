# Contributing to Azure Pricing MCP Server

Thank you for your interest in contributing to Azure Pricing MCP Server! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project follows the Spec-Driven Development (SDD) methodology and we expect all contributors to be respectful and constructive.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- A GitHub account

### Setting Up Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/azure-pricing-mcp.git
   cd azure-pricing-mcp
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install Pre-commit Hooks** (optional but recommended)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

- Follow the existing code style
- Write clear, descriptive commit messages
- Add tests for new functionality
- Update documentation as needed

### 3. Run Tests

```bash
# Run unit tests
pytest tests/ -v -m "not integration"

# Run with coverage
pytest tests/ --cov=azure_pricing_server --cov-report=html

# Run linting
black --check .
ruff check .
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature X"
# or
git commit -m "fix: resolve issue with Y"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `style:` - Code style changes
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style Guidelines

### Python Style

- Follow PEP 8
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use Black for formatting
- Use Ruff for linting

### Documentation

- Add docstrings to all public functions and classes
- Use Google-style docstrings
- Update README.md if adding new features
- Add examples to USAGE_EXAMPLES.md for new tools

### Testing

- Write tests for all new functionality
- Aim for >80% code coverage
- Use descriptive test names
- Include both positive and negative test cases
- Mock external API calls in unit tests

Example test:
```python
@pytest.mark.asyncio
async def test_search_azure_prices_basic(mock_aiohttp_session):
    """Test basic price search functionality."""
    server = AzurePricingServer()
    server.session = mock_aiohttp_session
    
    result = await server.search_azure_prices(
        service_name="Virtual Machines"
    )
    
    assert result is not None
    assert "items" in result
```

## Pull Request Process

1. **Update Documentation** - Ensure README, docstrings, and examples are updated
2. **Add Tests** - New features must have tests
3. **Pass CI Checks** - All tests and linting must pass
4. **Get Review** - At least one maintainer must approve
5. **Squash Commits** - We prefer clean git history

## Reporting Bugs

Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug_report.md) and include:

- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment details
- Error messages/logs
- Possible solution (if known)

## Requesting Features

Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature_request.md) and include:

- Clear description of the feature
- Use case and benefits
- Proposed implementation (if you have ideas)
- Examples

## Questions?

- Open a [Discussion](https://github.com/acedergren/azure-pricing-mcp/discussions)
- Check existing [Issues](https://github.com/acedergren/azure-pricing-mcp/issues)
- Review [Documentation](README.md)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Thank You!

Your contributions make this project better for everyone. We appreciate your time and effort! 🎉
