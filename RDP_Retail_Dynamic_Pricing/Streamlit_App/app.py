import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="pricepulse_–_ai_driven_dynamic_pricing",
    page_icon="https://i.imgur.com/Og6gFnB.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

solution_name = '''Solution 1: PricePulse – AI-driven Dynamic Pricing'''
solution_name_clean = '''pricepulse_–_ai_driven_dynamic_pricing'''
table_name = '''RDP_RECORDS'''
table_description = '''Consolidated table containing key retail data for dynamic pricing and inventory management'''
solution_content = '''Solution 1: PricePulse – AI-driven Dynamic Pricing**

* **Tagline:** "Maximize profits with real-time price optimization"
* **Primary business challenge:** Inability to respond quickly to market fluctuations, leading to lost revenue and overstocking
* **Key features:**
	+ Real-time market data analysis
	+ Predictive demand forecasting
	+ Automated price optimization
	+ Integration with inventory management systems
* **Data sources:**
	+ Point of Sale (POS): Shopify, Square, Lightspeed
	+ Customer Relationship Management (CRM): Salesforce, HubSpot, Zoho
	+ Inventory Management: Manhattan Associates, Oracle Retail, JDA Software
* **Competitive advantage:** PricePulse's real-time analysis and predictive capabilities enable retailers to respond quickly to market changes, maximizing profits and minimizing losses
* **Key stakeholders:** Pricing Manager, Inventory Manager, Marketing Manager, CEO
* **Technical approach:** Generative AI algorithms analyze market data, predict demand, and optimize prices in real-time
* **Expected business results:**
	+ 8% increase in revenue
	+ 12% reduction in overstocking
	+ 10% decrease in stockouts
	+ 5% improvement in customer satisfaction
* **Calculations:**
	+ 8% increase in revenue: **$ 10,000,000 annual revenue × 8% increase = $ 800,000 additional revenue/year**
	+ 12% reduction in overstocking: **$ 500,000 annual overstocking costs × 12% reduction = $ 60,000 savings/year**
	+ 10% decrease in stockouts: **$ 200,000 annual stockout costs × 10% decrease = $ 20,000 savings/year**
	+ 5% improvement in customer satisfaction: **80% baseline customer satisfaction rate × 5% improvement = 4% increase in customer satisfaction**
* **Success metrics:** Revenue growth, overstocking reduction, stockout decrease, customer satisfaction improvement
* **Risk assessment:** Integration challenges with existing systems, data quality issues, potential for over-reliance on AI
* **Long-term evolution:** Integration with emerging technologies like IoT and AR to enhance customer experience and improve supply chain efficiency

**'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Retail</p>
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
    key_metrics = ["order_total", "product_price", "inventory_level", "customer_ltv", "order_frequency", "average_order_value", "product_rating", "product_review_count", "price_elasticity", "demand_forecast", "inventory_turnover", "stockout_rate", "overstock_rate", "revenue_growth_rate", "customer_satisfaction_rate"]
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
    categorical_options = ["order_id", "customer_id", "product_id", "customer_segment", "order_status", "product_category", "product_subcategory", "price_optimization_result", "price_optimization_recommendation"]
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
        For the Overall Performance analysis of PricePulse:
        1. Provide a comprehensive analysis of the dynamic pricing system using revenue growth rate, customer satisfaction, and inventory metrics (stockout and overstock rates)
        2. Identify significant patterns in price elasticity, price optimization results, and their impact on sales performance
        3. Highlight 3-5 key retail metrics that best indicate pricing effectiveness (revenue growth, inventory turnover, average order value)
        4. Discuss both strengths and areas for improvement in the AI-driven price optimization algorithms
        5. Include 3-5 actionable insights for improving pricing strategies based on the data
        
        Structure your response with these retail-focused sections:
        - Pricing Optimization Insights (5 specific insights with supporting sales and inventory data)
        - Revenue and Inventory Trends (3-4 significant trends in pricing effectiveness and stock management)
        - Pricing Strategy Recommendations (3-5 data-backed recommendations for improving dynamic pricing)
        - Implementation Steps (3-5 concrete next steps for pricing managers and inventory teams)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of PricePulse:
        1. Focus specifically on areas where pricing optimization can be improved
        2. Identify inefficiencies in price recommendations, inventory management, and product category performance
        3. Analyze correlations between price elasticity, customer segments, and purchasing behavior
        4. Prioritize optimization opportunities based on potential impact on revenue growth and inventory reduction
        5. Suggest specific technical or process improvements for integration with existing retail systems
        
        Structure your response with these retail-focused sections:
        - Pricing Optimization Priorities (3-5 areas with highest revenue improvement potential)
        - Customer Impact Analysis (quantified benefits of addressing each opportunity in terms of satisfaction and lifetime value)
        - Retail Implementation Strategy (specific steps for merchandising teams to implement each optimization)
        - POS and Inventory System Integration Recommendations (specific technical changes needed for seamless integration with Shopify, Square, and inventory management systems)
        - Retail Risk Assessment (potential challenges for pricing teams and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of PricePulse:
        1. Focus on cost-benefit analysis and ROI in retail terms (implementation costs vs. revenue growth)
        2. Quantify financial impacts through increased sales, reduced overstock costs, and minimized stockout losses
        3. Identify revenue optimization opportunities across different product categories and customer segments
        4. Analyze price elasticity impact on customer lifetime value and average order value
        5. Project future financial outcomes based on improved pricing algorithms and inventory efficiency
        
        Structure your response with these retail-focused sections:
        - Retail Revenue Analysis (breakdown of sales growth and potential revenue expansion by product category)
        - Inventory Cost Savings (how reduced overstock and stockouts affect the bottom line)
        - Retail ROI Calculation (specific calculations showing return on investment in terms of revenue growth)
        - Pricing Opportunity Analysis (specific product categories with highest revenue potential)
        - Sales Forecasting (projections based on optimized pricing and inventory metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of PricePulse:
        1. Focus on long-term strategic implications for retail pricing competitiveness
        2. Identify competitive advantages against traditional fixed-pricing approaches
        3. Suggest new directions for AI integration with emerging retail technologies like IoT and AR
        4. Connect recommendations to broader retail goals of maximizing profits and enhancing customer experience
        5. Provide a retail transformation roadmap with prioritized initiatives
        
        Structure your response with these retail-focused sections:
        - Retail Market Context (how PricePulse fits into broader retail industry transformation)
        - Competitive Pricing Advantage Analysis (how to maximize pricing strategies compared to competitors)
        - Retail Strategic Priorities (3-5 high-impact strategic initiatives for improving dynamic pricing)
        - Future Retail Technology Integration (how to evolve PricePulse with IoT and AR for enhanced customer experience over 1-3 years)
        - Omnichannel Pricing Roadmap (sequenced steps for implementing dynamic pricing across all retail channels)
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

categorical_cols = [col for col in ["order_id", "customer_id", "product_id", "customer_segment", "order_status", "product_category", "product_subcategory", "price_optimization_result", "price_optimization_recommendation"] if col in data.columns]
numeric_cols = [col for col in ["order_total", "product_price", "inventory_level", "customer_ltv", "order_frequency", "average_order_value", "product_rating", "product_review_count", "price_elasticity", "demand_forecast", "inventory_turnover", "stockout_rate", "overstock_rate", "revenue_growth_rate", "customer_satisfaction_rate"] if col in data.columns]
date_cols = [col for col in ["order_date", "price_optimization_date"] if col in data.columns]

sample_cols = data.columns.tolist()
numeric_candidates = [col for col in sample_cols if data[col].dtype in ['float64', 'int64'] and 'id' not in col.lower()]
date_candidates = [col for col in sample_cols if 'date' in col.lower() or 'timestamp' in col.lower()]
cat_candidates = [col for col in sample_cols if data[col].dtype == 'object' and data[col].nunique() < 1000]

# Four tabs - with Metrics as the first tab (Tab 0)
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics Tab (Tab 0)
with tabs[0]:
    st.header("Retail Dynamic Pricing Metrics")
    
    # Overview metrics row - 4 KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics from the data
    avg_revenue_growth = data['revenue_growth_rate'].mean() if 'revenue_growth_rate' in data.columns else 0
    avg_overstock_rate = data['overstock_rate'].mean() if 'overstock_rate' in data.columns else 0
    avg_stockout_rate = data['stockout_rate'].mean() if 'stockout_rate' in data.columns else 0
    avg_customer_satisfaction = data['customer_satisfaction_rate'].mean() if 'customer_satisfaction_rate' in data.columns else 0
    
    # Targets based on solution content
    target_revenue_growth = 0.08  # 8% increase
    target_overstock_reduction = 0.12  # 12% reduction
    target_stockout_reduction = 0.10  # 10% reduction
    target_satisfaction_improvement = 0.05  # 5% improvement
    baseline_satisfaction = 0.80  # 80% baseline
    
    with col1:
        with st.container(border=True):
            revenue_delta = avg_revenue_growth - target_revenue_growth
            st.metric(
                "Avg Revenue Growth", 
                f"{avg_revenue_growth:.2%}",
                f"{revenue_delta:.2%}",
                help="Average revenue growth rate. Target: 8%"
            )
    
    with col2:
        with st.container(border=True):
            # For overstock and stockout, lower is better
            overstock_delta = -1 * (avg_overstock_rate - target_overstock_reduction)
            st.metric(
                "Avg Overstock Rate", 
                f"{avg_overstock_rate:.2%}",
                f"{overstock_delta:.2%}",
                help="Average overstock rate. Target reduction: 12%"
            )
    
    with col3:
        with st.container(border=True):
            stockout_delta = -1 * (avg_stockout_rate - target_stockout_reduction)
            st.metric(
                "Avg Stockout Rate", 
                f"{avg_stockout_rate:.2%}",
                f"{stockout_delta:.2%}",
                help="Average stockout rate. Target reduction: 10%"
            )
    
    with col4:
        with st.container(border=True):
            satisfaction_delta = avg_customer_satisfaction - baseline_satisfaction
            st.metric(
                "Customer Satisfaction", 
                f"{avg_customer_satisfaction:.2%}",
                f"{satisfaction_delta:.2%}",
                help="Average customer satisfaction rate. Baseline: 80%, Target improvement: 5%"
            )
    
    # Pricing Metrics Section
    st.subheader("Pricing Performance Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            avg_price = data['product_price'].mean() if 'product_price' in data.columns else 0
            st.metric("Avg Product Price", f"${avg_price:.2f}")
        
    with col2:
        with st.container(border=True):
            avg_order_value = data['average_order_value'].mean() if 'average_order_value' in data.columns else 0
            st.metric("Avg Order Value", f"${avg_order_value:.2f}")
        
    with col3:
        with st.container(border=True):
            avg_elasticity = data['price_elasticity'].mean() if 'price_elasticity' in data.columns else 0
            st.metric("Avg Price Elasticity", f"{avg_elasticity:.4f}")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    # Price Optimization Results Distribution
    with col1:
        st.subheader("Price Optimization Results Distribution")
        
        if 'price_optimization_result' in data.columns:
            result_counts = data['price_optimization_result'].value_counts().reset_index()
            result_counts.columns = ['result', 'count']
            
            # Result colors
            colors = {
                'Success': '#52BE80',  # Green
                'Failure': '#E74C3C'   # Red
            }
            
            # Price Optimization Results Distribution Chart
            chart = alt.Chart(result_counts).mark_bar().encode(
                x=alt.X('result:N', title='Price Optimization Result', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Products'),
                color=alt.Color('result:N', scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())))
            )
            
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-10
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Price optimization result data not available")
    
    # Price Recommendation Distribution
    with col2:
        st.subheader("Price Recommendation Distribution")
        
        if 'price_optimization_recommendation' in data.columns:
            recommendation_counts = data['price_optimization_recommendation'].value_counts().reset_index()
            recommendation_counts.columns = ['recommendation', 'count']
            
            # Price Recommendation Distribution Chart
            chart = alt.Chart(recommendation_counts).mark_bar().encode(
                x=alt.X('recommendation:N', title='Price Recommendation', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Products'),
                color=alt.Color('recommendation:N', scale=alt.Scale(scheme='category10'))
            )
            
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-10
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Price optimization recommendation data not available")
    
    # Customer Segment Distribution
    st.subheader("Customer Segment Distribution")
    
    if 'customer_segment' in data.columns:
        segment_counts = data['customer_segment'].value_counts().reset_index()
        segment_counts.columns = ['segment', 'count']
        
        # Define segment colors
        segment_colors = {
            'Low-Value': '#F4D03F',      # Yellow
            'Medium-Value': '#5DADE2',   # Blue
            'High-Value': '#52BE80'      # Green
        }
        
        # Customer Segment Distribution Chart
        chart = alt.Chart(segment_counts).mark_bar().encode(
            x=alt.X('segment:N', title='Customer Segment', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count:Q', title='Number of Customers'),
            color=alt.Color('segment:N', scale=alt.Scale(domain=list(segment_colors.keys()), range=list(segment_colors.values())))
        )
        
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-10
        ).encode(
            text='count:Q'
        )
        
        st.altair_chart((chart + text).properties(height=300), use_container_width=True)
    else:
        st.write("Customer segment data not available")
    
    # Product Category Analysis Section
    st.subheader("Product Category Analysis")
    
    # Create 2 columns for category metrics
    col1, col2 = st.columns(2)
    
    # Product Category Distribution
    with col1:
        st.subheader("Product Category Distribution")
        
        if 'product_category' in data.columns:
            category_counts = data['product_category'].value_counts().reset_index()
            category_counts.columns = ['category', 'count']
            
            # Product Category Distribution Chart
            chart = alt.Chart(category_counts).mark_bar().encode(
                y=alt.Y('category:N', title='Product Category', sort='-x'),
                x=alt.X('count:Q', title='Number of Products'),
                color=alt.Color('category:N', legend=None)
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
            st.write("Product category data not available")
    
    # Product Subcategory Distribution
    with col2:
        st.subheader("Top Product Subcategories")
        
        if 'product_subcategory' in data.columns:
            subcategory_counts = data['product_subcategory'].value_counts().head(10).reset_index()
            subcategory_counts.columns = ['subcategory', 'count']
            
            # Product Subcategory Distribution Chart
            chart = alt.Chart(subcategory_counts).mark_bar().encode(
                y=alt.Y('subcategory:N', title='Product Subcategory', sort='-x'),
                x=alt.X('count:Q', title='Number of Products'),
                color=alt.Color('subcategory:N', legend=None)
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
            st.write("Product subcategory data not available")
    
    # Revenue Growth vs Customer Satisfaction Quadrant Analysis
    st.subheader("Revenue Growth vs Customer Satisfaction Quadrant Analysis")
    
    if 'revenue_growth_rate' in data.columns and 'customer_satisfaction_rate' in data.columns:
        # Target values based on solution content
        target_revenue_growth = 0.08  # 8%
        target_satisfaction = 0.80 + (0.80 * 0.05)  # 80% baseline + 5% improvement = 84%
        
        # Create a copy of the data with just the columns we need
        quadrant_data = data[['revenue_growth_rate', 'customer_satisfaction_rate', 'product_category', 'price_optimization_result']].copy()
        
        # Calculate a performance score
        quadrant_data['performance_score'] = (quadrant_data['revenue_growth_rate'] / target_revenue_growth + 
                                             quadrant_data['customer_satisfaction_rate'] / target_satisfaction) / 2
        
        # Label quadrants
        quadrant_data['quadrant'] = 'Q3: Low Growth, Low Satisfaction'  # default
        
        # Q1: High Growth, High Satisfaction (optimal)
        mask_q1 = (quadrant_data['revenue_growth_rate'] >= target_revenue_growth) & (quadrant_data['customer_satisfaction_rate'] >= target_satisfaction)
        quadrant_data.loc[mask_q1, 'quadrant'] = 'Q1: High Growth, High Satisfaction ✓'
        
        # Q2: Low Growth, High Satisfaction
        mask_q2 = (quadrant_data['revenue_growth_rate'] < target_revenue_growth) & (quadrant_data['customer_satisfaction_rate'] >= target_satisfaction)
        quadrant_data.loc[mask_q2, 'quadrant'] = 'Q2: Low Growth, High Satisfaction'
        
        # Q4: High Growth, Low Satisfaction
        mask_q4 = (quadrant_data['revenue_growth_rate'] >= target_revenue_growth) & (quadrant_data['customer_satisfaction_rate'] < target_satisfaction)
        quadrant_data.loc[mask_q4, 'quadrant'] = 'Q4: High Growth, Low Satisfaction'
        
        # Top performers - to highlight
        top_performers = quadrant_data.sort_values('performance_score', ascending=False).head(5)
        
        # Create reference lines for targets
        vline = alt.Chart(pd.DataFrame({'x': [target_revenue_growth]})).mark_rule(
            color='gray', strokeDash=[5, 5]
        ).encode(x='x:Q')
        
        hline = alt.Chart(pd.DataFrame({'y': [target_satisfaction]})).mark_rule(
            color='gray', strokeDash=[5, 5]
        ).encode(y='y:Q')
        
        # Annotations for quadrants
        text_data = pd.DataFrame({
            'revenue_growth_rate': [target_revenue_growth/2, target_revenue_growth*1.5, target_revenue_growth/2, target_revenue_growth*1.5],
            'customer_satisfaction_rate': [target_satisfaction*1.05, target_satisfaction*1.05, target_satisfaction*0.95, target_satisfaction*0.95],
            'label': ['Q2', 'Q1 (Optimal)', 'Q3', 'Q4']
        })
        
        text_chart = alt.Chart(text_data).mark_text(
            align='center',
            baseline='middle',
            fontSize=14,
            opacity=0.7
        ).encode(
            x='revenue_growth_rate:Q',
            y='customer_satisfaction_rate:Q',
            text='label:N'
        )
        
        # Main scatter plot
        scatter = alt.Chart(quadrant_data).mark_circle(
            size=60,
            opacity=0.6
        ).encode(
            x=alt.X('revenue_growth_rate:Q', 
                   title='Revenue Growth Rate',
                   scale=alt.Scale(domain=[0, max(quadrant_data['revenue_growth_rate'])*1.05])),
            y=alt.Y('customer_satisfaction_rate:Q', 
                   title='Customer Satisfaction Rate',
                   scale=alt.Scale(domain=[0, max(quadrant_data['customer_satisfaction_rate'])*1.05])),
            color=alt.Color('quadrant:N', 
                          legend=alt.Legend(title="Performance Quadrant")),
            tooltip=['product_category', 'revenue_growth_rate', 'customer_satisfaction_rate', 
                    'price_optimization_result', 'quadrant']
        )
        
        # Highlight top performers
        highlight = alt.Chart(top_performers).mark_circle(
            size=100,
            stroke='black',
            strokeWidth=2
        ).encode(
            x='revenue_growth_rate:Q',
            y='customer_satisfaction_rate:Q',
            tooltip=['product_category', 'revenue_growth_rate', 'customer_satisfaction_rate', 
                   'price_optimization_result', 'performance_score']
        )
        
        # Target labels
        target_labels = alt.Chart(pd.DataFrame({
            'x': [target_revenue_growth],
            'y': [0],
            'text': [f'Target: {target_revenue_growth:.0%}']
        })).mark_text(
            align='center',
            baseline='top',
            dy=10,
            fontSize=10
        ).encode(
            x='x:Q',
            y='y:Q',
            text='text:N'
        )
        
        target_labels_y = alt.Chart(pd.DataFrame({
            'x': [0],
            'y': [target_satisfaction],
            'text': [f'Target: {target_satisfaction:.0%}']
        })).mark_text(
            align='left',
            baseline='middle',
            dx=10,
            fontSize=10
        ).encode(
            x='x:Q',
            y='y:Q',
            text='text:N'
        )
        
        # Combine all elements
        chart = (scatter + highlight + vline + hline + text_chart + target_labels + target_labels_y).interactive()
        
        # Add metrics about quadrant distribution
        q1_pct = (quadrant_data['quadrant'] == 'Q1: High Growth, High Satisfaction ✓').mean() * 100
        
        # Show chart and metrics
        st.altair_chart(chart, use_container_width=True)
        
        # Show quadrant distribution
        st.markdown(f"""
        **Quadrant Distribution:**
        - **Q1 (Optimal):** {q1_pct:.1f}% of products achieve both target revenue growth and customer satisfaction
        - **Top categories are highlighted with black outline**
        """)
        
        # Show top categories
        if 'product_category' in data.columns:
            # Get top categories by revenue growth
            top_categories = data.groupby('product_category')[['revenue_growth_rate', 'customer_satisfaction_rate']].mean().reset_index()
            top_categories = top_categories.sort_values('revenue_growth_rate', ascending=False).head(5)
            
            st.subheader("Top 5 Product Categories by Revenue Growth")
            top_display = top_categories[['product_category', 'revenue_growth_rate', 'customer_satisfaction_rate']].reset_index(drop=True)
            top_display['revenue_growth_rate'] = top_display['revenue_growth_rate'].apply(lambda x: f"{x:.2%}")
            top_display['customer_satisfaction_rate'] = top_display['customer_satisfaction_rate'].apply(lambda x: f"{x:.2%}")
            top_display.columns = ['Product Category', 'Revenue Growth Rate', 'Customer Satisfaction Rate']
            st.dataframe(top_display, hide_index=True)
        
    else:
        st.write("Revenue growth or customer satisfaction data not available")
    
    # Price Elasticity vs Inventory Analysis
    st.subheader("Price Elasticity vs Inventory Turnover Analysis")
    
    if 'price_elasticity' in data.columns and 'inventory_turnover' in data.columns:
        elasticity_turnover = data[['price_elasticity', 'inventory_turnover', 'product_category', 'price_optimization_recommendation']].copy()
        
        # Create scatter plot
        scatter = alt.Chart(elasticity_turnover).mark_circle(size=60).encode(
            x=alt.X('price_elasticity:Q', title='Price Elasticity'),
            y=alt.Y('inventory_turnover:Q', title='Inventory Turnover'),
            color='product_category:N',
            tooltip=['product_category', 'price_elasticity', 'inventory_turnover', 'price_optimization_recommendation']
        ).interactive()
        
        st.altair_chart(scatter, use_container_width=True)
        
        # Analysis text
        st.markdown("""
        **Price Elasticity vs Inventory Turnover Insights:**
        - Products in the bottom right (high elasticity, low turnover) are most sensitive to price changes and may benefit from price reductions
        - Products in the top left (low elasticity, high turnover) can potentially support price increases without significant impact on sales
        - Optimize pricing strategies based on the position of products in this chart
        """)
    else:
        st.write("Price elasticity or inventory turnover data not available")
    
    # Order Status Distribution
    st.subheader("Order Status Distribution")
    
    if 'order_status' in data.columns:
        status_counts = data['order_status'].value_counts().reset_index()
        status_counts.columns = ['status', 'count']
        
        # Calculate percentages
        total = status_counts['count'].sum()
        status_counts['percentage'] = status_counts['count'] / total * 100
        status_counts['label'] = status_counts['percentage'].apply(lambda x: f"{x:.1f}%")
        
        # Define custom colors for each status
        status_colors = {
            'Delivered': '#52BE80',  # Green
            'Shipped': '#5DADE2',    # Blue
            'Pending': '#F4D03F',    # Yellow
            'Cancelled': '#E74C3C'   # Red
        }
        
        # Create a more visually appealing horizontal bar chart with percentages
        bars = alt.Chart(status_counts).mark_bar().encode(
            y=alt.Y('status:N', title='Order Status', sort='-x'),
            x=alt.X('percentage:Q', title='Percentage (%)'),
            color=alt.Color('status:N', scale=alt.Scale(domain=list(status_colors.keys()), 
                                                        range=list(status_colors.values()))),
            tooltip=['status', 'count', alt.Tooltip('percentage:Q', format='.1f')]
        )
        
        # Add text labels showing percentage
        text = bars.mark_text(
            align='left',
            baseline='middle',
            dx=3,
            fontSize=12
        ).encode(
            text='label:N'
        )
        
        # Create a small dashboard with multiple related visualizations
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Show the improved bar chart
            st.altair_chart((bars + text).properties(height=300), use_container_width=True)
        
        with col2:
            # Add some key metrics in a visually appealing format
            # Calculate order fulfillment rate
            fulfilled_statuses = ['Delivered', 'Shipped']
            problem_statuses = ['Cancelled']
            
            fulfilled_orders = sum(status_counts.loc[status_counts['status'].isin(fulfilled_statuses), 'count'])
            problem_orders = sum(status_counts.loc[status_counts['status'].isin(problem_statuses), 'count'])
            
            fulfillment_rate = fulfilled_orders / total * 100
            cancellation_rate = problem_orders / total * 100
            
            # Display metrics in attractive containers
            with st.container(border=True):
                st.metric(
                    "Fulfillment Rate", 
                    f"{fulfillment_rate:.1f}%",
                    help="Orders that are Delivered or Shipped"
                )
            
            with st.container(border=True):
                st.metric(
                    "Cancellation Rate", 
                    f"{cancellation_rate:.1f}%",
                    help="Cancelled orders (lower is better)"
                )
            
            # Add a summary insight
            st.markdown(f"""
            **Order Processing Insights:**
            - {fulfillment_rate:.1f}% of orders are successfully processed
            - Dynamic pricing may help reduce the {cancellation_rate:.1f}% cancellation rate
            """)
    else:
        st.write("Order status data not available")
    
    # Inventory Management Summary
    st.subheader("Inventory Management Summary")
    
    if 'stockout_rate' in data.columns and 'overstock_rate' in data.columns and 'inventory_turnover' in data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            # Calculate inventory health metrics
            avg_stockout = data['stockout_rate'].mean()
            avg_overstock = data['overstock_rate'].mean()
            avg_turnover = data['inventory_turnover'].mean()
            
            # Display metrics
            st.metric("Average Inventory Turnover", f"{avg_turnover:.2f}", help="Higher is better")
            
            # Generate insights text
            st.markdown(f"""
            **Inventory Health Analysis:**
            - Average Stockout Rate: {avg_stockout:.2%}
            - Average Overstock Rate: {avg_overstock:.2%}
            - Target Stockout Reduction: {target_stockout_reduction:.0%}
            - Target Overstock Reduction: {target_overstock_reduction:.0%}
            
            Dynamic pricing has the potential to significantly improve inventory efficiency by reducing both stockouts and overstocking through real-time price adjustments.
            """)
        
        with col2:
            if 'product_category' in data.columns:
                # Calculate category-level inventory metrics
                category_inventory = data.groupby('product_category')[['stockout_rate', 'overstock_rate', 'inventory_turnover']].mean().reset_index()
                
                # Sort by stockout rate
                category_inventory = category_inventory.sort_values('stockout_rate', ascending=False)
                
                # Create a column chart for stockout rates by category
                bar = alt.Chart(category_inventory).mark_bar().encode(
                    y=alt.Y('product_category:N', title='Product Category', sort='-x'),
                    x=alt.X('stockout_rate:Q', title='Stockout Rate'),
                    color=alt.Color('stockout_rate:Q', scale=alt.Scale(scheme='redblue', reverse=True)),
                    tooltip=['product_category', 'stockout_rate', 'overstock_rate', 'inventory_turnover']
                )
                
                st.altair_chart(bar, use_container_width=True)
    else:
        st.write("Inventory metrics data not available")

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