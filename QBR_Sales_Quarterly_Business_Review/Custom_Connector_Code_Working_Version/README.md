# Quarterly Business Reviews (QBR) Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Quarterly Business Review (QBR) data from an API and load it into Snowflake via Fivetran, powering enterprise QBR generation and advanced account health analytics applications.

## Overview

The QBR connector fetches quarterly business review records from a REST API and loads them into a single table called `qbr_records` in your Snowflake database. The connector retrieves detailed information about customer accounts, contract details, health metrics, engagement scores, and success planning metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the QBR data
- **Data enrichment**: Extracts over 40 metrics and attributes related to customer account health
- **Efficient processing**: Handles large datasets (750+ records) with minimal resource usage
- **Business-focused**: Designed to handle quarterly business review data common in enterprise customer success operations

## Project Structure

```
qbr/
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
| `api_key`    | API key for authentication to the QBR API              | Required                                                  |
| `base_url`   | Base URL for the QBR API                               | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## QBR API Details

### Endpoint

The connector uses the following REST API endpoint to access quarterly business review data:

- `GET /qbr_data`: Retrieves a paginated list of Quarterly Business Review records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

### Data Schema

The QBR API returns records with the following structure (partial list):

| Field                          | Type    | Description                                      |
|-------------------------------|---------|--------------------------------------------------|
| `record_id`                   | string  | Unique identifier for the record (primary key)   |
| `company_id`                  | string  | Unique identifier for the company                |
| `company_name`                | string  | Name of the company                              |
| `industry`                    | string  | Industry of the company                          |
| `size`                        | string  | Size of the company (e.g., Enterprise, Small)    |
| `contract_value`              | integer | Value of the contract                            |
| `contract_start_date`         | date    | Start date of the contract                       |
| `contract_expiration_date`    | date    | Expiration date of the contract                  |
| `qbr_quarter`                 | string  | Quarter of the QBR (e.g., Q1, Q2)                |
| `qbr_year`                    | integer | Year of the QBR                                  |
| `deal_stage`                  | string  | Current stage of the deal                        |
| `renewal_probability`         | integer | Probability of contract renewal (0-100)          |
| `upsell_opportunity`          | integer | Potential upsell value                           |
| `active_users`                | integer | Number of active users                           |
| `feature_adoption_rate`       | float   | Rate of feature adoption (0-1)                   |
| `custom_integrations`         | integer | Number of custom integrations                    |
| `pending_feature_requests`    | integer | Number of pending feature requests               |
| `ticket_volume`               | integer | Number of support tickets                        |
| `avg_resolution_time_hours`   | float   | Average resolution time for tickets in hours     |
| `csat_score`                  | float   | Customer satisfaction score                      |
| `sla_compliance_rate`         | float   | Service Level Agreement compliance rate (0-1)    |
| `success_metrics_defined`     | string  | Indicates if success metrics are defined         |
| `roi_calculated`              | string  | Indicates if ROI is calculated                   |
| `estimated_roi_value`         | integer | Estimated ROI value                              |
| `health_score`                | float   | Overall health score of the account              |
| `champion_identified`         | string  | Indicates if a champion is identified            |
| `champion_level`              | string  | Level of the champion (e.g., VP, C-Level)        |
| `champion_engagement_score`   | integer | Engagement score of the champion (1-5)           |
| `pain_points_documented`      | string  | Documented pain points                           |
| `pain_impact_level`           | string  | Impact level of pain points (High, Medium, Low)  |
| `urgency_level`               | string  | Urgency level (High, Medium, Low)                |
| `competitive_situation`       | string  | Competitive situation (None, Single, Multiple)   |
| `competitive_position`        | string  | Competitive position (Leader, Strong, Weak)      |

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `qbr_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "qbr_records",
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
   mkdir qbr && cd qbr
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
✓ Detected table name: qbr_records
===========================================================
         Fivetran Connector Debug & Reset Script          
===========================================================

This will reset your connector, delete current state and warehouse.db files.
Do you want to continue? (Y/n): y

Step 1: Resetting Fivetran connector...
✓ Reset successful

Step 2: Running debug with configuration...
(Real-time output will be displayed below)

