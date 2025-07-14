# Agriculture Animal Health Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Agriculture Animal Health data from an API and load it into Snowflake via Fivetran, powering advanced agricultural animal health monitoring and farm management systems.

## Overview

The Agriculture Animal Health connector fetches livestock health and environmental data from a REST API and loads it into a single table called `agr_records` in your Snowflake database. The connector retrieves detailed information about farm animals, health status monitoring, vaccination tracking, environmental conditions, and AI-powered health risk predictions, including properties like predicted health risks, medication histories, weather impacts, and recommended care actions. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the agriculture data
- **Data enrichment**: Extracts comprehensive agricultural metrics and attributes
- **Efficient processing**: Handles large datasets with minimal resource usage
- **Agriculture-specific**: Designed to handle animal health data common in modern livestock farming operations

## Project Structure

```
agriculture/
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
| `api_key`    | API key for authentication to the Agriculture API      | Required                                                  |
| `base_url`   | Base URL for the Agriculture API                       | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## Agriculture API Details

### Endpoint

The connector uses the following REST API endpoint to access agricultural animal health data:

- `GET /agr_data`: Retrieves a paginated list of Agriculture Animal Health records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

### Data Schema

The Agriculture API returns animal health records with the following structure:

| Field                              | Type    | Description                                   |
|------------------------------------|---------|-----------------------------------------------|
| `record_id`                        | string  | Unique identifier for the animal health record (primary key) |
| `animal_id`                        | string  | Unique identifier for the individual animal   |
| `farm_id`                          | string  | Unique identifier for the farm                |
| `species`                          | string  | Species of the animal (Beef Cattle, Chickens, Pigs, etc.) |
| `breed`                            | string  | Specific breed of the animal                  |
| `age`                              | number  | Age of the animal in years                    |
| `weight`                           | float   | Weight of the animal                          |
| `health_status`                    | string  | Current health status (Healthy, Sick, Injured, etc.) |
| `vaccination_history`              | string  | Vaccination status (Up-to-date, Overdue, Not vaccinated) |
| `medication_history`               | string  | Medication history (Current, Previous, None)  |
| `weather_data`                     | string  | Weather conditions (Sunny, Rainy, Snowy, etc.) |
| `temperature`                      | float   | Environmental temperature                     |
| `humidity`                         | float   | Environmental humidity percentage             |
| `precipitation`                    | float   | Precipitation amount                          |
| `predicted_health_risk`            | float   | AI-predicted health risk score (0.0-1.0)     |
| `recommended_action`               | string  | Recommended care action (Monitor closely, Administer medication, etc.) |

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `agr_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "agr_records",
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
   mkdir agriculture && cd agriculture
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
✓ Detected table name: agr_records
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
May 17, 2025 10:01:12 AM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.agr_records 
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
Running query: SELECT * FROM tester.agr_records LIMIT 5;

┌──────────────────────┬─────────────────┬──────────────────────┬──────────────────┬───┬──────────────┬───────────────┬─────────────┐
│      record_id       │ farm_id         │ animal_id            │ species          │ … │ health_status │ predicted_health_risk │ recommended_action │
├──────────────────────┼─────────────────┼──────────────────────┼──────────────────┼───┼───────────────┼───────────────────────┼────────────────────┤
│ 42e76305-0fdf-44a6…  │ FARM_000000     │ ANIMAL_000000        │ Beef Cattle      │ … │ Healthy       │ 0.87                  │ Monitor closely    │
│ 11c55de5-44cf-4d7c…  │ FARM_000000     │ ANIMAL_000001        │ Beef Cattle      │ … │ Deceased      │ 0.18                  │ No action required │
│ 1d2dfc75-1224-4057…  │ FARM_000000     │ ANIMAL_000002        │ Beef Cattle      │ … │ Healthy       │ 0.17                  │ No action required │
│ bafc9f34-a011-4a08…  │ FARM_000000     │ ANIMAL_000003        │ Beef Cattle      │ … │ Sick          │ 0.51                  │ No action required │
│ d42435be-82c2-4bc4…  │ FARM_000000     │ ANIMAL_000004        │ Beef Cattle      │ … │ Sick          │ 0.27                  │ No action required │
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
   - A unique name for your connector (e.g., agr_0714)

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
Enter a unique Fivetran Connector Name [my_new_fivetran_custom_connector]: agr_0714
Deploying connector...
Jul 14, 2025 08:03:21 AM INFO Fivetran-Connector-SDK: Packaging your project for upload... 
✓
Jul 14, 2025 08:03:21 AM INFO Fivetran-Connector-SDK: Uploading your project... 
✓
Jul 14, 2025 08:03:24 AM INFO Fivetran-Connector-SDK: The connection 'agr_0714' has been created successfully.
Jul 14, 2025 08:03:24 AM INFO Fivetran-Connector-SDK: Python version 3.12 to be used at runtime. 
Jul 14, 2025 08:03:24 AM INFO Fivetran-Connector-SDK: Connection ID: academic_calyx 
Jul 14, 2025 08:03:24 AM INFO Fivetran-Connector-SDK: Visit the Fivetran dashboard to start the initial sync: https://fivetran.com/dashboard/connectors/academic_calyx/status
```

### What to Expect After Deployment

After successful deployment:

1. The connector will be created in your Fivetran account with a randomly generated Connection ID (e.g., `academic_calyx`)
2. You'll be provided a link to access the connector in the Fivetran dashboard
3. The connector will be ready for its initial sync

In the Fivetran dashboard, you will be able to:
- View your connector's sync status
- Configure sync frequency (hourly, daily, etc.)
- Monitor for any errors or warnings
- View the destination schema with the `agr_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the Agriculture API endpoint
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

