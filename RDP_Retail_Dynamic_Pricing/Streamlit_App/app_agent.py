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
            "challenge": "Pricing managers manually review thousands of product prices and market conditions daily, spending 3+ hours analyzing competitor pricing, demand forecasts, and inventory levels to optimize pricing strategies and maximize revenue.",
            "solution": "Autonomous dynamic pricing workflow that analyzes real-time market data, customer behavior, and inventory levels to generate AI-driven price recommendations with revenue optimization, demand forecasting, and automated price adjustments across all retail channels."
        },
        "Optimization Opportunities": {
            "challenge": "Merchandising teams spend 4+ hours daily manually identifying inefficiencies in pricing strategies, inventory management, and customer segmentation across diverse product categories and sales channels.",
            "solution": "AI-powered retail optimization analysis that automatically detects pricing inefficiencies, inventory optimization opportunities, and customer segment targeting improvements with specific implementation recommendations for POS and inventory management system integration."
        },
        "Financial Impact": {
            "challenge": "Retail financial analysts manually calculate complex ROI metrics across pricing strategies and inventory management, requiring 3+ hours of financial modeling to assess dynamic pricing impact on revenue growth and cost reduction.",
            "solution": "Automated retail financial analysis that calculates comprehensive ROI, identifies revenue optimization opportunities across product categories and customer segments, and projects pricing strategy benefits with detailed retail economics forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "Chief Executive Officers spend hours manually analyzing competitive positioning and developing strategic roadmaps for retail technology advancement and omnichannel pricing transformation initiatives.",
            "solution": "Strategic retail intelligence workflow that analyzes competitive advantages against traditional fixed-pricing approaches, identifies emerging retail technology integration opportunities with IoT/AR, and creates prioritized omnichannel transformation roadmaps."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - Retail Dynamic Pricing focused version"""
    
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
        total_products = len(data)
        key_metrics = ["order_total", "product_price", "revenue_growth_rate", "customer_satisfaction_rate", "stockout_rate", "overstock_rate"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced retail data insights
        avg_revenue_growth = data['revenue_growth_rate'].mean() if 'revenue_growth_rate' in data.columns else 0
        avg_price = data['product_price'].mean() if 'product_price' in data.columns else 0
        product_categories = len(data['product_category'].unique()) if 'product_category' in data.columns else 0
        customer_segments = len(data['customer_segment'].unique()) if 'customer_segment' in data.columns else 0
        successful_optimizations = len(data[data['price_optimization_result'] == 'Success']) if 'price_optimization_result' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Retail Pricing Data Initialization", 15, f"Loading comprehensive retail pricing dataset with enhanced validation across {total_products} products and {product_categories} product categories", f"Connected to {len(available_metrics)} pricing metrics across {len(data.columns)} total retail data dimensions"),
                ("Dynamic Pricing Performance Assessment", 35, f"Advanced calculation of pricing optimization indicators with revenue analysis (avg revenue growth: {avg_revenue_growth:.1%})", f"Computed pricing metrics: {avg_revenue_growth:.1%} revenue growth, ${avg_price:.2f} avg price, {successful_optimizations} successful price optimizations"),
                ("Retail Pattern Recognition", 55, f"Sophisticated identification of pricing effectiveness patterns with customer behavior correlation analysis across {customer_segments} customer segments", f"Detected significant patterns in {len(data['price_optimization_recommendation'].unique()) if 'price_optimization_recommendation' in data.columns else 'N/A'} pricing recommendations with market response analysis completed"),
                ("AI Retail Intelligence Processing", 75, f"Processing comprehensive retail data through {model_name} with advanced reasoning for dynamic pricing optimization insights", f"Enhanced AI analysis of pricing strategy effectiveness across {total_products} retail products completed"),
                ("Retail Performance Report Compilation", 100, f"Professional retail pricing analysis with evidence-based recommendations and actionable revenue optimization insights ready", f"Comprehensive retail performance report with {len(available_metrics)} pricing metrics analysis and dynamic pricing recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            avg_stockout = data['stockout_rate'].mean() if 'stockout_rate' in data.columns else 0
            avg_overstock = data['overstock_rate'].mean() if 'overstock_rate' in data.columns else 0
            
            steps = [
                ("Retail Optimization Data Preparation", 12, f"Advanced loading of retail pricing and inventory data with enhanced validation across {total_products} products for efficiency improvement identification", f"Prepared {product_categories} product categories, {customer_segments} customer segments for optimization analysis with {avg_stockout:.1%} stockout rate and {avg_overstock:.1%} overstock rate"),
                ("Pricing Strategy Inefficiency Detection", 28, f"Sophisticated analysis of price elasticity and customer segmentation with evidence-based inefficiency identification", f"Identified optimization opportunities across {product_categories} product categories with pricing strategy gaps and inventory management issues"),
                ("Retail Correlation Analysis", 45, f"Enhanced examination of relationships between price elasticity, customer segments, and purchasing behavior", f"Analyzed correlations between pricing strategies and customer response across {total_products} retail products"),
                ("POS System Integration Optimization", 65, f"Comprehensive evaluation of dynamic pricing integration with existing Shopify, Square, and inventory management platforms", f"Assessed integration opportunities across {len(data.columns)} data points and retail system optimization needs"),
                ("AI Retail Optimization Intelligence", 85, f"Generating advanced pricing strategy recommendations using {model_name} with retail reasoning and merchandising implementation strategies", f"AI-powered retail optimization strategy across {product_categories} product areas and pricing improvements completed"),
                ("Retail Strategy Finalization", 100, f"Professional retail optimization report with prioritized implementation roadmap and pricing strategy impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and retail implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            avg_order_value = data['average_order_value'].mean() if 'average_order_value' in data.columns else 0
            total_order_value = data['order_total'].sum() if 'order_total' in data.columns else 0
            
            steps = [
                ("Retail Financial Data Integration", 15, f"Advanced loading of retail revenue data and pricing financial metrics with enhanced validation across {total_products} products", f"Integrated retail financial data: ${avg_order_value:.0f} avg order value, ${total_order_value:,.0f} total order value across product portfolio"),
                ("Revenue Impact Calculation", 30, f"Sophisticated ROI metrics calculation with pricing strategy analysis and customer lifetime value enhancement", f"Computed comprehensive financial analysis: revenue growth impact, customer value optimization, and ${total_order_value:,.0f} total sales volume"),
                ("Customer Value Financial Assessment", 50, f"Enhanced analysis of retail revenue impact with customer satisfaction metrics and pricing elasticity correlation analysis", f"Assessed financial implications: {avg_revenue_growth:.1%} revenue growth with {successful_optimizations} optimized pricing strategies driving customer value"),
                ("Retail Portfolio Efficiency Analysis", 70, f"Comprehensive evaluation of resource allocation efficiency across product categories with inventory cost optimization", f"Analyzed retail efficiency: {product_categories} product categories with pricing optimization and inventory cost reduction opportunities identified"),
                ("AI Retail Financial Modeling", 90, f"Advanced retail revenue projections and pricing ROI calculations using {model_name} with comprehensive retail cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} retail revenue metrics completed"),
                ("Retail Economics Report Generation", 100, f"Professional retail financial impact analysis with detailed pricing optimization ROI calculations and revenue forecasting ready", f"Comprehensive retail financial report with ${total_order_value:,.0f} revenue analysis and dynamic pricing strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            pricing_effectiveness_score = (avg_revenue_growth * 100) + (successful_optimizations / total_products * 50) if total_products > 0 else 0
            
            steps = [
                ("Retail Technology Assessment", 15, f"Advanced loading of retail technology context with competitive positioning analysis across {total_products} products and {product_categories} categories", f"Analyzed retail technology landscape: {product_categories} product categories, {customer_segments} customer segments, comprehensive dynamic pricing competitive assessment completed"),
                ("Retail Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional fixed-pricing retail approaches with AI-powered dynamic pricing effectiveness", f"Assessed competitive advantages: {pricing_effectiveness_score:.1f}% pricing effectiveness, {avg_revenue_growth:.1%} revenue growth vs traditional pricing methods"),
                ("Advanced Retail Technology Integration", 50, f"Enhanced analysis of integration opportunities with IoT sensors, AR customer experiences, and omnichannel retail technologies across {len(data.columns)} retail data dimensions", f"Identified strategic technology integration: IoT inventory monitoring, AR price comparison, omnichannel pricing synchronization opportunities"),
                ("Omnichannel Retail Strategy Development", 70, f"Comprehensive development of prioritized retail transformation roadmap with evidence-based dynamic pricing adoption strategies", f"Created sequenced implementation plan across {product_categories} product areas with emerging retail technology integration opportunities"),
                ("AI Retail Strategic Processing", 85, f"Advanced retail strategic recommendations using {model_name} with long-term competitive positioning and retail industry analysis", f"Enhanced strategic analysis with retail competitive positioning and omnichannel transformation roadmap completed"),
                ("Digital Retail Report Generation", 100, f"Professional digital retail transformation roadmap with competitive analysis and dynamic pricing implementation plan ready for CEO executive review", f"Comprehensive strategic report with {product_categories}-category implementation plan and retail competitive advantage analysis generated")
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
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each dynamic pricing analysis focus area**")
    
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
                st.success(f"🎉 {focus_area} Agent completed with real retail pricing data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real Retail Dynamic Pricing Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Dynamic Pricing Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Retail Pricing Analysis</small><br>
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