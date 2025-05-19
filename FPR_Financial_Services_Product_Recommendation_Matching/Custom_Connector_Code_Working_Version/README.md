# Financial Services FPR Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Financial Services Product Recommendation (FPR) data from an API and load it into Snowflake via Fivetran, powering advanced financial product matching and recommendation analytics applications.

## Overview

The Financial Services FPR connector fetches product recommendation and matching records from a REST API and loads them into a single table called `fpr_records` in your Snowflake database. The connector retrieves detailed information about customer profiles, account balances, transaction data, product affinities, recommendations, and customer satisfaction metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the FPR data
- **Data enrichment**: Extracts over 30 metrics and attributes related to financial product matching
- **Efficient processing**: Handles large datasets (750+ records) with minimal resource usage
- **Finance-specific**: Designed to handle financial product recommendation data common in retail banking operations

## Project Structure

```
fpr/
├── configuration.json     # Configuration parameters for the connector
├── connector.py           # Main connector implementation
├── debug_and_reset.sh     # Script for testing and resetting the connector
├── deploy.sh              # Script for deploying the connector to Fivetran
└── requirements.txt       # Python dependencies (if any)
```

## Configuration Parameters

The connector uses the following configuration parameters:

| Parameter    | Description                                            | Default Value                                             |
|--------------|--------------------------------------------------------|-----------------------------------------------------------|
| `api_key`    | API key for authentication to the FPR API              | Required                                                  |
| `base_url`   | Base URL for the FPR API                               | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## FPR API Details

### Endpoint

The connector uses the following REST API endpoint to access financial product recommendation data:

- `GET /fpr_data`: Retrieves a paginated list of Financial Product Recommendation records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

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

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `fpr_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "fpr_records",
            "primary_key": ["record_id"]
        }
    ]
```

### Data Extraction

The connector follows a structured approach to extract data:

1. **Configuration validation**: Retrieves and validates the API key, base URL and page size
2. **Session setup**: Creates an authenticated session with the API key in the header
3. **State management**: Loads previous sync state to determine where to resume from
4. **Pagination handling**: Implements cursor-based pagination to fetch data in batches
5. **Data processing**: Yields upsert operations for each record to be loaded into Fivetran
6. **Checkpoint creation**: Saves checkpoints after every 100 records to ensure reliability
7. **Error handling**: Catches and logs API exceptions and unexpected errors

The connector uses this workflow to efficiently process large datasets while maintaining resiliency against failures.

## Setup and Usage

### Prerequisites

1. Python 3.7+ installed
2. The Fivetran Connector SDK installed:
   ```bash
   pip install fivetran-connector-sdk
   ```
3. DuckDB command-line tool (optional, for viewing debug output)
4. Basic understanding of the Fivetran platform

### Local Development and Testing

1. Clone or create the project directory:
   ```bash
   mkdir fpr && cd fpr
   ```

2. Create the required files:
   - `configuration.json`: Configure your API credentials and settings
   - `connector.py`: Implement the connector using the Fivetran SDK
   - `debug_and_reset.sh`: Script for testing
   - `deploy.sh`: Script for deployment

3. Make the scripts executable and run the debug script:
   ```bash
   chmod +x debug_and_reset.sh
   ./debug_and_reset.sh
   ```

   This will:
   - Reset the connector state
   - Run the connector in debug mode
   - Display sample data from the extracted records
   - Show operation statistics

### Debug Script Details

The `debug_and_reset.sh` script includes the following steps:

1. **Validation**: Checks for required files and extracts the table name
2. **Reset**: Clears previous state and data using `fivetran reset`
3. **Debug**: Runs the connector in debug mode with the specified configuration
4. **Query**: Executes a sample query against the extracted data using DuckDB
5. **Summary**: Displays a summary of operations performed (upserts, checkpoints, etc.)

When you run the debug script, you'll see output similar to the following:

