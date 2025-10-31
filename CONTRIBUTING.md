# Contributing to Azure Pricing MCP Server

Thank you for your interest in contributing to the Azure Pricing MCP Server! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)

### Setting Up Development Environment

1. **Fork and Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/azure-pricing-mcp.git
   cd azure-pricing-mcp
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On Linux/Mac
   source .venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   # Install runtime dependencies
   pip install -r requirements.txt
   
   # Install development dependencies
   pip install -r requirements-dev.txt
   
   # Install in editable mode
   pip install -e .
   ```

## 🧪 Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Run only unit tests (skip integration tests)
pytest tests/ -m "not integration"

# Run only integration tests
pytest tests/ -m "integration"
```

### Generate Coverage Report
```bash
pytest tests/ --cov=azure_pricing_server --cov-report=html
```

View the coverage report by opening `htmlcov/index.html` in your browser.

## 🎨 Code Quality

### Code Formatting
We use [Black](https://github.com/psf/black) for code formatting:
```bash
# Check formatting
black --check azure_pricing_server.py

# Auto-format code
black azure_pricing_server.py
```

### Linting
We use [Flake8](https://flake8.pycqa.org/) for linting:
```bash
flake8 azure_pricing_server.py
```

### Type Checking
We use [MyPy](http://mypy-lang.org/) for type checking:
```bash
mypy azure_pricing_server.py
```

## 📝 Contribution Workflow

### 1. Create a Branch
```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes
- Write clean, readable code
- Follow existing code style and conventions
- Add docstrings to functions and classes
- Update tests as needed

### 3. Test Your Changes
```bash
# Run tests
pytest tests/ -v

# Check code quality
black --check azure_pricing_server.py
flake8 azure_pricing_server.py
```

### 4. Commit Your Changes
```bash
git add .
git commit -m "Description of your changes"
```

**Commit Message Guidelines:**
- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 72 characters
- Reference issues and pull requests when relevant

### 5. Push and Create Pull Request
```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- A clear title and description
- Reference to related issues
- Screenshots for UI changes (if applicable)
- Test coverage information

## 🐛 Reporting Bugs

When reporting bugs, please include:
- Python version
- Operating system
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Error messages and stack traces

## 💡 Suggesting Features

Feature suggestions are welcome! Please:
- Search existing issues first
- Provide a clear use case
- Explain why this feature would be useful
- Consider implementation details

## 📚 Documentation

When adding new features:
- Update README.md if needed
- Add usage examples to USAGE_EXAMPLES.md
- Update docstrings in the code
- Add tests for new functionality

## 🔍 Code Review Process

All contributions go through code review:
1. Automated tests must pass (CI/CD checks)
2. Code must meet quality standards
3. Changes must be reviewed by maintainers
4. Feedback should be addressed promptly

## 📜 Code of Conduct

### Our Standards
- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Help each other learn and grow

### Unacceptable Behavior
- Harassment or discrimination
- Trolling or insulting comments
- Personal attacks
- Publishing private information

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be recognized in:
- GitHub contributors list
- Release notes
- Project documentation

## 📞 Getting Help

- GitHub Issues: For bug reports and feature requests
- GitHub Discussions: For questions and general discussion
- Pull Request Comments: For code-specific questions

Thank you for contributing to Azure Pricing MCP Server! 🎉
