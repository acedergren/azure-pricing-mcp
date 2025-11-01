"""Unit tests for Azure Pricing MCP Server core functionality."""

from unittest.mock import AsyncMock

import pytest

from azure_pricing_server import AzurePricingServer


class TestAzurePricingServer:
    """Test cases for AzurePricingServer class."""

    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """Test server can be initialized."""
        server = AzurePricingServer()
        assert server.session is None

    @pytest.mark.asyncio
    async def test_context_manager_creates_session(self):
        """Test async context manager creates aiohttp session."""
        server = AzurePricingServer()

        async with server as s:
            assert s.session is not None
            assert s is server

    @pytest.mark.asyncio
    async def test_search_azure_prices_basic(
        self, mock_aiohttp_session, sample_azure_prices_response
    ):
        """Test basic price search functionality."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        # Configure mock to return sample data
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_azure_prices_response)
        mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

        result = await server.search_azure_prices(service_name="Virtual Machines", region="eastus")

        assert result is not None
        assert "items" in result
        assert "count" in result
        assert result["count"] == 1
        assert len(result["items"]) == 1

    @pytest.mark.asyncio
    async def test_search_with_filters(self, mock_aiohttp_session, sample_azure_prices_response):
        """Test search with multiple filters."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_azure_prices_response)
        mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

        result = await server.search_azure_prices(
            service_name="Virtual Machines",
            region="eastus",
            sku_name="D2s v3",
            price_type="Consumption",
        )

        assert result is not None
        assert result["count"] >= 0

    @pytest.mark.asyncio
    async def test_search_empty_results(self, mock_aiohttp_session):
        """Test search with no results."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={"Items": [], "Count": 0, "NextPageLink": None})
        mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

        result = await server.search_azure_prices(service_name="NonExistent")

        assert result is not None
        assert result["count"] == 0
        assert len(result["items"]) == 0

    @pytest.mark.asyncio
    async def test_compare_prices(self, mock_aiohttp_session, sample_azure_prices_response):
        """Test price comparison across regions."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_azure_prices_response)
        mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

        result = await server.compare_prices(
            service_name="Virtual Machines", sku_name="D2s v3", regions=["eastus", "westus"]
        )

        assert result is not None
        assert "comparisons" in result

    @pytest.mark.asyncio
    async def test_estimate_costs(self, mock_aiohttp_session, sample_azure_prices_response):
        """Test cost estimation functionality."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_azure_prices_response)
        mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

        result = await server.estimate_costs(
            service_name="Virtual Machines", sku_name="D2s v3", region="eastus", hours_per_month=730
        )

        assert result is not None
        assert "on_demand_pricing" in result
        assert "monthly_cost" in result["on_demand_pricing"]

    @pytest.mark.asyncio
    async def test_discover_skus(self, mock_aiohttp_session, sample_azure_prices_response):
        """Test SKU discovery functionality."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value=sample_azure_prices_response)
        mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

        result = await server.discover_skus(service_name="Virtual Machines", region="eastus")

        assert result is not None
        assert "skus" in result

    @pytest.mark.asyncio
    async def test_error_handling_network_error(self, mock_aiohttp_session):
        """Test error handling for network failures."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        # Configure mock to raise an exception
        mock_aiohttp_session.get.side_effect = Exception("Network error")

        with pytest.raises(Exception) as exc_info:
            await server.search_azure_prices(service_name="Virtual Machines")

        assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_error_handling_api_error(self, mock_aiohttp_session):
        """Test error handling for API errors."""
        server = AzurePricingServer()
        server.session = mock_aiohttp_session

        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        mock_response.raise_for_status = AsyncMock(side_effect=Exception("API Error"))
        mock_aiohttp_session.get.return_value.__aenter__.return_value = mock_response

        # The server should handle this gracefully or raise
        with pytest.raises(Exception):
            await server.search_azure_prices(service_name="Virtual Machines")
