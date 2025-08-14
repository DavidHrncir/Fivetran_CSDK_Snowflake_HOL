# PHR Pharma Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Pharmaceutical Research (PHR) data from an API and load it into Snowflake via Fivetran, powering advanced clinical trial optimization and pharmaceutical research analytics applications. For lab day instructions see the **[rdp-lab-guide.md](../rdp-lab-guide.md)**.

## Overview

The PHR Pharma connector fetches clinical trial records from a REST API and loads them into a single table called `phr_records` in your Snowflake database. The connector retrieves detailed information about clinical trials, patient enrollment, protocol data, and regulatory status. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## PHR API Details

### Endpoint

The connector uses the following REST API endpoint to access pharmaceutical clinical trial data:

- `GET /phr_data`: Retrieves a paginated list of clinical trial records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

### Data Schema

The PHR API returns records with the following structure:

| Field                        | Type      | Description                                   |
|------------------------------|-----------|-----------------------------------------------|
| `record_id`                  | string    | Unique identifier for the record (primary key) |
| `trial_id`                   | string    | Unique identifier for the clinical trial      |
| `protocol_id`                | string    | Protocol identifier for the trial            |
| `trial_name`                 | string    | Descriptive name of the clinical trial       |
| `sponsor_name`               | string    | Name of the trial sponsor organization        |
| `disease_area`               | string    | Medical specialty (e.g., Dermatology, Ophthalmology, Hematology) |
| `patient_id`                 | string    | Unique identifier for the patient             |
| `patient_age`                | integer   | Patient's age at enrollment                   |
| `patient_gender`             | string    | Patient's gender                              |
| `enrollment_date`            | string    | Date when patient was enrolled in the trial  |
| `site_id`                    | string    | Unique identifier for the clinical trial site |
| `site_name`                  | string    | Name of the clinical trial site              |
| `regulatory_approval_status` | string    | Current regulatory approval status            |
| `trial_status`               | string    | Current status of the clinical trial         |
| `protocol_amendment_date`    | string    | Date of the most recent protocol amendment   |
| `enrollment_rate`            | float     | Patient enrollment rate for the trial        |
| `dropout_rate`               | float     | Patient dropout rate for the trial           |
| `last_updated_epoch`         | number  | Epoch value for the last updated date in epoch form |

### Sample Record
```bash
{
    "disease_area": "Immunology",
    "dropout_rate": 24.3023082354,
    "enrollment_date": "2025-06-17",
    "enrollment_rate": 99.7464688479,
    "last_updated_epoch": 1748797200,
    "patient_age": 79,
    "patient_gender": "Male",
    "patient_id": "PATIENT_000000",
    "protocol_amendment_date": "2025-02-19",
    "protocol_id": "PROTOCOL_000000",
    "record_id": "b2e363a9-18cd-4b42-b731-6f5fec91f22c",
    "regulatory_approval_status": "On Hold",
    "site_id": "SITE_000000",
    "site_name": "Contract Research Organization",
    "sponsor_name": "Academic Institution",
    "trial_id": "TRIAL_000000",
    "trial_name": "Pain Management",
    "trial_status": "Inactive"
}
```

## Downstream Application: TrialGenius

The data extracted by this connector powers TrialGenius, an AI-powered clinical trial design and optimization system designed for pharmaceutical companies. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in pharmaceutical research.

### Application Purpose

TrialGenius helps pharmaceutical companies:
- Reduce clinical trial costs and timelines through AI-powered optimization
- Improve patient recruitment and retention rates
- Optimize protocol design based on historical trial data
- Minimize trial failure risk through predictive analytics
- Transform reactive trial management into proactive optimization
- Generate synthetic control arms for rare disease studies

### Target Users

- **Primary**: Chief Medical Officer, VP of Clinical Development, Clinical Operations Directors
- **Secondary**: Biostatisticians, Regulatory Affairs Directors, Clinical Data Managers
- **Tertiary**: Site Investigators, Clinical Research Associates, Patient Recruitment Specialists
- **Top C-Level Executive**: Chief Medical Officer (CMO)

### Data Flow Architecture

1. **Data Sources** → 2. **PHR API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Pharmaceutical Data Sources

The PHR API provides synthetic data that simulates information from various pharmaceutical and clinical trial systems:

