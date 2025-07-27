# Consumer Packaged Goods (CPG) Insights Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Consumer Packaged Goods (CPG) data from a custom API and load it into Snowflake via Fivetran, powering advanced consumer insights and product analytics applications. For lab day instructions see the **[cpg-lab-guide.md](../cpg-lab-guide.md)**.

## Overview

The CPG Insights connector fetches consumer packaged goods records from a REST API and loads them into a single table called `cpg_records` in your Snowflake database. The connector retrieves detailed information about customer segments, product categories, inventory levels, price optimization, and customer satisfaction metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## CPG API Details

### Endpoint

The connector uses the following REST API endpoint to access consumer packaged goods data:

- `GET /cpg_data`: Retrieves a paginated list of CPG records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

### Data Schema

The CPG API returns records with the following structure (partial list):

| Field                          | Type    | Description                                      |
|-------------------------------|---------|--------------------------------------------------|
| `record_id`                   | string  | Unique identifier for the record (primary key)   |
| `order_id`                    | string  | Unique identifier for the order                  |
| `customer_id`                 | string  | Unique identifier for the customer               |
| `product_id`                  | string  | Unique identifier for the product                |
| `order_date`                  | date    | Date of the order (YYYY-MM-DD)                   |
| `order_total`                 | float   | Total value of the order                         |
| `product_price`               | float   | Price of the product                             |
| `inventory_level`             | integer | Current inventory level of the product           |
| `customer_segment`            | string  | Segment of the customer (e.g., Low-Value, High-Value) |
| `order_status`                | string  | Current status of the order                      |
| `product_category`            | string  | Category of the product (e.g., Beauty, Electronics) |
| `product_subcategory`         | string  | Subcategory of the product                       |
| `customer_ltv`                | float   | Lifetime value of the customer                   |
| `order_frequency`             | integer | Number of orders placed by the customer          |
| `average_order_value`         | float   | Average value of the customer's orders           |
| `product_rating`              | float   | Rating of the product                            |
| `product_review_count`        | integer | Number of reviews for the product                |
| `price_optimization_flag`     | boolean | Flag indicating if price optimization was applied |
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
    "customer_ltv": 4404.31,
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

## Downstream Application: InsightEdge

The data extracted by this connector powers InsightEdge, an AI-driven consumer insights generation system designed for CPG companies. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in the consumer packaged goods industry.

### Application Purpose

InsightEdge helps CPG companies:
- Transform large datasets into actionable consumer insights
- Identify emerging trends early to inform product development
- Improve customer satisfaction through real-time analysis
- Optimize pricing strategies based on consumer data
- Make data-driven decisions in marketing and sales

### Target Users

- Product Development Teams
- Marketing Managers
- Sales Analytics Teams
- Category Managers
- Consumer Insights Specialists
- Executive Leadership

### Data Flow Architecture

1. **Data Sources** → 2. **CPG API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated CPG Data Sources

The CPG API provides synthetic data that simulates information from various consumer insights systems:

- **Customer Feedback**:
  - Medallia
  - Qualtrics
  - SurveyMonkey
- **Market Research**:
  - Nielsen
  - Euromonitor
- **Social Media**:
  - Twitter
  - Facebook
  - Instagram

This approach allows for realistic CPG analytics without using protected consumer information, making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The InsightEdge application provides:
- Key performance metrics including customer satisfaction, revenue growth, product ratings, and inventory metrics
- Segment and category analysis showing customer segment distribution and product category breakdown
- Price optimization analysis displaying results and recommendations
- Satisfaction vs growth quadrant analysis mapping products by satisfaction and growth rates
- Inventory and order analysis monitoring turnover, overstock rates, and fulfillment
- AI-powered insights generating comprehensive analysis, optimization opportunities, financial impact, and strategic recommendations
- Data exploration tools for detailed record examination

### Benefits

The application delivers significant business value:
- 12% increase in product sales: $1,200,000 additional sales/year
- 10% reduction in product development costs: $500,000 savings/year
- 15% improvement in customer satisfaction: 12% increase in satisfied customers
- 10% reduction in marketing costs: $200,000 savings/year

## Notes

- This connector creates a single table named `cpg_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The CPG API returns approximately 750 consumer packaged goods records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the InsightEdge consumer insights application
- While this connector uses synthetic data, the approach mirrors real-world CPG data extraction patterns