1. If the Agriculture API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       record['health_risk_category'] = 'High' if record['predicted_health_risk'] > 0.7 else 'Medium' if record['predicted_health_risk'] > 0.3 else 'Low'
       record['needs_attention'] = record['health_status'] in ['Sick', 'Injured'] or record['predicted_health_risk'] > 0.8
       yield op.upsert("agr_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "agr_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "farm_summary",
               "primary_key": ["farm_id"]
           },
           {
               "table": "animal_health_analytics",
               "primary_key": ["species", "farm_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating farm summary records from animal health data
   farm_summaries = {}
   animal_health_analytics = {}
   
   for record in records:
       # Extract farm summary info for separate table
       farm_id = record['farm_id']
       if farm_id not in farm_summaries:
           farm_summaries[farm_id] = {
               'farm_id': farm_id,
               'total_animals': 1,
               'healthy_animals': 1 if record['health_status'] == 'Healthy' else 0,
               'at_risk_animals': 1 if record['predicted_health_risk'] > 0.7 else 0,
               'avg_health_risk': record['predicted_health_risk']
           }
       else:
           farm_sum = farm_summaries[farm_id]
           farm_sum['total_animals'] += 1
           farm_sum['healthy_animals'] += 1 if record['health_status'] == 'Healthy' else 0
           farm_sum['at_risk_animals'] += 1 if record['predicted_health_risk'] > 0.7 else 0
           farm_sum['avg_health_risk'] = (farm_sum['avg_health_risk'] + record['predicted_health_risk']) / 2
       
       # Extract animal health analytics by species
       species_key = f"{record['species']}_{record['farm_id']}"
       if species_key not in animal_health_analytics:
           animal_health_analytics[species_key] = {
               'species': record['species'],
               'farm_id': record['farm_id'],
               'avg_health_risk': record['predicted_health_risk'],
               'total_animals': 1,
               'vaccination_compliance': 1 if record['vaccination_history'] == 'Up-to-date' else 0
           }
       else:
           analytics = animal_health_analytics[species_key]
           analytics['total_animals'] += 1
           analytics['vaccination_compliance'] += 1 if record['vaccination_history'] == 'Up-to-date' else 0
           analytics['avg_health_risk'] = (analytics['avg_health_risk'] + record['predicted_health_risk']) / 2
       
       # Yield the original record
       yield op.upsert("agr_records", record)
   
   # Yield all farm summaries
   for farm_summary in farm_summaries.values():
       yield op.upsert("farm_summary", farm_summary)
   
   # Yield all animal health analytics
   for health_analytic in animal_health_analytics.values():
       yield op.upsert("animal_health_analytics", health_analytic)
   ```

### Dependencies Management

To add external dependencies:

1. Create a `requirements.txt` file in your project directory
2. Add your dependencies, for example:
   ```
   requests>=2.25.0
   python-dateutil>=2.8.1
   pandas>=1.3.0
   ```
3. The Fivetran deployment process will automatically install these dependencies in the connector environment

## Downstream Applications

The data extracted by this connector can power various agricultural animal health monitoring applications and livestock management systems, such as:

### Animal Health Management Dashboards
- **Health Risk Analytics**: Track predicted health risks, vaccination compliance, and disease patterns
- **Environmental Impact Monitoring**: Analyze weather and environmental factors affecting animal health
- **Preventive Care Optimization**: Schedule vaccinations, medications, and health interventions

### Target Users
- Livestock Veterinarians and Animal Health Specialists
- Farm Managers and Operations Teams
- Agricultural Research Scientists
- Animal Welfare Compliance Officers
- Agricultural Insurance Assessors

### Data Flow Architecture
1. **Animal Health Data Sources** → 2. **Agriculture API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Health Analytics Applications**

### Simulated Agricultural Data Sources
The Agriculture API provides synthetic data that simulates information from various livestock management systems:

- **Animal Health Management Systems**: 
  - VetSuccess by Henry Schein
  - AgriWebb Livestock Management
  - CattleMax Farm Management
- **Environmental Monitoring Platforms**: 
  - Davis Weather Stations
  - AgSense Remote Monitoring
  - Climate FieldView Environmental Data
- **Farm Management Software**: 
  - FarmLogs by Farmers Business Network
  - Granular Farm Management
  - Conservis Integrated Farm Management

### Analytics Capabilities
Applications built on this data can provide:
- Predictive health risk modeling using AI and environmental factors
- Vaccination and medication tracking and compliance reporting
- Weather impact analysis on animal health outcomes
- Species-specific health trend analysis and benchmarking
- Early disease outbreak detection and prevention strategies
- Animal welfare monitoring and regulatory compliance reporting
- Cost optimization for veterinary care and medication management

### Expected Business Results
Agricultural animal health analytics applications using this data can deliver:
- **20-25% reduction in animal mortality** through early disease detection
- **30% improvement in vaccination compliance** through automated tracking
- **40% decrease in veterinary costs** through preventive care optimization
- **50% reduction in disease outbreak incidents** through predictive monitoring

## Notes

- This connector creates a single table named `agr_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The Agriculture API returns comprehensive agricultural records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and agricultural animal health analytics applications
- While this connector uses synthetic data, the approach mirrors real-world livestock health data extraction patterns