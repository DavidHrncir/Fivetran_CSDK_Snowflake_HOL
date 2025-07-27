# Agriculture Animal Health Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Agriculture Animal Health data from a custom API and load it into Snowflake via Fivetran, powering advanced agricultural animal health monitoring and farm management systems.  This file contains the use cases behind this connector. For lab day instructions see the **[agr-lab-guide.md](../agr-lab-guide.md)**.

## Overview

The Agriculture Animal Health connector fetches livestock health and environmental data from a REST API and loads it into a single table called `agr_records` in your Snowflake database. The connector retrieves detailed information about farm animals, health status monitoring, vaccination tracking, environmental conditions, and AI-powered health risk predictions, including properties like predicted health risks, medication histories, weather impacts, and recommended care actions. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

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
- `x-api-key`: The name of the key to be added to the header.

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

### Sample Record
```bash
{
    "age": 5,
    "animal_id": "ANIMAL_000000",
    "breed": "Brahman",
    "farm_id": "FARM_000000",
    "health_status": "Healthy",
    "humidity": 68.71,
    "last_updated_epoch": 1748797200,
    "medication_history": "Previous",
    "precipitation": 97.32,
    "predicted_health_risk": 0.87,
    "recommended_action": "Monitor closely",
    "record_id": "42e76305-0fdf-44a6-aa5a-f5c767086027",
    "species": "Beef Cattle",
    "temperature": 8.15,
    "vaccination_history": "Overdue",
    "weather_data": "Snowy",
    "weight": 1338.71
}
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
