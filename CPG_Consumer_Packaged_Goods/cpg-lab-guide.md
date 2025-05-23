# Fivetran Connector SDK Hands on Lab at Snowflake Summit 2025: Consumer Packaged Goods Insights

## Overview
In this 20-minute hands on lab, you'll build a **custom Fivetran connector** using the **Fivetran Connector SDK** and the **Anthropic Workbench** to integrate consumer packaged goods data from a custom REST API into Snowflake. You'll then create a **Streamlit in Snowflake** application powering CPG metrics and **Snowflake Cortex AI-driven** consumer insights applications.

The CPG Insights custom connector should fetch consumer packaged goods records from a REST API and load them into a single table called `cpg_records` in your Snowflake database. The connector should deliver detailed information about customer segments, product categories, inventory levels, price optimization, and customer satisfaction metrics. It should handle authentication, pagination, error handling, and maintain state between sync runs using a cursor-based approach.

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
- **Control+`**: Open terminal in VS Code

## Step 1: Create a Custom Connector with the Fivetran Connector SDK (8 minutes)

### 1.1 Generate the Custom Connector Code Using AI Code Generation Assistance
1. Switch to **Chrome Tab 2 (Anthropic Workbench)**
2. Copy and paste the following **User prompt** into the workbench:

<details>
  <summary>Click to expand the User prompt and click the Copy icon in the right corner</summary>

```
- Provide a custom connector for CPG for the cpg_data endpoint. 1 table called cpg_records - all columns.  
- Make sure you copy the configuration.json file exactly - do not add any other variables to it.
- Here is the API spec: https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/cpg_api_spec

```
</details>

3. Click the black **Run** button in the upper right
4. After Claude generates the connector.py code, you will see a response similar to the example connector, but updated for the consumer packaged goods dataset.
5. Click [cpg_data](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/cpg_data) if you'd like to see the dataset.

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

        - Verifies data loading and schema creation by simulating a full sync (in this case, upserting 750 records into cpg_records).

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
cpg-insights-connector
```

12. Press Enter to deploy your new custom connector to Fivetran.

## Step 2: Start Data Sync in Fivetran (3 minutes)

1. Switch to **Chrome Tab 3 (Fivetran Automated Data Movement)**
2. Refresh the page and find your newly created connection named "cpg-insights-connector" in the connections list
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
    page_title="insightedge_–_ai_powered_consumer_insights_generation",
    page_icon="https://i.imgur.com/Og6gFnB.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

