# Changelog

All notable changes to the Azure Pricing MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive test suite with unit and integration tests
- CI/CD pipeline with GitHub Actions
- Code quality checks (flake8, pylint, black, isort)
- Test coverage reporting
- Automated dependency updates via Dependabot
- Contributing guidelines (CONTRIBUTING.md)
- Code of Conduct (CODE_OF_CONDUCT.md)
- Architecture documentation
- API reference documentation

### Changed
- Fixed undefined name 'true' → 'True' in azure_pricing_server.py
- Updated README with CI/CD badges
- Enhanced .gitignore for test artifacts

### Fixed
- Code formatting issues
- Import organization

## [1.0.0] - 2023-XX-XX

### Added
- Initial release of Azure Pricing MCP Server
- Core pricing search functionality
- Price comparison across regions and SKUs
- Cost estimation with usage patterns
- SKU discovery and fuzzy matching
- Support for Azure savings plans
- Multi-currency support
- Retry logic for API rate limiting
- SKU validation and suggestions
- Customer discount support

### Features
- `azure_price_search` - Search Azure retail prices with filters
- `azure_price_compare` - Compare prices across regions/SKUs
- `azure_cost_estimate` - Estimate costs based on usage
- `azure_discover_skus` - Discover available SKUs for a service
- `azure_sku_discovery` - Intelligent SKU discovery with fuzzy matching

### Documentation
- README.md with quick start guide
- QUICK_START.md with detailed setup instructions
- USAGE_EXAMPLES.md with example queries
- config_examples.json for Claude Desktop and VS Code

---

## Release Types

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
