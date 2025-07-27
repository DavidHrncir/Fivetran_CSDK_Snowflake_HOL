# Manufacturing MSO Fivetran Custom Connector

This connector uses the Fivetran Connector SDK to extract Manufacturing Material Supply Optimization (MSO) data from a custom API and load it into Snowflake via Fivetran, powering advanced manufacturing analytics applications. For lab day instructions see the **[mso-lab-guide.md](../mso-lab-guide.md)**.

## Overview

The Manufacturing MSO connector fetches material optimization records from a REST API and loads them into a single table called `mso_records` in your Snowflake database. The connector retrieves detailed information about material selection and optimization for manufacturing products, including properties like material characteristics, product performance metrics, cost savings, and design parameters. It handles authentication, pagination, error handling, and maintains state between sync runs using a cursor-based approach.

## MSO API Details

### Endpoint

The connector uses the following REST API endpoint to access manufacturing materials data:

- `GET /mso_data`: Retrieves a paginated list of Manufacturing MSO records

### Query Parameters

- `cursor`: The cursor for the next page of results (used for pagination)
- `page_size`: The number of records to return per page (1-200, defaults to 100)
- `has_more`: The return flag along with the cursor describes whether or not a callback is needed (boolean)

### Authentication

The API uses API key authentication, with the key passed in the request header:
- `x-api-key`: The name of the key to be added to the header.

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
| `last_updated_epoch`               | number  | Epoch value for the last updated date in epoch form |

### Sample Record
```bash
{
    "cad_file_name": "File 1.dwg",
    "cad_system": "Autodesk Inventor",
    "cost_savings": 527.3108956424,
    "density": 4.058131129,
    "designer_experience": 12,
    "designer_id": "DES_0000",
    "designer_name": "Designer 1",
    "designer_skill_level": "Intermediate",
    "last_updated_epoch": 1748797200,
    "material_cost": 102.9187119751,
    "material_id": "MTRL_0000",
    "material_name": "Material 1",
    "material_optimization_date": "2024-04-29",
    "material_optimization_recommendation": "Recommended",
    "material_optimization_score": 0.9039157259,
    "material_selection_date": "2024-04-28",
    "material_selection_recommendation": "Recommended",
    "material_selection_score": 0.9335058035,
    "material_waste": 6.0330629414,
    "material_weight": 67.5975964267,
    "performance_improvement": 94.8842301476,
    "poissons_ratio": 0.3076327141,
    "product_description": "Description of Product 1",
    "product_id": "PRD_0000",
    "product_lifecycle_stage": "Production",
    "product_lifecycle_status": "Active",
    "product_name": "Product 1",
    "product_performance": 900.7847057252,
    "record_id": "22eea48a-60c3-41ed-96be-34352d4c10b9",
    "waste_reduction": 5.9535572251,
    "weight_reduction": 12.6936057674,
    "youngs_modulus": 12572.906030128
}
```

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