solution_name = '''Solution 2: InsightEdge – AI-powered Consumer Insights Generation'''
solution_name_clean = '''insightedge_–_ai_powered_consumer_insights_generation'''
table_name = '''CPG_RECORDS'''
table_description = '''Consolidated table containing consumer insights data from customer feedback, market research, and social media sources'''
solution_content = '''Solution 2: InsightEdge – AI-powered Consumer Insights Generation**

**Primary Business Challenge:** 
- Difficulty in generating actionable insights from large datasets in the Consumer Product Goods industry.

**Key Features:**
- Advanced data analytics and machine learning algorithms to generate insights from large datasets.
- Integration with various data sources, including customer feedback, market research, and social media.
- Real-time monitoring and alerts for emerging trends and changes in consumer preferences.

**Data Sources:**
- Customer Feedback: Medallia, Qualtrics, SurveyMonkey
- Market Research: Nielsen, Euromonitor, Euromonitor
- Social Media: Twitter, Facebook, Instagram

**Competitive Advantage:**
- InsightEdge provides actionable insights that enable companies to make informed product development and marketing decisions, stay ahead of the competition, and improve customer satisfaction.

**Key Stakeholders:**
- Product Development Teams
- Marketing Teams
- Sales Teams
- Top C-level Executive: Chief Marketing Officer (CMO)

**Technical Approach:**
- Generative AI algorithms, such as Generative Adversarial Networks (GANs) and Variational Autoencoders (VAEs), to analyze and generate insights from large datasets.

**Expected Business Results:**
- 12% increase in product sales due to improved insights.
- 10% reduction in product development costs by identifying emerging trends early.
- 15% improvement in customer satisfaction by delivering products that meet their preferences.
- 10% reduction in marketing costs by targeting the right audience with the right message.

**Calculations:**
- 12% increase in product sales: 
  **$ 10,000,000 annual sales × 12% increase = $ 1,200,000 additional sales/year**
- 10% reduction in product development costs: 
  **$ 5,000,000 annual development costs × 10% reduction = $ 500,000 savings/year**
- 15% improvement in customer satisfaction: 
  **80% baseline satisfaction rate × 15% improvement = 12% increase in satisfied customers**
- 10% reduction in marketing costs: 
  **$ 2,000,000 annual marketing costs × 10% reduction = $ 200,000 savings/year**

**Success Metrics:**
- Accuracy of insights generated
- Time-to-market for new products
- Customer satisfaction ratings
- Return on investment (ROI) for marketing campaigns

**Risk Assessment:**
- Data quality and availability
- Integration with existing systems
- Change management for product development and marketing teams
- Mitigation strategies: data quality checks, integration testing, training and support for teams

**Long-term Evolution:**
- Integration with emerging technologies, such as augmented reality and the Internet of Things (IoT)
- Expansion to new markets and regions
- Development of more advanced AI algorithms to improve insights generation accuracy

---

**'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for CPG</p>
    </div>
</div>
''', unsafe_allow_html=True)

