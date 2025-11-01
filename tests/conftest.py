"""Pytest configuration and shared fixtures for Azure Pricing MCP Server tests."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add parent directory to path so we can import the server module
sys.path.insert(0, str(Path(__file__).parent.parent))

from azure_pricing_server import AzurePricingServer


@pytest.fixture
def mock_azure_api_response() -> Dict[str, Any]:
    """Mock response from Azure Retail Prices API."""
    return {
        "Count": 2,
        "Items": [
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.096,
                "unitPrice": 0.096,
                "armRegionName": "eastus",
                "location": "US East",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "00000000-0000-0000-0000-000000000000",
                "meterName": "D2s v3",
                "productId": "DZH318Z0BQ3P",
                "skuId": "DZH318Z0BQ3P/001J",
                "productName": "Virtual Machines Dsv3 Series",
                "skuName": "D2s v3",
                "serviceName": "Virtual Machines",
                "serviceId": "DZH317F1HKN0",
                "serviceFamily": "Compute",
                "unitOfMeasure": "1 Hour",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": "Standard_D2s_v3",
                "reservationTerm": None,
                "savingsPlan": []
            },
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.192,
                "unitPrice": 0.192,
                "armRegionName": "westus",
                "location": "US West",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "00000000-0000-0000-0000-000000000001",
                "meterName": "D4s v3",
                "productId": "DZH318Z0BQ3P",
                "skuId": "DZH318Z0BQ3P/002J",
                "productName": "Virtual Machines Dsv3 Series",
                "skuName": "D4s v3",
                "serviceName": "Virtual Machines",
                "serviceId": "DZH317F1HKN0",
                "serviceFamily": "Compute",
                "unitOfMeasure": "1 Hour",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": "Standard_D4s_v3",
                "reservationTerm": None,
                "savingsPlan": []
            }
        ],
        "NextPageLink": None
    }


@pytest.fixture
def pricing_server():
    """Create an AzurePricingServer instance for testing."""
    return AzurePricingServer()


@pytest.fixture
async def pricing_server_with_session(pricing_server):
    """Create an AzurePricingServer with initialized session."""
    async with pricing_server:
        yield pricing_server


@pytest.fixture
def mock_aiohttp_session():
    """Mock aiohttp ClientSession for testing."""
    from unittest.mock import MagicMock
    
    # Create a mock context manager for the response
    class MockResponse:
        def __init__(self):
            self.status = 200
            
        async def json(self):
            return {
                "Count": 1,
                "Items": [
                    {
                        "currencyCode": "USD",
                        "retailPrice": 0.096,
                        "unitPrice": 0.096,
                        "armRegionName": "eastus",
                        "location": "US East",
                        "productName": "Virtual Machines Dsv3 Series",
                        "skuName": "D2s v3",
                        "serviceName": "Virtual Machines",
                        "serviceFamily": "Compute",
                        "unitOfMeasure": "1 Hour",
                        "type": "Consumption"
                    }
                ],
                "NextPageLink": None
            }
        
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None
            
        def raise_for_status(self):
            pass
    
    session = MagicMock()
    session.get = MagicMock(return_value=MockResponse())
    
    return session


@pytest.fixture
def sample_pricing_items() -> List[Dict[str, Any]]:
    """Sample pricing items for testing."""
    return [
        {
            "currencyCode": "USD",
            "retailPrice": 0.096,
            "unitPrice": 0.096,
            "armRegionName": "eastus",
            "location": "US East",
            "productName": "Virtual Machines Dsv3 Series",
            "skuName": "D2s v3",
            "serviceName": "Virtual Machines",
            "serviceFamily": "Compute",
            "unitOfMeasure": "1 Hour",
            "type": "Consumption"
        },
        {
            "currencyCode": "USD",
            "retailPrice": 0.192,
            "unitPrice": 0.192,
            "armRegionName": "westus",
            "location": "US West",
            "productName": "Virtual Machines Dsv3 Series",
            "skuName": "D4s v3",
            "serviceName": "Virtual Machines",
            "serviceFamily": "Compute",
            "unitOfMeasure": "1 Hour",
            "type": "Consumption"
        }
    ]