May 18, 2025 08:30:02 AM WARNING Fivetran-Connector-SDK: `requirements.txt` is not required as no additional Python libraries are required or all required libraries for your code are pre-installed.
May 18, 2025 08:30:02 AM INFO Fivetran-Connector-SDK: Debugging connector at: /Users/kelly.kohlleffel/Documents/GitHub/Fivetran_Connector_SDK/examples/quick_start_examples/qbr
May 18, 2025 08:30:02 AM INFO Fivetran-Connector-SDK: Running connector tester...
May 18, 2025 08:30:03 AM: INFO Fivetran-Tester-Process: Version: 0.25.0424.001 
May 18, 2025 08:30:03 AM: INFO Fivetran-Tester-Process: Destination schema: /Users/kelly.kohlleffel/Documents/GitHub/Fivetran_Connector_SDK/examples/quick_start_examples/qbr/files/warehouse.db/tester 
May 18, 2025 08:30:05 AM: INFO Fivetran-Tester-Process: Previous state:
{} 
May 18, 2025 08:30:05 AM INFO Fivetran-Connector-SDK: Initiating the 'schema' method call...
May 18, 2025 08:30:05 AM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.qbr_records 
May 18, 2025 08:30:05 AM INFO Fivetran-Connector-SDK: Initiating the 'update' method call...
May 18, 2025 08:30:05 AM INFO: Fetching data with params: {'page_size': 100}
May 18, 2025 08:30:05 AM INFO: Checkpoint saved after 100 records
May 18, 2025 08:30:05 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': '7061bf1008b8a9a0257238e47d6c4299'}

...

May 18, 2025 08:30:06 AM INFO: Checkpoint saved after 700 records
May 18, 2025 08:30:06 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': 'b9911219b2d39984d27ca2971f5fd939'}
May 18, 2025 08:30:06 AM INFO: No more pages to fetch

✓ Debug completed

Step 3: Querying sample data from DuckDB...
Running query: SELECT * FROM tester.qbr_records LIMIT 5;

┌──────────────────────┬─────────────┬──────────────────────┬──────────────────────┬───┬──────────┬──────────────────────┬──────────────────────┐
│      record_id       │ qbr_quarter │ pending_feature_re…  │ success_metrics_de…  │ … │ qbr_year │ champion_engagemen…  │ decision_maker_level │
│       varchar        │   varchar   │        int64         │       varchar        │   │  int64   │        int64         │       varchar        │
├──────────────────────┼─────────────┼──────────────────────┼──────────────────────┼───┼──────────┼──────────────────────┼──────────────────────┤
│ 49fdca8c-8cb4-41e3…  │ Q1          │                    5 │ True                 │ … │     2023 │                    2 │ VP                   │
│ 4af92aa9-62e1-4dee…  │ Q1          │                    1 │ True                 │ … │     2023 │                    1 │ C-Level              │
│ dd9ef72e-7b55-47a6…  │ Q1          │                    6 │ False                │ … │     2023 │                    2 │ VP                   │
│ 991e0cc7-60eb-4c59…  │ Q1          │                    0 │ False                │ … │     2023 │                    4 │ C-Level              │
│ 9f48d546-99ec-4f07…  │ Q1          │                    6 │ False                │ … │     2023 │                    5 │ Director             │
└──────────────────────┴─────────────┴──────────────────────┴──────────────────────┴───┴──────────┴──────────────────────┴──────────────────────┘

==================== OPERATION SUMMARY ====================
  Operation       | Calls     
  ----------------+------------
  Upserts         | 755       
  Updates         | 0         
  Deletes         | 0         
  Truncates       | 0         
  SchemaChanges   | 1         
  Checkpoints     | 7         
====================================================================

✓ Debug and reset operations completed.
Next sync state: {"next_cursor": "b9911219b2d39984d27ca2971f5fd939"}
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
6. **Operation Summary**: Shows that 755 records were processed through:
   - 755 upsert operations
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
   - A unique name for your connector (e.g., qbr_new_custom_connector)

4. The script will package and upload your connector to Fivetran

### Deploy Script Details

The `deploy.sh` script performs the following actions:

1. **Configuration Check**: Validates that the necessary configuration files are present
2. **Account Information**: Prompts for Fivetran account details and retrieves API key
3. **Deployment**: Packages and uploads the connector to your Fivetran account
4. **Confirmation**: Displays the connector ID and a link to access it in the Fivetran dashboard

Sample output from a successful deployment:
```
Enter your Fivetran Account Name [MDS_SNOWFLAKE_HOL]: 
Enter your Fivetran Destination Name [NEW_SALES_ENG_HANDS_ON_LAB]: 
Enter a unique Fivetran Connector Name [my_new_fivetran_custom_connector]: qbr_new_custom_connector
Deploying connector...
May 18, 2025 08:31:16 AM INFO Fivetran-Connector-SDK: We support only `.py` files and a `requirements.txt` file as part of the code upload. *No other code files* are supported or uploaded during the deployment process. Ensure that your code is structured accordingly and all dependencies are listed in `requirements.txt`
May 18, 2025 08:31:16 AM WARNING Fivetran-Connector-SDK: `requirements.txt` is not required as no additional Python libraries are required or all required libraries for your code are pre-installed.
May 18, 2025 08:31:16 AM INFO Fivetran-Connector-SDK: Successful validation of requirements.txt
May 18, 2025 08:31:17 AM INFO Fivetran-Connector-SDK: Deploying '/Users/kelly.kohlleffel/Documents/GitHub/Fivetran_Connector_SDK/examples/quick_start_examples/qbr' to connection 'qbr_new_custom_connector' in destination 'NEW_SALES_ENG_HANDS_ON_LAB'.\n
May 18, 2025 08:31:17 AM INFO Fivetran-Connector-SDK: Packaging your project for upload...
✓
May 18, 2025 08:31:17 AM INFO Fivetran-Connector-SDK: Uploading your project...
✓
May 18, 2025 08:31:19 AM INFO Fivetran-Connector-SDK: The connection 'qbr_new_custom_connector' has been created successfully.\n
May 18, 2025 08:31:19 AM INFO Fivetran-Connector-SDK: Python Version: 3.12.8
May 18, 2025 08:31:19 AM INFO Fivetran-Connector-SDK: Connection ID: swim_triumph
May 18, 2025 08:31:19 AM INFO Fivetran-Connector-SDK: Visit the Fivetran dashboard to start the initial sync: https://fivetran.com/dashboard/connectors/swim_triumph/status
```

