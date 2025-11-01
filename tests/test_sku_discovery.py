"""Unit tests for SKU discovery functionality."""

import pytest
from unittest.mock import AsyncMock
from azure_pricing_server import AzurePricingServer


@pytest.mark.asyncio
async def test_discover_skus_basic(pricing_server, mock_aiohttp_session):
    """Test basic SKU discovery."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.discover_skus(
        service_name="Virtual Machines"
    )
    
    assert result is not None
    assert "skus" in result
    assert "total_skus" in result


@pytest.mark.asyncio
async def test_discover_skus_with_region(pricing_server, mock_aiohttp_session):
    """Test SKU discovery filtered by region."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.discover_skus(
        service_name="Virtual Machines",
        region="eastus"
    )
    
    assert result is not None
    assert "skus" in result


@pytest.mark.asyncio
async def test_fuzzy_matching_service_discovery(pricing_server, mock_aiohttp_session):
    """Test fuzzy matching for service discovery."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.search_azure_prices_with_fuzzy_matching(
        service_name="Virtual Machines"
    )
    
    assert result is not None


@pytest.mark.asyncio
async def test_discover_service_skus(pricing_server, mock_aiohttp_session):
    """Test service SKU discovery."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.discover_service_skus(
        service_hint="virtual machines"
    )
    
    assert result is not None
