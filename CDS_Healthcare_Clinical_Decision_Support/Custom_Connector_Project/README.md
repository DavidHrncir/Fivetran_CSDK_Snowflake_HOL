# Healthcare Clinical Decision Support (CDS) Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Healthcare Clinical Decision Support (CDS) data from a custom API and load it into Snowflake via Fivetran, powering advanced healthcare analytics and AI-driven clinical decision support applications. For lab day instructions see the **[cds-lab-guide.md](../cds-lab-guide.md)**.

## Overview

The Healthcare CDS connector fetches clinical decision support records from a REST API and loads them into a single table called `cds_records` in your Snowflake database. The connector retrieves detailed information about patient records, medical histories, lab results, diagnoses, treatments, clinical trials, and various healthcare performance metrics. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## CDS API Details

### Endpoint

The connector uses the following REST API endpoint to access healthcare clinical decision support data:

- `GET /cds_data`: Retrieves a paginated list of Clinical Decision Support records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

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
| `medication_adherence`      | string  | Patient's adherence to prescribed medication        |
| `patient_satisfaction`      | string  | Patient's satisfaction with care received           |
| `readmission_risk`          | float   | Calculated risk of patient readmission              |
| `medical_error_rate`        | float   | Rate of medical errors in patient's care            |
| `patient_outcome_score`     | float   | Score representing overall patient outcome          |
| `cost_of_care`              | float   | Total cost of care for the patient                  |
| `length_of_stay`            | integer | Length of hospital stay in days                     |
| `medication_cost`           | float   | Total cost of patient's medications                 |
| `total_cost_savings`        | float   | Total cost savings achieved for the patient         |
| `medication_recommendation` | string | Recommended medication                             |
| `treatment_recommendation`  | string | Recommended treatment                              |
| `last_updated_epoch`        | number  | Epoch value for the last updated date in epoch form |

### Sample Record
```bash
{
    "allergies": "Life-Threatening",
    "clinical_trial_id": "Trial_000000",
    "cost_of_care": 54931.53,
    "current_medications": "Atorvastatin",
    "diagnosis": "Asthma",
    "family_medical_history": "Stroke",
    "genetic_data": "None",
    "lab_results": "Life-Threatening",
    "last_updated_epoch": 1748797200,
    "length_of_stay": 41,
    "medical_conditions": "Heart Disease",
    "medical_error_rate": 0.74,
    "medical_history": "Heart Disease",
    "medical_publication_id": "Publication_000000",
    "medication_adherence": "Non-Adherent",
    "medication_cost": 9453.1,
    "medication_recommendation": "Ibuprofen",
    "medication_side_effects": "Severe",
    "patient_id": "Patient_000000",
    "patient_outcome_score": 0.1,
    "patient_satisfaction": "Satisfied",
    "publication_date": "2024-11-19",
    "publication_title": "Publication 1",
    "readmission_risk": 0.02,
    "record_id": "a0d9d670-1bdc-434e-8ef4-39eafec4907f",
    "total_cost_savings": 36727.2,
    "treatment_outcome": "Ongoing",
    "treatment_plan": "Surgery",
    "treatment_recommendation": "Lifestyle Changes",
    "trial_name": "Trial 2",
    "trial_status": "Enrolling",
    "vital_signs": "Life-Threatening"
}
```

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
