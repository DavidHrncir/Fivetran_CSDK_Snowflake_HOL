# Oil and Gas FTS Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Oil and Gas Field Technician Task Summarization (FTS) data from an API and load it into Snowflake via Fivetran, powering LogLynx and other advanced field operations analytics applications.

## Overview

The Oil and Gas FTS connector fetches field technician task summaries from a REST API and loads them into a single table called `fts_records` in your Snowflake database. The connector retrieves detailed information about technician logs, maintenance activities, equipment servicing, and AI-generated task summaries, including properties like maintenance costs, downtime hours, failure rates, and time savings from automated summarization. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the FTS data
- **Data enrichment**: Extracts 14 key metrics and attributes related to field technician task summarization
- **Efficient processing**: Handles large datasets (750+ records) with minimal resource usage
- **Field operations-specific**: Designed to handle technician log data common in oil and gas field operations

## Project Structure

```
fts/
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
| `api_key`    | API key for authentication to the FTS API              | Required                                                  |
| `base_url`   | Base URL for the FTS API                               | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## FTS API Details

### Endpoint

The connector uses the following REST API endpoint to access field technician task summarization data:

- `GET /fts_data`: Retrieves a paginated list of Oil and Gas Field Technician Task Summarization records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

### Data Schema

The FTS API returns records with the following structure:

| Field                              | Type    | Description                                   |
|------------------------------------|---------|-----------------------------------------------|
| `record_id`                        | string  | Unique identifier for the technician task summary record (primary key) |
| `log_date`                         | date    | The date when the task log was recorded       |
| `technician_id`                    | string  | Unique identifier for the technician who performed the task |
| `log_description`                  | string  | Detailed description of the task performed by the technician |
| `equipment_id`                     | string  | Unique identifier for the equipment on which the task was performed |
| `maintenance_type`                 | string  | Type of maintenance performed (Predictive, Corrective, Condition-Based) |
| `maintenance_status`               | string  | Current status of the maintenance task (Completed, Delayed, In Progress, Cancelled) |
| `erp_order_id`                     | string  | Enterprise Resource Planning (ERP) order ID associated with the task |
| `customer_id`                      | string  | Unique identifier for the customer associated with the task |
| `summarized_log`                   | string  | AI-generated summarized version of the task log |
| `failure_rate`                     | float   | Calculated failure rate associated with the equipment or task |
| `maintenance_cost`                 | float   | Total cost incurred for the maintenance task  |
| `downtime_hours`                   | integer | Number of hours the equipment was down due to maintenance |
| `summarization_time_saved`         | integer | Estimated time saved (in hours) by using AI summarization |

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `fts_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "fts_records",
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
   mkdir fts && cd fts
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
✓ Detected table name: fts_records
===========================================================
         Fivetran Connector Debug & Reset Script          
===========================================================

This will reset your connector, delete current state and warehouse.db files.
Do you want to continue? (Y/n): y

Step 1: Resetting Fivetran connector...
✓ Reset successful

Step 2: Running debug with configuration...
(Real-time output will be displayed below)

May 17, 2025 10:01:09 AM INFO Fivetran-Connector-SDK: Debugging connector at: /path/to/connector
May 17, 2025 10:01:09 AM INFO Fivetran-Connector-SDK: Running connector tester...
May 17, 2025 10:01:12 AM INFO Fivetran-Connector-SDK: Initiating the 'schema' method call...
May 17, 2025 10:01:12 AM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.fts_records 
May 17, 2025 10:01:12 AM INFO Fivetran-Connector-SDK: Initiating the 'update' method call...

May 17, 2025 10:01:12 AM INFO: Fetching data with params: {'page_size': 100}
May 17, 2025 10:01:12 AM INFO: Checkpoint saved after 100 records
May 17, 2025 10:01:12 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': '41b3cba91ddab1541cf48828361b7f1c'}
...
May 17, 2025 10:01:12 AM INFO: Checkpoint saved after 700 records
May 17, 2025 10:01:12 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': '0d011521148b3f11f4f4ec315800cf40'}
May 17, 2025 10:01:12 AM INFO: No more pages to fetch

✓ Debug completed

Step 3: Querying sample data from DuckDB...
Running query: SELECT * FROM tester.fts_records LIMIT 5;

