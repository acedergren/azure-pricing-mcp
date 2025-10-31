#!/bin/bash
# Quality Assurance Script for Azure Pricing MCP Server

set -e

echo "==================================="
echo "Running Code Quality Checks"
echo "==================================="

# Run black formatting check
echo ""
echo "1. Checking code formatting with black..."
python -m black --check azure_pricing_server.py tests/ || {
    echo "❌ Code formatting issues found. Run 'black .' to fix."
    exit 1
}
echo "✅ Code formatting passed"

# Run flake8 linting
echo ""
echo "2. Running flake8 linting..."
python -m flake8 azure_pricing_server.py tests/ || {
    echo "⚠️  Flake8 found some issues (check output above)"
}

# Run tests with coverage
echo ""
echo "3. Running tests with coverage..."
python -m pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

echo ""
echo "==================================="
echo "✅ Quality checks complete!"
echo "==================================="
echo ""
echo "Coverage report generated in htmlcov/index.html"
