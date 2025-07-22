# Consumer Packaged Goods (CPG) Insights Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Consumer Packaged Goods (CPG) data from an API and load it into Snowflake via Fivetran, powering advanced consumer insights and product analytics applications.

## Overview

The CPG Insights connector fetches consumer packaged goods records from a REST API and loads them into a single table called `cpg_records` in your Snowflake database. The connector retrieves detailed information about customer segments, product categories, inventory levels, price optimization, and customer satisfaction metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the CPG data
- **Data enrichment**: Extracts over 25 metrics and attributes related to consumer products
- **Efficient processing**: Handles large datasets (750+ records) with minimal resource usage
- **CPG-specific**: Designed to handle consumer packaged goods data common in retail operations

## Project Structure

```
cpg/
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
| `api_key`    | API key for authentication to the CPG API              | Required                                                  |
| `base_url`   | Base URL for the CPG API                               | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## CPG API Details

### Endpoint

The connector uses the following REST API endpoint to access consumer packaged goods data:

- `GET /cpg_data`: Retrieves a paginated list of CPG records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

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

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `cpg_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "cpg_records",
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
   mkdir cpg && cd cpg
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
✓ Detected table name: cpg_records
===========================================================
         Fivetran Connector Debug & Reset Script          
===========================================================

This will reset your connector, delete current state and warehouse.db files.
Do you want to continue? (Y/n): y

Step 1: Resetting Fivetran connector...
✓ Reset successful

Step 2: Running debug with configuration...
(Real-time output will be displayed below)

May 18, 2025 08:21:40 AM INFO Fivetran-Connector-SDK: Debugging connector at: /path/to/connector
May 18, 2025 08:21:40 AM INFO Fivetran-Connector-SDK: Running connector tester...
May 18, 2025 08:21:43 AM INFO Fivetran-Connector-SDK: Initiating the 'schema' method call...
May 18, 2025 08:21:43 AM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.cpg_records 
May 18, 2025 08:21:43 AM INFO Fivetran-Connector-SDK: Initiating the 'update' method call...

May 18, 2025 08:21:43 AM INFO: Fetching data with params: {'page_size': 100}
May 18, 2025 08:21:43 AM INFO: Checkpoint saved after 100 records
May 18, 2025 08:21:43 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': 'd18af5766518903a85e4a5da6aaff8da'}
...
May 18, 2025 08:21:43 AM INFO: Checkpoint saved after 700 records
May 18, 2025 08:21:43 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': '83e273d3e68754534f3548d024c07452'}
May 18, 2025 08:21:43 AM INFO: No more pages to fetch

✓ Debug completed

Step 3: Querying sample data from DuckDB...
Running query: SELECT * FROM tester.cpg_records LIMIT 5;

┌──────────────────────┬───────────────┬────────────────────┬───────────────────┬───┬─────────────────┬──────────────┬──────────────────┬────────────────┐
│      record_id       │ stockout_rate │ inventory_turnover │ _fivetran_deleted │ … │   customer_id   │   order_id   │ product_category │ product_rating │
│       varchar        │     float     │       float        │      boolean      │   │     varchar     │   varchar    │     varchar      │     float      │
├──────────────────────┼───────────────┼────────────────────┼───────────────────┼───┼─────────────────┼──────────────┼──────────────────┼────────────────┤
│ 2f06d249-1391-4079…  │    0.07934512 │           6.742079 │ false             │ … │ CUSTOMER_000000 │ ORDER_000000 │ Beauty           │      1.1266253 │
│ eb598398-591f-49bb…  │   0.035458054 │          7.8101616 │ false             │ … │ CUSTOMER_000001 │ ORDER_000001 │ Apparel          │      2.1695437 │
│ 7bbc65a8-0d65-43df…  │    0.06316803 │           9.974329 │ false             │ … │ CUSTOMER_000002 │ ORDER_000002 │ Beauty           │      2.6974366 │
│ 3c03dcca-ebee-443c…  │    0.04502107 │          7.9158206 │ false             │ … │ CUSTOMER_000003 │ ORDER_000003 │ Electronics      │      1.7124845 │
│ 90910b97-fbd3-4c60…  │    0.06984392 │          4.7447762 │ false             │ … │ CUSTOMER_000004 │ ORDER_000004 │ Electronics      │      3.2076395 │
└──────────────────────┴───────────────┴────────────────────┴───────────────────┴───┴─────────────────┴──────────────┴──────────────────┴────────────────┘

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
Next sync state: {"next_cursor": "83e273d3e68754534f3548d024c07452"}
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
   - A unique name for your connector (e.g., cpg_new_custom_connector)

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
The connection 'cpg_new_custom_connector' has been created successfully.
Python Version: 3.12.8
Connection ID: broadband_contention
Visit the Fivetran dashboard to start the initial sync: https://fivetran.com/dashboard/connectors/broadband_contention/status
```

### What to Expect After Deployment

After successful deployment:

1. The connector will be created in your Fivetran account with a randomly generated Connection ID (e.g., `broadband_contention`)
2. You'll be provided a link to access the connector in the Fivetran dashboard
3. The connector will be ready for its initial sync

In the Fivetran dashboard, you will be able to:
- View your connector's sync status
- Configure sync frequency (hourly, daily, etc.)
- Monitor for any errors or warnings
- View the destination schema with the `cpg_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the CPG API endpoint
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

1. If the CPG API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       record['profit_margin'] = (record['product_price'] - (record['product_price'] * 0.7)) / record['product_price'] if record['product_price'] > 0 else 0
       yield op.upsert("cpg_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "cpg_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "cpg_products",
               "primary_key": ["product_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating product records from CPG data
   product_records = {}
   for record in records:
       # Extract product info for separate table
       product_id = record['product_id']
       if product_id not in product_records:
           product_records[product_id] = {
               'product_id': product_id,
               'product_category': record['product_category'],
               'product_subcategory': record['product_subcategory'],
               'product_price': record['product_price'],
               'product_rating': record['product_rating'],
               'product_review_count': record['product_review_count']
           }
       # Yield the original record
       yield op.upsert("cpg_records", record)
   
   # Yield all unique product records
   for product in product_records.values():
       yield op.upsert("cpg_products", product)
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
