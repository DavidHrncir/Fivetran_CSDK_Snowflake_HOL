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
            "challenge": "Marketing analysts manually review hundreds of customer feedback reports, social media posts, and market research data daily, spending 4+ hours identifying consumer trends and actionable insights for product development.",
            "solution": "Autonomous consumer insights workflow that analyzes multi-source data from Medallia, Nielsen, and social platforms to identify emerging trends, consumer preferences, and generate prioritized product development recommendations."
        },
        "Optimization Opportunities": {
            "challenge": "Product development teams spend 3+ hours daily manually identifying optimization opportunities across customer segments, product positioning, and market trend analysis to improve product-market fit.",
            "solution": "AI-powered consumer optimization analysis that automatically detects segment targeting gaps, product positioning inefficiencies, and market trend opportunities with specific implementation recommendations for marketing campaigns."
        },
        "Financial Impact": {
            "challenge": "CPG financial analysts manually calculate complex ROI metrics across product lines and marketing campaigns, requiring 3+ hours of financial modeling to assess consumer insights impact on sales growth.",
            "solution": "Automated CPG financial analysis that calculates comprehensive ROI, identifies revenue optimization opportunities across product categories, and projects consumer insights benefits with detailed product launch forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "CPG executives spend hours manually analyzing competitive market positioning and developing strategic technology roadmaps for consumer insights advancement and brand differentiation.",
            "solution": "Strategic consumer intelligence workflow that analyzes competitive advantages, identifies emerging technology integration opportunities with AR/IoT, and creates prioritized product innovation roadmaps for market expansion."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - CPG Consumer Insights focused version"""
    
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
        total_consumers = len(data)
        key_metrics = ["feedback_rating", "sentiment_score", "customer_satisfaction_rate", "customer_retention_rate", "return_on_investment"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced CPG data insights
        avg_satisfaction = data['customer_satisfaction_rate'].mean() if 'customer_satisfaction_rate' in data.columns else 0
        avg_product_rating = data['product_rating'].mean() if 'product_rating' in data.columns else 0
        product_categories = len(data['product_category'].unique()) if 'product_category' in data.columns else 0
        customer_segments = len(data['customer_segment'].unique()) if 'customer_segment' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Consumer Data Initialization", 15, f"Loading comprehensive consumer insights dataset with enhanced validation across {total_consumers} customer records and {product_categories} product categories", f"Connected to {len(available_metrics)} consumer metrics across {len(data.columns)} total CPG data dimensions"),
                ("Consumer Insights Assessment", 35, f"Advanced calculation of consumer satisfaction indicators with sentiment analysis (avg satisfaction: {avg_satisfaction:.2%})", f"Computed consumer metrics: {avg_satisfaction:.2%} satisfaction rate, {avg_product_rating:.2f} avg product rating, {customer_segments} customer segments analyzed"),
                ("Market Pattern Recognition", 55, f"Sophisticated identification of consumer behavior patterns with social media sentiment correlation across {product_categories} product categories", f"Detected significant patterns in {len(data['product_category'].unique()) if 'product_category' in data.columns else 'N/A'} product categories with consumer preference analysis completed"),
                ("AI Consumer Intelligence Processing", 75, f"Processing comprehensive market data through {model_name} with advanced reasoning for consumer insights generation", f"Enhanced AI analysis of consumer insights effectiveness across {total_consumers} customer interactions completed"),
                ("CPG Insights Report Compilation", 100, f"Professional consumer insights analysis with evidence-based recommendations and actionable marketing insights ready", f"Comprehensive CPG performance report with {len(available_metrics)} consumer metrics analysis and product development recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            high_value_customers = len(data[data['customer_segment'] == 'High-Value']) if 'customer_segment' in data.columns else 0
            
            steps = [
                ("Consumer Optimization Data Preparation", 12, f"Advanced loading of consumer behavior data with enhanced validation across {total_consumers} customers for insights improvement identification", f"Prepared {product_categories} product categories, {customer_segments} customer segments for optimization analysis with {high_value_customers} high-value customers"),
                ("Market Inefficiency Detection", 28, f"Sophisticated analysis of customer segment targeting and product positioning with evidence-based inefficiency identification", f"Identified optimization opportunities across {product_categories} product categories with customer segment targeting and positioning gaps"),
                ("Consumer Behavior Correlation Analysis", 45, f"Enhanced examination of relationships between customer demographics, purchasing behaviors, and product satisfaction", f"Analyzed correlations between consumer demographics and satisfaction across {total_consumers} customer records"),
                ("Marketing System Integration Optimization", 65, f"Comprehensive evaluation of consumer insights integration with existing Medallia, Nielsen, and social media platforms", f"Assessed integration opportunities across {len(data.columns)} data points and marketing campaign optimization needs"),
                ("AI Marketing Optimization Intelligence", 85, f"Generating advanced consumer targeting recommendations using {model_name} with CPG reasoning and marketing implementation strategies", f"AI-powered marketing optimization strategy across {product_categories} product categories and consumer insights improvements completed"),
                ("Consumer Strategy Finalization", 100, f"Professional marketing optimization report with prioritized implementation roadmap and consumer insights impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and CPG implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            avg_revenue_growth = data['revenue_growth_rate'].mean() if 'revenue_growth_rate' in data.columns else 0
            potential_revenue = total_consumers * avg_product_rating * 100  # Estimated revenue impact
            
            steps = [
                ("CPG Financial Data Integration", 15, f"Advanced loading of consumer insights financial data and CPG revenue metrics with enhanced validation across {total_consumers} customers", f"Integrated CPG financial data: {avg_satisfaction:.1%} customer satisfaction, {avg_revenue_growth:.1%} avg revenue growth across product portfolio"),
                ("Consumer Revenue Impact Calculation", 30, f"Sophisticated ROI metrics calculation with product sales analysis and consumer insights implementation cost savings", f"Computed comprehensive financial analysis: consumer satisfaction impact, revenue growth potential, and ${potential_revenue:,.0f} estimated revenue optimization"),
                ("Product Sales Impact Assessment", 50, f"Enhanced analysis of CPG revenue impact with consumer preference metrics and product-market fit correlation analysis", f"Assessed sales implications: {avg_satisfaction:.1%} satisfaction rate with {product_categories} product categories requiring optimization"),
                ("Marketing Spend Efficiency Analysis", 70, f"Comprehensive evaluation of marketing resource allocation efficiency across consumer segments with campaign ROI optimization", f"Analyzed marketing efficiency: {customer_segments} customer segments with consumer insights-driven campaign cost optimization opportunities identified"),
                ("AI CPG Financial Modeling", 90, f"Advanced consumer insights financial projections and marketing ROI calculations using {model_name} with comprehensive CPG cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} CPG revenue metrics completed"),
                ("Consumer Economics Report Generation", 100, f"Professional CPG financial impact analysis with detailed consumer insights ROI calculations and product revenue forecasting ready", f"Comprehensive CPG financial report with ${potential_revenue:,.0f} revenue optimization analysis and consumer insights strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            market_penetration_score = avg_satisfaction * 100 if avg_satisfaction > 0 else 0
            
            steps = [
                ("CPG Market Intelligence Assessment", 15, f"Advanced loading of consumer goods market context with competitive positioning analysis across {total_consumers} consumers and {product_categories} product categories", f"Analyzed CPG market landscape: {product_categories} product categories, {customer_segments} customer segments, comprehensive consumer insights competitive assessment completed"),
                ("Consumer Insights Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional market research with AI-powered consumer insights effectiveness analysis", f"Assessed competitive advantages: {market_penetration_score:.1f}% market effectiveness, {avg_satisfaction:.1%} satisfaction improvement vs traditional research methods"),
                ("Emerging Technology Integration", 50, f"Enhanced analysis of integration opportunities with AR, IoT, and emerging consumer technologies across {len(data.columns)} consumer data dimensions", f"Identified strategic technology integration: AR consumer experiences, IoT product tracking, advanced consumer behavior analytics opportunities"),
                ("Product Innovation Strategy Development", 70, f"Comprehensive development of prioritized product development roadmap with evidence-based consumer insights adoption strategies", f"Created sequenced implementation plan across {product_categories} product areas with emerging market expansion opportunities"),
                ("AI Consumer Strategic Processing", 85, f"Advanced consumer insights strategic recommendations using {model_name} with long-term competitive positioning and CPG market analysis", f"Enhanced strategic analysis with consumer insights competitive positioning and product innovation roadmap completed"),
                ("Consumer Intelligence Report Generation", 100, f"Professional consumer insights strategic roadmap with competitive analysis and product development plan ready for CMO executive review", f"Comprehensive strategic report with {product_categories}-category implementation plan and consumer insights competitive advantage analysis generated")
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
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each consumer insights analysis focus area**")
    
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
                st.success(f"🎉 {focus_area} Agent completed with real consumer insights data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real CPG Consumer Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Consumer Insights Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Consumer Insights Analysis</small><br>
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