┌──────────────────────┬─────────────────┬──────────────────────┬──────────────────┬───┬──────────────┬───────────────┬─────────────┐
│      record_id       │ maintenance_cost│ maintenance_status   │ maintenance_type │ … │ technician_id│ equipment_id  │ customer_id │
├──────────────────────┼─────────────────┼──────────────────────┼──────────────────┼───┼──────────────┼───────────────┼─────────────┤
│ 20040c16-ddca-4bcd…  │         157.03  │ Delayed              │ Predictive       │ … │ TECH_000000  │ EQUIP_000000  │ CUST_000000 │
│ 530e4b98-a812-481e…  │         383.56  │ Completed            │ Corrective       │ … │ TECH_000001  │ EQUIP_000001  │ CUST_000001 │
│ e441d4b3-d4e3-4a5a…  │         815.95  │ Cancelled            │ Corrective       │ … │ TECH_000002  │ EQUIP_000002  │ CUST_000002 │
│ 6697ec2a-909c-480d…  │         964.86  │ Completed            │ Condition-Based  │ … │ TECH_000003  │ EQUIP_000003  │ CUST_000003 │
│ 48680f93-ad2d-4a97…  │         476.28  │ In Progress          │ Predictive       │ … │ TECH_000004  │ EQUIP_000004  │ CUST_000004 │
└──────────────────────┴─────────────────┴──────────────────────┴──────────────────┴───┴──────────────┴───────────────┴─────────────┘

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
Next sync state: {"next_cursor": "0d011521148b3f11f4f4ec315800cf40"}
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
   - A unique name for your connector (e.g., a_new_fts_connector)

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
The connection 'a_new_fts_connector' has been created successfully.
Python Version: 3.12.8
Connection ID: spleen_divide
Visit the Fivetran dashboard to start the initial sync: https://fivetran.com/dashboard/connectors/spleen_divide/status
```

### What to Expect After Deployment

After successful deployment:

1. The connector will be created in your Fivetran account with a randomly generated Connection ID (e.g., `spleen_divide`)
2. You'll be provided a link to access the connector in the Fivetran dashboard
3. The connector will be ready for its initial sync

In the Fivetran dashboard, you will be able to:
- View your connector's sync status
- Configure sync frequency (hourly, daily, etc.)
- Monitor for any errors or warnings
- View the destination schema with the `fts_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the FTS API endpoint
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

1. If the FTS API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       record['cost_per_hour'] = record['maintenance_cost'] / record['downtime_hours'] if record['downtime_hours'] > 0 else 0
       yield op.upsert("fts_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "fts_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "fts_technicians",
               "primary_key": ["technician_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating technician records from FTS data
   technician_records = {}
   for record in records:
       # Extract technician info for separate table
       technician_id = record['technician_id']
       if technician_id not in technician_records:
           technician_records[technician_id] = {
               'technician_id': technician_id,
               'total_tasks': 1,
               'total_maintenance_cost': record['maintenance_cost'],
               'total_downtime_hours': record['downtime_hours'],
               'total_time_saved': record['summarization_time_saved']
           }
       else:
           tech_rec = technician_records[technician_id]
           tech_rec['total_tasks'] += 1
           tech_rec['total_maintenance_cost'] += record['maintenance_cost']
           tech_rec['total_downtime_hours'] += record['downtime_hours']
           tech_rec['total_time_saved'] += record['summarization_time_saved']
       # Yield the original record
       yield op.upsert("fts_records", record)
   
   # Yield all unique technician records
   for technician in technician_records.values():
       yield op.upsert("fts_technicians", technician)
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

## Downstream Application: LogLynx

The data extracted by this connector powers LogLynx, an AI-driven field technician log summarization and analysis system designed for oil and gas companies. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in the energy industry.

### Application Purpose

LogLynx helps energy teams:
- Automate summarization of daily logs from field technicians
- Reduce maintenance costs through better analysis and decision-making
- Minimize equipment downtime through improved maintenance scheduling
- Save time on manual log summarization tasks
- Identify trends and patterns in equipment failures and maintenance activities

### Target Users

- Field Technicians
- Maintenance Managers
- Operations Managers
- Chief Operating Officer (COO)

### Data Flow Architecture

1. **Data Sources** → 2. **FTS API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Oil and Gas Data Sources

The FTS API provides synthetic data that simulates information from various oil and gas field operations systems:

- **Field Technician Logs**: 
  - SAP
  - Oracle
  - Microsoft Dynamics
- **Computerized Maintenance Management Systems (CMMS)**: 
  - IBM Maximo
  - Infor EAM
  - SAP EAM
- **Enterprise Resource Planning (ERP) Systems**: 
  - SAP
  - Oracle
  - Microsoft Dynamics

This approach allows for realistic field operations analytics without using proprietary technician data, making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The LogLynx application provides:
- Automated AI-powered summarization of field technician logs
- Analysis of maintenance costs and patterns across equipment and technicians
- Equipment failure rate tracking and trend analysis
- Maintenance type effectiveness evaluation (Predictive vs. Corrective vs. Condition-Based)
- Technician performance metrics and time savings quantification
- Downtime analysis and optimization recommendations
- Customer-specific maintenance insights and reporting

### Expected Business Results

Based on the LogLynx solution profile, the application delivers:
- **300 fewer failed treatments per year** (15% reduction from 3% baseline failure rate)
- **$1,200,000 in maintenance cost savings annually** (30% reduction from $4M annual costs)
- **25% reduction in maintenance downtime** (300 hours saved per year)
- **90% reduction in manual summarization time** (1,200 hours saved per year)

## Notes

- This connector creates a single table named `fts_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The FTS API returns approximately 750 field technician task summarization records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the LogLynx field operations application
- While this connector uses synthetic data, the approach mirrors real-world field technician log extraction patterns