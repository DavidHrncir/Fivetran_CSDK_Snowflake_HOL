# Oil and Gas FTS Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Oil and Gas Field Technician Task Summarization (FTS) data from a custom API and load it into Snowflake via Fivetran, powering LogLynx and other advanced field operations analytics applications. For lab day instructions see the **[fts-lab-guide.md](../fts-lab-guide.md)**.

## Overview

The Oil and Gas FTS connector fetches field technician task summaries from a REST API and loads them into a single table called `fts_records` in your Snowflake database. The connector retrieves detailed information about technician logs, maintenance activities, equipment servicing, and AI-generated task summaries, including properties like maintenance costs, downtime hours, failure rates, and time savings from automated summarization. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## FTS API Details

### Endpoint

The connector uses the following REST API endpoint to access field technician task summarization data:

- `GET /fts_data`: Retrieves a paginated list of Oil and Gas Field Technician Task Summarization records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

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
| `last_updated_epoch`               | number  | Epoch value for the last updated date in epoch form |

### Sample Record
```bash
{
    "customer_id": "CUST_000600",
    "downtime_hours": 4,
    "equipment_id": "EQUIP_000600",
    "erp_order_id": "ORDER_000600",
    "failure_rate": 0.67,
    "last_updated_epoch": 1748970000,
    "log_date": "2026-02-17",
    "log_description": "Performed routine maintenance on equipment",
    "maintenance_cost": 759.88,
    "maintenance_status": "Cancelled",
    "maintenance_type": "Reliability-Centered Maintenance",
    "record_id": "65b2df8b-1fe4-4095-9de6-f2dd0a42b817",
    "summarization_time_saved": 4,
    "summarized_log": "Issue resolved",
    "technician_id": "TECH_000600"
}
```

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