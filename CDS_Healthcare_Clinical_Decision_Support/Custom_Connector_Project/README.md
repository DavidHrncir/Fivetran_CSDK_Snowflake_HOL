# Healthcare Clinical Decision Support (CDS) Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Healthcare Clinical Decision Support (CDS) data from an API and load it into Snowflake via Fivetran, powering advanced healthcare analytics and AI-driven clinical decision support applications.

## Overview

The Healthcare CDS connector fetches clinical decision support records from a REST API and loads them into a single table called `cds_records` in your Snowflake database. The connector retrieves detailed information about patient records, medical histories, lab results, diagnoses, treatments, clinical trials, and various healthcare performance metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## Features

- **Incremental syncs**: Uses cursor-based pagination to efficiently process data in chunks
- **State management**: Tracks sync progress and saves checkpoints every 100 records
- **Error handling**: Gracefully handles API and runtime errors with detailed logging
- **Configuration management**: Customizable API endpoint, page size, and authentication
- **Minimal permissions**: Requires only an API key to access the CDS data
- **Data enrichment**: Extracts over 30 healthcare metrics and attributes related to clinical decisions
- **Efficient processing**: Handles large datasets (750+ records) with minimal resource usage
- **Healthcare-specific**: Designed to handle clinical data common in healthcare operations

## Project Structure

