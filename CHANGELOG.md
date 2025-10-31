# Changelog

All notable changes to the Azure Pricing MCP Server project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project documentation structure
- `.github/COPILOT_AGENT_TASKS.md` for task tracking
- `.github/copilot-instructions.md` for development guidelines
- `CONTRIBUTING.md` with contribution guidelines
- `CHANGELOG.md` for version tracking

## [1.0.0] - 2025-10-31

### Added
- Initial release of Azure Pricing MCP Server
- Core MCP server implementation with Azure Retail Prices API integration
- `azure_price_search` tool for searching Azure service prices
- `azure_price_compare` tool for comparing prices across regions and SKUs
- `azure_cost_estimate` tool for cost estimation based on usage patterns
- `azure_discover_skus` tool for discovering available SKUs
- `azure_sku_discovery` tool with intelligent fuzzy matching
- Retry logic for API requests with exponential backoff
- SKU validation and intelligent suggestions
- Discount application support
- Savings plan pricing support (API version 2023-01-01-preview)
- Cross-platform setup scripts (Python and PowerShell)
- Comprehensive documentation (README, QUICK_START, USAGE_EXAMPLES)
- Test scripts for validation
- Debug utilities for troubleshooting

### Features
- Multi-currency support (USD, EUR, etc.)
- Real-time data from Azure Retail Prices API
- Flexible filtering (service name, family, region, SKU)
- Intelligent SKU discovery with fuzzy matching
- Comprehensive error handling
- Detailed logging for troubleshooting

### Documentation
- README.md with project overview and quick start
- QUICK_START.md with step-by-step setup guide
- USAGE_EXAMPLES.md with detailed usage examples
- config_examples.json with configuration examples

---

## Version History

### Format
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

---

[Unreleased]: https://github.com/acedergren/azure-pricing-mcp/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/acedergren/azure-pricing-mcp/releases/tag/v1.0.0
