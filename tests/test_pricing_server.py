"""Unit tests for Azure Pricing Server core functionality."""

import sys
import os

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from aiohttp import ClientResponseError

# Add parent directory to path to allow importing without package installation
# This is a common pattern for development testing
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure_pricing_server import AzurePricingServer, AZURE_PRICING_BASE_URL  # noqa: E402


@pytest.fixture
def pricing_server():
    """Create an AzurePricingServer instance for testing."""
    return AzurePricingServer()


@pytest.fixture
def mock_api_response():
    """Create a mock API response with sample pricing data."""
    return {
        "Items": [
            {
                "serviceName": "Virtual Machines",
                "skuName": "Standard_D2s_v3",
                "productName": "Virtual Machines DS Series Windows",
                "retailPrice": 0.096,
                "unitOfMeasure": "1 Hour",
                "armRegionName": "eastus",
                "currencyCode": "USD",
                "priceType": "Consumption",
            },
            {
                "serviceName": "Virtual Machines",
                "skuName": "Standard_D4s_v3",
                "productName": "Virtual Machines DS Series Windows",
                "retailPrice": 0.192,
                "unitOfMeasure": "1 Hour",
                "armRegionName": "eastus",
                "currencyCode": "USD",
                "priceType": "Consumption",
            },
        ],
        "NextPageLink": None,
        "Count": 2,
    }


@pytest.fixture
def mock_empty_response():
    """Create a mock empty API response."""
    return {"Items": [], "NextPageLink": None, "Count": 0}


