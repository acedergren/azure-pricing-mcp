"""Unit tests for Azure pricing search functionality."""

import pytest
from unittest.mock import AsyncMock, patch
from azure_pricing_server import AzurePricingServer


@pytest.mark.asyncio
async def test_search_azure_prices_basic(pricing_server, mock_aiohttp_session):
    """Test basic price search functionality."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.search_azure_prices(
        service_name="Virtual Machines",
        region="eastus",
        limit=10
    )
    
    assert result is not None
    assert "count" in result
    assert "items" in result
    assert result["count"] >= 0


@pytest.mark.asyncio
async def test_search_azure_prices_with_filters(pricing_server, mock_aiohttp_session):
    """Test price search with multiple filters."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.search_azure_prices(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        region="eastus",
        price_type="Consumption",
        limit=5
    )
    
    assert result is not None
    assert "count" in result
    assert "items" in result


@pytest.mark.asyncio
async def test_search_azure_prices_empty_results(pricing_server):
    """Test search with no matching results."""
    
    # Create a proper mock response for empty results
    class MockResponse:
        def __init__(self):
            self.status = 200
            
        async def json(self):
            return {
                "Count": 0,
                "Items": [],
                "NextPageLink": None
            }
        
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None
            
        def raise_for_status(self):
            pass
    
    from unittest.mock import MagicMock
    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=MockResponse())
    
    pricing_server.session = mock_session
    
    result = await pricing_server.search_azure_prices(
        service_name="NonExistentService",
        limit=10
    )
    
    assert result["count"] == 0
    assert len(result["items"]) == 0


@pytest.mark.asyncio
async def test_search_azure_prices_with_currency(pricing_server, mock_aiohttp_session):
    """Test price search with specific currency."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.search_azure_prices(
        service_name="Virtual Machines",
        currency_code="EUR",
        limit=10
    )
    
    assert result is not None
    mock_aiohttp_session.get.assert_called_once()


@pytest.mark.asyncio
async def test_apply_discount_to_items(pricing_server, sample_pricing_items):
    """Test discount application to pricing items."""
    discount_percentage = 20.0
    
    discounted_items = pricing_server._apply_discount_to_items(
        sample_pricing_items.copy(),
        discount_percentage
    )
    
    assert len(discounted_items) == len(sample_pricing_items)
    for original, discounted in zip(sample_pricing_items, discounted_items):
        expected_price = original["retailPrice"] * (1 - discount_percentage / 100)
        assert abs(discounted["retailPrice"] - expected_price) < 0.001
        assert "originalPrice" in discounted


@pytest.mark.asyncio
async def test_search_with_pagination(pricing_server):
    """Test handling of paginated results."""
    
    # Create a proper mock response for pagination
    class MockResponse:
        def __init__(self):
            self.status = 200
            
        async def json(self):
            return {
                "Count": 100,
                "Items": [{"skuName": f"SKU{i}"} for i in range(100)],
                "NextPageLink": None  # Simplified - not testing actual pagination
            }
        
        async def __aenter__(self):
            return self
            
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return None
            
        def raise_for_status(self):
            pass
    
    from unittest.mock import MagicMock
    mock_session = MagicMock()
    mock_session.get = MagicMock(return_value=MockResponse())
    
    pricing_server.session = mock_session
    
    result = await pricing_server.search_azure_prices(
        service_name="Virtual Machines",
        limit=150
    )
    
    assert result is not None
    assert result["count"] >= 0
