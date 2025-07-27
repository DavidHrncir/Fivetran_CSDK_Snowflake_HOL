# Insurance ICP Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Insurance Claims Processing (ICP) data from a custom API and load it into Snowflake via Fivetran, powering advanced insurance analytics applications. For lab day instructions see the **[icp-lab-guide.md](../icp-lab-guide.md)**.

## Overview

The Insurance ICP connector fetches claims processing records from a REST API and loads them into a single table called `icp_records` in your Snowflake database. The connector retrieves detailed information about insurance claims processing, including properties like claim status, processing metrics, customer satisfaction data, and operational costs. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## ICP API Details

### Endpoint

The connector uses the following REST API endpoint to access insurance claims data:

- `GET /icp_data`: Retrieves a paginated list of Insurance Claims Processing records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

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
| `last_updated_epoch`               | number  | Epoch value for the last updated date in epoch form |

### Sample Record
```bash
{
    "claim_amount": 38079.4717658889,
    "claim_category": "Vandalism",
    "claim_date": "2024-10-17",
    "claim_description": "Vandalism",
    "claim_id": "CLAIM_000000",
    "claim_outcome": "Denied",
    "claim_outcome_confidence": 0.6791716995,
    "claim_outcome_date": "2024-07-05",
    "claim_outcome_probability": 0.5032204149,
    "claim_processing_duration": 39,
    "claim_processing_end_date": "2024-10-31",
    "claim_processing_error": false,
    "claim_processing_error_reduction": 21.6135812311,
    "claim_processing_notes": "Notes 0",
    "claim_processing_start_date": "2024-08-20",
    "claim_processing_time": 12.5729060301,
    "claim_processing_time_reduction": 7.2574798045,
    "claim_status": "Reopened",
    "claim_status_history": "Status 0",
    "claim_subcategory": "Lightning",
    "claim_type": "Flood",
    "customer_email": "customer0@example.com",
    "customer_id": "CUSTOMER_000000",
    "customer_interaction_history": "Interaction 0",
    "customer_name": "Customer 0",
    "customer_satisfaction_rating": 2,
    "customer_satisfaction_rating_improvement": 5,
    "customer_segment": "Commercial",
    "last_updated_epoch": 1748797200,
    "operational_cost": 2836.7727367756,
    "operational_cost_reduction": 4935.091826606,
    "policy_effective_date": "2024-10-09",
    "policy_id": "POLICY_000000",
    "record_id": "e4fd12be-10f1-4306-8a21-3abe5a9ddb36"
}
```

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
