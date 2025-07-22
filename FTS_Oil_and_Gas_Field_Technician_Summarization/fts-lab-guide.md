# Fivetran Connector SDK Hands on Lab with Snowflake 2025: Oil and Gas Field Technician Summarization

## Overview
In this hands on lab, you'll build a **custom Fivetran connector** using the **Fivetran Connector SDK** and the **LLM service of your choice** to integrate this vertical's data from a custom REST API into Snowflake. You'll then create a **Streamlit (in Snowflake)** application with various tools and dashboards powering this vertical's metrics which includes a **Snowflake Cortex AI-driven** feature to drive even deeper analytics, descriptive, and prescriptive insights.

The Oil and Gas FTS custom connector should fetch field technician records from a REST API and load them into a single table called `fts_records` in your Snowflake database. The connector should deliver detailed information about field operations, maintenance activities, and technician log summarization for oil and gas operations, including properties like failure rates, maintenance costs, downtime hours, and summarization time savings. It should handle authentication, pagination, error handling, and maintain state between sync runs using a cursor-based approach.

## Lab Steps Quick Access

- [Step 1: Create a Custom Connector with the Fivetran Connector SDK](#step-1-create-a-custom-connector-with-the-fivetran-connector-sdk)
- [Step 2: Start Data Sync in Fivetran](#step-2-start-data-sync-in-fivetran)
- [Step 3: Create a Streamlit in Snowflake Gen AI Data App](#step-3-create-a-streamlit-in-snowflake-gen-ai-data-app)

## Lab Environment
- Machine with Python 3.9 - 3.12 loaded and ready with an environment pre-created
- Chrome browser or equivalent
- Browser tabs (leave them open throughout the lab):
  - Tab 1: GitHub Lab Repo: Lab Guide
  - Tab 2: [Fivetran: Automated Data Movement Platform](https://www.fivetran.com/login)
  - Tab 3: [Snowflake: Data and AI Platform](https://aa67604.us-central1.gcp.snowflakecomputing.com/console/login#/)
  - Tab 4: [Fivetran Connector SDK Docs](https://fivetran.com/docs/connector-sdk)

## Step 1: Create a Custom Connector with the Fivetran Connector SDK (8 minutes)

### 1.1 Generate the Custom Connector Code Using AI Code Generation Assistance
1. Switch to **Chrome Tab 2 (Anthropic Workbench)**
2. Copy and paste the following **User prompt** into the workbench:

<details>
  <summary>Click to expand the User prompt and click the Copy icon in the right corner</summary>

```
- Provide a custom connector for Oil and Gas for the fts_data endpoint. 1 table called fts_records - all columns.  
- Make sure you copy the configuration.json file exactly - do not add any other variables to it.
- Here is the API spec: https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fts_api_spec
```
</details>

3. Click the black **Run** button in the upper right
4. After Claude generates the connector.py code, you will see a response similar to the example connector, but updated for the oil and gas field technician summarization dataset.
5. Click [fts_data](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fts_data) if you'd like to see the dataset.

### 1.2 Debug and Deploy the Custom Connector in VS Code
1. When you see the connector.py code generated in the Anthropic Workbench, click the **Copy** button in the upper right of the code connector.py code block
2. Go to **VS Code** with Command + Tab or open from the dock
3. Click on the `connector.py` file in your project
4. Press Command+V to paste the connector code into the `connector.py` file
5. Save the updated `connector.py` by pressing Command+S
6. To test your code locally with configuration values specified in `configuration.json`, you can run the default Fivetran Connector SDK debug command:  
   `fivetran debug --configuration configuration.json`  
   This command provides out-of-the-box debugging without any additional scripting. 
7. We have created a helper script to debug and validate your connector with enhanced logging, state clearing and data validation. To run the helper script please run it in the VS Code terminal (bottom right). You can copy the `debug_and_validate` command using the icon on the right:

```
./debug_and_validate.sh
```

8. When prompted with "Do you want to continue? (Y/N):", type `Y` and press Enter.

    - You'll see output displaying the results of the debug script including:

        - Resets the connector state by deleting the existing warehouse.db file and any saved sync checkpoints to start with a clean slate.

        - Runs the fivetran debug command using your configuration file to test the connector in real time.(debug emulates a regular Fivetran sync where the schema() and update() methods are called).

        - Execute the Custom `Connector.py` code you wrote fetching data and executing pagination and checkpoint saving for incremental sync as per your custom code and the current state variable. The helper script emulates an initial full sync.

        - Verifies data loading and schema creation by simulating a full sync (in this case, upserting 750 records into fts_records).

        - Queries and displays sample records from the resulting DuckDB table to confirm the connector outputs expected data.

9. Fivetran provides a built-in command to deploy your connector directly using the SDK:  
   `fivetran deploy --api-key <BASE64_API_KEY> --destination <DESTINATION_NAME> --connection <CONNECTION_NAME>`  
   This command deploys your code to Fivetran and creates or updates the connection. If the connection already exists, it prompts you before overwriting.  
   You can also provide additional optional parameters:  
   - `--configuration` to pass configuration values  
   - `--force` to bypass confirmation prompts, great for CI/CD uses  
   - `--python-version` to specify Python runtime  
   - `--hybrid-deployment-agent-id` for non-default hybrid agent selection  

10. To simplify the lab experience, we've created a helper script that wraps the deploy logic. Run the following command in the VS Code terminal (copy the command using the icon in the right corner):

```
./deploy.sh
```

11. Click enter twice to accept the default values for the Fivetran Account Name and the Fivetran Destination. When prompted for the **connection name**, type in:

```
oil_gas_fts_connector
```

12. Press Enter to deploy your new custom connector to Fivetran.

## Step 2: Start Data Sync in Fivetran (3 minutes)

1. Switch to **Chrome Tab 3 (Fivetran Automated Data Movement)**
2. Refresh the page and find your newly created connection named "oil-gas-fts-connector" in the connections list
3. Click on the connection to open the **Status** page
4. Click the **Start Initial Sync** button
5. You should see a status message indicating that the sync is **Active** and that it is the first time syncing data for this connection.
6. Once your sync completes, you will see a message "Next sync will run in x hours" and if you click on the **1 HOUR** selection on the right side, you will see some sync metrics.
    * You may need to refresh the UI to see updated sync progress and logs in the UI. 
7. Once your sync completes, you will see a message "Next sync will run in x hours" and if you click on the **1 HOUR** selection on the right side, you will see some sync metrics.

## Step 3: Create a Streamlit in Snowflake Gen AI Data App (5 minutes)

### 3.1 Copy the Streamlit Data App Code
1. Copy the Streamlit code below (click the Copy icon in the right corner)

<details>
  <summary>Click to expand the Streamlit Data App Code and click the Copy icon in the right corner</summary>

```python
import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="loglynx_–_ai_driven_field_technician_task_summarization",
    page_icon="https://i.imgur.com/Og6gFnB.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add CSS for agent progress styling
st.markdown("""
<style>
.agent-current {
    background-color: #e3f2fd;
    border-left: 4px solid #2196f3;
    padding: 10px;
    margin: 5px 0;
    border-radius: 5px;
    font-weight: 500;
}

.agent-completed {
    background-color: #e8f5e8;
    border-left: 4px solid #4caf50;
    padding: 8px;
    margin: 3px 0;
    border-radius: 5px;
    font-size: 0.9em;
    color: #2e7d32;
}

.agent-container {
    background-color: #f8f9fa;
    padding: 15px;
    border-radius: 10px;
    margin: 10px 0;
    border: 1px solid #e0e0e0;
}

.agent-status-active {
    color: #4CAF50;
    font-weight: bold;
    font-size: 1.1em;
}

.agent-button-container {
    display: flex;
    gap: 10px;
    align-items: center;
    margin: 10px 0;
}

.agent-report-header {
    background-color: #f8f9fa;
    padding: 10px;
    border-radius: 5px;
    margin: 10px 0;
    border-left: 4px solid #2196F3;
}
</style>
""", unsafe_allow_html=True)

solution_name = '''Solution 1: LogLynx – AI-driven Field Technician Task Summarization'''
solution_name_clean = '''loglynx_–_ai_driven_field_technician_task_summarization'''
table_name = '''LOGLYNX'''
table_description = '''Consolidated data from field technician logs, CMMS, and ERP systems for LogLynx solution'''
solution_content = '''Solution 1: LogLynx – AI-driven Field Technician Task Summarization**

### Business Challenge
The primary business challenge addressed by LogLynx is the manual and time-consuming process of summarizing daily logs from field technicians in the Oil and Gas industry. This process hinders the ability to quickly identify trends, patterns, and potential issues, leading to delayed maintenance, increased costs, and reduced operational efficiency.

### Key Features
- Automated summarization of daily logs from field technicians
- Real-time data analysis and insights
- Customizable dashboards for easy monitoring and decision-making
- Integration with existing CMMS (Computerized Maintenance Management System) and ERP (Enterprise Resource Planning) systems

### Data Sources
- Field Technician Logs: SAP, Oracle, Microsoft Dynamics
- CMMS: IBM Maximo, Infor EAM, SAP EAM
- ERP: SAP, Oracle, Microsoft Dynamics

### Competitive Advantage
LogLynx differentiates itself by leveraging generative AI to automate the summarization process, reducing manual labor and increasing the speed of insights. This allows for faster decision-making and improved operational efficiency.

### Key Stakeholders
- Field Technicians
- Maintenance Managers
- Operations Managers
- C-level Executive: Chief Operating Officer (COO)

### Technical Approach
LogLynx utilizes a combination of natural language processing (NLP) and machine learning algorithms to analyze and summarize field technician logs. This approach enables the system to identify key information, trends, and patterns, providing actionable insights for maintenance and operations teams.

### Expected Business Results
- **300 fewer failed treatments per year**
  **10,000 field technician logs × 3% baseline failure rate × 15% reduction = 300 fewer failed treatments/year**
- **$ 1,200,000 in maintenance cost savings annually**
  **$ 4,000,000 annual maintenance costs × 30% reduction = $ 1,200,000 savings/year**
- **25% reduction in maintenance downtime**
  **100 hours of downtime/month × 12 months/year × 25% reduction = 300 hours saved/year**
- **90% reduction in manual summarization time**
  **100 hours/month × 12 months/year × 90% reduction = 1,200 hours saved/year**

### Success Metrics
- Reduction in failed treatments
- Maintenance cost savings
- Maintenance downtime reduction
- Time saved in manual summarization

### Risk Assessment
Potential challenges include:
- Data quality and consistency
- Integration with existing systems
- Training and adoption by field technicians

Mitigation strategies:
- Implement data quality checks and data cleansing processes
- Conduct thorough system integration testing
- Provide comprehensive training and support for field technicians

### Long-term Evolution
Over the next 3-5 years, LogLynx will continue to evolve by incorporating more advanced NLP techniques, integrating with emerging technologies like IoT sensors, and expanding its capabilities to include predictive maintenance and real-time monitoring.'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Oil & Gas</p>
    </div>
</div>
''', unsafe_allow_html=True)

# Define available models as strings
MODELS = [
    "claude-4-sonnet", "claude-3-7-sonnet", "claude-3-5-sonnet", "llama3.1-8b", "llama3.1-70b", "llama4-maverick", "llama4-scout", "llama3.2-1b", "snowflake-llama-3.1-405b", "snowflake-llama-3.3-70b", "mistral-large2", "mistral-7b", "deepseek-r1", "snowflake-arctic", "reka-flash", "jamba-instruct", "gemma-7b"
]

if 'insights_history' not in st.session_state:
    st.session_state.insights_history = []

if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {}

# Initialize completed steps for each focus area
focus_areas = ["Overall Performance", "Optimization Opportunities", "Financial Impact", "Strategic Recommendations"]
for area in focus_areas:
    if f'{area.lower().replace(" ", "_")}_completed_steps' not in st.session_state:
        st.session_state[f'{area.lower().replace(" ", "_")}_completed_steps'] = []

try:
    session = get_active_session()
except Exception as e:
    st.error(f"❌ Error connecting to Snowflake: {str(e)}")
    st.stop()

def query_snowflake(query):
    try:
        return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Query failed: {str(e)}")
        return pd.DataFrame()

def load_data():
    query = f"SELECT * FROM {table_name} LIMIT 1000"
    df = query_snowflake(query)
    df.columns = [col.lower() for col in df.columns]
    return df

def call_cortex_model(prompt, model_name):
    try:
        cortex_query = "SELECT SNOWFLAKE.CORTEX.COMPLETE(?, ?) AS response"
        response = session.sql(cortex_query, params=[model_name, prompt]).collect()[0][0]
        return response
    except Exception as e:
        st.error(f"❌ Cortex error: {str(e)}")
        return None

def get_focus_area_info(focus_area):
    """Get business challenge and agent solution for each focus area"""
    
    focus_info = {
        "Overall Performance": {
            "challenge": "Operations managers manually review hundreds of field technician logs daily, spending 3+ hours summarizing maintenance activities, equipment failures, and operational insights to identify critical issues and performance trends.",
            "solution": "Autonomous field operations workflow that analyzes technician logs, maintenance records, and equipment data to generate automated summaries, identify failure patterns, and produce prioritized operational insights with predictive maintenance recommendations."
        },
        "Optimization Opportunities": {
            "challenge": "Maintenance managers spend 4+ hours daily manually identifying inefficiencies in equipment maintenance schedules, technician productivity, and resource allocation across oil and gas field operations.",
            "solution": "AI-powered field operations optimization analysis that automatically detects maintenance scheduling gaps, equipment performance inefficiencies, and resource allocation improvements with specific implementation recommendations for CMMS integration."
        },
        "Financial Impact": {
            "challenge": "Operations financial analysts manually calculate complex ROI metrics across maintenance activities and equipment performance, requiring 3+ hours of cost modeling to assess operational efficiency and maintenance cost optimization.",
            "solution": "Automated oil & gas financial analysis that calculates comprehensive ROI, identifies maintenance cost reduction opportunities across equipment categories, and projects operational efficiency benefits with detailed cost forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "Chief Operating Officers spend hours manually analyzing digital transformation opportunities and developing strategic technology roadmaps for field operations advancement and predictive maintenance implementation.",
            "solution": "Strategic field operations intelligence workflow that analyzes competitive advantages against traditional manual processes, identifies IoT and predictive maintenance integration opportunities, and creates prioritized digital transformation roadmaps."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - Oil & Gas Field Operations focused version"""
    
    try:
        # FIRST: Generate the actual insights (behind the scenes)
        insights = generate_insights(data, focus_area, model_name)
        
        # THEN: Prepare for animation
        session_key = f'{focus_area.lower().replace(" ", "_")}_completed_steps'
        st.session_state[session_key] = []
        
        def update_progress(step_name, progress_percent, details, results):
            """Update progress display with completed steps"""
            if progress_placeholder:
                with progress_placeholder.container():
                    # Progress bar
                    st.progress(progress_percent / 100)
                    st.write(f"**{step_name} ({progress_percent}%)**")
                    
                    if details:
                        st.markdown(f'<div class="agent-current">{details}</div>', unsafe_allow_html=True)
                    
                    if results:
                        st.session_state[session_key].append((step_name, results))
                        
                    # Display completed steps
                    for completed_step, completed_result in st.session_state[session_key]:
                        st.markdown(f'<div class="agent-completed">✅ {completed_step}: {completed_result}</div>', unsafe_allow_html=True)
        
        # Calculate real data for enhanced context
        total_logs = len(data)
        key_metrics = ["failure_rate", "maintenance_cost", "downtime_hours", "summarization_time_saved"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced oil & gas data insights
        avg_failure_rate = data['failure_rate'].mean() if 'failure_rate' in data.columns else 0
        avg_maintenance_cost = data['maintenance_cost'].mean() if 'maintenance_cost' in data.columns else 0
        maintenance_types = len(data['maintenance_type'].unique()) if 'maintenance_type' in data.columns else 0
        equipment_count = len(data['equipment_id'].unique()) if 'equipment_id' in data.columns else 0
        avg_time_saved = data['summarization_time_saved'].mean() if 'summarization_time_saved' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Field Operations Data Initialization", 15, f"Loading comprehensive field technician dataset with enhanced validation across {total_logs} logs and {equipment_count} equipment units", f"Connected to {len(available_metrics)} operational metrics across {len(data.columns)} total field operations data dimensions"),
                ("Maintenance Performance Assessment", 35, f"Advanced calculation of field operations indicators with failure analysis (avg failure rate: {avg_failure_rate:.3f})", f"Computed operational metrics: {avg_failure_rate:.3f} failure rate, ${avg_maintenance_cost:,.0f} avg maintenance cost, {avg_time_saved:.1f}h time saved per log"),
                ("Field Operations Pattern Recognition", 55, f"Sophisticated identification of equipment performance patterns with maintenance correlation analysis across {maintenance_types} maintenance types", f"Detected significant patterns in {len(data['maintenance_status'].unique()) if 'maintenance_status' in data.columns else 'N/A'} maintenance categories with equipment correlation analysis completed"),
                ("AI Field Operations Intelligence Processing", 75, f"Processing comprehensive field data through {model_name} with advanced reasoning for operational efficiency insights", f"Enhanced AI analysis of field technician log summarization effectiveness across {total_logs} operational records completed"),
                ("Operations Performance Report Compilation", 100, f"Professional field operations analysis with evidence-based recommendations and actionable maintenance insights ready", f"Comprehensive operations performance report with {len(available_metrics)} field metrics analysis and equipment maintenance recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            completed_maintenance = len(data[data['maintenance_status'] == 'Completed']) if 'maintenance_status' in data.columns else 0
            completion_rate = (completed_maintenance / total_logs) * 100 if total_logs > 0 else 0
            
            steps = [
                ("Field Operations Optimization Data Preparation", 12, f"Advanced loading of maintenance operations data with enhanced validation across {total_logs} logs for efficiency improvement identification", f"Prepared {maintenance_types} maintenance types, {equipment_count} equipment units for optimization analysis with {completion_rate:.1f}% completion rate"),
                ("Equipment Maintenance Inefficiency Detection", 28, f"Sophisticated analysis of maintenance scheduling and equipment performance with evidence-based inefficiency identification", f"Identified optimization opportunities across {maintenance_types} maintenance types with equipment performance and scheduling gaps"),
                ("Field Operations Correlation Analysis", 45, f"Enhanced examination of relationships between maintenance types, failure rates, and technician productivity", f"Analyzed correlations between maintenance activities and equipment performance across {total_logs} field operation records"),
                ("CMMS Integration Optimization", 65, f"Comprehensive evaluation of field operations integration with existing SAP, Oracle, and IBM Maximo CMMS systems", f"Assessed integration opportunities across {len(data.columns)} data points and field operations system optimization needs"),
                ("AI Field Operations Intelligence", 85, f"Generating advanced maintenance optimization recommendations using {model_name} with oil & gas reasoning and implementation strategies", f"AI-powered field operations optimization strategy across {maintenance_types} maintenance areas and equipment improvements completed"),
                ("Field Operations Strategy Finalization", 100, f"Professional field operations optimization report with prioritized implementation roadmap and maintenance impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and field operations implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            total_maintenance_cost = data['maintenance_cost'].sum() if 'maintenance_cost' in data.columns else 0
            total_downtime = data['downtime_hours'].sum() if 'downtime_hours' in data.columns else 0
            
            steps = [
                ("Oil & Gas Financial Data Integration", 15, f"Advanced loading of field operations financial data and maintenance cost metrics with enhanced validation across {total_logs} operations", f"Integrated field operations financial data: ${avg_maintenance_cost:,.0f} avg maintenance cost, {total_downtime:.0f}h total downtime across operations portfolio"),
                ("Maintenance Cost-Benefit Calculation", 30, f"Sophisticated ROI metrics calculation with equipment maintenance analysis and operational efficiency cost savings", f"Computed comprehensive cost analysis: maintenance expenses, downtime costs, and ${total_maintenance_cost:,.0f} total maintenance optimization potential"),
                ("Equipment Efficiency Impact Assessment", 50, f"Enhanced analysis of field operations revenue impact with equipment reliability metrics and maintenance cost correlation analysis", f"Assessed operational implications: {avg_failure_rate:.1%} failure rate with {equipment_count} equipment units requiring cost optimization"),
                ("Field Operations Resource Efficiency Analysis", 70, f"Comprehensive evaluation of resource allocation efficiency across maintenance activities with equipment lifecycle cost optimization", f"Analyzed resource efficiency: {maintenance_types} maintenance categories with equipment downtime cost reduction opportunities identified"),
                ("AI Oil & Gas Financial Modeling", 90, f"Advanced field operations financial projections and maintenance ROI calculations using {model_name} with comprehensive oil & gas cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} operational cost metrics completed"),
                ("Field Operations Economics Report Generation", 100, f"Professional oil & gas financial impact analysis with detailed maintenance ROI calculations and operational cost forecasting ready", f"Comprehensive field operations financial report with ${total_maintenance_cost:,.0f} cost optimization analysis and equipment efficiency strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            automation_efficiency_score = avg_time_saved * 10 if avg_time_saved > 0 else 0
            
            steps = [
                ("Oil & Gas Technology Assessment", 15, f"Advanced loading of field operations digital context with competitive positioning analysis across {total_logs} operations and {equipment_count} equipment assets", f"Analyzed oil & gas technology landscape: {maintenance_types} maintenance categories, {equipment_count} equipment units, comprehensive field digitization assessment completed"),
                ("Field Operations Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional manual field operations with AI-powered log summarization effectiveness", f"Assessed competitive advantages: {automation_efficiency_score:.1f}% automation efficiency, {avg_time_saved:.1f}h time savings vs manual methods"),
                ("Advanced Field Technology Integration", 50, f"Enhanced analysis of integration opportunities with IoT sensors, predictive maintenance, and digital oil field technologies across {len(data.columns)} operational data dimensions", f"Identified strategic technology integration: IoT equipment monitoring, predictive maintenance algorithms, automated field operations opportunities"),
                ("Digital Field Operations Strategy Development", 70, f"Comprehensive development of prioritized digital transformation roadmap with evidence-based field technology adoption strategies", f"Created sequenced implementation plan across {maintenance_types} operational areas with advanced technology integration opportunities"),
                ("AI Oil & Gas Strategic Processing", 85, f"Advanced field operations strategic recommendations using {model_name} with long-term competitive positioning and oil & gas technology analysis", f"Enhanced strategic analysis with field operations competitive positioning and digital transformation roadmap completed"),
                ("Digital Field Operations Report Generation", 100, f"Professional digital oil & gas transformation roadmap with competitive analysis and field technology implementation plan ready for COO executive review", f"Comprehensive strategic report with {maintenance_types}-category implementation plan and field operations competitive advantage analysis generated")
            ]
        
        # NOW: Animate the progress with pre-calculated results
        for step_name, progress_percent, details, results in steps:
            update_progress(step_name, progress_percent, details, results)
            time.sleep(1.2)
        
        return insights
        
    except Exception as e:
        if progress_placeholder:
            progress_placeholder.error(f"❌ Enhanced Agent Analysis failed: {str(e)}")
        return f"Enhanced Agent Analysis failed: {str(e)}"

def generate_insights(data, focus_area, model_name):
    data_summary = f"Table: {table_name}\n"
    data_summary += f"Description: {table_description}\n"
    data_summary += f"Records analyzed: {len(data)}\n"

    # Calculate basic statistics for numeric columns only - exclude ID columns
    numeric_stats = {}
    # Only include actual numeric metrics, not ID columns
    key_metrics = ["failure_rate", "maintenance_cost", "downtime_hours", "summarization_time_saved"]
    
    # Filter to only columns that exist and are actually numeric
    available_metrics = []
    for col in key_metrics:
        if col in data.columns:
            try:
                # Test if the column is actually numeric by trying to calculate mean
                test_mean = pd.to_numeric(data[col], errors='coerce').mean()
                if not pd.isna(test_mean):
                    available_metrics.append(col)
            except:
                # Skip columns that can't be converted to numeric
                continue
    
    for col in available_metrics:
        try:
            numeric_data = pd.to_numeric(data[col], errors='coerce')
            numeric_stats[col] = {
                "mean": numeric_data.mean(),
                "min": numeric_data.min(),
                "max": numeric_data.max(),
                "std": numeric_data.std()
            }
            data_summary += f"- {col} (avg: {numeric_data.mean():.2f}, min: {numeric_data.min():.2f}, max: {numeric_data.max():.2f})\n"
        except Exception as e:
            # Skip columns that cause errors
            continue

    # Get top values for categorical columns
    categorical_stats = {}
    categorical_options = ["log_description", "maintenance_type", "maintenance_status", "summarized_log"]
    for cat_col in categorical_options:
        if cat_col in data.columns:
            try:
                top = data[cat_col].value_counts().head(3)
                categorical_stats[cat_col] = top.to_dict()
                data_summary += f"\nTop {cat_col} values:\n" + "\n".join(f"- {k}: {v}" for k, v in top.items())
            except:
                # Skip columns that cause errors
                continue

    # Calculate correlations if enough numeric columns available
    correlation_info = ""
    if len(available_metrics) >= 2:
        try:
            # Create a dataframe with only the numeric columns
            numeric_df = data[available_metrics].apply(pd.to_numeric, errors='coerce')
            correlations = numeric_df.corr()
            
            # Get the top 3 strongest correlations (absolute value)
            corr_pairs = []
            for i in range(len(correlations.columns)):
                for j in range(i+1, len(correlations.columns)):
                    col1 = correlations.columns[i]
                    col2 = correlations.columns[j]
                    corr_value = correlations.iloc[i, j]
                    if not pd.isna(corr_value):
                        corr_pairs.append((col1, col2, abs(corr_value), corr_value))

            # Sort by absolute correlation value
            corr_pairs.sort(key=lambda x: x[2], reverse=True)

            # Add top correlations to the summary
            if corr_pairs:
                correlation_info = "Top correlations between metrics:\n"
                for col1, col2, _, corr_value in corr_pairs[:3]:
                    correlation_info += f"- {col1} and {col2}: r = {corr_value:.2f}\n"
        except Exception as e:
            correlation_info = "Could not calculate correlations between metrics.\n"

    # Define specific instructions for each focus area
    focus_area_instructions = {
        "Overall Performance": """
        For the Overall Performance analysis of LogLynx:
        1. Provide a comprehensive analysis of the field technician log summarization system using failure rate, maintenance cost, downtime hours, and time saved metrics
        2. Identify significant patterns in maintenance types, equipment performance, and technician efficiency across oil and gas operations
        3. Highlight 3-5 key operational metrics that best indicate log summarization effectiveness (failure rate reduction, cost savings, downtime reduction)
        4. Discuss both strengths and areas for improvement in the AI-powered log analysis process
        5. Include 3-5 actionable insights for improving field operations based on the technician log data
        
        Structure your response with these oil & gas focused sections:
        - Field Operations Insights (5 specific insights with supporting technician and equipment data)
        - Maintenance Performance Trends (3-4 significant trends in failure rates and downtime reduction)
        - Operational Efficiency Recommendations (3-5 data-backed recommendations for improving field operations)
        - Implementation Steps (3-5 concrete next steps for field technicians and maintenance managers)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of LogLynx:
        1. Focus specifically on areas where field technician log analysis and maintenance efficiency can be improved
        2. Identify inefficiencies in maintenance scheduling, equipment downtime, and technician productivity across oil and gas operations
        3. Analyze correlations between maintenance types, failure rates, and summarization time savings
        4. Prioritize optimization opportunities based on potential impact on operational costs and equipment reliability
        5. Suggest specific technical or process improvements for integration with existing CMMS and ERP systems
        
        Structure your response with these oil & gas focused sections:
        - Field Operations Optimization Priorities (3-5 areas with highest cost and downtime reduction potential)
        - Operational Impact Analysis (quantified benefits of addressing each opportunity in terms of maintenance metrics)
        - CMMS Integration Strategy (specific steps for maintenance teams to implement each optimization)
        - System Integration Recommendations (specific technical changes needed for seamless integration with SAP, Oracle, and IBM Maximo)
        - Field Operations Risk Assessment (potential challenges for technicians and maintenance teams and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of LogLynx:
        1. Focus on cost-benefit analysis and ROI in oil and gas operations terms (maintenance cost vs. operational efficiency gains)
        2. Quantify financial impacts through maintenance cost savings, downtime reduction, and productivity improvements
        3. Identify cost savings opportunities across different maintenance types and equipment categories
        4. Analyze resource allocation efficiency across different technicians and operational areas
        5. Project future financial outcomes based on improved log summarization accuracy and expanding to predictive maintenance
        
        Structure your response with these oil & gas focused sections:
        - Maintenance Cost Analysis (breakdown of maintenance costs and potential savings by equipment and maintenance type)
        - Operational Efficiency Impact (how improved log summarization affects operational costs and throughput)
        - Oil & Gas ROI Calculation (specific calculations showing return on investment in terms of maintenance cost reduction)
        - Downtime Reduction Opportunities (specific areas to reduce equipment downtime and associated costs)
        - Operations Cost Forecasting (projections based on improved maintenance efficiency metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of LogLynx:
        1. Focus on long-term strategic implications for digital transformation in oil and gas operations
        2. Identify competitive advantages against traditional manual log summarization approaches
        3. Suggest new directions for AI integration with emerging oil and gas technologies (e.g., IoT sensors, predictive maintenance)
        4. Connect recommendations to broader operational goals of reducing costs and improving equipment reliability
        5. Provide a digital operations roadmap with prioritized initiatives
        
        Structure your response with these oil & gas focused sections:
        - Digital Operations Context (how LogLynx fits into broader digital transformation in oil and gas)
        - Operational Competitive Advantage Analysis (how to maximize efficiency advantages compared to traditional manual processes)
        - Field Technology Strategic Priorities (3-5 high-impact strategic initiatives for improving field operations)
        - Advanced Technology Integration Vision (how to evolve LogLynx with IoT sensors and predictive maintenance over 1-3 years)
        - Operations Transformation Roadmap (sequenced steps for expanding to real-time monitoring and predictive maintenance)
        """
    }

    # Get the specific instructions for the selected focus area
    selected_focus_instructions = focus_area_instructions.get(focus_area, "")

    prompt = f'''
    You are an expert data analyst specializing in {focus_area.lower()} analysis for oil and gas operations.

    SOLUTION CONTEXT:
    {solution_name}

    {solution_content}

    DATA SUMMARY:
    {data_summary}

    {correlation_info}

    ANALYSIS INSTRUCTIONS:
    {selected_focus_instructions}

    IMPORTANT GUIDELINES:
    - Base all insights directly on the data provided
    - Use specific metrics and numbers from the data in your analysis
    - Maintain a professional, analytical tone
    - Be concise but thorough in your analysis
    - Focus specifically on {focus_area} as defined in the instructions
    - Ensure your response is unique and tailored to this specific focus area
    - Include a mix of observations, analysis, and actionable recommendations
    - Use bullet points and clear section headers for readability
    - Frame all insights in the context of oil and gas field operations and maintenance
    '''

    return call_cortex_model(prompt, model_name)

def create_metrics_charts(data):
    """Create metric visualizations for the oil and gas data"""
    charts = []
    
    # Maintenance Cost Distribution
    if 'maintenance_cost' in data.columns:
        cost_chart = alt.Chart(data).mark_bar().encode(
            alt.X('maintenance_cost:Q', bin=alt.Bin(maxbins=20), title='Maintenance Cost ($)'),
            alt.Y('count()', title='Number of Records'),
            color=alt.value('#1f77b4')
        ).properties(
            title='Cost Distribution',
            width=380,
            height=280
        )
        charts.append(('Cost Distribution', cost_chart))
    
    # Failure Rate by Maintenance Type
    if 'failure_rate' in data.columns and 'maintenance_type' in data.columns:
        failure_chart = alt.Chart(data).mark_boxplot().encode(
            alt.X('maintenance_type:N', title='Maintenance Type'),
            alt.Y('failure_rate:Q', title='Failure Rate'),
            color=alt.Color('maintenance_type:N', legend=None)
        ).properties(
            title='Failure Rate by Type',
            width=380,
            height=280
        )
        charts.append(('Failure Rate by Type', failure_chart))
    
    # Downtime Hours Trend
    if 'downtime_hours' in data.columns and 'log_date' in data.columns:
        downtime_chart = alt.Chart(data).mark_line(point=True).encode(
            alt.X('log_date:T', title='Date'),
            alt.Y('mean(downtime_hours):Q', title='Average Downtime Hours'),
            color=alt.value('#ff7f0e')
        ).properties(
            title='Downtime Trends',
            width=380,
            height=280
        )
        charts.append(('Downtime Trends', downtime_chart))
    
    # Maintenance Status Distribution
    if 'maintenance_status' in data.columns:
        status_chart = alt.Chart(data).mark_arc().encode(
            theta=alt.Theta('count():Q'),
            color=alt.Color('maintenance_status:N', title='Status'),
            tooltip=['maintenance_status:N', 'count():Q']
        ).properties(
            title='Status Distribution',
            width=380,
            height=280
        )
        charts.append(('Status Distribution', status_chart))
    
    # Time Saved vs Maintenance Cost Correlation
    if 'summarization_time_saved' in data.columns and 'maintenance_cost' in data.columns:
        correlation_chart = alt.Chart(data).mark_circle(size=80).encode(
            alt.X('summarization_time_saved:Q', title='Time Saved (hours)'),
            alt.Y('maintenance_cost:Q', title='Maintenance Cost ($)'),
            color=alt.Color('failure_rate:Q', title='Failure Rate', scale=alt.Scale(scheme='viridis')),
            tooltip=['summarization_time_saved:Q', 'maintenance_cost:Q', 'failure_rate:Q']
        ).properties(
            title='Time Saved vs Cost',
            width=380,
            height=280
        )
        charts.append(('Time Saved vs Cost', correlation_chart))
    
    # Equipment Performance Bar Chart
    if 'equipment_id' in data.columns and 'failure_rate' in data.columns:
        # Group by equipment and calculate average failure rate
        equipment_data = data.groupby('equipment_id')['failure_rate'].mean().reset_index()
        equipment_data = equipment_data.head(12).sort_values('failure_rate', ascending=False)  # Top 12 highest failure rates
        
        equipment_chart = alt.Chart(equipment_data).mark_bar().encode(
            alt.X('equipment_id:O', title='Equipment ID', sort='-y'),
            alt.Y('failure_rate:Q', title='Average Failure Rate'),
            color=alt.Color('failure_rate:Q', title='Failure Rate', scale=alt.Scale(scheme='reds')),
            tooltip=['equipment_id:O', alt.Tooltip('failure_rate:Q', format='.3f')]
        ).properties(
            title='Equipment Performance',
            width=380,
            height=280
        )
        charts.append(('Equipment Performance', equipment_chart))
    
    return charts

data = load_data()
if data.empty:
    st.error("No data found.")
    st.stop()

categorical_cols = [col for col in ["log_description", "maintenance_type", "maintenance_status", "summarized_log"] if col in data.columns]
numeric_cols = [col for col in ["technician_id", "equipment_id", "erp_order_id", "customer_id", "failure_rate", "maintenance_cost", "downtime_hours", "summarization_time_saved"] if col in data.columns]
date_cols = [col for col in ["log_date", "created_at", "updated_at"] if col in data.columns]

sample_cols = data.columns.tolist()
numeric_candidates = [col for col in sample_cols if data[col].dtype in ['float64', 'int64'] and 'id' not in col.lower()]
date_candidates = [col for col in sample_cols if 'date' in col.lower() or 'timestamp' in col.lower()]
cat_candidates = [col for col in sample_cols if data[col].dtype == 'object' and data[col].nunique() < 1000]

# Four tabs - Metrics tab first, then AI Insights
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics tab (now first)
with tabs[0]:
    st.subheader("📊 Key Performance Metrics")
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'failure_rate' in data.columns:
            avg_failure_rate = data['failure_rate'].mean()
            st.metric("Avg Failure Rate", f"{avg_failure_rate:.3f}", delta=f"{(avg_failure_rate - 0.03)*100:.1f}% vs baseline")
    
    with col2:
        if 'maintenance_cost' in data.columns:
            avg_cost = data['maintenance_cost'].mean()
            st.metric("Avg Maintenance Cost", f"${avg_cost:,.0f}", delta=f"-${(4000000/12 - avg_cost):,.0f} vs target")
    
    with col3:
        if 'downtime_hours' in data.columns:
            avg_downtime = data['downtime_hours'].mean()
            st.metric("Avg Downtime Hours", f"{avg_downtime:.1f}h", delta=f"{(avg_downtime - 8.33):.1f}h vs target")
    
    with col4:
        if 'summarization_time_saved' in data.columns:
            avg_time_saved = data['summarization_time_saved'].mean()
            st.metric("Avg Time Saved", f"{avg_time_saved:.1f}h", delta=f"{(avg_time_saved - 2.5):.1f}h vs baseline")
    
    st.markdown("---")
    
    # Create and display charts
    charts = create_metrics_charts(data)
    
    if charts:
        st.subheader("📈 Performance Visualizations")
        
        # Display charts in a 2-column grid, ensuring all 6 charts are shown
        num_charts = len(charts)
        for i in range(0, num_charts, 2):
            cols = st.columns(2)
            
            # Left column chart
            if i < num_charts:
                chart_title, chart = charts[i]
                with cols[0]:
                    st.altair_chart(chart, use_container_width=True)
            
            # Right column chart
            if i + 1 < num_charts:
                chart_title, chart = charts[i + 1]
                with cols[1]:
                    st.altair_chart(chart, use_container_width=True)
        
        # Display chart count for debugging
        st.caption(f"Displaying {num_charts} performance charts")
    else:
        st.info("No suitable data found for creating visualizations.")
    
    # Enhanced Summary statistics table
    st.subheader("📈 Summary Statistics")
    if numeric_candidates:
        # Create enhanced summary statistics
        summary_stats = data[numeric_candidates].describe()
        
        # Transpose for better readability and add formatting
        summary_df = summary_stats.T.round(3)
        
        # Add meaningful column names and formatting
        summary_df.columns = ['Count', 'Mean', 'Std Dev', 'Min', '25%', '50% (Median)', '75%', 'Max']
        
        # Format specific columns for better readability
        format_dict = {}
        for col in summary_df.index:
            if 'cost' in col.lower():
                format_dict[col] = "${:,.2f}"
            elif 'rate' in col.lower():
                format_dict[col] = "{:.3f}"
            elif 'hours' in col.lower() or 'time' in col.lower():
                format_dict[col] = "{:.1f}h"
            else:
                format_dict[col] = "{:.2f}"
        
        # Create three columns for better organization
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Key Performance Metrics**")
            key_metrics = ['failure_rate', 'maintenance_cost', 'downtime_hours', 'summarization_time_saved']
            key_metrics_present = [m for m in key_metrics if m in summary_df.index]
            
            if key_metrics_present:
                key_stats_df = summary_df.loc[key_metrics_present]
                
                # Create a more readable format
                for metric in key_stats_df.index:
                    mean_val = key_stats_df.loc[metric, 'Mean']
                    min_val = key_stats_df.loc[metric, 'Min']
                    max_val = key_stats_df.loc[metric, 'Max']
                    
                    # Format based on metric type
                    if 'cost' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"${mean_val:,.0f}",
                            help=f"Range: ${min_val:,.0f} - ${max_val:,.0f}"
                        )
                    elif 'rate' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.3f}",
                            help=f"Range: {min_val:.3f} - {max_val:.3f}"
                        )
                    elif 'hours' in metric.lower() or 'time' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.1f}h",
                            help=f"Range: {min_val:.1f}h - {max_val:.1f}h"
                        )
                    else:
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.2f}",
                            help=f"Range: {min_val:.2f} - {max_val:.2f}"
                        )
        
        with col2:
            st.markdown("**📊 Distribution Insights**")
            
            # Calculate and display key insights
            insights = []
            
            if 'failure_rate' in summary_df.index:
                fr_mean = summary_df.loc['failure_rate', 'Mean']
                fr_std = summary_df.loc['failure_rate', 'Std Dev']
                insights.append(f"• **Failure Rate Variability**: {fr_std:.3f} (σ)")
                
                if fr_mean > 0.5:
                    insights.append(f"• **High failure rate detected** (>{fr_mean:.1%})")
                else:
                    insights.append(f"• **Acceptable failure rate** ({fr_mean:.1%})")
            
            if 'maintenance_cost' in summary_df.index:
                mc_q75 = summary_df.loc['maintenance_cost', '75%']
                mc_q25 = summary_df.loc['maintenance_cost', '25%']
                iqr = mc_q75 - mc_q25
                insights.append(f"• **Cost IQR**: ${iqr:,.0f}")
            
            if 'downtime_hours' in summary_df.index:
                dt_median = summary_df.loc['downtime_hours', '50% (Median)']
                dt_max = summary_df.loc['downtime_hours', 'Max']
                insights.append(f"• **Median Downtime**: {dt_median:.1f}h")
                if dt_max > 10:
                    insights.append(f"• **⚠️ High downtime events**: up to {dt_max:.1f}h")
            
            if 'summarization_time_saved' in summary_df.index:
                ts_mean = summary_df.loc['summarization_time_saved', 'Mean']
                insights.append(f"• **Avg Time Saved**: {ts_mean:.1f}h per log")
            
            for insight in insights:
                st.markdown(insight)
        
        # Full detailed table (collapsible)
        with st.expander("📋 Detailed Statistics Table", expanded=False):
            st.dataframe(
                summary_df.style.format({
                    'Count': '{:.0f}',
                    'Mean': '{:.3f}',
                    'Std Dev': '{:.3f}',
                    'Min': '{:.3f}',
                    '25%': '{:.3f}',
                    '50% (Median)': '{:.3f}',
                    '75%': '{:.3f}',
                    'Max': '{:.3f}'
                }),
                use_container_width=True
            )

# AI Insights tab
with tabs[1]:
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each field operations analysis focus area**")
    
    focus_area = st.radio("Focus Area", [
        "Overall Performance", 
        "Optimization Opportunities", 
        "Financial Impact", 
        "Strategic Recommendations"
    ])
    
    # Show business challenge and solution
    focus_info = get_focus_area_info(focus_area)
    if focus_info["challenge"]:
        st.markdown("#### Business Challenge")
        st.info(focus_info["challenge"])
        st.markdown("#### Agent Solution")
        st.success(focus_info["solution"])
    
    st.markdown("**Select Snowflake Cortex Model for Analysis:**")
    selected_model = st.selectbox("", MODELS, index=0, label_visibility="collapsed")

    # Agent control buttons and status
    col1, col2, col3 = st.columns([2, 1, 1])
    
    agent_running_key = f"{focus_area}_agent_running"
    if agent_running_key not in st.session_state:
        st.session_state[agent_running_key] = False
    
    with col1:
        if st.button("🚀 Start Agent"):
            st.session_state[agent_running_key] = True
            st.rerun()
    
    with col2:
        if st.button("⏹ Stop Agent"):
            st.session_state[agent_running_key] = False
            st.rerun()
    
    with col3:
        st.markdown("**Status**")
        if st.session_state[agent_running_key]:
            st.markdown('<div class="agent-status-active">✅ Active</div>', unsafe_allow_html=True)
        else:
            st.markdown("⏸ Ready")

    # Progress placeholder
    progress_placeholder = st.empty()
    
    # Run agent if active
    if st.session_state[agent_running_key]:
        with st.spinner("Agent Running..."):
            insights = generate_insights_with_agent_workflow(data, focus_area, selected_model, progress_placeholder)
            
            if insights:
                # Show completion message
                st.success(f"🎉 {focus_area} Agent completed with real field operations data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real Oil & Gas Field Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Field Operations Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Field Operations Analysis</small><br>
                        <small>AI Model: {selected_model}</small>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(insights)
                
                # Save to history
                timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.insights_history.append({
                    "timestamp": timestamp,
                    "focus": focus_area,
                    "insights": insights,
                    "model": selected_model
                })
                
                # Stop the agent after completion
                st.session_state[agent_running_key] = False

# Insights History tab (now third)
with tabs[2]:
    st.subheader("📁 Insights History")
    if st.session_state.insights_history:
        for i, item in enumerate(reversed(st.session_state.insights_history)):
            with st.expander(f"{item['timestamp']} - {item['focus']} ({item['model']})", expanded=False):
                st.markdown(item["insights"])
    else:
        st.info("No insights generated yet. Go to the AI Insights tab to generate some insights.")

# Data Explorer tab (now fourth)
with tabs[3]:
    st.subheader("🔍 Data Explorer")
    rows_per_page = st.slider("Rows per page", 5, 50, 10)
    page = st.number_input("Page", min_value=1, value=1)
    start = (page - 1) * rows_per_page
    end = min(start + rows_per_page, len(data))
    st.dataframe(data.iloc[start:end], use_container_width=True)
    st.caption(f"Showing rows {start + 1}–{end} of {len(data)}")
```

</details>

## 3.2 Create and Deploy the Streamlit in Snowflake Gen AI Data App
1. Switch to **Chrome Tab 4 (Snowflake UI)**
2. Click on **Projects** in the left navigation panel
3. Click on **Streamlit**
4. Click the **+ Streamlit App** blue button in the upper right corner
5. Configure your app:
   - App title: `LogLynx`
   - Database: Select `SF_LABUSER#_DB` (only option available for your user)
   - Schema: Select `oil_gas_fts_connector` the schema created by your Fivetran connector (this should be the only schema available other than Public - do not select Public)
6. In the Streamlit Editor that appears (left side of the Streamlit UI), select all text (Command+A) and delete it
7. Paste the copied Streamlit application code into the empty editor (Command+V):
8. Click the blue **Run** button in the upper right corner
9. Close the editor by clicking the middle icon in the bottom left navigation

## 3.3 Explore the Streamlit in Snowflake Gen AI Data App
The LogLynx data app should now be running with the following sections:
- **Metrics**: View failure rates, maintenance costs, downtime hours, and time savings metrics with operational visualizations
- **AI Insights**: Generate AI-powered analysis of the oil and gas field operations data across four focus areas
- **Insights History**: Access previously generated AI insights
- **Data Explorer**: Browse the underlying field technician and maintenance data

## Done!
You've successfully:
1. Created a custom Fivetran connector using the Fivetran Connector SDK
2. Deployed the connector to sync oil and gas field technician summarization data into Snowflake
3. Built a Streamlit in Snowflake data app to visualize and analyze the data using Snowflake Cortex

## Next Steps
Consider how you might adapt this solution for your own use:
- Integration with field operations systems like SAP, Oracle, or Microsoft Dynamics
- Adding real-time equipment monitoring from CMMS systems like IBM Maximo or Infor EAM
- Implementing machine learning models for more sophisticated predictive maintenance algorithms
- Customizing the Streamlit app for specific oil and gas operational processes

## Resources
- Fivetran Connector SDK Documentation: [https://fivetran.com/docs/connectors/connector-sdk](https://fivetran.com/docs/connectors/connector-sdk)  
- Fivetran Connector SDK Examples: [https://fivetran.com/docs/connector-sdk/examples](https://fivetran.com/docs/connector-sdk/examples)
- API Connector Reference: [https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fts_api_spec](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fts_api_spec)
- Snowflake Cortex Documentation: [https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- Snowflake Streamlit Documentation: [https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)