class TestAzurePricingServer:
    """Test cases for AzurePricingServer class."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test that AzurePricingServer works as an async context manager."""
        async with AzurePricingServer() as server:
            assert server.session is not None
        # Session should be closed after exiting context
        assert server.session.closed

    @pytest.mark.asyncio
    async def test_make_request_success(self, pricing_server, mock_api_response):
        """Test successful API request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=mock_api_response)
        mock_response.raise_for_status = MagicMock()

        async with pricing_server:
            with patch.object(pricing_server.session, "get") as mock_get:
                mock_get.return_value.__aenter__.return_value = mock_response

                result = await pricing_server._make_request(
                    AZURE_PRICING_BASE_URL, {"api-version": "2023-01-01-preview"}
                )

                assert result == mock_api_response
                assert "Items" in result
                assert len(result["Items"]) == 2

    @pytest.mark.asyncio
    async def test_make_request_rate_limit_retry(self, pricing_server, mock_api_response):
        """Test that rate limiting (429) triggers retry logic."""
        # First call returns 429, second call succeeds
        mock_response_429 = AsyncMock()
        mock_response_429.status = 429

        mock_response_success = AsyncMock()
        mock_response_success.status = 200
        mock_response_success.json = AsyncMock(return_value=mock_api_response)
        mock_response_success.raise_for_status = MagicMock()

        async with pricing_server:
            with patch.object(pricing_server.session, "get") as mock_get:
                # First call returns 429, second call succeeds
                mock_get.return_value.__aenter__.side_effect = [mock_response_429, mock_response_success]

                with patch("asyncio.sleep") as mock_sleep:
                    result = await pricing_server._make_request(
                        AZURE_PRICING_BASE_URL, {"api-version": "2023-01-01-preview"}, max_retries=3
                    )

                    # Should have slept once before retry
                    mock_sleep.assert_called_once()
                    assert result == mock_api_response

    @pytest.mark.asyncio
    async def test_make_request_http_error(self, pricing_server):
        """Test handling of HTTP errors."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.raise_for_status = MagicMock(
            side_effect=ClientResponseError(
                request_info=MagicMock(), history=(), status=500, message="Internal Server Error"
            )
        )

        async with pricing_server:
            with patch.object(pricing_server.session, "get") as mock_get:
                mock_get.return_value.__aenter__.return_value = mock_response

                with pytest.raises(ClientResponseError):
                    await pricing_server._make_request(AZURE_PRICING_BASE_URL)

    @pytest.mark.asyncio
    async def test_search_azure_prices_with_filters(self, pricing_server, mock_api_response):
        """Test searching Azure prices with various filters."""
        async with pricing_server:
            with patch.object(pricing_server, "_make_request", return_value=mock_api_response):
                result = await pricing_server.search_azure_prices(
                    service_name="Virtual Machines",
                    region="eastus",
                    sku_name="Standard_D2s_v3",
                    price_type="Consumption",
                    currency_code="USD",
                    limit=10,
                )

                assert result["count"] == 2
                assert result["currency"] == "USD"
                assert len(result["items"]) == 2
                assert result["items"][0]["skuName"] == "Standard_D2s_v3"
                assert "filters_applied" in result

    @pytest.mark.asyncio
    async def test_search_azure_prices_with_discount(self, pricing_server, mock_api_response):
        """Test price search with discount applied."""
        async with pricing_server:
            with patch.object(pricing_server, "_make_request", return_value=mock_api_response):
                result = await pricing_server.search_azure_prices(
                    service_name="Virtual Machines", discount_percentage=10.0, limit=10
                )

                assert "discount_applied" in result
                assert result["discount_applied"]["percentage"] == 10.0
                # Check that prices were discounted
                original_price = 0.096
                expected_price = original_price * 0.9  # 10% discount
                assert result["items"][0]["retailPrice"] == pytest.approx(expected_price, rel=1e-5)
                assert result["items"][0]["originalPrice"] == original_price

    @pytest.mark.asyncio
    async def test_search_azure_prices_empty_results(self, pricing_server, mock_empty_response):
        """Test handling of empty search results."""
        async with pricing_server:
            with patch.object(pricing_server, "_make_request", return_value=mock_empty_response):
                with patch.object(pricing_server, "_validate_and_suggest_skus", return_value={}):
                    result = await pricing_server.search_azure_prices(
                        service_name="NonExistentService", validate_sku=False
                    )

                    assert result["count"] == 0
                    assert result["items"] == []

    @pytest.mark.asyncio
    async def test_apply_discount_to_items(self, pricing_server):
        """Test discount application logic."""
        items = [
            {"retailPrice": 100.0, "skuName": "Test1"},
            {"retailPrice": 50.0, "skuName": "Test2"},
            {"retailPrice": None, "skuName": "Test3"},
        ]

        discounted = pricing_server._apply_discount_to_items(items, 20.0)

        assert discounted[0]["retailPrice"] == 80.0
        assert discounted[0]["originalPrice"] == 100.0
        assert discounted[1]["retailPrice"] == 40.0
        assert discounted[1]["originalPrice"] == 50.0
        # Item without price should not have discount applied
        assert "originalPrice" not in discounted[2]

    @pytest.mark.asyncio
    async def test_apply_discount_with_savings_plan(self, pricing_server):
        """Test discount application with savings plans."""
        items = [
            {
                "retailPrice": 100.0,
                "skuName": "Test1",
                "savingsPlan": [{"retailPrice": 80.0, "term": "1 Year"}, {"retailPrice": 70.0, "term": "3 Years"}],
            }
        ]

        discounted = pricing_server._apply_discount_to_items(items, 10.0)

        assert discounted[0]["retailPrice"] == 90.0
        assert discounted[0]["savingsPlan"][0]["retailPrice"] == 72.0
        assert discounted[0]["savingsPlan"][0]["originalPrice"] == 80.0
        assert discounted[0]["savingsPlan"][1]["retailPrice"] == 63.0

    @pytest.mark.asyncio
    async def test_get_customer_discount(self, pricing_server):
        """Test customer discount retrieval."""
        async with pricing_server:
            result = await pricing_server.get_customer_discount("customer123")

            assert result["customer_id"] == "customer123"
            assert result["discount_percentage"] == 10.0
            assert result["discount_type"] == "standard"
            assert result["applicable_services"] == "all"

    @pytest.mark.asyncio
    async def test_get_customer_discount_default(self, pricing_server):
        """Test customer discount with no customer ID."""
        async with pricing_server:
            result = await pricing_server.get_customer_discount()

            assert result["customer_id"] == "default"
            assert result["discount_percentage"] == 10.0

    @pytest.mark.asyncio
    async def test_validate_and_suggest_skus(self, pricing_server):
        """Test SKU validation and suggestion logic."""
        broad_search_result = {
            "items": [
                {
                    "skuName": "Standard_D2s_v3",
                    "productName": "VM D Series",
                    "retailPrice": 0.096,
                    "unitOfMeasure": "1 Hour",
                    "armRegionName": "eastus",
                },
                {
                    "skuName": "Standard_D4s_v3",
                    "productName": "VM D Series",
                    "retailPrice": 0.192,
                    "unitOfMeasure": "1 Hour",
                    "armRegionName": "eastus",
                },
                {
                    "skuName": "Standard_D8s_v3",
                    "productName": "VM D Series",
                    "retailPrice": 0.384,
                    "unitOfMeasure": "1 Hour",
                    "armRegionName": "eastus",
                },
            ]
        }

        async with pricing_server:
            with patch.object(pricing_server, "search_azure_prices", return_value=broad_search_result):
                result = await pricing_server._validate_and_suggest_skus(
                    service_name="Virtual Machines", sku_name="D2s", currency_code="USD"
                )

                assert "sku_validation" in result
                assert result["sku_validation"]["original_sku"] == "D2s"
                assert result["sku_validation"]["found"] is False
                assert len(result["sku_validation"]["suggestions"]) > 0
                # Should find Standard_D2s_v3 as a suggestion
                assert any("D2s" in s["sku_name"] for s in result["sku_validation"]["suggestions"])

    @pytest.mark.asyncio
    async def test_compare_prices_basic(self, pricing_server, mock_api_response):
        """Test basic price comparison functionality."""
        async with pricing_server:
            with patch.object(pricing_server, "_make_request", return_value=mock_api_response):
                result = await pricing_server.compare_prices(
                    service_name="Virtual Machines", regions=["eastus", "westus"], currency_code="USD"
                )

                assert "comparisons" in result or "items" in result

    @pytest.mark.asyncio
    async def test_estimate_cost_basic(self, pricing_server, mock_api_response):
        """Test basic cost estimation functionality."""
        async with pricing_server:
            with patch.object(
                pricing_server,
                "search_azure_prices",
                return_value={"items": [mock_api_response["Items"][0]], "count": 1},
            ):
                result = await pricing_server.estimate_costs(
                    service_name="Virtual Machines",
                    sku_name="Standard_D2s_v3",
                    region="eastus",
                    hours_per_month=730,
                    currency_code="USD",
                )

                assert "on_demand_pricing" in result
                assert "monthly_cost" in result["on_demand_pricing"]
                assert result["on_demand_pricing"]["monthly_cost"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