# Define available models as strings
MODELS = [
    "llama3.1-8b", "snowflake-llama-3.1-405b", "snowflake-llama-3.3-70b", "mistral-large2", "llama3.1-70b", "llama4-maverick", "llama4-scout", "claude-3-5-sonnet", "deepseek-r1"
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
    data_summary = f"Table: {table_name}\nDescription: {table_description}\nRecords analyzed: {len(data)}\n"
    
    # Calculate basic statistics for numeric columns
    key_metrics = ["feedback_rating", "sentiment_score", "customer_satisfaction_rate", "customer_retention_rate", 
                  "return_on_investment", "time_to_market", "insight_accuracy", "sentiment_score_trend", 
                  "customer_satisfaction_trend"]
    
    for col in key_metrics:
        if col in data.columns:
            data_summary += f"- {col} (avg: {data[col].mean():.2f}, min: {data[col].min():.2f}, max: {data[col].max():.2f})\n"

    # Get top values for categorical columns
    categorical_options = ["customer_id", "feedback_text", "market_research_id", "market_trend", "social_media_id", 
                          "social_media_post", "product_id", "product_name", "product_category", "insight_type", 
                          "insight_description", "recommended_action", "action_status", "customer_segment", 
                          "customer_subsegment", "product_category_trend"]
    
    for cat_col in categorical_options:
        if cat_col in data.columns:
            top = data[cat_col].value_counts().head(3)
            data_summary += f"\nTop {cat_col} values:\n" + "\n".join(f"- {k}: {v}" for k, v in top.items())

    # Define specific instructions for each focus area
    focus_area_instructions = {
        "Overall Performance": """
        For the Overall Performance analysis of InsightEdge:
        1. Provide a comprehensive analysis of the consumer insights generation system using customer satisfaction rates, product ratings, and marketing effectiveness metrics
        2. Identify significant patterns in consumer preferences, product category performance, and customer segment behaviors
        3. Highlight 3-5 key CPG metrics that best indicate insights effectiveness (customer satisfaction improvement, product review sentiment, sales growth by category)
        4. Discuss both strengths and areas for improvement in the AI-powered consumer insights algorithms
        5. Include 3-5 actionable insights for product development and marketing teams based on the data
        
        Structure your response with these CPG-focused sections:
        - Consumer Insights (5 specific insights with supporting customer behavior data)
        - Product Performance Trends (3-4 significant trends in consumer preferences and product reception)
        - Marketing Strategy Recommendations (3-5 data-backed recommendations for improving product-market fit)
        - Implementation Steps (3-5 concrete next steps for product development and marketing teams)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of InsightEdge:
        1. Focus specifically on areas where consumer insights generation can be improved
        2. Identify inefficiencies in customer segment targeting, product positioning, and trend identification
        3. Analyze correlations between customer demographics, purchasing behaviors, and product satisfaction
        4. Prioritize optimization opportunities based on potential impact on product sales and customer satisfaction
        5. Suggest specific technical or process improvements for integration with feedback platforms and market research tools
        
        Structure your response with these CPG-focused sections:
        - Consumer Insights Optimization Priorities (3-5 areas with highest sales improvement potential)
        - Product Development Impact Analysis (quantified benefits of addressing each opportunity in terms of time-to-market and customer satisfaction)
        - Marketing Implementation Strategy (specific steps for marketing teams to implement each insight)
        - Data Integration Recommendations (specific technical changes needed for seamless integration with Medallia, Nielsen, and social media platforms)
        - CPG Market Risk Assessment (potential challenges for product teams and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of InsightEdge:
        1. Focus on cost-benefit analysis and ROI in CPG terms (insights implementation costs vs. product sales growth)
        2. Quantify financial impacts through increased product sales, reduced development costs, and optimized marketing spend
        3. Identify revenue optimization opportunities across different product categories and customer segments
        4. Analyze customer lifetime value impact across different product lines and market segments
        5. Project future financial outcomes based on improved product-market fit and accelerated trend identification
        
        Structure your response with these CPG-focused sections:
        - Product Revenue Analysis (breakdown of sales growth and potential revenue expansion by product category)
        - Development Cost Savings (how accelerated trend identification affects product development costs)
        - Marketing ROI Calculation (specific calculations showing return on investment in terms of campaign effectiveness)
        - Product Launch Opportunity Analysis (specific product categories with highest sales potential)
        - CPG Market Forecasting (projections based on consumer trend analysis and product innovation pipeline)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of InsightEdge:
        1. Focus on long-term strategic implications for CPG consumer insights and product development
        2. Identify competitive advantages against traditional market research approaches
        3. Suggest new directions for AI integration with emerging technologies like AR and IoT for consumer behavior tracking
        4. Connect recommendations to broader CPG goals of increasing market share and building brand loyalty
        5. Provide a product innovation roadmap with prioritized initiatives
        
        Structure your response with these CPG-focused sections:
        - CPG Market Context (how InsightEdge fits into broader consumer goods industry transformation)
        - Product Innovation Advantage Analysis (how to maximize speed-to-market compared to competitors)
        - CPG Strategic Priorities (3-5 high-impact strategic initiatives for improving consumer insights)
        - Future Consumer Technology Integration (how to evolve InsightEdge with AR and IoT for enhanced consumer understanding over 1-3 years)
        - Product Development Transformation Roadmap (sequenced steps for implementing AI-driven insights across new markets and regions)
        """
    }

    selected_focus_instructions = focus_area_instructions.get(focus_area, "")

    prompt = f'''
    You are an expert data analyst specializing in {focus_area.lower()} analysis.

    SOLUTION CONTEXT:
    {solution_name}

    {solution_content}

    DATA SUMMARY:
    {data_summary}

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

# Four tabs - with Metrics as the first tab (Tab 0)
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics Tab (Tab 0)
with tabs[0]:
    st.header("Consumer Insights Performance Metrics")
    
    # Global variables/constants for targets
    baseline_satisfaction = 0.80  # 80% baseline
    target_satisfaction_improvement = 0.15  # 15% improvement  
    target_satisfaction = baseline_satisfaction * (1 + target_satisfaction_improvement)  # 92% target
    target_revenue_growth = 0.12  # 12% increase
    
    # === KEY PERFORMANCE INDICATORS ===
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics
    avg_cust_satisfaction = data['customer_satisfaction_rate'].mean() if 'customer_satisfaction_rate' in data.columns else 0
    avg_revenue_growth = data['revenue_growth_rate'].mean() if 'revenue_growth_rate' in data.columns else 0
    avg_product_rating = data['product_rating'].mean() if 'product_rating' in data.columns else 0
    avg_stockout_rate = data['stockout_rate'].mean() if 'stockout_rate' in data.columns else 0
    
    with col1:
        with st.container(border=True):
            satisfaction_delta = avg_cust_satisfaction - baseline_satisfaction
            st.metric("Customer Satisfaction", f"{avg_cust_satisfaction:.2%}", f"{satisfaction_delta:.2%}")
    with col2:
        with st.container(border=True):
            revenue_delta = avg_revenue_growth - target_revenue_growth
            st.metric("Revenue Growth", f"{avg_revenue_growth:.2%}", f"{revenue_delta:.2%}")    
    with col3:
        with st.container(border=True):
            st.metric("Product Rating", f"{avg_product_rating:.2f}")    
    with col4:
        with st.container(border=True):
            st.metric("Stockout Rate", f"{avg_stockout_rate:.2%}")
    
    # === SEGMENT AND CATEGORY ANALYSIS ===
    st.subheader("Segment & Category Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer Segment Distribution
        if 'customer_segment' in data.columns:
            segment_counts = data['customer_segment'].value_counts().reset_index()
            segment_counts.columns = ['segment', 'count']
            
            segment_colors = {
                'Low-Value': '#F4D03F', 'Medium-Value': '#5DADE2', 'High-Value': '#52BE80'
            }
            
            chart = alt.Chart(segment_counts).mark_bar().encode(
                x=alt.X('segment:N', title='Customer Segment', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Count'),
                color=alt.Color('segment:N', scale=alt.Scale(domain=list(segment_colors.keys()), 
                                                        range=list(segment_colors.values())))
            ).properties(title="Customer Segment Distribution")
            
            # Add value labels to the bars
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                fontSize=12
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart(chart + text, use_container_width=True)
    
    with col2:
        # Product Category Distribution
        if 'product_category' in data.columns:
            category_counts = data['product_category'].value_counts().reset_index()
            category_counts.columns = ['category', 'count']
            
            chart = alt.Chart(category_counts).mark_bar().encode(
                y=alt.Y('category:N', title='Product Category', sort='-x'),
                x=alt.X('count:Q', title='Count'),
                color=alt.Color('category:N', legend=None)
            ).properties(title="Product Category Distribution")
            
            st.altair_chart(chart, use_container_width=True)
    
    # === PRICE OPTIMIZATION ANALYSIS ===
    st.subheader("Price Optimization Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        if 'price_optimization_result' in data.columns:
            result_counts = data['price_optimization_result'].value_counts().reset_index()
            result_counts.columns = ['result', 'count']
            
            colors = {'Success': '#52BE80', 'Failure': '#E74C3C'}
            
            chart = alt.Chart(result_counts).mark_bar().encode(
                x=alt.X('result:N', title='Result', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Count'),
                color=alt.Color('result:N', scale=alt.Scale(domain=list(colors.keys()), 
                                                        range=list(colors.values())))
            ).properties(title="Price Optimization Results")
            
            # Add value labels to the bars
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                fontSize=12
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart(chart + text, use_container_width=True)
    
    with col2:
        if 'price_optimization_recommendation' in data.columns:
            recommendation_counts = data['price_optimization_recommendation'].value_counts().reset_index()
            recommendation_counts.columns = ['recommendation', 'count']
            
            chart = alt.Chart(recommendation_counts).mark_bar().encode(
                x=alt.X('recommendation:N', title='Recommendation', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Count'),
                color='recommendation:N'
            ).properties(title="Price Recommendations")
            
            # Add value labels to the bars
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-5,
                fontSize=12
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart(chart + text, use_container_width=True)
    
    # === SATISFACTION vs GROWTH QUADRANT ===
    st.subheader("Satisfaction vs Growth Quadrant Analysis")
    
    if 'revenue_growth_rate' in data.columns and 'customer_satisfaction_rate' in data.columns:
        quadrant_data = data[['revenue_growth_rate', 'customer_satisfaction_rate', 'product_category']].copy()
        
        # Define quadrants
        quadrant_data['quadrant'] = 'Q3: Low Growth, Low Satisfaction'
        mask_q1 = (quadrant_data['revenue_growth_rate'] >= target_revenue_growth) & (quadrant_data['customer_satisfaction_rate'] >= target_satisfaction)
        mask_q2 = (quadrant_data['revenue_growth_rate'] < target_revenue_growth) & (quadrant_data['customer_satisfaction_rate'] >= target_satisfaction)
        mask_q4 = (quadrant_data['revenue_growth_rate'] >= target_revenue_growth) & (quadrant_data['customer_satisfaction_rate'] < target_satisfaction)
        
        quadrant_data.loc[mask_q1, 'quadrant'] = 'Q1: High Growth, High Satisfaction'
        quadrant_data.loc[mask_q2, 'quadrant'] = 'Q2: Low Growth, High Satisfaction'
        quadrant_data.loc[mask_q4, 'quadrant'] = 'Q4: High Growth, Low Satisfaction'
        
        # Create reference lines
        vline = alt.Chart(pd.DataFrame({'x': [target_revenue_growth]})).mark_rule(
            color='gray', strokeDash=[5, 5]
        ).encode(x='x:Q')
        
        hline = alt.Chart(pd.DataFrame({'y': [target_satisfaction]})).mark_rule(
            color='gray', strokeDash=[5, 5]
        ).encode(y='y:Q')
        
        # Main scatter plot
        scatter = alt.Chart(quadrant_data).mark_circle(size=60).encode(
            x=alt.X('revenue_growth_rate:Q', title='Revenue Growth Rate'),
            y=alt.Y('customer_satisfaction_rate:Q', title='Customer Satisfaction Rate'),
            color='quadrant:N',
            tooltip=['product_category', 'revenue_growth_rate', 'customer_satisfaction_rate', 'quadrant']
        ).properties(title="Satisfaction vs Growth Quadrant")
        
        # Combine all elements
        chart = (scatter + vline + hline).interactive()
        st.altair_chart(chart, use_container_width=True)
        
        # Show top categories
        if 'product_category' in data.columns:
            top_categories = data.groupby('product_category')[['revenue_growth_rate', 
                'customer_satisfaction_rate']].mean().reset_index()
            top_categories = top_categories.sort_values('revenue_growth_rate', ascending=False).head(5)
            
            st.subheader("Top 5 Product Categories by Revenue Growth")
            top_display = top_categories[['product_category', 'revenue_growth_rate', 
                'customer_satisfaction_rate']].reset_index(drop=True)
            top_display['revenue_growth_rate'] = top_display['revenue_growth_rate'].apply(lambda x: f"{x:.2%}")
            top_display['customer_satisfaction_rate'] = top_display['customer_satisfaction_rate'].apply(lambda x: f"{x:.2%}")
            top_display.columns = ['Product Category', 'Revenue Growth Rate', 'Customer Satisfaction Rate']
            st.dataframe(top_display, hide_index=True)
    
    # === INVENTORY & ORDER ANALYSIS ===
    st.subheader("Inventory & Order Analysis")
    
    # Create 4 columns with the last one being wider for the Order Status chart
    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])
    
    # Inventory Turnover
    with col1:
        if 'inventory_turnover' in data.columns:
            avg_inventory_turnover = data['inventory_turnover'].mean()
            with st.container(border=True):
                st.metric("Inventory Turnover", f"{avg_inventory_turnover:.2f}")
    
    # Overstock Rate
    with col2:
        if 'overstock_rate' in data.columns:
            avg_overstock = data['overstock_rate'].mean()
            with st.container(border=True):
                st.metric("Avg Overstock Rate", f"{avg_overstock:.2%}")
    
    # Fulfillment Rate
    with col3:
        if 'order_status' in data.columns:
            status_counts = data['order_status'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            total = status_counts['count'].sum()
            fulfilled_statuses = ['Delivered', 'Shipped']
            fulfilled = sum(status_counts.loc[status_counts['status'].isin(fulfilled_statuses), 'count'])
            fulfillment_rate = fulfilled / total * 100
            
            with st.container(border=True):
                st.metric("Fulfillment Rate", f"{fulfillment_rate:.1f}%")
    
    # Order Status Chart
    with col4:
        if 'order_status' in data.columns:
            status_colors = {
                'Delivered': '#52BE80', 'Shipped': '#5DADE2', 
                'Pending': '#F4D03F', 'Cancelled': '#E74C3C'
            }
            
            chart = alt.Chart(status_counts).mark_bar().encode(
                y=alt.Y('status:N', title='Status', sort='-x'),
                x=alt.X('count:Q', title='Count'),
                color=alt.Color('status:N', scale=alt.Scale(domain=list(status_colors.keys()), 
                                                      range=list(status_colors.values())))
            ).properties(title="Order Status")
            
            # Add text labels to the bars
            text = chart.mark_text(
                align='left',
                baseline='middle',
                dx=3,
                fontSize=12
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart(chart + text, use_container_width=True)

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
                    "insights": insights
                })
                st.download_button("Download Insights", insights, file_name=f"{solution_name.replace(' ', '_').lower()}_insights.md")
            else:
                st.error("No insights returned.")

# Insights History tab
with tabs[2]:
    st.subheader("📁 Insights History")
    if st.session_state.insights_history:
        for i, item in enumerate(reversed(st.session_state.insights_history)):
            with st.expander(f"{item['timestamp']} - {item['focus']}", expanded=False):
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
   - App title: `InsightEdge`
   - Database: Select `SF_LABUSER#_DB` (only option available for your user)
   - Schema: Select `cpg_insights_connector` the schema created by your Fivetran connector (this should be the only schema available other than Public - do not select Public)
6. In the Streamlit Editor that appears (left side of the Streamlit UI), select all text (Command+A) and delete it
7. Paste the copied Streamlit application code into the empty editor (Command+V):
8. Click the blue **Run** button in the upper right corner
9. Close the editor by clicking the middle icon in the bottom left navigation

### 3.3 Explore the Streamlit in Snowflake Gen AI Data App
The InsightEdge data app should now be running with the following sections:
- **Metrics**: View customer satisfaction, revenue growth, product ratings, and inventory metrics
- **AI Insights**: Generate AI-powered analysis of the consumer data across four focus areas
- **Insights History**: Access previously generated AI insights
- **Data Explorer**: Browse the underlying data

## Done!
You've successfully:
1. Created a custom Fivetran connector using the Fivetran Connector SDK
2. Deployed the connector to sync consumer packaged goods data into Snowflake
3. Built a Streamlit in Snowflake data app to visualize and analyze the data using Snowflake Cortex

## Next Steps
Consider how you might adapt this solution for your own use:
- Integration with retail systems like Medallia, Nielsen, or Euromonitor
- Adding real-time customer feedback monitoring from social media platforms
- Implementing machine learning models for more sophisticated trend predictions
- Customizing the Streamlit app for specific CPG categories

## Resources
- Fivetran Connector SDK Documentation: [https://fivetran.com/docs/connectors/connector-sdk](https://fivetran.com/docs/connectors/connector-sdk)  
- Fivetran Connector SDK Examples: [https://fivetran.com/docs/connector-sdk/examples](https://fivetran.com/docs/connector-sdk/examples)
- API Connector Reference: [https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/icp_api_spec](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/icp_api_spec)
- Snowflake Cortex Documentation: [https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- Snowflake Streamlit Documentation: [https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)