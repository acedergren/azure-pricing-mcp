# GitHub Copilot Agent Instructions

This file configures specialized agents for the Azure Pricing MCP Server project. Each agent is assigned specific responsibilities to ensure focused and efficient development.

## Agent Assignments

### 1. API Integration Agent
**Responsibility**: Azure Retail Prices API integration and request handling

**Tasks**:
- Implement and maintain Azure Pricing API calls
- Handle API authentication and rate limiting
- Manage API versioning and endpoint configuration
- Parse and transform API responses
- Implement retry logic for failed requests

**Files**:
- `azure_pricing_server.py` (API request methods)
- Configuration for API endpoints and versions

**Skills**: REST API integration, async/await patterns, error handling, rate limiting strategies

---

### 2. Testing Agent
**Responsibility**: Test coverage and quality assurance

**Tasks**:
- Write and maintain unit tests
- Create integration tests for API calls
- Implement mock responses for testing
- Ensure test coverage for all tools
- Debug failing tests

**Files**:
- `test_mcp.py`
- `test_mcp_server.py`
- `exact_mcp_handler_test.py`
- `simulate_mcp_call.py`
- `test_setup.ps1`

**Skills**: pytest, unittest, mocking, async testing, test-driven development

---

### 3. Documentation Agent
**Responsibility**: Documentation and user guides

**Tasks**:
- Write and update README files
- Create usage examples and tutorials
- Document API methods and parameters
- Maintain quick start guides
- Update inline code documentation

**Files**:
- `README.md`
- `QUICK_START.md`
- `USAGE_EXAMPLES.md`
- Docstrings in `azure_pricing_server.py`

**Skills**: Technical writing, markdown, example creation, user experience

---

### 4. Configuration Agent
**Responsibility**: Setup, configuration, and deployment

**Tasks**:
- Maintain setup scripts
- Update configuration examples
- Manage dependencies and requirements
- Handle virtual environment setup
- Configure MCP server settings

**Files**:
- `setup.py`
- `setup.ps1`
- `requirements.txt`
- `config_examples.json`
- `project.json`
- `__init__.py`
- `__main__.py`

**Skills**: Python packaging, PowerShell scripting, dependency management, cross-platform compatibility

---

### 5. Error Handling Agent
**Responsibility**: Error handling and debugging

**Tasks**:
- Implement comprehensive error handling
- Create informative error messages
- Add logging and debugging tools
- Handle edge cases and validation
- Improve error recovery mechanisms

**Files**:
- `azure_pricing_server.py` (error handling sections)
- `debug_handler_return.py`
- `debug_suggestions.py`

**Skills**: Exception handling, logging, debugging, input validation, error recovery

---

## Agent Usage Guidelines

### When to Use Each Agent

1. **API Integration Agent**: When modifying API calls, adding new endpoints, or handling API responses
2. **Testing Agent**: When adding new features, fixing bugs, or improving test coverage
3. **Documentation Agent**: When adding new features, changing functionality, or clarifying usage
4. **Configuration Agent**: When updating dependencies, changing setup process, or modifying configurations
5. **Error Handling Agent**: When improving reliability, adding validation, or enhancing error messages

### Collaboration Between Agents

- **API Integration + Testing**: New API features require corresponding tests
- **API Integration + Error Handling**: API calls need robust error handling
- **Configuration + Documentation**: Setup changes require documentation updates
- **All Agents + Documentation**: Feature changes require documentation updates

### Development Workflow

1. **Feature Development**:
   - API Integration Agent implements the feature
   - Testing Agent creates tests
   - Documentation Agent updates docs
   - Error Handling Agent ensures robustness

2. **Bug Fixes**:
   - Error Handling Agent identifies and fixes the issue
   - Testing Agent adds regression tests
   - Documentation Agent updates if needed

3. **Setup Changes**:
   - Configuration Agent implements changes
   - Testing Agent verifies setup works
   - Documentation Agent updates setup guides

## Task Assignment Rules

- **One agent per task**: Each task should be assigned to exactly one specialized agent
- **Agent expertise**: Choose the agent whose skills best match the task requirements
- **Clear boundaries**: Agents should focus on their assigned responsibilities
- **Coordination**: Agents may need to coordinate for cross-cutting concerns
- **Escalation**: Complex tasks spanning multiple areas may require multiple agents sequentially

## Best Practices

1. **Start with the right agent**: Identify which agent's expertise matches the task
2. **Single responsibility**: Keep agent tasks focused and well-defined
3. **Clear handoffs**: When one agent completes their part, clearly transition to the next
4. **Document decisions**: Agents should document significant decisions in code comments
5. **Test coverage**: Testing Agent should review all code changes
6. **Update documentation**: Documentation Agent should review all user-facing changes

## Examples

### Example 1: Adding a New Pricing Tool
- **Primary**: API Integration Agent (implement the tool)
- **Secondary**: Testing Agent (create tests)
- **Tertiary**: Documentation Agent (document usage)

### Example 2: Fixing a Setup Script Bug
- **Primary**: Configuration Agent (fix the script)
- **Secondary**: Testing Agent (verify the fix)
- **Tertiary**: Documentation Agent (update setup guide if needed)

### Example 3: Improving Error Messages
- **Primary**: Error Handling Agent (improve messages)
- **Secondary**: Testing Agent (test error scenarios)
- **Tertiary**: Documentation Agent (document common errors)

---

**Note**: This structure ensures that GitHub Copilot assigns tasks to the most appropriate specialized agent, improving code quality and development efficiency.
