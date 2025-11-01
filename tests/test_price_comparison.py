"""Unit tests for price comparison functionality."""

import pytest
from unittest.mock import AsyncMock
from azure_pricing_server import AzurePricingServer


@pytest.mark.asyncio
async def test_compare_prices_basic(pricing_server, mock_aiohttp_session):
    """Test basic price comparison functionality."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.compare_prices(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        regions=["eastus", "westus"]
    )
    
    assert result is not None
    assert "comparisons" in result
    assert "service_name" in result


@pytest.mark.asyncio
async def test_compare_prices_single_region(pricing_server, mock_aiohttp_session):
    """Test comparison with single region."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.compare_prices(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        regions=["eastus"]
    )
    
    assert result is not None
    assert "comparisons" in result


@pytest.mark.asyncio
async def test_compare_prices_no_sku(pricing_server, mock_aiohttp_session):
    """Test comparison without specific SKU."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.compare_prices(
        service_name="Virtual Machines",
        regions=["eastus"]
    )
    
    assert result is not None


@pytest.mark.asyncio
async def test_compare_prices_with_discount(pricing_server, mock_aiohttp_session):
    """Test price comparison with discount."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.compare_prices(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        regions=["eastus", "westus"],
        discount_percentage=10.0
    )
    
    assert result is not None
    assert "comparisons" in result
