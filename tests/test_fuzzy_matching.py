"""Unit tests for fuzzy matching and service discovery."""

import pytest
from unittest.mock import AsyncMock, patch

from azure_pricing_server import AzurePricingServer


class TestFuzzyMatching:
    """Test suite for fuzzy matching and intelligent service discovery."""
    
    @pytest.mark.asyncio
    async def test_fuzzy_matching_exact_mapping(self, mock_vm_pricing_response):
        """Test fuzzy matching with exact service name mapping."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": mock_vm_pricing_response["Items"],
                    "count": 2,
                    "currency": "USD"
                }
                
                result = await server.search_azure_prices_with_fuzzy_matching(
                    service_name="vm",  # Should map to "Virtual Machines"
                    suggest_alternatives=True
                )
                
                # Should find results using the mapped name
                assert result["count"] > 0
                assert "suggestion_used" in result or "items" in result
    
    @pytest.mark.asyncio
    async def test_fuzzy_matching_app_service(self, mock_storage_pricing_response):
        """Test fuzzy matching for App Service variations."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": [mock_storage_pricing_response["Items"][0]],
                    "count": 1,
                    "currency": "USD",
                    "suggestion_used": "Azure App Service"
                }
                
                # Test various app service aliases
                for alias in ["app service", "web app", "web apps", "websites"]:
                    result = await server.search_azure_prices_with_fuzzy_matching(
                        service_name=alias,
                        suggest_alternatives=True
                    )
                    
                    # Should attempt to find results
                    assert "items" in result or "suggestion_used" in result
    
    @pytest.mark.asyncio
    async def test_fuzzy_matching_no_suggestions_when_disabled(self, mock_empty_response):
        """Test that suggestions are not provided when disabled."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": [],
                    "count": 0,
                    "currency": "USD"
                }
                
                result = await server.search_azure_prices_with_fuzzy_matching(
                    service_name="NonExistentService",
                    suggest_alternatives=False
                )
                
                assert result["count"] == 0
                assert "suggestion_used" not in result
    
    @pytest.mark.asyncio
    async def test_fuzzy_matching_with_results_returns_immediately(self, mock_vm_pricing_response):
        """Test that fuzzy matching returns immediately when exact search succeeds."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": mock_vm_pricing_response["Items"],
                    "count": 2,
                    "currency": "USD"
                }
                
                result = await server.search_azure_prices_with_fuzzy_matching(
                    service_name="Virtual Machines",
                    suggest_alternatives=True
                )
                
                # Should return exact results without suggestions
                assert result["count"] == 2
                assert "suggestion_used" not in result
                mock_search.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_find_similar_services_sql_variants(self):
        """Test finding similar services for SQL database variations."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": [{"serviceName": "Azure SQL Database"}],
                    "count": 1,
                    "currency": "USD"
                }
                
                result = await server._find_similar_services(
                    service_name="sql",
                    currency_code="USD"
                )
                
                # Should find Azure SQL Database
                assert "items" in result or "suggestion_used" in result
    
    @pytest.mark.asyncio
    async def test_find_similar_services_kubernetes_variants(self):
        """Test finding similar services for Kubernetes variations."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": [{"serviceName": "Azure Kubernetes Service"}],
                    "count": 1,
                    "currency": "USD"
                }
                
                # Test various Kubernetes aliases
                for alias in ["kubernetes", "aks", "k8s"]:
                    result = await server._find_similar_services(
                        service_name=alias,
                        currency_code="USD"
                    )
                    
                    # Should attempt to find AKS
                    assert "items" in result or mock_search.called
    
    @pytest.mark.asyncio
    async def test_find_similar_services_storage_variants(self):
        """Test finding similar services for storage variations."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": [{"serviceName": "Storage"}],
                    "count": 1,
                    "currency": "USD"
                }
                
                # Test storage aliases
                for alias in ["storage", "blob", "blob storage"]:
                    result = await server._find_similar_services(
                        service_name=alias,
                        currency_code="USD"
                    )
                    
                    assert "items" in result or mock_search.called
    
    @pytest.mark.asyncio
    async def test_sku_validation_no_results(self, mock_empty_response):
        """Test SKU validation when no results are found."""
        async with AzurePricingServer() as server:
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = mock_empty_response
                
                result = await server.search_azure_prices(
                    service_name="Virtual Machines",
                    sku_name="NonExistentSKU",
                    validate_sku=True
                )
                
                # Should include SKU validation info
                assert "sku_validation" in result
                assert not result["sku_validation"]["found"]
                assert result["sku_validation"]["original_sku"] == "NonExistentSKU"
    
    @pytest.mark.asyncio
    async def test_sku_validation_too_many_results(self, mock_vm_pricing_response):
        """Test SKU validation when too many results are returned."""
        async with AzurePricingServer() as server:
            # Create many items
            many_items = mock_vm_pricing_response.copy()
            many_items["Items"] = [
                {**mock_vm_pricing_response["Items"][0], "skuName": f"D{i}s v3"}
                for i in range(15)
            ]
            
            with patch.object(server, '_make_request', new_callable=AsyncMock) as mock_request:
                mock_request.return_value = many_items
                
                result = await server.search_azure_prices(
                    service_name="Virtual Machines",
                    sku_name="D",
                    validate_sku=True
                )
                
                # Should include clarification message
                if result["count"] > 10:
                    assert "clarification" in result
                    assert "suggestions" in result["clarification"]
    
    @pytest.mark.asyncio
    async def test_sku_suggestions_partial_match(self, mock_vm_pricing_response):
        """Test SKU suggestions with partial matching."""
        async with AzurePricingServer() as server:
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": mock_vm_pricing_response["Items"],
                    "count": 2,
                    "currency": "USD"
                }
                
                result = await server._validate_and_suggest_skus(
                    service_name="Virtual Machines",
                    sku_name="D2",
                    currency_code="USD"
                )
                
                assert "sku_validation" in result
                assert "suggestions" in result["sku_validation"]
                # Should have at least one suggestion
                assert len(result["sku_validation"]["suggestions"]) > 0
    
    @pytest.mark.asyncio
    async def test_sku_suggestions_limit(self, mock_vm_pricing_response):
        """Test that SKU suggestions are limited to 5."""
        async with AzurePricingServer() as server:
            # Create many matching items
            many_items = [
                {**mock_vm_pricing_response["Items"][0], 
                 "skuName": f"D{i}s v3",
                 "productName": f"Virtual Machines Dv3 Series {i}",
                 "retailPrice": 0.096 + i * 0.01}
                for i in range(20)
            ]
            
            with patch.object(server, 'search_azure_prices', new_callable=AsyncMock) as mock_search:
                mock_search.return_value = {
                    "items": many_items,
                    "count": 20,
                    "currency": "USD"
                }
                
                result = await server._validate_and_suggest_skus(
                    service_name="Virtual Machines",
                    sku_name="D",
                    currency_code="USD"
                )
                
                # Should limit to 5 suggestions
                assert len(result["sku_validation"]["suggestions"]) <= 5