```
✓ Detected table name: fpr_records
===========================================================
         Fivetran Connector Debug & Reset Script          
===========================================================

This will reset your connector, delete current state and warehouse.db files.
Do you want to continue? (Y/n): y

Step 1: Resetting Fivetran connector...
✓ Reset successful

Step 2: Running debug with configuration...
(Real-time output will be displayed below)

May 17, 2025 01:36:13 PM INFO Fivetran-Connector-SDK: Debugging connector at: /path/to/connector
May 17, 2025 01:36:14 PM INFO Fivetran-Connector-SDK: Running connector tester...
May 17, 2025 01:36:17 PM INFO Fivetran-Connector-SDK: Initiating the 'schema' method call...
May 17, 2025 01:36:17 PM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.fpr_records 
May 17, 2025 01:36:17 PM INFO Fivetran-Connector-SDK: Initiating the 'update' method call...

May 17, 2025 01:36:17 PM INFO: Fetching data with params: {'page_size': 100}
May 17, 2025 01:36:17 PM INFO: Checkpoint saved after 100 records
May 17, 2025 01:36:17 PM INFO: Fetching data with params: {'page_size': 100, 'cursor': '081081de25a9dab3767f1cdf063faef6'}
...
May 17, 2025 01:36:17 PM INFO: Checkpoint saved after 700 records
May 17, 2025 01:36:17 PM INFO: Fetching data with params: {'page_size': 100, 'cursor': 'ef07e7c8d1916a346f4228db8233150b'}
May 17, 2025 01:36:17 PM INFO: No more pages to fetch

✓ Debug completed

Step 3: Querying sample data from DuckDB...
Running query: SELECT * FROM tester.fpr_records LIMIT 5;

┌──────────────────────┬──────────────────────┬─────────────────┬──────────────────────┬───┬──────────────────────┬───────────────┬─────────────┐
│      record_id       │ customer_transacti…  │ account_balance │ customer_product_a…  │ … │ customer_lifecycle…  │ customer_name │ customer_id │
│       varchar        │        float         │      float      │        float         │   │       varchar        │    varchar    │   varchar   │
├──────────────────────┼──────────────────────┼─────────────────┼──────────────────────┼───┼──────────────────────┼───────────────┼─────────────┤
│ 23f99867-3171-4769…  │            1257.2906 │       38079.473 │           0.49646115 │ … │ 2024-07-27           │ Customer 1    │ CUST_000000 │
│ 430d3780-36c4-4db2…  │             9404.338 │        95120.72 │            0.4368507 │ … │ 2024-12-21           │ Customer 2    │ CUST_000001 │
│ b36b10d4-ce5a-4f8d…  │            6314.3096 │         73467.4 │            0.7295082 │ … │ 2024-07-06           │ Customer 3    │ CUST_000002 │
│ 352abb48-1f9a-4284…  │            3415.5657 │        60267.19 │            0.7655129 │ … │ 2024-10-10           │ Customer 4    │ CUST_000003 │
│ fcc56e12-6cbe-4c2d…  │            1478.7936 │       16445.846 │           0.15890817 │ … │ 2024-09-04           │ Customer 5    │ CUST_000004 │
└──────────────────────┴──────────────────────┴─────────────────┴──────────────────────┴───┴──────────────────────┴───────────────┴─────────────┘

==================== OPERATION SUMMARY ====================
  Operation       | Calls     
  ----------------+------------
  Upserts         | 750       
  Updates         | 0         
  Deletes         | 0         
  Truncates       | 0         
  SchemaChanges   | 1         
  Checkpoints     | 7         
====================================================================

✓ Debug and reset operations completed.
Next sync state: {"next_cursor": "ef07e7c8d1916a346f4228db8233150b"}
```

In this output, you can observe:

1. **Initial Setup**: The script detects the table name automatically from your connector code
2. **Reset Process**: Confirms reset was successful after user confirmation
3. **Debug Logging**: Detailed logs of the SDK initializing and making method calls
4. **Data Fetching**: Shows each API request with pagination parameters:
   - Starting with no cursor (first page)
   - Continuing with cursors for subsequent pages
   - Creating checkpoints after every 100 records
   - Terminating when no more pages are available
