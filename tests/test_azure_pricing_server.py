"""Unit tests for Azure Pricing Server core functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientResponseError
import asyncio

from azure_pricing_server import AzurePricingServer


class TestAzurePricingServer:
    """Test suite for AzurePricingServer class."""
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test that AzurePricingServer works as async context manager."""
        async with AzurePricingServer() as server:
            assert server.session is not None
            assert not server.session.closed
        
        # Session should be closed after context exit
        assert server.session.closed
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, mock_vm_pricing_response):
        """Test successful API request."""
        async with AzurePricingServer() as server:
            with patch.object(server.session, 'get') as mock_get:
                # Mock successful response
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value=mock_vm_pricing_response)
                mock_response.raise_for_status = MagicMock()
                
                mock_get.return_value.__aenter__.return_value = mock_response
                
                result = await server._make_request("https://test.com")
                
                assert result == mock_vm_pricing_response
                mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_request_retry_on_429(self, mock_vm_pricing_response):
        """Test retry logic on rate limiting (429)."""
        async with AzurePricingServer() as server:
            with patch.object(server.session, 'get') as mock_get:
                # First call returns 429, second succeeds
                mock_response_429 = AsyncMock()
                mock_response_429.status = 429
                
                mock_response_success = AsyncMock()
                mock_response_success.status = 200
                mock_response_success.json = AsyncMock(return_value=mock_vm_pricing_response)
                mock_response_success.raise_for_status = MagicMock()
                
                mock_get.return_value.__aenter__.side_effect = [
                    mock_response_429,
                    mock_response_success
                ]
                
                # Mock sleep to speed up test
                with patch('asyncio.sleep', new_callable=AsyncMock):
                    result = await server._make_request("https://test.com")
                
                assert result == mock_vm_pricing_response
                assert mock_get.call_count == 2
    
    @pytest.mark.asyncio
    async def test_make_request_max_retries_exceeded(self):
        """Test that max retries are respected."""
        async with AzurePricingServer() as server:
            with patch.object(server.session, 'get') as mock_get:
                # Always return 429
                mock_response_429 = AsyncMock()
                mock_response_429.status = 429
                mock_response_429.raise_for_status = MagicMock(
                    side_effect=ClientResponseError(
                        request_info=MagicMock(),
                        history=(),
                        status=429
                    )
                )
                
                mock_get.return_value.__aenter__.return_value = mock_response_429
                
                # Mock sleep to speed up test
                with patch('asyncio.sleep', new_callable=AsyncMock):
                    with pytest.raises(ClientResponseError):
                        await server._make_request("https://test.com", max_retries=2)
                
                # Should try initial + 2 retries = 3 times
                assert mock_get.call_count == 3
    
    @pytest.mark.asyncio
    async def test_search_azure_prices_basic(self, mock_vm_pricing_response):
        """Test basic price search."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_vm_pricing_response
                
                result = await server.search_azure_prices(
                    service_name="Virtual Machines",
                    region="eastus",
                    limit=50,
                    validate_sku=False
                )
                
                assert result["count"] == 2
                assert len(result["items"]) == 2
                assert result["currency"] == "USD"
                assert not result["has_more"]
                assert "serviceName eq 'Virtual Machines'" in result["filters_applied"][0]
    
    @pytest.mark.asyncio
    async def test_search_azure_prices_with_filters(self, mock_vm_pricing_response):
        """Test price search with multiple filters."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_vm_pricing_response
                
                result = await server.search_azure_prices(
                    service_name="Virtual Machines",
                    service_family="Compute",
                    region="eastus",
                    sku_name="D2s",
                    price_type="Consumption",
                    currency_code="USD",
                    limit=10,
                    validate_sku=False
                )
                
                assert result["count"] == 2
                assert result["currency"] == "USD"
                filters = result["filters_applied"]
                assert any("serviceName" in f for f in filters)
                assert any("serviceFamily" in f for f in filters)
                assert any("armRegionName" in f for f in filters)
    
    @pytest.mark.asyncio
    async def test_search_azure_prices_no_results(self, mock_empty_response):
        """Test price search with no results."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_empty_response
                
                result = await server.search_azure_prices(
                    service_name="NonExistentService",
                    validate_sku=False
                )
                
                assert result["count"] == 0
                assert len(result["items"]) == 0
                assert not result["has_more"]
    
    @pytest.mark.asyncio
    async def test_apply_discount_to_items(self):
        """Test discount application to pricing items."""
        server = AzurePricingServer()
        
        items = [
            {
                "retailPrice": 100.0,
                "skuName": "Test SKU"
            },
            {
                "retailPrice": 50.0,
                "skuName": "Test SKU 2",
                "savingsPlan": [
                    {"retailPrice": 40.0, "term": "1 Year"}
                ]
            }
        ]
        
        discounted = server._apply_discount_to_items(items, 10.0)
        
        assert len(discounted) == 2
        assert discounted[0]["retailPrice"] == 90.0
        assert discounted[0]["originalPrice"] == 100.0
        assert discounted[1]["retailPrice"] == 45.0
        assert discounted[1]["originalPrice"] == 50.0
        assert discounted[1]["savingsPlan"][0]["retailPrice"] == 36.0
        assert discounted[1]["savingsPlan"][0]["originalPrice"] == 40.0
    
    @pytest.mark.asyncio
    async def test_apply_discount_to_empty_items(self):
        """Test discount application to empty list."""
        server = AzurePricingServer()
        
        discounted = server._apply_discount_to_items([], 10.0)
        
        assert len(discounted) == 0
    
    @pytest.mark.asyncio
    async def test_search_with_discount(self, mock_vm_pricing_response):
        """Test price search with discount applied."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_vm_pricing_response
                
                result = await server.search_azure_prices(
                    service_name="Virtual Machines",
                    discount_percentage=10.0,
                    validate_sku=False
                )
                
                assert "discount_applied" in result
                assert result["discount_applied"]["percentage"] == 10.0
                
                # Check that prices were discounted
                original_price = mock_vm_pricing_response["Items"][0]["retailPrice"]
                discounted_price = result["items"][0]["retailPrice"]
                assert discounted_price == original_price * 0.9
    
    @pytest.mark.asyncio
    async def test_get_customer_discount(self):
        """Test customer discount retrieval."""
        async with AzurePricingServer() as server:
            result = await server.get_customer_discount("test-customer")
            
            assert result["customer_id"] == "test-customer"
            assert result["discount_percentage"] == 10.0
            assert result["discount_type"] == "standard"
    
    @pytest.mark.asyncio
    async def test_get_customer_discount_default(self):
        """Test customer discount with no customer ID."""
        async with AzurePricingServer() as server:
            result = await server.get_customer_discount()
            
            assert result["customer_id"] == "default"
            assert result["discount_percentage"] == 10.0
    
    @pytest.mark.asyncio
    async def test_validate_and_suggest_skus(self, mock_vm_pricing_response):
        """Test SKU validation and suggestion."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": mock_vm_pricing_response["Items"],
                    "count": 2
                }
                
                result = await server._validate_and_suggest_skus(
                    service_name="Virtual Machines",
                    sku_name="D2",
                    currency_code="USD"
                )
                
                assert "sku_validation" in result
                assert not result["sku_validation"]["found"]
                assert result["sku_validation"]["original_sku"] == "D2"
                assert len(result["sku_validation"]["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_compare_prices_across_regions(self, mock_multi_region_response):
        """Test price comparison across regions."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_multi_region_response
                
                result = await server.compare_prices(
                    service_name="Virtual Machines",
                    sku_name="D2s v3",
                    regions=["eastus", "westeurope"]
                )
                
                assert "comparison_type" in result
                # Actual implementation uses "regions" for regional comparison
                assert result["comparison_type"] == "regions"
                assert "comparisons" in result
                # Should have data for both regions
                assert len(result["comparisons"]) > 0
    
    @pytest.mark.asyncio
    async def test_cost_estimate(self, mock_vm_pricing_response):
        """Test cost estimation."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_vm_pricing_response
                
                result = await server.estimate_costs(
                    service_name="Virtual Machines",
                    sku_name="D2s v3",
                    region="eastus",
                    hours_per_month=240
                )
                
                # Actual implementation uses "on_demand_pricing" structure
                assert "on_demand_pricing" in result
                assert "monthly_cost" in result["on_demand_pricing"]
                assert "hourly_rate" in result["on_demand_pricing"]
                
                # Verify calculation
                hourly_rate = mock_vm_pricing_response["Items"][0]["retailPrice"]
                expected_monthly = round(hourly_rate * 240, 2)
                assert result["on_demand_pricing"]["monthly_cost"] == expected_monthly
    
    @pytest.mark.asyncio
    async def test_discover_skus(self, mock_vm_pricing_response):
        """Test SKU discovery."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_vm_pricing_response
                
                result = await server.discover_skus(
                    service_name="Virtual Machines",
                    region="eastus"
                )
                
                assert "service_name" in result
                assert "skus" in result
                assert "total_skus" in result
                assert result["total_skus"] > 0
