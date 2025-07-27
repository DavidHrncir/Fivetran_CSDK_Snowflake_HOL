# Retail Dynamic Pricing RDP Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Retail Dynamic Pricing (RDP) data from a custom API and load it into Snowflake via Fivetran, powering advanced retail analytics and dynamic pricing applications. For lab day instructions see the **[rdp-lab-guide.md](../rdp-lab-guide.md)**.

## Overview

The Retail Dynamic Pricing connector fetches pricing, inventory, and product performance data from a REST API and loads it into a single table called `rdp_records` in your Snowflake database. The connector retrieves detailed information about product pricing, inventory levels, customer segments, order status, price elasticity, and optimization metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## RDP API Details

### Endpoint

The connector uses the following REST API endpoint to access retail dynamic pricing data:

- `GET /rdp_data`: Retrieves a paginated list of Retail Dynamic Pricing records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

### Data Schema

The RDP API returns records with the following structure (partial list):

| Field                         | Type    | Description                                      |
|-------------------------------|---------|--------------------------------------------------|
| `record_id`                   | string  | Unique identifier for the record (primary key)   |
| `order_id`                    | string  | Unique identifier for the order                  |
| `customer_id`                 | string  | Unique identifier for the customer               |
| `product_id`                  | string  | Unique identifier for the product                |
| `order_date`                  | date    | Date when the order was placed                   |
| `order_total`                 | float   | Total value of the order                         |
| `product_price`               | float   | Price of the product                             |
| `inventory_level`             | integer | Current inventory level of the product           |
| `customer_segment`            | string  | Segment the customer belongs to                  |
| `order_status`                | string  | Current status of the order                      |
| `product_category`            | string  | Category of the product                          |
| `product_subcategory`         | string  | Subcategory of the product                       |
| `customer_lifetime_value`     | float   | Lifetime value of the customer                   |
| `order_frequency`             | integer | Number of orders placed by the customer          |
| `average_order_value`         | float   | Average value of the customer's orders           |
| `product_rating`              | float   | Rating of the product                            |
| `product_review_count`        | integer | Number of reviews for the product                |
| `price_optimization_flag`     | boolean | Flag indicating if price optimization was applied|
| `price_elasticity`            | float   | Price elasticity of the product                  |
| `demand_forecast`             | integer | Forecasted demand for the product                |
| `inventory_turnover`          | float   | Rate at which inventory is sold and replaced     |
| `stockout_rate`               | float   | Rate of stockouts for the product                |
| `overstock_rate`              | float   | Rate of overstock for the product                |
| `revenue_growth_rate`         | float   | Rate of revenue growth                           |
| `customer_satisfaction_rate`  | float   | Rate of customer satisfaction                    |
| `price_optimization_date`     | date    | Date of the last price optimization              |
| `price_optimization_result`   | string  | Result of the price optimization                 |
| `price_optimization_recommendation` | string | Recommendation from the price optimization  |
| `last_updated_epoch`               | number  | Epoch value for the last updated date in epoch form |

### Sample Record
```bash
{
    "average_order_value": 295.83,
    "customer_id": "CUSTOMER_000000",
    "customer_lifetime_value": 4404.31,
    "customer_satisfaction_rate": 0.7399786595,
    "customer_segment": "Medium-Value",
    "demand_forecast": 14,
    "inventory_level": 294,
    "inventory_turnover": 6.7420788752,
    "last_updated_epoch": 1748797200,
    "order_date": "2024-09-01",
    "order_frequency": 2,
    "order_id": "ORDER_000000",
    "order_status": "Shipped",
    "order_total": 495.47,
    "overstock_rate": 0.0470208128,
    "price_elasticity": 0.9547121322,
    "price_optimization_date": "2024-11-17",
    "price_optimization_flag": false,
    "price_optimization_recommendation": "Increase Price",
    "price_optimization_result": "Failure",
    "product_category": "Beauty",
    "product_id": "PRODUCT_000000",
    "product_price": 996.06,
    "product_rating": 1.1266253446,
    "product_review_count": 74,
    "product_subcategory": "Laptops",
    "record_id": "2f06d249-1391-4079-8726-7d2862911ff4",
    "revenue_growth_rate": 0.0353156353,
    "stockout_rate": 0.0793451208
}
```

## Downstream Application: PricePulse

The data extracted by this connector powers PricePulse, an AI-driven dynamic pricing system designed for retailers. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in the retail industry.

### Application Purpose

PricePulse helps retailers:
- Optimize product pricing in real-time based on multiple factors
- Predict future demand to adjust inventory levels
- Reduce stockouts and overstocking
- Analyze customer segments and purchasing patterns
- Transform retail pricing into a data-driven process

### Target Users

- Retail Pricing Managers
- Inventory Managers
- Marketing Teams
- Product Managers
- Category Managers

### Data Flow Architecture

1. **Data Sources** → 2. **RDP API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Retail Data Sources

The RDP API provides synthetic data that simulates information from various retail systems:

- **Point of Sale (POS)**: 
  - Shopify
  - Square
  - Lightspeed
- **Customer Relationship Management (CRM)**: 
  - Salesforce
  - HubSpot
  - Zoho
- **Inventory Management**: 
  - Manhattan Associates
  - Oracle Retail
  - JDA Software

This approach allows for realistic retail analytics without using protected customer information, making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The PricePulse application provides:
- Key performance metrics including revenue growth, stockout rates, and overstock rates
- Pricing performance metrics including product prices, order values, and price elasticity
- Distribution analysis for price optimization results and customer segments
- Product category and subcategory analysis
- AI-powered insights for overall performance, optimization opportunities, financial impact, and strategic recommendations
- Data exploration tools for detailed record examination

### Benefits

The application delivers significant business value:
- 8% increase in revenue: $800,000 additional revenue/year
- 12% reduction in overstocking: $60,000 savings/year
- 10% decrease in stockouts: $20,000 savings/year
- 5% improvement in customer satisfaction: 4% increase in customer retention

## Notes

- This connector creates a single table named `rdp_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector uses cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The RDP API returns approximately 750 retail dynamic pricing records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the PricePulse dynamic pricing application
- While this connector uses synthetic data, the approach mirrors real-world retail data extraction patterns