5. **Sample Data**: Displays the first 5 records from the extracted dataset to verify content
6. **Operation Summary**: Shows that 750 records were processed through:
   - 750 upsert operations
   - 1 schema change
   - 7 checkpoint operations (one per page of 100 records)
7. **Final State**: The cursor value that will be used in the next sync to retrieve only new records

### Deploying to Fivetran

1. Ensure you have a Fivetran account and destination configured

2. Make the deploy script executable and run it:
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. When prompted, enter:
   - Your Fivetran account name (default: MDS_SNOWFLAKE_HOL)
   - Your Fivetran destination name (default: NEW_SALES_ENG_HANDS_ON_LAB)
   - A unique name for your connector (e.g., fpr_new_custom_connector)

4. The script will package and upload your connector to Fivetran

### Deploy Script Details

The `deploy.sh` script performs the following actions:

1. **Configuration Check**: Validates that the necessary configuration files are present
2. **Account Information**: Prompts for Fivetran account details and retrieves API key
3. **Deployment**: Packages and uploads the connector to your Fivetran account
4. **Confirmation**: Displays the connector ID and a link to access it in the Fivetran dashboard

Sample output from a successful deployment:
```
Deploying connector...
✓ Packaging your project for upload...
✓ Uploading your project...
The connection 'fpr_new_custom_connector' has been created successfully.
Python Version: 3.12.8
Connection ID: weathering_thrilled
Visit the Fivetran dashboard to start the initial sync: https://fivetran.com/dashboard/connectors/weathering_thrilled/status
```

### What to Expect After Deployment

After successful deployment:

1. The connector will be created in your Fivetran account with a randomly generated Connection ID (e.g., `weathering_thrilled`)
2. You'll be provided a link to access the connector in the Fivetran dashboard
3. The connector will be ready for its initial sync

In the Fivetran dashboard, you will be able to:
- View your connector's sync status
- Configure sync frequency (hourly, daily, etc.)
- Monitor for any errors or warnings
- View the destination schema with the `fpr_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the FPR API endpoint
- **Schema Changes**: If the API changes its schema, you may need to update the connector
- **Cursor Issues**: If the cursor becomes invalid, reset the connector to perform a full sync
- **Memory Limitations**: For very large datasets, consider decreasing the page size

### Monitoring

- Check the Fivetran dashboard for sync status and errors
- Review logs in the Fivetran dashboard for detailed error information
- Use the debug script locally to test changes before deployment
- Monitor the timestamps of the most recent records to ensure data freshness

### Debug and Reset

If you encounter issues with the connector, you can use the debug_and_reset.sh script to:

1. Reset the connector state (start fresh)
2. Run in debug mode to see detailed logs
3. Inspect the sample data to verify correct data extraction
4. Check operation statistics to ensure proper functioning

The script outputs detailed information that can help diagnose issues:
- API request parameters and response details
- Error messages and stack traces
- Operation counts (upserts, updates, deletes, etc.)
- Checkpoint state information

## Advanced Customization

To extend or modify this connector:

### Adding New Fields

1. If the FPR API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       record['product_affinity_score'] = record['customer_product_affinity'] * record['recommendation_score'] if record['recommendation_score'] > 0 else 0
       yield op.upsert("fpr_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "fpr_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "fpr_customers",
               "primary_key": ["customer_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating customer records from FPR data
   customer_records = {}
   for record in records:
       # Extract customer info for separate table
       customer_id = record['customer_id']
       if customer_id not in customer_records:
           customer_records[customer_id] = {
               'customer_id': customer_id,
               'customer_name': record['customer_name'],
               'customer_email': record['customer_email'],
               'customer_segment': record['customer_segment']
           }
       # Yield the original record
       yield op.upsert("fpr_records", record)
   
   # Yield all unique customer records
   for customer in customer_records.values():
       yield op.upsert("fpr_customers", customer)
   ```

### Dependencies Management

To add external dependencies:

1. Create a `requirements.txt` file in your project directory
2. Add your dependencies, for example:
   ```
   requests>=2.25.0
   python-dateutil>=2.8.1
   ```
3. The Fivetran deployment process will automatically install these dependencies in the connector environment

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
