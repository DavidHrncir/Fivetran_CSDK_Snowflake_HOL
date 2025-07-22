# Insurance ICP Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Insurance Claims Processing (ICP) data from an API and load it into Snowflake via Fivetran, powering advanced insurance analytics applications.

## Overview

The Insurance ICP connector fetches claims processing records from a REST API and loads them into a single table called `icp_records` in your Snowflake database. The connector retrieves detailed information about insurance claims processing, including properties like claim status, processing metrics, customer satisfaction data, and operational costs. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the ICP data
- **Data enrichment**: Extracts over 35 metrics and attributes related to insurance claims processing
- **Efficient processing**: Handles large datasets (750+ records) with minimal resource usage
- **Insurance-specific**: Designed to handle claims data common in insurance operations

## Project Structure

```
icp/
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
| `api_key`    | API key for authentication to the ICP API              | Required                                                  |
| `base_url`   | Base URL for the ICP API                               | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## ICP API Details

### Endpoint

The connector uses the following REST API endpoint to access insurance claims data:

- `GET /icp_data`: Retrieves a paginated list of Insurance Claims Processing records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

### Data Schema

The ICP API returns records with the following structure (partial list):

| Field                              | Type    | Description                                   |
|------------------------------------|---------|-----------------------------------------------|
| `record_id`                        | string  | Unique identifier for the record (primary key) |
| `claim_id`                         | string  | Unique identifier for the claim               |
| `policy_id`                        | string  | Unique identifier for the policy              |
| `customer_id`                      | string  | Unique identifier for the customer            |
| `customer_name`                    | string  | Name of the customer                          |
| `customer_email`                   | string  | Email address of the customer                 |
| `claim_type`                       | string  | Type of the insurance claim                   |
| `claim_category`                   | string  | Category of the claim                         |
| `claim_subcategory`                | string  | Subcategory of the claim                      |
| `claim_status`                     | string  | Current status of the claim                   |
| `claim_date`                       | date    | Date when the claim was filed                 |
| `claim_amount`                     | float   | Amount claimed                                |
| `claim_outcome`                    | string  | Final outcome of the claim                    |
| `claim_outcome_date`               | date    | Date when the claim outcome was decided       |
| `claim_processing_time`            | float   | Time taken to process the claim               |
| `claim_processing_duration`        | integer | Total duration of claim processing in days    |
| `claim_processing_start_date`      | date    | Date when claim processing started            |
| `claim_processing_end_date`        | date    | Date when claim processing ended              |
| `claim_processing_error`           | boolean | Indicates if there was an error during processing |
| `customer_satisfaction_rating`     | integer | Customer's satisfaction rating                |
| `operational_cost`                 | float   | Operational cost for processing the claim     |
| `claim_processing_time_reduction`  | float   | Reduction in claim processing time achieved   |
| `claim_processing_error_reduction` | float   | Reduction in claim processing errors          |
| `operational_cost_reduction`       | float   | Reduction in operational costs                |

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `icp_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "icp_records",
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
   mkdir icp && cd icp
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
✓ Detected table name: icp_records
===========================================================
         Fivetran Connector Debug & Reset Script          
===========================================================

This will reset your connector, delete current state and warehouse.db files.
Do you want to continue? (Y/n): y

Step 1: Resetting Fivetran connector...
✓ Reset successful

Step 2: Running debug with configuration...
(Real-time output will be displayed below)

May 17, 2025 01:22:28 PM INFO Fivetran-Connector-SDK: Debugging connector at: /path/to/connector
May 17, 2025 01:22:28 PM INFO Fivetran-Connector-SDK: Running connector tester...
May 17, 2025 01:22:31 PM INFO Fivetran-Connector-SDK: Initiating the 'schema' method call...
May 17, 2025 01:22:31 PM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.icp_records 
May 17, 2025 01:22:31 PM INFO Fivetran-Connector-SDK: Initiating the 'update' method call...

May 17, 2025 01:22:31 PM INFO: Fetching data with params: {'page_size': 100}
May 17, 2025 01:22:31 PM INFO: Checkpoint saved after 100 records
May 17, 2025 01:22:31 PM INFO: Fetching data with params: {'page_size': 100, 'cursor': '6cf667db09caa806bf7d9683f6a2220c'}
...
May 17, 2025 01:22:32 PM INFO: Checkpoint saved after 700 records
May 17, 2025 01:22:32 PM INFO: Fetching data with params: {'page_size': 100, 'cursor': 'f9f9de8e2f949ca83d731e23f7ec9957'}
May 17, 2025 01:22:32 PM INFO: No more pages to fetch

✓ Debug completed

