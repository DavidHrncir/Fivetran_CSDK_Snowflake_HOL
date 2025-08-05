# HED Higher Education Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Higher Education Data (HED) from an API and load it into Snowflake via Fivetran, powering advanced student success and retention analytics applications. For lab day instructions see the **[rdp-lab-guide.md](../rdp-lab-guide.md)**.

## Overview

The HED Higher Education connector fetches student academic and engagement records from a REST API and loads them into a single table called `hed_records` in your Snowflake database. The connector retrieves detailed information about student performance, engagement metrics, academic standing, and intervention data. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## HED API Details

### Endpoint

The connector uses the following REST API endpoint to access higher education student data:

- `GET /hed_data`: Retrieves a paginated list of Higher Education student records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

### Data Schema

The HED API returns records with the following structure:

| Field                    | Type      | Description                                   |
|--------------------------|-----------|-----------------------------------------------|
| `record_id`              | string    | Unique identifier for the record (primary key) |
| `student_id`             | string    | Unique identifier for the student             |
| `enrollment_date`        | timestamp | Date when the student enrolled                |
| `academic_standing`      | string    | Current academic standing of the student      |
| `current_gpa`            | number    | Student's current GPA                         |
| `credit_hours_attempted` | number    | Total credit hours attempted                  |
| `credit_hours_earned`    | number    | Total credit hours earned                     |
| `major_code`             | string    | Student's major code                          |
| `advisor_id`             | string    | Unique identifier for the student's advisor   |
| `financial_aid_amount`   | number    | Amount of financial aid received              |
| `last_login_date`        | timestamp | Date of student's last system login          |
| `total_course_views`     | number    | Total number of course page views             |
| `assignment_submissions` | number    | Number of assignments submitted               |
| `discussion_posts`       | number    | Number of discussion forum posts              |
| `avg_assignment_score`   | number    | Average score on assignments                  |
| `course_completion_rate` | number    | Rate of course completion                     |
| `plagiarism_incidents`   | number    | Number of plagiarism incidents                |
| `writing_quality_score`  | number    | Score indicating writing quality              |
| `engagement_score`       | number    | Overall student engagement score              |
| `at_risk_flag`           | boolean   | Flag indicating if student is at risk         |
| `intervention_count`     | number    | Number of interventions performed             |
| `last_updated`           | timestamp | Date when the record was last updated         |

### Sample Record
```bash
Here is a sample record:
{
    "academic_standing": "Satisfactory Progress",
    "advisor_id": "ADV_1131",
    "assignment_submissions": 11,
    "at_risk_flag": false,
    "avg_assignment_score": 54.9,
    "course_completion_rate": 0.99,
    "credit_hours_attempted": 16,
    "credit_hours_earned": 15,
    "current_gpa": 3.13,
    "discussion_posts": 25,
    "engagement_score": 63.9,
    "enrollment_date": "2024-08-11 0:00:00",
    "financial_aid_amount": 13793.33,
    "intervention_count": 2,
    "last_login_date": "2025-07-27 14:28:37",
    "last_updated": "2025-07-31 23:57:37",
    "last_updated_epoch": 1748797200,
    "major_code": "PHIL",
    "plagiarism_incidents": 0,
    "record_id": "076cc9ae-6c0b-43fd-8d78-277fec3d0a8a",
    "student_id": "STU_202400000",
    "total_course_views": 144,
    "writing_quality_score": 79.3
}
```

## Downstream Application: StudentSuccess

The data extracted by this connector powers StudentSuccess, an AI-driven freshman retention insights system designed for higher education institutions. The application is built as a Streamlit in Snowflake data application, utilizing both Fivetran and Cortex for data integration and analysis in higher education.

### Application Purpose

StudentSuccess helps higher education institutions:
- Improve freshman retention rates through predictive analytics
- Reduce time to identify at-risk students
- Minimize intervention costs through targeted support
- Increase student success through data-driven insights
- Transform reactive academic advising into proactive student support

### Target Users

- Academic Advisors
- Student Success Coordinators
- Enrollment Management Teams
- Provost and Vice President of Student Affairs
- Academic Success Analysts

### Data Flow Architecture

1. **Data Sources** → 2. **HED API** → 3. **Fivetran Custom Connector** → 4. **Snowflake Data Warehouse** → 5. **Streamlit in Snowflake Application**

### Simulated Higher Education Data Sources

The HED API provides synthetic data that simulates information from various higher education systems:

- **Student Information Systems**: 
  - Banner
  - PeopleSoft
  - Colleague
- **Learning Management Systems**: 
  - Canvas
  - Blackboard
  - Moodle
- **Academic Integrity Systems**: 
  - Turnitin
  - SafeAssign
- **Engagement Analytics**: 
  - BrightBytes
  - Civitas Learning

This approach allows for realistic higher education analytics without using protected student information, making it ideal for demonstration, development, and training purposes.

### Analytics Capabilities

The StudentSuccess application provides:
- Real-time analysis of student performance and engagement metrics
- AI-driven student success predictions and retention analytics
- Early intervention identification and recommendation systems
- Comprehensive dashboards for academic performance indicators
- Predictive analytics for student outcome forecasting
- Advanced agent workflows for transparent student success analysis

## Notes

- This connector creates a single table named `hed_records` in your Snowflake database
- The connector uses checkpoints to track sync progress, enabling resumable syncs
- The connector is configured to use cursor-based pagination for efficient data extraction
- During initial sync, all records will be loaded; subsequent syncs will only fetch new or updated records
- The HED API returns approximately 600 higher education student records in a complete dataset
- The connector handles paginated requests with a default of 100 records per page
- The data is optimized for use with Snowflake and the StudentSuccess higher education application
- While this connector uses synthetic data, the approach mirrors real-world higher education data extraction patterns