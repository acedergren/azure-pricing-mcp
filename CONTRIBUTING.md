# Contributing to Azure Pricing MCP Server

Thank you for your interest in contributing to the Azure Pricing MCP Server! This document provides guidelines for contributing to the project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When creating a bug report, include:

- **Clear title and description** of the issue
- **Steps to reproduce** the problem
- **Expected behavior** vs. actual behavior
- **Environment details** (Python version, OS, etc.)
- **Code samples** or test cases if applicable

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description** of the proposed feature
- **Use cases** explaining why this enhancement would be useful
- **Possible implementation** if you have ideas

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Ensure all tests pass** by running `pytest tests/`
5. **Update documentation** if needed
6. **Commit your changes** with clear, descriptive commit messages
7. **Push to your fork** and submit a pull request

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/acedergren/azure-pricing-mcp.git
   cd azure-pricing-mcp
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for code formatting (max line length: 120)
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Run linters before committing:
  ```bash
  black azure_pricing_server.py tests/
  isort azure_pricing_server.py tests/
  flake8 azure_pricing_server.py
  pylint azure_pricing_server.py
  ```

### Testing

- Write unit tests for all new functionality
- Maintain test coverage above 80%
- Run tests with: `pytest tests/ -v --cov=azure_pricing_server`
- Integration tests should be marked with `@pytest.mark.integration`

### Documentation

- Add docstrings to all public functions and classes
- Update README.md for user-facing changes
- Update CHANGELOG.md for all changes
- Keep code comments concise and meaningful

## Project Structure

```
azure-pricing-mcp/
├── .github/
│   ├── workflows/         # CI/CD workflows
│   ├── dependabot.yml     # Dependency updates
│   └── COPILOT_AGENT_TASKS.md  # Development tasks
├── tests/                 # Test suite
│   ├── conftest.py       # Test fixtures
│   ├── test_*.py         # Test modules
│   └── test_integration.py
├── azure_pricing_server.py  # Main server implementation
├── requirements.txt       # Production dependencies
├── requirements-dev.txt   # Development dependencies
├── setup.py              # Setup script
└── README.md             # Project documentation
```

## Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions or changes
- `refactor:` for code refactoring
- `chore:` for maintenance tasks

Example: `feat: add support for reserved instance pricing`

## Review Process

1. All pull requests require at least one review
2. CI/CD checks must pass (tests, linting)
3. Documentation must be updated if needed
4. Maintain backward compatibility when possible

## Release Process

1. Update version in `__init__.py`
2. Update CHANGELOG.md
3. Create a GitHub release with release notes
4. Tag the release (e.g., `v1.0.0`)

## Getting Help

- **Issues**: For bug reports and feature requests
- **Discussions**: For questions and general discussion
- **Email**: For private inquiries

## Recognition

Contributors are recognized in:
- GitHub's contributor graph
- CHANGELOG.md release notes
- README.md acknowledgments (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Azure Pricing MCP Server! 🎉