- **Clinical Trial Management Systems (CTMS)**:
  - Veeva Vault CTMS
  - Oracle Clinical One
  - Medidata Rave
- **Electronic Data Capture (EDC)**:
  - Medidata Rave EDC
  - Oracle Clinical One Data Collection
  - Veeva Vault EDC
- **Real-World Evidence Databases**:
  - Flatiron Health
  - IQVIA Real-World Data
  - Optum Clinformatics
- **Regulatory Databases**:
  - FDA Orange Book
  - EMA Clinical Data Publication Policy
  - ClinicalTrials.gov
- **Patient Registries**:
  - TriNetX
  - IBM Watson Health
  - Syapse
- **Genomic Databases**:
  - gnomAD
  - UK Biobank
  - All of Us Research Program

This approach allows for realistic pharmaceutical analytics without using protected patient information, making it ideal for demonstration, development, and training purposes.

### Expected Business Results

TrialGenius powered by this connector delivers:

- **40% reduction in trial failure risk**
  - 100 trials/year × 90% baseline failure rate × 40% reduction = 36 fewer failed trials/year
- **$520 million in development cost savings annually**
  - $2.6 billion average cost per drug × 20% cost reduction = $520 million savings per approved drug
- **30% improvement in patient enrollment timelines**
  - 18 months average enrollment time × 30% improvement = 5.4 months faster enrollment
- **50% reduction in protocol amendment frequency**
  - Average 3 amendments per trial × 50% reduction = 1.5 fewer amendments per trial

### Analytics Capabilities

The TrialGenius application provides:
- Real-time analysis of clinical trial performance and enrollment metrics
- AI-driven trial optimization and protocol design recommendations
- Predictive analytics for patient recruitment and retention forecasting
- Comprehensive dashboards for clinical trial performance indicators
- Advanced simulation capabilities for trial scenario modeling
- Intelligent protocol amendment suggestions based on emerging data patterns

### Competitive Advantage

TrialGenius differentiates from traditional clinical trial optimization through its generative AI capability to create novel trial designs rather than simply analyzing existing ones. Unlike conventional statistical modeling tools, it generates synthetic patient populations and simulates thousands of trial scenarios simultaneously, enabling pharmaceutical companies to identify optimal trial parameters before patient enrollment begins. This proactive approach reduces trial failure risk by 40% compared to reactive optimization methods.

## Business Use Cases

This connector enables several key pharmaceutical analytics use cases:

### Clinical Trial Optimization
- **Patient Recruitment Analysis**: Identify optimal sites and patient populations based on historical enrollment data
- **Protocol Design**: Analyze historical trial data to improve future protocol designs and reduce amendment frequency
- **Risk Assessment**: Predict trial failure risks based on enrollment patterns, dropout rates, and site performance
- **Site Selection**: Evaluate site performance metrics to optimize future trial site selection

### Regulatory Compliance
- **Audit Trails**: Complete history of protocol amendments and regulatory approvals
- **Reporting**: Automated regulatory reporting and compliance monitoring
- **Data Integrity**: Validated data pipelines for regulatory submissions
- **Amendment Tracking**: Monitor protocol amendment frequency and timing patterns

### Operational Analytics
- **Enrollment Forecasting**: Predict patient enrollment timelines based on historical patterns
- **Cost Optimization**: Analyze trial costs and identify opportunities for efficiency improvements
- **Resource Planning**: Optimize resource allocation across multiple concurrent trials
- **Performance Benchmarking**: Compare trial performance against industry standards

### Real-World Evidence Integration
- **Outcomes Analysis**: Compare trial results with real-world patient outcomes
- **Safety Monitoring**: Post-market surveillance and adverse event tracking
- **Market Access**: Evidence generation for payer negotiations and market access strategies
- **Comparative Effectiveness**: Analyze trial data against real-world treatment patterns

## Notes

- This connector creates a single table named `phr_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The PHR API returns approximately 600 clinical trial records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the TrialGenius pharmaceutical application
- While this connector uses synthetic data, the approach mirrors real-world pharmaceutical data extraction patterns
- The connector includes comprehensive error handling for common pharmaceutical API scenarios
- Built-in safety mechanisms prevent infinite loops and handle rate limiting automatically
- Supports Python 3.12 runtime environment in Fivetran cloud infrastructure