```
cds/
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
| `api_key`    | API key for authentication to the CDS API              | Required                                                  |
| `base_url`   | Base URL for the CDS API                               | `https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com` |
| `page_size`  | Number of records to fetch per API request             | `100`                                                     |

## CDS API Details

### Endpoint

The connector uses the following REST API endpoint to access healthcare clinical decision support data:

- `GET /cds_data`: Retrieves a paginated list of Clinical Decision Support records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)

### Authentication

The API uses API key authentication, with the key passed in the request header:

```
api_key: YOUR_API_KEY
```

### Data Schema

The CDS API returns records with the following structure (partial list):

| Field                     | Type    | Description                                         |
|---------------------------|---------|-----------------------------------------------------|
| `record_id`               | string  | Unique identifier for the record (primary key)      |
| `patient_id`              | string  | Unique identifier for the patient                   |
| `medical_history`         | string  | The patient's medical history                       |
| `current_medications`     | string  | The patient's current medications                   |
| `lab_results`             | string  | The patient's latest lab results                    |
| `vital_signs`             | string  | The patient's latest vital signs                    |
| `diagnosis`               | string  | The patient's diagnosis                             |
| `treatment_plan`          | string  | The recommended treatment plan                      |
| `clinical_trial_id`       | string  | Identifier of clinical trial patient is enrolled in |
| `trial_name`              | string  | Name of the clinical trial                          |
| `trial_status`            | string  | Current status of the clinical trial                |
| `medical_publication_id`  | string  | Identifier of a relevant medical publication        |
| `publication_title`       | string  | Title of the medical publication                    |
| `publication_date`        | date    | Publication date                                    |
| `medication_side_effects` | string  | Observed side effects of medications                |
| `allergies`               | string  | Patient's known allergies                           |
| `medical_conditions`      | string  | Relevant medical conditions                         |
| `family_medical_history`  | string  | Family medical history                              |
| `genetic_data`            | string  | Relevant genetic data                               |
| `treatment_outcome`       | string  | Current outcome of the treatment                    |
| `medication_adherence`    | string  | Patient's adherence to prescribed medication        |
| `patient_satisfaction`    | string  | Patient's satisfaction with care received           |
| `readmission_risk`        | float   | Calculated risk of patient readmission              |
| `medical_error_rate`      | float   | Rate of medical errors in patient's care            |
| `patient_outcome_score`   | float   | Score representing overall patient outcome          |
| `cost_of_care`            | float   | Total cost of care for the patient                  |
| `length_of_stay`          | integer | Length of hospital stay in days                     |
| `medication_cost`         | float   | Total cost of patient's medications                 |
| `total_cost_savings`      | float   | Total cost savings achieved for the patient         |
| `medication_recommendation` | string | Recommended medication                             |
| `treatment_recommendation`  | string | Recommended treatment                              |

## Implementation Details

### Schema Definition

The connector defines a simple schema with a single table `cds_records` and specifies `record_id` as the primary key.

```python
def schema(configuration: dict):
    # Return minimal schema with ONLY table name and primary key
    return [
        {
            "table": "cds_records",
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
   mkdir cds && cd cds
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
✓ Detected table name: cds_records
===========================================================
         Fivetran Connector Debug & Reset Script          
===========================================================

This will reset your connector, delete current state and warehouse.db files.
Do you want to continue? (Y/n): y

Step 1: Resetting Fivetran connector...
✓ Reset successful

Step 2: Running debug with configuration...
(Real-time output will be displayed below)

May 18, 2025 07:50:42 AM INFO Fivetran-Connector-SDK: Debugging connector at: /path/to/connector
May 18, 2025 07:50:42 AM INFO Fivetran-Connector-SDK: Running connector tester...
May 18, 2025 07:50:43 AM INFO Fivetran-Connector-SDK: Initiating the 'schema' method call...
May 18, 2025 07:50:45 AM: INFO Fivetran-Tester-Process: [SchemaChange]: tester.cds_records 
May 18, 2025 07:50:45 AM INFO Fivetran-Connector-SDK: Initiating the 'update' method call...

May 18, 2025 07:50:45 AM INFO: Fetching data with params: {'page_size': 100}
May 18, 2025 07:50:46 AM INFO: Checkpoint saved after 100 records
May 18, 2025 07:50:46 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': 'f3eeb6082a54bcabed4c44cfbcdb6452'}
...
May 18, 2025 07:50:47 AM INFO: Checkpoint saved after 700 records
May 18, 2025 07:50:47 AM INFO: Fetching data with params: {'page_size': 100, 'cursor': '6002fb76bd111a9bf2c81d48d844e386'}
May 18, 2025 07:50:47 AM INFO: No more pages to fetch

✓ Debug completed

Step 3: Querying sample data from DuckDB...
Running query: SELECT * FROM tester.cds_records LIMIT 5;

┌──────────────────────┬──────────────────┬──────────────────┬───┬───────────────────┬────────────────┬────────────────────┬──────────────────────┐
│      record_id       │    allergies     │   vital_signs    │ … │ treatment_outcome │ length_of_stay │ medical_error_rate │  medical_conditions  │
│       varchar        │     varchar      │     varchar      │   │      varchar      │     int64      │       float        │       varchar        │
├──────────────────────┼──────────────────┼──────────────────┼───┼───────────────────┼────────────────┼────────────────────┼──────────────────────┤
│ a0d9d670-1bdc-434e…  │ Life-Threatening │ Life-Threatening │ … │ Ongoing           │             41 │               0.74 │ Heart Disease        │
│ ddf4f953-81c4-47e5…  │ Life-Threatening │ Unstable         │ … │ Successful        │             32 │               0.18 │ Hypertension         │
│ 21bb3ee1-6b48-446b…  │ None             │ Stable           │ … │ Partial Success   │             60 │                0.8 │ Cancer               │
│ 97ebfaa8-efb2-4eb2…  │ None             │ Unstable         │ … │ Successful        │            112 │               0.65 │ Cancer               │
│ acab90e0-49df-4405…  │ Mild             │ Unstable         │ … │ Unsuccessful      │            155 │               0.58 │ Neurological Disor…  │
└──────────────────────┴──────────────────┴──────────────────┴───┴───────────────────┴────────────────┴────────────────────┴──────────────────────┘

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
Next sync state: {"next_cursor": "6002fb76bd111a9bf2c81d48d844e386"}
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
   - A unique name for your connector (e.g., cds_new_custom_connector)

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
The connection 'cds_new_custom_connector' has been created successfully.
Python Version: 3.12.8
Connection ID: know_barman
Visit the Fivetran dashboard to start the initial sync: https://fivetran.com/dashboard/connectors/know_barman/status
```

### What to Expect After Deployment

After successful deployment:

1. The connector will be created in your Fivetran account with a randomly generated Connection ID (e.g., `know_barman`)
2. You'll be provided a link to access the connector in the Fivetran dashboard
3. The connector will be ready for its initial sync

In the Fivetran dashboard, you will be able to:
- View your connector's sync status
- Configure sync frequency (hourly, daily, etc.)
- Monitor for any errors or warnings
- View the destination schema with the `cds_records` table in Snowflake
- Track the data volume and record count
- Configure schema and field mapping if needed

The first sync will extract all available data, while subsequent syncs will be incremental, only fetching new or changed records based on the stored cursor position.

## Maintenance and Troubleshooting

### Common Issues

- **API Key Issues**: Ensure your API key is valid and has the correct permissions
- **Network Connectivity**: Check that your network can reach the CDS API endpoint
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

1. If the CDS API adds new fields, you can capture them automatically. Since the connector uses the entire record for upserts, new fields will be included without schema changes.

2. To add transformations or derived fields:
   ```python
   # Example of adding a derived field in the update function
   for record in records:
       # Add a derived field based on existing data
       record['treatment_risk_score'] = record['medical_error_rate'] * (1 - record['patient_outcome_score']) if record['patient_outcome_score'] > 0 else 0
       yield op.upsert("cds_records", record)
   ```

### Supporting Multiple Tables

1. Update the schema function to define additional tables:
   ```python
   def schema(configuration: dict):
       return [
           {
               "table": "cds_records",
               "primary_key": ["record_id"]
           },
           {
               "table": "cds_patients",
               "primary_key": ["patient_id"]
           }
       ]
   ```

2. Modify the update function to yield operations for multiple tables:
   ```python
   # Example: Creating patient records from CDS data
   patient_records = {}
   for record in records:
       # Extract patient info for separate table
       patient_id = record['patient_id']
       if patient_id not in patient_records:
           patient_records[patient_id] = {
               'patient_id': patient_id,
               'medical_history': record['medical_history'],
               'current_medications': record['current_medications'],
               'allergies': record['allergies'],
               'medical_conditions': record['medical_conditions']
           }
       # Yield the original record
       yield op.upsert("cds_records", record)
   
   # Yield all unique patient records
   for patient in patient_records.values():
       yield op.upsert("cds_patients", patient)
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

## Downstream Application: MedMind

The data extracted by this connector powers MedMind, an AI-driven clinical decision support system designed for healthcare providers. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in the healthcare industry.

### Application Purpose

MedMind helps healthcare providers:
- Deliver data-driven, personalized patient care recommendations
- Reduce medical errors through improved decision support
- Improve patient outcomes with evidence-based treatment recommendations
- Optimize resource utilization and reduce healthcare costs
- Transform clinical decision-making into a data-informed process

### Target Users

- Physicians and Clinicians
- Hospital Administrators
- Quality Improvement Teams
- Care Coordinators
- Clinical Researchers

### Data Flow Architecture

1. **Data Sources** → 2. **CDS API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Healthcare Data Sources

The CDS API provides synthetic data that simulates information from various healthcare systems:

- **Electronic Health Records (EHRs)**: 
  - Epic Systems Corporation
  - Cerner
  - Meditech
- **Clinical Trials**: 
  - ClinicalTrials.gov
  - National Institutes of Health (NIH)
- **Medical Literature**: 
  - PubMed
  - National Library of Medicine

This approach allows for realistic healthcare analytics without using protected health information (PHI), making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The MedMind application provides:
- Key performance indicators including patient outcome scores, medical error rates, readmission risks, and cost savings
- Financial metrics like cost of care, medication costs, and length of stay
- Distribution analysis for patient outcomes and treatment success rates
- Patient satisfaction monitoring
- AI-powered insights for overall performance, optimization opportunities, financial impact, and strategic recommendations
- Data exploration tools for detailed record examination

### Benefits

The application delivers significant clinical and financial value:
- 10% reduction in medical errors: 1,000 fewer medical errors/year
- 15% improvement in patient outcomes: 300 fewer complications/year
- 20% reduction in hospital readmissions: 200 fewer readmissions/year
- 5% reduction in healthcare costs: $500,000 savings/year

## Notes

- This connector creates a single table named `cds_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector uses cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The CDS API returns approximately 750 healthcare clinical decision support records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the MedMind clinical decision support application
- While this connector uses synthetic data, the approach mirrors real-world healthcare data extraction patterns
