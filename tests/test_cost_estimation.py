"""Unit tests for cost estimation functionality."""

import pytest
from unittest.mock import AsyncMock
from azure_pricing_server import AzurePricingServer


@pytest.mark.asyncio
async def test_estimate_costs_basic(pricing_server, mock_aiohttp_session):
    """Test basic cost estimation."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.estimate_costs(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        region="eastus",
        hours_per_month=160  # 8 hours/day * 20 days
    )
    
    assert result is not None
    assert "on_demand_pricing" in result
    assert "monthly_cost" in result["on_demand_pricing"]
    assert result["on_demand_pricing"]["monthly_cost"] > 0


@pytest.mark.asyncio
async def test_estimate_costs_full_time(pricing_server, mock_aiohttp_session):
    """Test cost estimation for 24/7 usage."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.estimate_costs(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        region="eastus",
        hours_per_month=720  # Full month
    )
    
    assert result is not None
    assert result["on_demand_pricing"]["monthly_cost"] > 0


@pytest.mark.asyncio
async def test_estimate_costs_with_discount(pricing_server, mock_aiohttp_session):
    """Test cost estimation with customer discount."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.estimate_costs(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        region="eastus",
        hours_per_month=720,
        discount_percentage=20.0
    )
    
    assert result is not None
    assert result["on_demand_pricing"]["monthly_cost"] > 0


@pytest.mark.asyncio
async def test_estimate_costs_default_hours(pricing_server, mock_aiohttp_session):
    """Test cost estimation with default hours (730)."""
    pricing_server.session = mock_aiohttp_session
    
    result = await pricing_server.estimate_costs(
        service_name="Virtual Machines",
        sku_name="D2s v3",
        region="eastus"
    )
    
    assert result is not None
    assert result["on_demand_pricing"]["monthly_cost"] > 0
    assert "usage_assumptions" in result
