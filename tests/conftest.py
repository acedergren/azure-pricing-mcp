"""Pytest configuration and fixtures for Azure Pricing MCP Server tests."""

import asyncio
from unittest.mock import AsyncMock

import aiohttp
import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def mock_aiohttp_session() -> AsyncMock:
    """Create a mock aiohttp ClientSession."""
    session = AsyncMock(spec=aiohttp.ClientSession)

    # Mock response
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"Items": [], "Count": 0, "NextPageLink": None})

    # Configure session.get to return the mock response
    session.get.return_value.__aenter__.return_value = mock_response

    return session


@pytest.fixture
def sample_azure_price_item():
    """Sample Azure price item for testing."""
    return {
        "currencyCode": "USD",
        "tierMinimumUnits": 0.0,
        "retailPrice": 0.096,
        "unitPrice": 0.096,
        "armRegionName": "eastus",
        "location": "US East",
        "effectiveStartDate": "2023-01-01T00:00:00Z",
        "meterId": "12345678-1234-1234-1234-123456789012",
        "meterName": "D2s v3",
        "productId": "DZH318Z0BQ36",
        "skuId": "DZH318Z0BQ36/001P",
        "productName": "Virtual Machines Dsv3 Series",
        "skuName": "D2s v3",
        "serviceName": "Virtual Machines",
        "serviceId": "DZH313Z7MMC8",
        "serviceFamily": "Compute",
        "unitOfMeasure": "1 Hour",
        "type": "Consumption",
        "isPrimaryMeterRegion": True,
        "armSkuName": "Standard_D2s_v3",
    }


@pytest.fixture
def sample_azure_prices_response(sample_azure_price_item):
    """Sample Azure Retail Prices API response."""
    return {
        "BillingCurrency": "USD",
        "CustomerEntityId": "Default",
        "CustomerEntityType": "Retail",
        "Items": [sample_azure_price_item],
        "NextPageLink": None,
        "Count": 1,
    }


@pytest.fixture
def sample_search_filters():
    """Sample search filters for testing."""
    return {
        "service_name": "Virtual Machines",
        "region": "eastus",
        "sku_name": "D2s v3",
        "price_type": "Consumption",
    }