Step 3: Querying sample data from DuckDB...
Running query: SELECT * FROM tester.icp_records LIMIT 5;

┌──────────────────────┬────────────────────┬──────────────────────┬───────────────┬───┬───────────────┬─────────────────┬────────────┐
│      record_id       │ claim_outcome_date │ claim_outcome_conf…  │   policy_id   │ … │ customer_name │   customer_id   │ claim_date │
├──────────────────────┼────────────────────┼──────────────────────┼───────────────┼───┼───────────────┼─────────────────┼────────────┤
│ e4fd12be-10f1-4306…  │ 2024-07-05         │            0.6791717 │ POLICY_000000 │ … │ Customer 0    │ CUSTOMER_000000 │ 2024-10-17 │
│ b2b91956-edfb-4f6c…  │ 2024-06-13         │           0.07407491 │ POLICY_000001 │ … │ Customer 1    │ CUSTOMER_000001 │ 2024-08-21 │
│ 7d388018-31be-4ef4…  │ 2025-01-08         │            0.9928321 │ POLICY_000002 │ … │ Customer 2    │ CUSTOMER_000002 │ 2024-04-11 │
│ e8bca069-3242-4af2…  │ 2024-11-28         │           0.40789425 │ POLICY_000003 │ … │ Customer 3    │ CUSTOMER_000003 │ 2024-10-25 │
│ b75ddc44-b928-444b…  │ 2024-05-27         │           0.28740254 │ POLICY_000004 │ … │ Customer 4    │ CUSTOMER_000004 │ 2024-07-27 │
└──────────────────────┴────────────────────┴──────────────────────┴───────────────┴───┴───────────────┴─────────────────┴────────────┘

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
Next sync state: {"next_cursor": "f9f9de8e2f949ca83d731e23f7ec9957"}
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
   - A unique name for your connector (e.g., icp_new_custom_connector)

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
The connection 'icp_new_custom_connector' has been created successfully.
Python Version: 3.12.8
Connection ID: carnivore_propagation
Visit the Fivetran dashboard to start the initial sync: https://fivetran.com/dashboard/connectors/carnivore_propagation/status
```

### What to Expect After Deployment

After successful deployment:

1. The connector will be created in your Fivetran account with a randomly generated Connection ID (e.g., `carnivore_propagation`)
2. You'll be provided a link to access the connector in the Fivetran dashboard
3. The connector will be ready for its initial sync

In the Fivetran dashboard, you will be able to:
- View your connector's sync status
- Configure sync frequency (hourly, daily, etc.)
- Monitor for any errors or warnings
- View the destination schema with the `icp_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the ICP API endpoint
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

1. If the ICP API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       record['claim_efficiency_ratio'] = record['claim_processing_time_reduction'] / record['claim_processing_time'] if record['claim_processing_time'] > 0 else 0
       yield op.upsert("icp_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "icp_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "icp_customers",
               "primary_key": ["customer_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating customer records from ICP data
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
       yield op.upsert("icp_records", record)
   
   # Yield all unique customer records
   for customer in customer_records.values():
       yield op.upsert("icp_customers", customer)
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

## Downstream Application: ClaimSphere

The data extracted by this connector powers ClaimSphere, an AI-driven claims processing automation system designed for insurance companies. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in the insurance industry.

### Application Purpose

ClaimSphere helps insurance companies:
- Reduce processing time for insurance claims
- Minimize errors in claims handling
- Improve customer satisfaction through efficient processing
- Decrease operational costs in claims departments
- Transform manual claims handling into a streamlined, efficient process

### Target Users

- Claims Managers
- Underwriters
- Customer Service Representatives
- Insurance Analysts
- Operations Directors

### Data Flow Architecture

1. **Data Sources** → 2. **ICP API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Insurance Data Sources

The ICP API provides synthetic data that simulates information from various insurance systems:

- **Claims Management Systems**: 
  - Guidewire
  - Duck Creek
  - Insurity
- **Policy Administration Systems**: 
  - Oracle
  - SAP
  - Insurity
- **Customer Relationship Management (CRM)**: 
  - Salesforce
  - HubSpot
  - Zoho

This approach allows for realistic insurance analytics without using protected policyholder information, making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The ClaimSphere application provides:
- Real-time analysis of claims processing metrics
- Performance comparison between different claim types and processing approaches
- Cost-saving opportunity identification
- AI-driven claims classification and routing
- Predictive analytics for claims outcome forecasting
- Comprehensive dashboards for key performance indicators

## Notes

- This connector creates a single table named `icp_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The ICP API returns approximately 750 insurance claims records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the ClaimSphere insurance application
- While this connector uses synthetic data, the approach mirrors real-world insurance data extraction patterns
