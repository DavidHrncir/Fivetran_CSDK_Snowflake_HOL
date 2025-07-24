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
├── connector.py           # Main connector implementation (blank by default)
├── agr_manual.env         # The file containing the environment variables to be set, copied, and run in the OS's terminal
├── setenv.bat             # (for Windows) Script to set the environment in the CMD terminal
├── setenv.sh              # (for Mac) Script to set the environment in the zsh terminal
├── agr.env                # The file containing the environment variables for the above 'setenv' scripts above (blank by default)
├── workingconnectorpy.txt # A working copy of the the connector.py file for this vertical
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
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

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
| `last_updated_epoch`               | number  | Epoch value for the last updated date in epoch form |

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

### Local Development Setup

1. Create the project directory:
On a Windows or Mac, create the `agriculture` folder in a folder that does not reside under a system folder such as "My Documents"

2. Download the required files from the git repo:
   - `agr.env`: Environment variables loading file used for environment scripts
   - `agr_alt.env`: Environment variables list that can manually be run in a terminal
   - `configuration.json`: Configure your API credentials and settings
   - `connector.py`: Implement the connector using the Fivetran SDK
   - `requirements.txt`: Python requirements file
   - `setenv.bat`: (Windows only; cmd terminal) script to set environment variables
   - `setenv.sh`: (Mac only; zsh terminal) script to set environment variables
   - `workingconnectorpy.txt`: A working copy of the connector code
   - Once the above files are downloaded copy/move them to the newly created `agriculture` folder

3. Make the scripts executable (Mac only):
   ```bash
   chmod +x setenv.sh
   ```

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

1. Update the schema function to define additional tables (requires SDK testing API to be updated first):
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