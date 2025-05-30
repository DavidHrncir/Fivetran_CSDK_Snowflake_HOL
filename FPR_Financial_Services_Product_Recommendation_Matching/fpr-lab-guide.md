# Fivetran Connector SDK Hands on Lab at Snowflake Summit 2025: Financial Product Recommendations

## Overview
In this 20-minute hands on lab, you'll build a **custom Fivetran connector** using the **Fivetran Connector SDK** and the **Anthropic Workbench** to integrate financial product recommendation data from a custom REST API into Snowflake. You'll then create a **Streamlit in Snowflake** application powering financial metrics and **Snowflake Cortex AI-driven** financial product matching applications.

The Financial Services FPR custom connector should fetch financial product recommendation records from a REST API and load them into a single table called `fpr_records` in your Snowflake database. The connector should deliver detailed information about customer profiles, account balances, transaction data, product affinities, recommendations, and customer satisfaction metrics. It should handle authentication, pagination, error handling, and maintain state between sync runs using a cursor-based approach.

## Lab Steps Quick Access

- [Step 1: Create a Custom Connector with the Fivetran Connector SDK (8 minutes)](#step-1-create-a-custom-connector-with-the-fivetran-connector-sdk-8-minutes)
- [Step 2: Start Data Sync in Fivetran (3 minutes)](#step-2-start-data-sync-in-fivetran-3-minutes)
- [Step 3: Create a Streamlit in Snowflake Gen AI Data App (5 minutes)](#step-3-create-a-streamlit-in-snowflake-gen-ai-data-app-5-minutes)

## Lab Environment
- MacBook Pro laptop with Chrome browser, VS Code, DBeaver and the Fivetran Connector SDK
- 6 Chrome tabs are pre-configured (leave them open throughout the lab):
  - Tab 1: GitHub Lab Repo: Lab Guide
  - Tab 2: Anthropic Workbench: AI Code Generation Assistant (Claude)
  - Tab 3: Fivetran: Automated Data Movement Platform
  - Tab 4: Snowflake: Data and AI Platform including Cortex (AI functions) and Streamlit (data apps)
  - Tab 5: Fivetran Connector SDK Examples Open Source Github Repository
  - Tab 6: Fivetran Connector SDK Docs

## Mac Keyboard Shortcuts Reference
- **Command+A**: Select all
- **Command+C**: Copy
- **Command+V**: Paste
- **Command+S**: Save
- **Command+Tab**: Switch between applications
- **Control+`**: Open terminal in VS Code

## Trackpad/MousePad Reference
- **Single finger tap**: Left click
- **Two finger tap**: Right click
- **Two finger slide**: Scroll up and down

## Step 1: Create a Custom Connector with the Fivetran Connector SDK (8 minutes)

### 1.1 Generate the Custom Connector Code Using AI Code Generation Assistance
1. Switch to **Chrome Tab 2 (Anthropic Workbench)**
2. Copy and paste the following **User prompt** into the workbench:

<details>
  <summary>Click to expand the User prompt and click the Copy icon in the right corner</summary>

```
- Provide a custom connector for Financial Services for the fpr_data endpoint. 1 table called fpr_records - all columns.  
- Make sure you copy the configuration.json file exactly - do not add any other variables to it.
- Here is the API spec: https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fpr_api_spec
```
</details>

3. Click the black **Run** button in the upper right
4. After Claude generates the connector.py code, you will see a response similar to the example connector, but updated for the financial product recommendation dataset.
5. Click [fpr_data](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fpr_data) if you'd like to see the dataset.

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

        - Excute the Custom `Connector.py` code you wrote fetching data and executing pagination and checkpoint saving for incremental sync as per your custom code and the current state variable. The helper script emulates an initial full sync.

        - Verifies data loading and schema creation by simulating a full sync (in this case, upserting 750 records into fpr_records).

        - Queries and displays sample records from the resulting DuckDB table to confirm the connector outputs expected data.

9. Fivetran provides a built-in command to deploy your connector directly using the SDK:  
   `fivetran deploy --api-key <BASE64_API_KEY> --destination <DESTINATION_NAME> --connection <CONNECTION_NAME>`  
   This command deploys your code to Fivetran and creates or updates the connection. If the connection already exists, it prompts you before overwriting.  
   You can also provide additional optional parameters:  
   - `--configuration` to pass configuration values  
   - `--force` to bypass confirmation prompts, great for CI/CD uses  
   - `--python-version` to specify Python runtime  
   - `--hybrid-deployment-agent-id` for non-default hybrid agent selection  

10. To simplify the lab experience, we’ve created a helper script that wraps the deploy logic. Run the following command in the VS Code terminal (copy the command using the icon in the right corner):

```
./deploy.sh
```

11. Click enter twice to accept the default values for the Fivetran Account Name and the Fivetran Destination. When prompted for the **connection name**, type in:

```
financial_product_recommendation_connector
```

12. Press Enter to deploy your new custom connector to Fivetran.

## Step 2: Start Data Sync in Fivetran (3 minutes)

1. Switch to **Chrome Tab 3 (Fivetran Automated Data Movement)**
2. Refresh the page and find your newly created connection named "financial-product-recommendation-connector" in the connections list
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
    page_title="finmatch_–_ai_driven_financial_product_matching",
    page_icon="https://i.imgur.com/Og6gFnB.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

solution_name = '''Solution 1: FinMatch – AI-driven Financial Product Matching'''
solution_name_clean = '''finmatch_–_ai_driven_financial_product_matching'''
table_name = '''FPR_RECORDS'''
table_description = '''Consolidated table containing customer, product, and transaction data for FinMatch solution'''
solution_content = '''Solution 1: FinMatch – AI-driven Financial Product Matching**

* **Tagline:** "Matching customers with the right financial products"
* **Primary Business Challenge:** Financial institutions struggle to provide personalized product recommendations to customers, leading to missed revenue opportunities and decreased customer satisfaction.
* **Key Features:**
	+ AI-powered product matching engine
	+ Integration with core banking systems (FIS, Fiserv, Temenos)
	+ Real-time customer data analysis
	+ Personalized product recommendations
* **Data Sources:**
	+ Core Banking Systems: FIS, Fiserv, Temenos
	+ Customer Relationship Management (CRM): Salesforce, HubSpot, Zoho
	+ Customer Transaction Data: Core banking systems, transaction logs
* **Competitive Advantage:** FinMatch uses generative AI to analyze customer data and provide personalized product recommendations, differentiating from traditional rule-based approaches.
* **Key Stakeholders:** Retail banking managers, product managers, customer experience managers, and the Chief Customer Officer.
* **Technical Approach:** Generative AI (Generative Adversarial Networks, GANs) to analyze customer data and generate personalized product recommendations.
* **Expected Business Results:**
	+ 10% increase in product sales
	+ 15% reduction in customer churn
	+ 20% increase in customer satisfaction
	+ 5% increase in average revenue per user (ARPU)
* **Calculations:**
	+ 10% increase in product sales: **$ 10,000,000 annual product sales × 10% increase = $ 1,000,000 additional sales/year**
	+ 15% reduction in customer churn: **10,000 customers/year × 20% baseline churn rate × 15% reduction = 300 fewer churned customers/year**
	+ 20% increase in customer satisfaction: **50,000 customers/year × 20% baseline satisfaction rate × 20% increase = 2,000 additional satisfied customers/year**
	+ 5% increase in ARPU: **$ 100,000,000 annual revenue × 5% increase = $ 5,000,000 additional revenue/year**
* **Success Metrics:** Product sales, customer churn rate, customer satisfaction rate, ARPU
* **Risk Assessment:** Integration with core banking systems, data quality issues, regulatory compliance
* **Long-term Evolution:** Integration with emerging technologies like blockchain and IoT to provide more personalized and secure product recommendations.

**'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Financial Services</p>
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

def generate_insights(data, focus_area, model_name):
    data_summary = f"Table: {table_name}\n"
    data_summary += f"Description: {table_description}\n"
    data_summary += f"Records analyzed: {len(data)}\n"

    # Calculate basic statistics for numeric columns
    numeric_stats = {}
    key_metrics = ["account_balance", "recommendation_score", "customer_transaction_value", "customer_transaction_count", "customer_product_affinity", "product_sales_amount", "customer_satisfaction_score", "customer_churn_probability"]
    for col in key_metrics:
        if col in data.columns:
            numeric_stats[col] = {
                "mean": data[col].mean(),
                "min": data[col].min(),
                "max": data[col].max(),
                "std": data[col].std()
            }
            data_summary += f"- {col} (avg: {data[col].mean():.2f}, min: {data[col].min():.2f}, max: {data[col].max():.2f})\n"

    # Get top values for categorical columns
    categorical_stats = {}
    categorical_options = ["customer_id", "customer_name", "customer_email", "transaction_history", "product_id", "product_name", "product_type", "product_terms", "product_recommendation", "customer_segment", "customer_lifecycle_stage", "customer_product_usage", "customer_product_interests", "product_recommendation_status", "customer_product_usage_trend", "customer_product_affinity_trend"]
    for cat_col in categorical_options:
        if cat_col in data.columns:
            top = data[cat_col].value_counts().head(3)
            categorical_stats[cat_col] = top.to_dict()
            data_summary += f"\nTop {cat_col} values:\n" + "\n".join(f"- {k}: {v}" for k, v in top.items())

    # Calculate correlations if enough numeric columns available
    correlation_info = ""
    if len(key_metrics) >= 2:
        try:
            correlations = data[key_metrics].corr()
            # Get the top 3 strongest correlations (absolute value)
            corr_pairs = []
            for i in range(len(correlations.columns)):
                for j in range(i+1, len(correlations.columns)):
                    col1 = correlations.columns[i]
                    col2 = correlations.columns[j]
                    corr_value = correlations.iloc[i, j]
                    corr_pairs.append((col1, col2, abs(corr_value), corr_value))

            # Sort by absolute correlation value
            corr_pairs.sort(key=lambda x: x[2], reverse=True)

            # Add top correlations to the summary
            if corr_pairs:
                correlation_info = "Top correlations between metrics:\n"
                for col1, col2, _, corr_value in corr_pairs[:3]:
                    correlation_info += f"- {col1} and {col2}: r = {corr_value:.2f}\n"
        except:
            correlation_info = "Could not calculate correlations between metrics.\n"

    # Define specific instructions for each focus area
    focus_area_instructions = {
        "Overall Performance": """
        For the Overall Performance analysis of FinMatch:
        1. Provide a comprehensive analysis of the financial product matching system using recommendation scores, customer satisfaction, and product sales metrics
        2. Identify significant patterns in customer product affinity, transaction behavior, and recommendation acceptance rates
        3. Highlight 3-5 key banking metrics that best indicate recommendation effectiveness (product sales growth, customer churn reduction, satisfaction improvement)
        4. Discuss both strengths and areas for improvement in the AI-powered product matching engine
        5. Include 3-5 actionable insights for improving financial product recommendations based on the data
        
        Structure your response with these banking-focused sections:
        - Financial Product Matching Insights (5 specific insights with supporting customer and transaction data)
        - Customer Engagement Trends (3-4 significant trends in product recommendation acceptance and usage)
        - Recommendation Strategy Improvements (3-5 data-backed recommendations for enhancing product matching)
        - Implementation Steps (3-5 concrete next steps for retail banking and product management teams)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of FinMatch:
        1. Focus specifically on areas where financial product matching accuracy can be improved
        2. Identify inefficiencies in customer segmentation, product affinity analysis, and recommendation delivery
        3. Analyze correlations between customer lifecycle stages, transaction patterns, and product acceptance
        4. Prioritize optimization opportunities based on potential impact on sales conversion and customer retention
        5. Suggest specific technical or process improvements for integration with core banking systems
        
        Structure your response with these banking-focused sections:
        - Product Matching Optimization Priorities (3-5 areas with highest conversion improvement potential)
        - Customer Experience Impact Analysis (quantified benefits of addressing each opportunity in terms of satisfaction scores)
        - Banking Integration Strategy (specific steps for banking teams to implement each optimization)
        - Core System Integration Recommendations (specific technical changes needed for seamless integration with FIS, Fiserv, Temenos)
        - Regulatory Risk Assessment (potential compliance challenges and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of FinMatch:
        1. Focus on cost-benefit analysis and ROI in retail banking terms (implementation costs vs. revenue growth)
        2. Quantify financial impacts through increased product sales, reduced churn, and improved average revenue per user
        3. Identify cross-selling and upselling opportunities across different customer segments
        4. Analyze customer lifetime value impact across different product categories
        5. Project future financial outcomes based on improved matching accuracy and expanded product offerings
        
        Structure your response with these banking-focused sections:
        - Product Revenue Analysis (breakdown of sales growth and potential revenue expansion by product type)
        - Customer Retention Value (how reduced churn affects lifetime customer value and revenue)
        - Banking ROI Calculation (specific calculations showing return on investment in terms of increased ARPU)
        - Cross-Selling Opportunities (specific product combinations with highest conversion potential)
        - Banking Portfolio Forecasting (projections based on improved product matching metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of FinMatch:
        1. Focus on long-term strategic implications for personalized banking services
        2. Identify competitive advantages against traditional banking recommendation approaches
        3. Suggest new directions for AI integration with emerging financial technologies like blockchain and IoT
        4. Connect recommendations to broader retail banking goals of enhancing customer relationships and wallet share
        5. Provide a digital banking transformation roadmap with prioritized initiatives
        
        Structure your response with these banking-focused sections:
        - Retail Banking Context (how FinMatch fits into broader digital banking transformation initiatives)
        - Financial Services Competitive Advantage Analysis (how to maximize personalization advantage compared to traditional banks)
        - Banking Strategic Priorities (3-5 high-impact strategic initiatives for improving customer financial product fit)
        - Future FinTech Integration Vision (how to evolve FinMatch with blockchain, IoT, and open banking over 1-3 years)
        - Digital Banking Transformation Roadmap (sequenced steps for enterprise-wide adoption and expansion)
        """
    }

    # Get the specific instructions for the selected focus area
    selected_focus_instructions = focus_area_instructions.get(focus_area, "")

    prompt = f'''
    You are an expert data analyst specializing in {focus_area.lower()} analysis.

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
    '''

    return call_cortex_model(prompt, model_name)

data = load_data()
if data.empty:
    st.error("No data found.")
    st.stop()

categorical_cols = [col for col in ["customer_id", "customer_name", "customer_email", "transaction_history", "product_id", "product_name", "product_type", "product_terms", "product_recommendation", "customer_segment", "customer_lifecycle_stage", "customer_product_usage", "customer_product_interests", "product_recommendation_status", "customer_product_usage_trend", "customer_product_affinity_trend"] if col in data.columns]
numeric_cols = [col for col in ["account_balance", "recommendation_score", "customer_transaction_value", "customer_transaction_count", "customer_product_affinity", "product_sales_amount", "customer_satisfaction_score", "customer_churn_probability"] if col in data.columns]
date_cols = [col for col in ["product_sales_date", "customer_lifecycle_stage_transition_date", "product_recommendation_date"] if col in data.columns]

sample_cols = data.columns.tolist()
numeric_candidates = [col for col in sample_cols if data[col].dtype in ['float64', 'int64'] and 'id' not in col.lower()]
date_candidates = [col for col in sample_cols if 'date' in col.lower() or 'timestamp' in col.lower()]
cat_candidates = [col for col in sample_cols if data[col].dtype == 'object' and data[col].nunique() < 1000]

# Four tabs - with Metrics as the first tab (Tab 0)
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics Tab (Tab 0)
with tabs[0]:
    st.header("Financial Product Matching Metrics")
    
    # Overview metrics row - 4 KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics from the data
    avg_recommendation_score = data['recommendation_score'].mean() if 'recommendation_score' in data.columns else 0
    avg_satisfaction_score = data['customer_satisfaction_score'].mean() if 'customer_satisfaction_score' in data.columns else 0
    avg_churn_probability = data['customer_churn_probability'].mean() if 'customer_churn_probability' in data.columns else 0
    total_sales_amount = data['product_sales_amount'].sum() if 'product_sales_amount' in data.columns else 0
    
    with col1:
        with st.container(border=True):
            st.metric(
                "Avg Recommendation Score", 
                f"{avg_recommendation_score:.2f}",
                f"{(avg_recommendation_score - 0.5) / 0.5 * 100:.1f}%" if avg_recommendation_score > 0.5 else f"{(avg_recommendation_score - 0.5) / 0.5 * 100:.1f}%",
                help="Average product recommendation score (0-1 scale). Higher is better."
            )
    
    with col2:
        with st.container(border=True):
            st.metric(
                "Avg Customer Satisfaction", 
                f"{avg_satisfaction_score:.2f}",
                f"{(avg_satisfaction_score - 0.5) / 0.5 * 100:.1f}%" if avg_satisfaction_score > 0.5 else f"{(avg_satisfaction_score - 0.5) / 0.5 * 100:.1f}%",
                help="Average customer satisfaction score (0-1 scale). Higher is better."
            )
    
    with col3:
        with st.container(border=True):
            st.metric(
                "Avg Churn Probability", 
                f"{avg_churn_probability:.2f}",
                f"{(0.5 - avg_churn_probability) / 0.5 * 100:.1f}%" if avg_churn_probability < 0.5 else f"{(0.5 - avg_churn_probability) / 0.5 * 100:.1f}%",
                help="Average customer churn probability (0-1 scale). Lower is better."
            )
    
    with col4:
        with st.container(border=True):
            st.metric(
                "Total Product Sales", 
                f"${total_sales_amount:,.2f}",
                help="Total product sales amount across all customers"
            )
    
    # Financial Metrics Section - 3 Financial Metrics
    st.subheader("Financial Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            avg_transaction_value = data['customer_transaction_value'].mean() if 'customer_transaction_value' in data.columns else 0
            st.metric("Avg Transaction Value", f"${avg_transaction_value:,.2f}")
        
    with col2:
        with st.container(border=True):
            avg_account_balance = data['account_balance'].mean() if 'account_balance' in data.columns else 0
            st.metric("Avg Account Balance", f"${avg_account_balance:,.2f}")
        
    with col3:
        with st.container(border=True):
            avg_transaction_count = data['customer_transaction_count'].mean() if 'customer_transaction_count' in data.columns else 0
            st.metric("Avg Transaction Count", f"{avg_transaction_count:.1f}")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    # Recommendation Status Distribution
    with col1:
        st.subheader("Recommendation Status Distribution")
        
        if 'product_recommendation_status' in data.columns:
            status_counts = data['product_recommendation_status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            # Status colors
            colors = {
                'Accepted': '#52BE80',  # Green
                'Pending': '#F4D03F',   # Yellow
                'In Progress': '#5DADE2',  # Blue
                'Declined': '#E74C3C'   # Red
            }
            
            # Recommendation Status Distribution Chart
            chart = alt.Chart(status_counts).mark_bar().encode(
                x=alt.X('status:N', title='Recommendation Status', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Customers'),
                color=alt.Color('status:N', scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())))
            )
            
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-15  # Increased space above bars
            ).encode(
                text='count:Q'
            )
            
            # Use the same approach for both charts
            st.altair_chart((chart + text).properties(height=300, width=500), use_container_width=True)
        else:
            st.write("Recommendation status data not available")
    
    # Product Affinity Distribution
    with col2:
        st.subheader("Product Affinity Distribution")
        
        if 'customer_product_affinity' in data.columns:
            # Create bins for affinity scores
            bins = [0, 0.25, 0.5, 0.75, 1.0]
            labels = ['Low (0-0.25)', 'Medium-Low (0.25-0.5)', 'Medium-High (0.5-0.75)', 'High (0.75-1.0)']
            data['affinity_category'] = pd.cut(data['customer_product_affinity'], bins=bins, labels=labels, include_lowest=True)
            
            affinity_counts = data['affinity_category'].value_counts().reset_index()
            affinity_counts.columns = ['category', 'count']
            
            # Product Affinity Distribution Chart
            chart = alt.Chart(affinity_counts).mark_bar().encode(
                x=alt.X('category:N', title='Affinity Level', sort=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Customers'),
                color=alt.Color('category:N', scale=alt.Scale(domain=labels, range=['#E74C3C', '#F4D03F', '#5DADE2', '#52BE80']))
            )
            
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-15  # Increased space above bars
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300, width=500), use_container_width=True)
        else:
            st.write("Customer product affinity data not available")
    
    # Customer Lifecycle Stage
    st.subheader("Customer Lifecycle Stage Distribution")
    
    if 'customer_lifecycle_stage' in data.columns:
        lifecycle_counts = data['customer_lifecycle_stage'].value_counts().reset_index()
        lifecycle_counts.columns = ['stage', 'count']
        
        # Define lifecycle stage colors
        lifecycle_colors = {
            'Lead': '#F4D03F',      # Yellow
            'Onboarding': '#5DADE2', # Blue
            'Engaged': '#52BE80',    # Green
            'Converted': '#8E44AD'   # Purple
        }
        
        # Customer Lifecycle Stage Chart
        chart = alt.Chart(lifecycle_counts).mark_bar().encode(
            x=alt.X('stage:N', title='Lifecycle Stage', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count:Q', title='Number of Customers'),
            color=alt.Color('stage:N', scale=alt.Scale(domain=list(lifecycle_colors.keys()), range=list(lifecycle_colors.values())))
        )
        
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-15  # Increased space above bars
        ).encode(
            text='count:Q'
        )
        
        st.altair_chart((chart + text).properties(height=300, width=500), use_container_width=True)
    else:
        st.write("Customer lifecycle stage data not available")
    
    # Product Metrics Section
    st.subheader("Product Metrics")
    
    # Create 2 columns for product metrics
    col1, col2 = st.columns(2)
    
    # Top Product Types
    with col1:
        st.subheader("Top Product Types")
        
        if 'product_type' in data.columns:
            product_counts = data['product_type'].value_counts().head(5).reset_index()
            product_counts.columns = ['product_type', 'count']
            
            # Top Product Types Chart
            chart = alt.Chart(product_counts).mark_bar().encode(
                y=alt.Y('product_type:N', title='Product Type', sort='-x'),
                x=alt.X('count:Q', title='Number of Customers'),
                color=alt.Color('product_type:N', legend=None)
            )
            
            text = chart.mark_text(
                align='left',
                baseline='middle',
                dx=3
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Product type data not available")
    
    # Top Customer Segments
    with col2:
        st.subheader("Top Customer Segments")
        
        if 'customer_segment' in data.columns:
            segment_counts = data['customer_segment'].value_counts().head(5).reset_index()
            segment_counts.columns = ['segment', 'count']
            
            # Top Customer Segments Chart
            chart = alt.Chart(segment_counts).mark_bar().encode(
                y=alt.Y('segment:N', title='Customer Segment', sort='-x'),
                x=alt.X('count:Q', title='Number of Customers'),
                color=alt.Color('segment:N', legend=None)
            )
            
            text = chart.mark_text(
                align='left',
                baseline='middle',
                dx=3
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Customer segment data not available")

# AI Insights tab
with tabs[1]:
    st.subheader("✨ AI-Powered Insights")
    focus_area = st.radio("Focus Area", [
        "Overall Performance", 
        "Optimization Opportunities", 
        "Financial Impact", 
        "Strategic Recommendations"
    ])
    selected_model = st.selectbox("Cortex Model", MODELS, index=0)

    if st.button("Generate Insights"):
        with st.spinner("Generating with Snowflake Cortex..."):
            insights = generate_insights(data, focus_area, selected_model)
            if insights:
                st.markdown(insights)
                timestamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.insights_history.append({
                    "timestamp": timestamp,
                    "focus": focus_area,
                    "insights": insights,
                    "model": selected_model
                })
                st.download_button("Download Insights", insights, file_name=f"{solution_name.replace(' ', '_').lower()}_insights.md")
            else:
                st.error("No insights returned.")

# Insights History tab
with tabs[2]:
    st.subheader("📁 Insights History")
    if st.session_state.insights_history:
        for i, item in enumerate(reversed(st.session_state.insights_history)):
            with st.expander(f"{item['timestamp']} - {item['focus']} ({item['model']})", expanded=False):
                st.markdown(item["insights"])
    else:
        st.info("No insights generated yet. Go to the AI Insights tab to generate some insights.")

# Data Explorer tab
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

### 3.2 Create and Deploy the Streamlit in Snowflake Gen AI Data App
1. Switch to **Chrome Tab 4 (Snowflake UI)**
2. Click on **Projects** in the left navigation panel
3. Click on **Streamlit**
4. Click the **+ Streamlit App** blue button in the upper right corner
5. Configure your app:
   - App title: `FinMatch`
   - Database: Select `SF_LABUSER#_DB` (only option available for your user)
   - Schema: Select `financial_product_recommendation_connector` the schema created by your Fivetran connector (this should be the only schema available other than Public - do not select Public)
6. In the Streamlit Editor that appears (left side of the Streamlit UI), select all text (Command+A) and delete it
7. Paste the copied Streamlit application code into the empty editor (Command+V):
8. Click the blue **Run** button in the upper right corner
9. Close the editor by clicking the middle icon in the bottom left navigation

### 3.3 Explore the Streamlit in Snowflake Gen AI Data App
The FinMatch data app should now be running with the following sections:
- **Metrics**: View recommendation scores, customer satisfaction, churn probability, and product sales metrics
- **AI Insights**: Generate AI-powered analysis of the financial product recommendation data across four focus areas
- **Insights History**: Access previously generated AI insights
- **Data Explorer**: Browse the underlying data

## Done!
You've successfully:
1. Created a custom Fivetran connector using the Fivetran Connector SDK
2. Deployed the connector to sync financial product recommendation data into Snowflake
3. Built a Streamlit in Snowflake data app to visualize and analyze the data using Snowflake Cortex

## Next Steps
Consider how you might adapt this solution for your own use:
- Integration with banking systems like FIS, Fiserv, or Temenos
- Adding real-time transaction monitoring from payment networks
- Implementing machine learning models for more sophisticated recommendation algorithms
- Customizing the Streamlit app for specific financial product categories

## Resources
- Fivetran Connector SDK Documentation: [https://fivetran.com/docs/connectors/connector-sdk](https://fivetran.com/docs/connectors/connector-sdk)  
- Fivetran Connector SDK Examples: [https://fivetran.com/docs/connector-sdk/examples](https://fivetran.com/docs/connector-sdk/examples)
- API Connector Reference: [https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/icp_api_spec](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/icp_api_spec)
- Snowflake Cortex Documentation: [https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- Snowflake Streamlit Documentation: [https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)