"""Unit tests for MCP tool handlers."""

import pytest
from unittest.mock import AsyncMock, patch

from azure_pricing_server import handle_call_tool, pricing_server


class TestMCPToolHandlers:
    """Test suite for MCP tool handlers."""
    
    @pytest.mark.asyncio
    async def test_azure_price_search_tool(self, mock_vm_pricing_response):
        """Test azure_price_search tool handler."""
        with patch.object(pricing_server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
            with patch.object(pricing_server, 'get_customer_discount', new_callable=AsyncMock) as mock_discount:
                mock_discount.return_value = {"discount_percentage": 10.0}
                mock_search.return_value = {
                    "items": mock_vm_pricing_response["Items"],
                    "count": 2,
                    "has_more": False,
                    "currency": "USD",
                    "filters_applied": []
                }
                
                result = await handle_call_tool(
                    "azure_price_search",
                    {
                        "service_name": "Virtual Machines",
                        "region": "eastus",
                        "limit": 10
                    }
                )
                
                assert len(result) > 0
                assert hasattr(result[0], 'text')
                
                # Check response contains expected text
                response_text = result[0].text
                assert "Azure pricing results" in response_text or "Virtual Machines" in response_text
    
    @pytest.mark.asyncio
    async def test_azure_price_compare_tool(self, mock_multi_region_response):
        """Test azure_price_compare tool handler."""
        with patch.object(pricing_server, 'compare_prices', new_callable=AsyncMock) as mock_compare:
            with patch.object(pricing_server, 'get_customer_discount', new_callable=AsyncMock) as mock_discount:
                mock_discount.return_value = {"discount_percentage": 10.0}
                mock_compare.return_value = {
                    "comparison_type": "regions",
                    "service_name": "Virtual Machines",
                    "comparisons": [
                        {
                            "region": "eastus",
                            "retail_price": 0.096,
                            "sku_name": "D2s v3"
                        },
                        {
                            "region": "westeurope",
                            "retail_price": 0.108,
                            "sku_name": "D2s v3"
                        }
                    ]
                }
                
                result = await handle_call_tool(
                    "azure_price_compare",
                    {
                        "service_name": "Virtual Machines",
                        "sku_name": "D2s v3",
                        "regions": ["eastus", "westeurope"]
                    }
                )
                
                assert len(result) > 0
                assert hasattr(result[0], 'text')
                
                response_text = result[0].text
                assert "comparison" in response_text.lower() or "Virtual Machines" in response_text
    
    @pytest.mark.asyncio
    async def test_azure_cost_estimate_tool(self, mock_vm_pricing_response):
        """Test azure_cost_estimate tool handler."""
        with patch.object(pricing_server, 'estimate_costs', new_callable=AsyncMock) as mock_estimate:
            with patch.object(pricing_server, 'get_customer_discount', new_callable=AsyncMock) as mock_discount:
                mock_discount.return_value = {"discount_percentage": 10.0}
                mock_estimate.return_value = {
                    "service_name": "Virtual Machines",
                    "sku_name": "D2s v3",
                    "region": "eastus",
                    "product_name": "Virtual Machines Dv3 Series",
                    "unit_of_measure": "1 Hour",
                    "currency": "USD",
                    "on_demand_pricing": {
                        "hourly_rate": 0.096,
                        "daily_cost": 2.30,
                        "monthly_cost": 23.04,
                        "yearly_cost": 276.48
                    },
                    "usage_assumptions": {
                        "hours_per_month": 240,
                        "hours_per_day": 8.0
                    },
                    "savings_plans": []
                }
                
                result = await handle_call_tool(
                    "azure_cost_estimate",
                    {
                        "service_name": "Virtual Machines",
                        "sku_name": "D2s v3",
                        "region": "eastus",
                        "hours_per_month": 240
                    }
                )
                
                assert len(result) > 0
                assert hasattr(result[0], 'text')
                
                response_text = result[0].text
                assert "cost" in response_text.lower() or "Virtual Machines" in response_text
    
    @pytest.mark.asyncio
    async def test_azure_discover_skus_tool(self, mock_vm_pricing_response):
        """Test azure_discover_skus tool handler."""
        with patch.object(pricing_server, 'discover_skus', new_callable=AsyncMock) as mock_discover:
            mock_discover.return_value = {
                "service_name": "Virtual Machines",
                "skus": [
                    {
                        "sku_name": "D2s v3",
                        "product_name": "Virtual Machines Dv3 Series",
                        "sample_price": 0.096
                    }
                ],
                "total_skus": 1
            }
            
            result = await handle_call_tool(
                "azure_discover_skus",
                {
                    "service_name": "Virtual Machines",
                    "region": "eastus"
                }
            )
            
            assert len(result) > 0
            assert hasattr(result[0], 'text')
            
            response_text = result[0].text
            assert "SKU" in response_text or "Virtual Machines" in response_text
    
    @pytest.mark.asyncio
    async def test_azure_sku_discovery_tool(self, mock_vm_pricing_response):
        """Test azure_sku_discovery tool with fuzzy matching."""
        with patch.object(pricing_server, 'search_azure_prices_with_fuzzy_matching', new_callable=AsyncMock) as mock_fuzzy:
            mock_fuzzy.return_value = {
                "items": mock_vm_pricing_response["Items"],
                "count": 2,
                "currency": "USD",
                "suggestion_used": "Virtual Machines",
                "original_search": "vm",
                "match_type": "exact_mapping"
            }
            
            result = await handle_call_tool(
                "azure_sku_discovery",
                {
                    "service_hint": "vm",
                    "region": "eastus"
                }
            )
            
            assert len(result) > 0
            assert hasattr(result[0], 'text')
            
            response_text = result[0].text
            assert len(response_text) > 0
    
    @pytest.mark.asyncio
    async def test_get_customer_discount_tool(self):
        """Test get_customer_discount tool handler."""
        with patch.object(pricing_server, 'get_customer_discount', new_callable=AsyncMock) as mock_discount:
            mock_discount.return_value = {
                "customer_id": "test-customer",
                "discount_percentage": 10.0,
                "discount_type": "standard",
                "description": "Standard customer discount",
                "applicable_services": "all",
                "note": "Contact sales for enterprise discounts"
            }
            
            result = await handle_call_tool(
                "get_customer_discount",
                {
                    "customer_id": "test-customer"
                }
            )
            
            assert len(result) > 0
            assert hasattr(result[0], 'text')
            
            response_text = result[0].text
            assert "discount" in response_text.lower()
    
    @pytest.mark.asyncio
    async def test_tool_with_invalid_name(self):
        """Test handling of invalid tool name."""
        result = await handle_call_tool(
            "invalid_tool_name",
            {}
        )
        
        assert len(result) > 0
        assert hasattr(result[0], 'text')
        
        # Should return error response
        response_text = result[0].text
        assert "error" in response_text.lower() or "unknown" in response_text.lower()
    
    @pytest.mark.asyncio
    async def test_tool_with_missing_required_params(self):
        """Test handling of missing required parameters."""
        # azure_cost_estimate requires service_name, sku_name, and region
        # The tool should handle missing parameters gracefully
        with patch.object(pricing_server, 'estimate_costs', new_callable=AsyncMock) as mock_estimate:
            mock_estimate.side_effect = TypeError("missing required argument")
            
            result = await handle_call_tool(
                "azure_cost_estimate",
                {
                    "service_name": "Virtual Machines"
                    # Missing sku_name and region
                }
            )
            
            assert len(result) > 0
            assert hasattr(result[0], 'text')
            
            # Should return error or handle gracefully
            response_text = result[0].text
            assert len(response_text) > 0
    
    @pytest.mark.asyncio
    async def test_search_with_discount_parameter(self, mock_vm_pricing_response):
        """Test price search with explicit discount parameter."""
        with patch.object(pricing_server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
            with patch.object(pricing_server, 'get_customer_discount', new_callable=AsyncMock) as mock_discount:
                mock_discount.return_value = {"discount_percentage": 10.0}
                
                # Mock response with discount applied
                discounted_items = [
                    {**item, "retailPrice": item["retailPrice"] * 0.85, "originalPrice": item["retailPrice"]}
                    for item in mock_vm_pricing_response["Items"]
                ]
                
                mock_search.return_value = {
                    "items": discounted_items,
                    "count": 2,
                    "has_more": False,
                    "currency": "USD",
                    "filters_applied": [],
                    "discount_applied": {
                        "percentage": 15.0,
                        "note": "Prices shown are after discount"
                    }
                }
                
                result = await handle_call_tool(
                    "azure_price_search",
                    {
                        "service_name": "Virtual Machines",
                        "discount_percentage": 15.0
                    }
                )
                
                assert len(result) > 0
                response_text = result[0].text
                assert "discount" in response_text.lower() or "15" in response_text
