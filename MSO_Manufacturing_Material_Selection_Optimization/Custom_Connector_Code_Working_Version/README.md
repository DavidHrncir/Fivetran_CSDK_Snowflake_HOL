# Manufacturing MSO Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Manufacturing Material Supply Optimization (MSO) data from an API and load it into Snowflake via Fivetran, powering advanced manufacturing analytics applications.

## Overview

The Manufacturing MSO connector fetches material optimization records from a REST API and loads them into a single table called `mso_records` in your Snowflake database. The connector retrieves detailed information about material selection and optimization for manufacturing products, including properties like material characteristics, product performance metrics, cost savings, and design parameters. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the MSO data
- **Data enrichment**: Extracts over 30 metrics and attributes related to manufacturing material optimization
- **Efficient processing**: Handles large datasets (750+ records) with minimal resource usage
- **Manufacturing-specific**: Designed to handle material data common in manufacturing operations

## Project Structure

```
mso/
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
| `api_key`    | API key for authentication to the MSO API              | Required                                                  |
| `base_url`   | Base URL for the MSO API                               | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## MSO API Details

### Endpoint

The connector uses the following REST API endpoint to access manufacturing materials data:

- `GET /mso_data`: Retrieves a paginated list of Manufacturing MSO records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

### Data Schema

The MSO API returns records with the following structure (partial list):

| Field                              | Type    | Description                                   |
|------------------------------------|---------|-----------------------------------------------|
| `record_id`                        | string  | Unique identifier for the record (primary key) |
| `material_id`                      | string  | Unique identifier for the material            |
| `material_name`                    | string  | Name of the material                          |
| `product_id`                       | string  | Unique identifier for the product             |
| `product_name`                     | string  | Name of the product                           |
| `designer_id`                      | string  | Unique identifier for the designer            |
| `designer_name`                    | string  | Name of the designer                          |
| `cad_system`                       | string  | CAD system used for design                    |
| `cad_file_name`                    | string  | Name of the CAD file                          |
| `material_cost`                    | float   | Cost of the material                          |
| `material_weight`                  | float   | Weight of the material                        |
| `material_waste`                   | float   | Amount of material wasted                     |
| `density`                          | float   | Density of the material                       |
| `youngs_modulus`                   | float   | Young's modulus of the material               |
| `poissons_ratio`                   | float   | Poisson's ratio of the material               |
| `designer_experience`              | integer | Experience level of the designer              |
| `material_selection_date`          | date    | Date of material selection                    |
| `material_optimization_date`       | date    | Date of material optimization                 |
| `material_selection_score`         | float   | Score of the material selection process       |
| `material_optimization_score`      | float   | Score of the material optimization process    |
| `material_selection_recommendation` | string  | Recommendation for material selection         |
| `material_optimization_recommendation` | string | Recommendation for material optimization     |
| `cost_savings`                     | float   | Cost savings achieved                         |
| `weight_reduction`                 | float   | Weight reduction achieved                     |
| `performance_improvement`          | float   | Performance improvement achieved              |
| `waste_reduction`                  | float   | Waste reduction achieved                      |
| `product_lifecycle_stage`          | string  | Current stage of the product lifecycle        |
| `product_lifecycle_status`         | string  | Current status of the product lifecycle       |
| `designer_skill_level`             | string  | Skill level of the designer                   |

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `mso_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "mso_records",
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
   mkdir mso && cd mso
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
✓ Detected table name: mso_records
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
May 17, 2025 10:01:12 AM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.mso_records 
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
Running query: SELECT * FROM tester.mso_records LIMIT 5;

┌──────────────────────┬─────────────────┬──────────────────────┬──────────────────┬───┬──────────────┬───────────────┬─────────────┐
│      record_id       │ material_weight │ designer_skill_level │ product_lifecy…  │ … │ product_name │ cad_file_name │ material_id │
├──────────────────────┼─────────────────┼──────────────────────┼──────────────────┼───┼──────────────┼───────────────┼─────────────┤
│ 22eea48a-60c3-41ed…  │       67.597595 │ Intermediate         │ Production       │ … │ Product 1    │ File 1.dwg    │ MTRL_0000   │
│ b0a58780-ec52-4c07…  │        79.87146 │ Advanced             │ Design           │ … │ Product 2    │ File 2.dwg    │ MTRL_0001   │
│ c82c7b14-ef28-42d3…  │       25.796322 │ Advanced             │ Development      │ … │ Product 3    │ File 3.dwg    │ MTRL_0002   │
│ 534c6abd-2fab-46b3…  │       62.862537 │ Intermediate         │ Production       │ … │ Product 4    │ File 4.dwg    │ MTRL_0003   │
│ 48680f93-ad2d-4a97…  │        57.60285 │ Intermediate         │ Design           │ … │ Product 5    │ File 5.dwg    │ MTRL_0004   │
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
   - A unique name for your connector (e.g., a_new_mso_connector)

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
The connection 'a_new_mso_connector' has been created successfully.
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
- View the destination schema with the `mso_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the MSO API endpoint
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

1. If the MSO API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       record['efficiency_ratio'] = record['performance_improvement'] / record['material_cost'] if record['material_cost'] > 0 else 0
       yield op.upsert("mso_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "mso_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "mso_products",
               "primary_key": ["product_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating product records from MSO data
   product_records = {}
   for record in records:
       # Extract product info for separate table
       product_id = record['product_id']
       if product_id not in product_records:
           product_records[product_id] = {
               'product_id': product_id,
               'product_name': record['product_name'],
               'product_description': record['product_description'],
               'product_lifecycle_stage': record['product_lifecycle_stage'],
               'product_lifecycle_status': record['product_lifecycle_status']
           }
       # Yield the original record
       yield op.upsert("mso_records", record)
   
   # Yield all unique product records
   for product in product_records.values():
       yield op.upsert("mso_products", product)
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

## Downstream Application: MaterialMind

The data extracted by this connector powers MaterialMind, an AI-driven material selection and optimization system designed for manufacturers. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in the manufacturing industry.

### Application Purpose

MaterialMind helps manufacturing teams:
- Reduce material costs in production processes
- Decrease product weight for improved efficiency
- Increase product performance through better material selection
- Reduce material waste in manufacturing operations
- Make better material selection decisions for manufacturing operations

### Target Users

- Product Designers
- Materials Engineers
- Operations Directors
- Manufacturing Analysts

### Data Flow Architecture

1. **Data Sources** → 2. **MSO API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Manufacturing Data Sources

The MSO API provides synthetic data that simulates information from various manufacturing systems:

- **Material Properties Databases**: 
  - MatWeb
  - Granta Design
  - Material Properties Database
- **Product Lifecycle Management (PLM) Systems**: 
  - Siemens Teamcenter
  - PTC Windchill
  - Oracle Agile
- **Computer-Aided Design (CAD) Systems**: 
  - Autodesk Inventor
  - SolidWorks
  - Siemens NX

This approach allows for realistic manufacturing analytics without using proprietary material data, making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The MaterialMind application provides:
- Real-time analysis of material properties
- Performance comparison between different materials
- Cost-saving opportunity identification
- Material optimization recommendations
- Designer efficiency metrics
- Lifecycle stage analytics

## Notes

- This connector creates a single table named `mso_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The MSO API returns approximately 750 manufacturing material records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the MaterialMind manufacturing application
- While this connector uses synthetic data, the approach mirrors real-world manufacturing data extraction patterns
