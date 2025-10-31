"""Pytest configuration and fixtures for Azure Pricing MCP Server tests."""

import pytest
from typing import Dict, Any, List


@pytest.fixture
def mock_vm_pricing_response() -> Dict[str, Any]:
    """Mock Azure API response for VM pricing."""
    return {
        "BillingCurrency": "USD",
        "CustomerEntityId": "",
        "CustomerEntityType": "",
        "Items": [
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.096,
                "unitPrice": 0.096,
                "armRegionName": "eastus",
                "location": "US East",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "test-meter-id-1",
                "meterName": "D2s v3",
                "productId": "test-product-id",
                "skuId": "test-sku-id",
                "productName": "Virtual Machines Dv3 Series",
                "skuName": "D2s v3",
                "serviceName": "Virtual Machines",
                "serviceId": "test-service-id",
                "serviceFamily": "Compute",
                "unitOfMeasure": "1 Hour",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": "Standard_D2s_v3",
                "savingsPlan": [
                    {
                        "term": "1 Year",
                        "retailPrice": 0.0672
                    },
                    {
                        "term": "3 Years",
                        "retailPrice": 0.0528
                    }
                ]
            },
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.192,
                "unitPrice": 0.192,
                "armRegionName": "eastus",
                "location": "US East",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "test-meter-id-2",
                "meterName": "D4s v3",
                "productId": "test-product-id-2",
                "skuId": "test-sku-id-2",
                "productName": "Virtual Machines Dv3 Series",
                "skuName": "D4s v3",
                "serviceName": "Virtual Machines",
                "serviceId": "test-service-id",
                "serviceFamily": "Compute",
                "unitOfMeasure": "1 Hour",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": "Standard_D4s_v3"
            }
        ],
        "NextPageLink": None,
        "Count": 2
    }


@pytest.fixture
def mock_storage_pricing_response() -> Dict[str, Any]:
    """Mock Azure API response for Storage pricing."""
    return {
        "BillingCurrency": "USD",
        "CustomerEntityId": "",
        "CustomerEntityType": "",
        "Items": [
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.18,
                "unitPrice": 0.18,
                "armRegionName": "eastus",
                "location": "US East",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "test-storage-meter-id",
                "meterName": "LRS Data Stored",
                "productId": "test-storage-product-id",
                "skuId": "test-storage-sku-id",
                "productName": "Storage - Block Blob",
                "skuName": "Standard LRS",
                "serviceName": "Storage",
                "serviceId": "test-storage-service-id",
                "serviceFamily": "Storage",
                "unitOfMeasure": "1 GB/Month",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": ""
            }
        ],
        "NextPageLink": None,
        "Count": 1
    }


@pytest.fixture
def mock_empty_response() -> Dict[str, Any]:
    """Mock empty Azure API response."""
    return {
        "BillingCurrency": "USD",
        "CustomerEntityId": "",
        "CustomerEntityType": "",
        "Items": [],
        "NextPageLink": None,
        "Count": 0
    }


@pytest.fixture
def mock_paginated_response() -> Dict[str, Any]:
    """Mock Azure API response with pagination."""
    return {
        "BillingCurrency": "USD",
        "CustomerEntityId": "",
        "CustomerEntityType": "",
        "Items": [
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.096,
                "unitPrice": 0.096,
                "armRegionName": "eastus",
                "location": "US East",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "test-meter-id",
                "meterName": "Test VM",
                "productId": "test-product-id",
                "skuId": "test-sku-id",
                "productName": "Virtual Machines",
                "skuName": "Standard_Test",
                "serviceName": "Virtual Machines",
                "serviceId": "test-service-id",
                "serviceFamily": "Compute",
                "unitOfMeasure": "1 Hour",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": "Standard_Test"
            }
        ],
        "NextPageLink": "https://prices.azure.com/api/retail/prices?$skip=100",
        "Count": 1
    }


@pytest.fixture
def mock_multi_region_response() -> Dict[str, Any]:
    """Mock Azure API response with multiple regions."""
    return {
        "BillingCurrency": "USD",
        "CustomerEntityId": "",
        "CustomerEntityType": "",
        "Items": [
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.096,
                "unitPrice": 0.096,
                "armRegionName": "eastus",
                "location": "US East",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "test-meter-id-1",
                "meterName": "D2s v3",
                "productId": "test-product-id",
                "skuId": "test-sku-id",
                "productName": "Virtual Machines Dv3 Series",
                "skuName": "D2s v3",
                "serviceName": "Virtual Machines",
                "serviceId": "test-service-id",
                "serviceFamily": "Compute",
                "unitOfMeasure": "1 Hour",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": "Standard_D2s_v3"
            },
            {
                "currencyCode": "USD",
                "tierMinimumUnits": 0.0,
                "retailPrice": 0.108,
                "unitPrice": 0.108,
                "armRegionName": "westeurope",
                "location": "West Europe",
                "effectiveStartDate": "2023-01-01T00:00:00Z",
                "meterId": "test-meter-id-2",
                "meterName": "D2s v3",
                "productId": "test-product-id",
                "skuId": "test-sku-id",
                "productName": "Virtual Machines Dv3 Series",
                "skuName": "D2s v3",
                "serviceName": "Virtual Machines",
                "serviceId": "test-service-id",
                "serviceFamily": "Compute",
                "unitOfMeasure": "1 Hour",
                "type": "Consumption",
                "isPrimaryMeterRegion": True,
                "armSkuName": "Standard_D2s_v3"
            }
        ],
        "NextPageLink": None,
        "Count": 2
    }
