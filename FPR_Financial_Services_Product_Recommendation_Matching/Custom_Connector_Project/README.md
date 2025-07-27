# Financial Services FPR Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Financial Services Product Recommendation (FPR) data from a custom API and load it into Snowflake via Fivetran, powering advanced financial product matching and recommendation analytics applications. For lab day instructions see the **[fpr-lab-guide.md](../fpr-lab-guide.md)**.

## Overview

The Financial Services FPR connector fetches product recommendation and matching records from a REST API and loads them into a single table called `fpr_records` in your Snowflake database. The connector retrieves detailed information about customer profiles, account balances, transaction data, product affinities, recommendations, and customer satisfaction metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## FPR API Details

### Endpoint

The connector uses the following REST API endpoint to access financial product recommendation data:

- `GET /fpr_data`: Retrieves a paginated list of Financial Product Recommendation records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

### Data Schema

The FPR API returns records with the following structure (partial list):

| Field                                 | Type    | Description                                      |
|--------------------------------------|---------|--------------------------------------------------|
| `record_id`                          | string  | Unique identifier for the record (primary key)   |
| `customer_id`                        | string  | Unique identifier for the customer               |
| `customer_name`                      | string  | Name of the customer                             |
| `customer_email`                     | string  | Email address of the customer                    |
| `customer_segment`                   | string  | Customer segment (e.g., Commercial, Retail)      |
| `customer_lifecycle_stage`           | string  | Current stage of the customer lifecycle          |
| `customer_lifecycle_stage_transition_date` | date | Date of the last lifecycle stage transition   |
| `account_balance`                    | float   | Current balance of the customer's account        |
| `transaction_history`                | string  | Summary of customer transaction history          |
| `customer_transaction_value`         | float   | Value of the customer's recent transactions      |
| `customer_transaction_count`         | integer | Number of recent transactions by the customer    |
| `product_id`                         | string  | Unique identifier for the product                |
| `product_name`                       | string  | Name of the product                              |
| `product_type`                       | string  | Type of the product (e.g., Loan, Credit Card)    |
| `product_terms`                      | string  | Terms and conditions of the product              |
| `product_sales_amount`               | float   | Amount for which the product was sold            |
| `product_sales_date`                 | date    | Date when the product was sold                   |
| `product_recommendation`             | string  | Recommended financial product                    |
| `product_recommendation_date`        | date    | Date when the product recommendation was made    |
| `product_recommendation_status`      | string  | Current status of the product recommendation     |
| `recommendation_score`               | float   | Score indicating the strength of the recommendation |
| `customer_product_usage`             | string  | How the customer uses the product                |
| `customer_product_affinity`          | float   | Measure of customer's preference for the product |
| `customer_product_affinity_trend`    | string  | Trend in customer's product affinity             |
| `customer_product_usage_trend`       | string  | Trend in customer's product usage                |
| `customer_product_interests`         | string  | Products the customer has shown interest in      |
| `customer_satisfaction_score`        | float   | Score indicating customer satisfaction           |
| `customer_churn_probability`         | float   | Probability of the customer leaving              |
| `last_updated_epoch`               | number  | Epoch value for the last updated date in epoch form |

### Sample Record
```bash
{
    "account_balance": 38079.4717658889,
    "customer_churn_probability": 0.7825001444,
    "customer_email": "customer1@example.com",
    "customer_id": "CUST_000000",
    "customer_lifecycle_stage": "Inactive",
    "customer_lifecycle_stage_transition_date": "2024-07-27",
    "customer_name": "Customer 1",
    "customer_product_affinity": 0.4964611524,
    "customer_product_affinity_trend": "Product Affinity Trend 1",
    "customer_product_interests": "Product Interest 1",
    "customer_product_usage": "Product Usage 1",
    "customer_product_usage_trend": "Product Usage Trend 1",
    "customer_satisfaction_score": 0.2465199056,
    "customer_segment": "Commercial",
    "customer_transaction_count": 48,
    "customer_transaction_value": 1257.2906030128,
    "last_updated_epoch": 1748797200,
    "product_id": "PROD_000000",
    "product_name": "Product 1",
    "product_recommendation": "Insurance",
    "product_recommendation_date": "2024-09-12",
    "product_recommendation_status": "Accepted",
    "product_sales_amount": 6152.2323619448,
    "product_sales_date": "2025-03-24",
    "product_terms": "No Collateral Required",
    "product_type": "Savings Account",
    "recommendation_score": 0.2741640377,
    "record_id": "23f99867-3171-4769-9ca3-36edeac4f0ac",
    "transaction_history": "Transaction History 1"
}
```

## Downstream Application: FinMatch

The data extracted by this connector powers FinMatch, an AI-driven financial product matching system designed for financial institutions. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in the financial services industry.

### Application Purpose

FinMatch helps financial institutions:
- Provide personalized product recommendations to their customers
- Increase product sales by targeting customers with relevant offerings
- Reduce customer churn through improved customer satisfaction
- Optimize customer lifecycle management
- Transform product marketing into a data-driven process

### Target Users

- Retail Banking Managers
- Product Managers
- Customer Experience Teams
- Marketing Analysts
- Financial Advisors

### Data Flow Architecture

1. **Data Sources** → 2. **FPR API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Financial Data Sources

The FPR API provides synthetic data that simulates information from various financial systems:

- **Core Banking Systems**: 
  - FIS
  - Fiserv
  - Temenos
- **Customer Relationship Management (CRM)**: 
  - Salesforce
  - HubSpot
  - Zoho
- **Customer Transaction Data**: 
  - Core banking systems
  - Transaction logs

This approach allows for realistic financial analytics without using protected customer information, making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The FinMatch application provides:
- Key performance metrics including recommendation scores, customer satisfaction, and product sales
- Financial metrics like transaction values, account balances, and transaction counts
- Distribution analysis for recommendation statuses and product affinities
- Customer lifecycle stage analysis
- AI-powered insights for overall performance, optimization opportunities, financial impact, and strategic recommendations
- Data exploration tools for detailed record examination

### Benefits

The application delivers significant business value:
- 10% increase in product sales: $1,000,000 additional sales/year
- 15% reduction in customer churn: 300 fewer churned customers/year
- 20% increase in customer satisfaction: 2,000 additional satisfied customers/year
- 5% increase in average revenue per user (ARPU): $5,000,000 additional revenue/year

## Notes

- This connector creates a single table named `fpr_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The FPR API returns approximately 750 financial product recommendation records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the FinMatch financial product recommendation application
- While this connector uses synthetic data, the approach mirrors real-world financial data extraction patterns