### What to Expect After Deployment

After successful deployment:

1. The connector will be created in your Fivetran account with a randomly generated Connection ID (e.g., `swim_triumph`)
2. You'll be provided a link to access the connector in the Fivetran dashboard
3. The connector will be ready for its initial sync

In the Fivetran dashboard, you will be able to:
- View your connector's sync status
- Configure sync frequency (hourly, daily, etc.)
- Monitor for any errors or warnings
- View the destination schema with the `qbr_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the QBR API endpoint
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

1. If the QBR API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       if record['renewal_probability'] > 0 and record['health_score'] > 0:
           record['risk_factor'] = (100 - record['renewal_probability']) / (record['health_score'] / 100)
       else:
           record['risk_factor'] = 0
       yield op.upsert("qbr_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "qbr_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "qbr_companies",
               "primary_key": ["company_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating company records from QBR data
   company_records = {}
   for record in records:
       # Extract company info for separate table
       company_id = record['company_id']
       if company_id not in company_records:
           company_records[company_id] = {
               'company_id': company_id,
               'company_name': record['company_name'],
               'industry': record['industry'],
               'size': record['size']
           }
       # Yield the original record
       yield op.upsert("qbr_records", record)
   
   # Yield all unique company records
   for company in company_records.values():
       yield op.upsert("qbr_companies", company)
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

## Downstream Application: Enterprise QBR Generator

The data extracted by this connector powers the Enterprise QBR Generator, an AI-driven quarterly business review generation system designed for customer success teams, account managers, and executives. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis.

### Application Purpose

Enterprise QBR Generator helps organizations:
- Generate comprehensive, data-driven Quarterly Business Reviews in minutes instead of days
- Create standardized, insightful, and actionable QBRs tailored to various business needs
- Combine sales data, support metrics, product usage, and historical context in one place
- Track customer health and engagement over time
- Identify renewal risks and upsell opportunities
- Transform customer success into a data-driven process

### Target Users

- Customer Success Managers
- Account Executives
- Customer Success Leaders
- Sales Leaders
- Executive Stakeholders

### Data Flow Architecture

1. **Data Sources** → 2. **QBR API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Enterprise Data Sources

The QBR API provides synthetic data that simulates information from various enterprise systems:

- **CRM Systems**: 
  - Salesforce
  - HubSpot
  - Microsoft Dynamics
- **Support Ticketing Systems**: 
  - Zendesk
  - ServiceNow
  - Freshdesk
- **Product Analytics Platforms**: 
  - Amplitude
  - Mixpanel
  - Pendo

This approach allows for realistic QBR generation without using confidential customer information, making it ideal for demonstration, development, and training purposes.

### Application Features

The Enterprise QBR Generator provides:
- AI-powered QBR content generation using Snowflake Cortex
- Multiple QBR templates (Standard, Executive Summary, Technical Deep Dive, Customer Success Focus)
- Customizable view types for different audiences (Sales, Executive, Technical, Customer Success)
- Historical QBR tracking to access previously generated QBRs
- Data explorer to browse and filter underlying QBR data
- Key metrics dashboard including Health Score, Contract Value, CSAT Score, and Active Users
- One-click generation of comprehensive QBRs
- Download option to save generated QBRs as Markdown files

### Benefits

The application delivers significant business value:
- Time savings: Reduce QBR preparation time from days to minutes
- Consistency: Create standardized QBRs across all accounts
- Customization: Tailor content for different stakeholders
- Completeness: Ensure all key metrics and insights are included
- Historical tracking: Maintain a record of all QBRs
- Scalability: Produce QBRs across large numbers of accounts

## Notes

- This connector creates a single table named `qbr_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector uses cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The QBR API returns approximately 755 quarterly business review records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with the Enterprise QBR Generator application in Snowflake
- While this connector uses synthetic data, the approach mirrors real-world enterprise data extraction patterns
