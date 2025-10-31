# Azure Pricing MCP Server 💰

[![CI](https://github.com/acedergren/azure-pricing-mcp/workflows/CI/badge.svg)](https://github.com/acedergren/azure-pricing-mcp/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Model Context Protocol (MCP) server that provides tools for querying Azure retail pricing information using the Azure Retail Prices API.

## 🚀 Quick Start

1. **Clone/Download** this repository
2. **Run setup**: `setup.ps1` (Windows PowerShell) or `python setup.py` (Cross-platform)
3. **Configure Claude Desktop** (see [QUICK_START.md](QUICK_START.md))
4. **Ask Claude**: "What's the price of a Standard_D2s_v3 VM in East US?"

## ✨ Features

- **🔍 Azure Price Search**: Search for Azure service prices with flexible filtering
- **⚖️ Service Comparison**: Compare prices across different regions and SKUs
- **💡 Cost Estimation**: Calculate estimated costs based on usage patterns
- **💰 Savings Plan Information**: Get Azure savings plan pricing when available
- **🌍 Multi-Currency**: Support for multiple currencies (USD, EUR, etc.)
- **📊 Real-time Data**: Uses live Azure Retail Prices API

## 🛠️ Tools Available

| Tool | Description | Example Use |
|------|-------------|-------------|
| `azure_price_search` | Search Azure retail prices with filters | Find VM prices in specific regions |
| `azure_price_compare` | Compare prices across regions/SKUs | Compare storage costs across regions |
| `azure_cost_estimate` | Estimate costs based on usage | Calculate monthly costs for 8hr/day usage |
| `azure_discover_skus` | Discover available SKUs for a service | Find all VM types for a service |
| `azure_sku_discovery` | Intelligent SKU discovery with fuzzy matching | "Find app service plans" or "web app pricing" |

## 📋 Installation

### Automated Setup (Recommended)
```bash
# Windows PowerShell
.\setup.ps1

# Cross-platform (Python)
python setup.py
```

### Manual Setup
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

Add to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "azure-pricing": {
      "command": "python",
      "args": ["-m", "azure_pricing_server"],
      "cwd": "/path/to/azure_pricing"
    }
  }
}
```

## 💬 Example Queries

Once configured with Claude, you can ask:

- **Basic Pricing**: "What's the price of Azure SQL Database?"
- **Comparisons**: "Compare VM prices between East US and West Europe"
- **Cost Estimation**: "Estimate costs for running a D4s_v3 VM 12 hours per day"
- **Savings**: "What are the reserved instance savings for virtual machines?"
- **GPU Pricing**: "Show me all GPU-enabled VMs with pricing"
- **Service Discovery**: "Find all App Service plan pricing" or "What storage options are available?"
- **SKU Discovery**: "Show me all web app hosting plans"

## 🧪 Testing

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=azure_pricing_server --cov-report=html

# Run only unit tests (skip integration tests)
pytest tests/ -m "not integration"
```

### Test Setup Verification

```bash
# Windows PowerShell
.\test_setup.ps1

# Cross-platform test
python -m azure_pricing_server --test
```

### Code Quality

```bash
# Format code
black azure_pricing_server.py

# Lint code
flake8 azure_pricing_server.py

# Type checking
mypy azure_pricing_server.py
```

## 📚 Documentation

- **[QUICK_START.md](QUICK_START.md)** - Step-by-step setup guide
- **[USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)** - Detailed usage examples and API responses
- **[config_examples.json](config_examples.json)** - Example configurations for Claude Desktop and VS Code

## 🔌 API Integration

This server uses the official Azure Retail Prices API:
- **Endpoint**: `https://prices.azure.com/api/retail/prices`
- **Version**: `2023-01-01-preview` (supports savings plans)
- **Authentication**: None required (public API)
- **Rate Limits**: Generous limits for retail pricing data

## 🌟 Key Features

### Smart Filtering
- Filter by service name, family, region, SKU
- Support for partial matches and contains operations
- Case-sensitive filtering for precise results

### Cost Optimization
- Automatic savings plan detection
- Reserved instance pricing comparisons
- Multi-region cost analysis
- Intelligent SKU discovery for finding the best pricing options

### Developer Friendly
- Comprehensive error handling
- Detailed logging for troubleshooting
- Flexible parameter support
- Cross-platform setup scripts (PowerShell and Python)

## 🤝 Contributing

Contributions are welcome! We appreciate your help in making this project better.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`pytest tests/`)
6. Format your code (`black azure_pricing_server.py`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/azure-pricing-mcp.git
cd azure-pricing-mcp

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

## 📄 License

MIT License - see LICENSE file for details

## 🙋‍♂️ Support

- Check [QUICK_START.md](QUICK_START.md) for setup issues
- Review [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for query patterns
- Open an issue for bugs or feature requests

---

*Built with the Model Context Protocol (MCP) for seamless integration with Claude and other AI assistants.*