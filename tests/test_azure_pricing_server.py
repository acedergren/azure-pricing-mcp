"""
Comprehensive tests for Azure Pricing MCP Server.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import aiohttp

# Import the server modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure_pricing_server import AzurePricingServer, AZURE_PRICING_BASE_URL


class TestAzurePricingServer:
    """Test cases for AzurePricingServer class."""
    
    @pytest.fixture
    async def server(self):
        """Create a server instance for testing."""
        server = AzurePricingServer()
        async with server:
            yield server
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test that server initializes correctly."""
        server = AzurePricingServer()
        assert server.session is None
        
        async with server:
            assert server.session is not None
            assert isinstance(server.session, aiohttp.ClientSession)
        
        # Session should be closed after exiting context
        assert server.session.closed
    
    @pytest.mark.asyncio
    async def test_make_request_without_session(self):
        """Test that _make_request fails if session not initialized."""
        server = AzurePricingServer()
        
        with pytest.raises(RuntimeError, match="HTTP session not initialized"):
            await server._make_request("https://example.com")
    
    @pytest.mark.asyncio
    async def test_make_request_success(self, server):
        """Test successful API request."""
        mock_response_data = {
            "Items": [
                {
                    "serviceName": "Virtual Machines",
                    "skuName": "Standard_D2s_v3",
                    "retailPrice": 0.096
                }
            ]
        }
        
        with patch.object(server.session, 'get') as mock_get:
            mock_response = AsyncMock()
            mock_response.status = 200
            mock_response.json = AsyncMock(return_value=mock_response_data)
            mock_response.raise_for_status = Mock()
            mock_get.return_value.__aenter__.return_value = mock_response
            
            result = await server._make_request(AZURE_PRICING_BASE_URL)
            assert result == mock_response_data
            assert "Items" in result
    
    @pytest.mark.asyncio
    async def test_make_request_retry_on_429(self, server):
        """Test that request retries on 429 rate limit error."""
        mock_response_data = {"Items": []}
        
        with patch.object(server.session, 'get') as mock_get:
            # First call returns 429, second call succeeds
            mock_response_429 = AsyncMock()
            mock_response_429.status = 429
            
            mock_response_success = AsyncMock()
            mock_response_success.status = 200
            mock_response_success.json = AsyncMock(return_value=mock_response_data)
            mock_response_success.raise_for_status = Mock()
            
            mock_get.return_value.__aenter__.side_effect = [
                mock_response_429,
                mock_response_success
            ]
            
            with patch('asyncio.sleep', new_callable=AsyncMock) as mock_sleep:
                result = await server._make_request(AZURE_PRICING_BASE_URL)
                assert result == mock_response_data
                # Should have slept once (5 seconds) before retry
                assert mock_sleep.call_count == 1
    
    @pytest.mark.asyncio
    async def test_search_azure_prices_basic(self, server):
        """Test basic price search."""
        mock_api_response = {
            "Items": [
                {
                    "serviceName": "Virtual Machines",
                    "skuName": "Standard_D2s_v3",
                    "retailPrice": 0.096,
                    "armRegionName": "eastus",
                    "location": "US East",
                    "unitOfMeasure": "1 Hour",
                    "type": "Consumption"
                }
            ],
            "NextPageLink": None
        }
        
        with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_api_response
            
            result = await server.search_azure_prices(
                service_name="Virtual Machines",
                sku_name="Standard_D2s_v3"
            )
            
            assert result["count"] == 1
            assert len(result["items"]) == 1
            assert result["items"][0]["skuName"] == "Standard_D2s_v3"
            assert result["currency"] == "USD"
            assert result["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_search_azure_prices_with_filters(self, server):
        """Test price search with multiple filters."""
        mock_api_response = {"Items": [], "NextPageLink": None}
        
        with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_api_response
            
            result = await server.search_azure_prices(
                service_name="Virtual Machines",
                service_family="Compute",
                region="eastus",
                sku_name="Standard_D2s_v3",
                price_type="Consumption",
                currency_code="EUR",
                limit=10
            )
            
            # Verify the request was made with correct parameters
            call_args = mock_request.call_args
            assert call_args is not None
            params = call_args[0][1]  # Second argument is params
            assert params["currencyCode"] == "EUR"
            assert "$filter" in params
            # Check that filters are applied (they may be in any order)
            filter_str = params["$filter"]
            assert "Virtual Machines" in filter_str or "Compute" in filter_str
    
    @pytest.mark.asyncio
    async def test_search_azure_prices_with_discount(self, server):
        """Test price search with discount applied."""
        mock_api_response = {
            "Items": [
                {
                    "serviceName": "Virtual Machines",
                    "skuName": "Standard_D2s_v3",
                    "retailPrice": 0.096,
                    "armRegionName": "eastus"
                }
            ],
            "NextPageLink": None
        }
        
        with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_api_response
            
            result = await server.search_azure_prices(
                service_name="Virtual Machines",
                discount_percentage=10.0
            )
            
            assert "discount_applied" in result
            assert result["discount_applied"]["percentage"] == 10.0
            # Price should be discounted
            discounted_price = result["items"][0]["retailPrice"]
            assert discounted_price == pytest.approx(0.0864, rel=1e-4)  # 0.096 * 0.9
    
    @pytest.mark.asyncio
    async def test_search_azure_prices_limit(self, server):
        """Test that limit parameter works correctly."""
        # Create more items than limit
        items = [
            {
                "serviceName": "Virtual Machines",
                "skuName": f"Standard_D{i}s_v3",
                "retailPrice": 0.096 * i
            }
            for i in range(1, 21)  # 20 items
        ]
        
        mock_api_response = {
            "Items": items,
            "NextPageLink": None
        }
        
        with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_api_response
            
            result = await server.search_azure_prices(
                service_name="Virtual Machines",
                limit=10
            )
            
            # Should only return 10 items even though 20 were returned from API
            assert result["count"] == 10
            assert len(result["items"]) == 10
    
    @pytest.mark.asyncio
    async def test_get_customer_discount_default(self, server):
        """Test getting default customer discount."""
        result = await server.get_customer_discount()
        
        assert "discount_percentage" in result
        assert result["discount_percentage"] == 10.0
        assert result["customer_id"] == "default"
    
    @pytest.mark.asyncio
    async def test_get_customer_discount_specific_customer(self, server):
        """Test getting discount for specific customer."""
        result = await server.get_customer_discount(customer_id="customer123")
        
        assert result["customer_id"] == "customer123"
        assert result["discount_percentage"] == 10.0  # Should still be 10%
    
    @pytest.mark.asyncio
    async def test_apply_discount_to_items(self, server):
        """Test discount application to price items."""
        items = [
            {"retailPrice": 100.0, "serviceName": "Test1"},
            {"retailPrice": 50.0, "serviceName": "Test2"},
            {"retailPrice": 25.0, "serviceName": "Test3"}
        ]
        
        discounted_items = server._apply_discount_to_items(items, 10.0)
        
        assert len(discounted_items) == 3
        assert discounted_items[0]["retailPrice"] == 90.0
        assert discounted_items[0]["originalPrice"] == 100.0
        assert discounted_items[1]["retailPrice"] == 45.0
        assert discounted_items[2]["retailPrice"] == 22.5
    
    @pytest.mark.asyncio
    async def test_apply_discount_zero_percentage(self, server):
        """Test that zero discount modifies items (adds originalPrice)."""
        items = [{"retailPrice": 100.0}]
        
        result = server._apply_discount_to_items(items, 0.0)
        
        # Even with 0% discount, originalPrice is added
        assert result[0]["retailPrice"] == 100.0
        assert result[0]["originalPrice"] == 100.0
    
    @pytest.mark.asyncio
    async def test_discover_service_skus(self, server):
        """Test SKU discovery functionality."""
        mock_search_result = {
            "items": [
                {
                    "skuName": "Standard_D2s_v3",
                    "armSkuName": "Standard_D2s_v3",
                    "productName": "Virtual Machines Dsv3 Series",
                    "retailPrice": 0.096,
                    "unitOfMeasure": "1 Hour",
                    "armRegionName": "eastus"
                }
            ],
            "match_type": "exact"
        }
        
        with patch.object(server, 'search_azure_prices_with_fuzzy_matching', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_search_result
            
            result = await server.discover_service_skus(
                service_hint="virtual machines",
                region="eastus"
            )
            
            assert result["total_skus"] >= 1
            assert "Standard_D2s_v3" in result["skus"]
            assert result["match_type"] == "exact"
    
    @pytest.mark.asyncio
    async def test_validate_and_suggest_skus(self, server):
        """Test SKU validation and suggestion."""
        # Mock the search to return similar SKUs
        mock_search_result = {
            "items": [
                {"skuName": "Standard_D2s_v3"},
                {"skuName": "Standard_D4s_v3"},
                {"skuName": "Standard_D8s_v3"}
            ],
            "count": 3
        }
        
        with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
            mock_search.return_value = mock_search_result
            
            result = await server._validate_and_suggest_skus(
                service_name="Virtual Machines",
                sku_name="Standard_D2",
                currency_code="USD"
            )
            
            assert "sku_validation" in result or "suggestions" in result


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    @pytest.mark.asyncio
    async def test_empty_search_results(self):
        """Test handling of empty search results."""
        server = AzurePricingServer()
        async with server:
            mock_api_response = {"Items": [], "NextPageLink": None}
            
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_api_response
                
                result = await server.search_azure_prices(
                    service_name="NonExistentService"
                )
                
                assert result["count"] == 0
                assert len(result["items"]) == 0
                assert result["has_more"] is False
    
    @pytest.mark.asyncio
    async def test_network_error_handling(self):
        """Test handling of network errors."""
        server = AzurePricingServer()
        async with server:
            with patch.object(server.session, 'get') as mock_get:
                mock_get.side_effect = aiohttp.ClientError("Network error")
                
                with pytest.raises(aiohttp.ClientError):
                    await server._make_request(AZURE_PRICING_BASE_URL)
    
    @pytest.mark.asyncio
    async def test_invalid_currency_code(self):
        """Test search with invalid currency code (should still work, API handles validation)."""
        server = AzurePricingServer()
        async with server:
            mock_api_response = {"Items": [], "NextPageLink": None}
            
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_api_response
                
                # API should accept it, even if invalid
                result = await server.search_azure_prices(
                    service_name="Virtual Machines",
                    currency_code="INVALID"
                )
                
                assert result["currency"] == "INVALID"


class TestIntegration:
    """Integration tests that make actual API calls (can be skipped in CI)."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_api_call(self):
        """Test actual API call to Azure (requires internet)."""
        server = AzurePricingServer()
        async with server:
            result = await server.search_azure_prices(
                service_name="Virtual Machines",
                region="eastus",
                limit=5
            )
            
            # Should get some results
            assert result["count"] >= 0
            assert "items" in result
            assert "currency" in result
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_real_sku_discovery(self):
        """Test real SKU discovery (requires internet)."""
        server = AzurePricingServer()
        async with server:
            result = await server.discover_service_skus(
                service_hint="virtual machines",
                limit=10
            )
            
            assert "skus" in result
            assert result["total_skus"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
