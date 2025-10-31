# Contributing to Azure Pricing MCP Server

Thank you for your interest in contributing to the Azure Pricing MCP Server! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please be respectful and constructive in all interactions.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/azure-pricing-mcp.git
   cd azure-pricing-mcp
   ```
3. **Set up the development environment**:
   ```bash
   python setup.py
   # or
   .\setup.ps1  # Windows PowerShell
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Process

### Before Starting

1. Check [COPILOT_AGENT_TASKS.md](.github/COPILOT_AGENT_TASKS.md) for planned work
2. Open an issue to discuss significant changes
3. Ensure your idea aligns with project goals

### Development Workflow

1. **Plan your changes**: Create a clear plan for what you'll modify
2. **Write tests first**: Follow Test-Driven Development (TDD) when possible
3. **Make minimal changes**: Keep changes focused and surgical
4. **Test frequently**: Run tests after each significant change
5. **Document as you go**: Update docs alongside code changes

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `test/` - Test additions or modifications
- `refactor/` - Code refactoring

## Coding Standards

### Python Style

- Follow **PEP 8** style guide
- Use **4 spaces** for indentation (no tabs)
- Maximum line length: **88 characters** (Black formatter standard)
- Use **type hints** for all function parameters and return values

### Code Quality

```python
# Good: Type hints, clear names, docstring
def calculate_monthly_cost(hourly_rate: float, hours_per_day: int, days_per_month: int = 30) -> float:
    """
    Calculate monthly cost based on hourly rate and usage.
    
    Args:
        hourly_rate: Cost per hour in USD
        hours_per_day: Number of hours used per day
        days_per_month: Number of days in the month (default: 30)
        
    Returns:
        Total monthly cost in USD
    """
    return hourly_rate * hours_per_day * days_per_month
```

### Docstrings

Use **Google-style** docstrings:

```python
def function_name(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain the purpose and behavior.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When param2 is negative
    """
```

### Error Handling

- Always include appropriate error handling
- Provide meaningful error messages
- Log errors at appropriate levels

```python
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid input: {str(e)}")
    return {"error": f"Invalid input: {str(e)}"}
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}")
    return {"error": "An unexpected error occurred"}
```

## Testing Guidelines

### Writing Tests

1. **Test file naming**: `test_*.py`
2. **Test function naming**: `test_<functionality>_<scenario>`
3. **Coverage target**: Aim for >80% code coverage
4. **Test structure**: Arrange, Act, Assert

```python
def test_calculate_monthly_cost_standard_month():
    # Arrange
    hourly_rate = 0.50
    hours_per_day = 8
    days_per_month = 30
    
    # Act
    result = calculate_monthly_cost(hourly_rate, hours_per_day, days_per_month)
    
    # Assert
    assert result == 120.0
```

### Running Tests

```bash
# Run all tests
python test_mcp_server.py

# Run specific test file
python test_mcp.py

# Test with debug output
python -m pytest -v
```

### Test Coverage

- Unit tests for all functions
- Integration tests for API interactions
- Edge case testing
- Error condition testing

## Documentation

### What to Document

1. **Code changes**: Update docstrings and comments
2. **New features**: Add to README.md and USAGE_EXAMPLES.md
3. **API changes**: Update tool descriptions and schemas
4. **Breaking changes**: Clearly document in commit messages

### Documentation Files

- `README.md` - Project overview and quick start
- `QUICK_START.md` - Step-by-step setup guide
- `USAGE_EXAMPLES.md` - Detailed usage examples
- `.github/COPILOT_AGENT_TASKS.md` - Task tracking
- `.github/copilot-instructions.md` - Development guidelines

## Submitting Changes

### Before Submitting

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] Commits are well-formatted
- [ ] No sensitive information in code

### Commit Messages

Follow conventional commit format:

```
type(scope): brief description

Detailed description if needed.

Fixes #123
```

Types:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

Example:
```
feat(tools): add azure_cost_breakdown tool

Implement new tool to break down costs by service category.
Includes comprehensive error handling and pagination support.

Addresses #42
```

### Pull Request Process

1. **Update documentation**: Ensure all docs are current
2. **Describe changes**: Provide clear PR description
3. **Link issues**: Reference related issues
4. **Request review**: Tag relevant reviewers
5. **Address feedback**: Respond to review comments
6. **Update COPILOT_AGENT_TASKS.md**: Mark completed tasks

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Related Issues
Fixes #XX

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Documentation
- [ ] README.md updated
- [ ] USAGE_EXAMPLES.md updated
- [ ] Docstrings updated
- [ ] COPILOT_AGENT_TASKS.md updated

## Checklist
- [ ] Code follows style guidelines
- [ ] All tests pass
- [ ] No breaking changes (or clearly documented)
- [ ] Commits are well-formatted
```

## Review Process

1. **Automated checks**: CI/CD pipeline must pass
2. **Code review**: At least one approval required
3. **Testing**: Reviewer validates functionality
4. **Documentation**: Reviewer checks documentation
5. **Merge**: Maintainer merges after approval

## Questions?

- Check existing documentation
- Open an issue for clarification
- Join discussions on existing issues
- Contact maintainers

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Azure Pricing MCP Server! 🎉
