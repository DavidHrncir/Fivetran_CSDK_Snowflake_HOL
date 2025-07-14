import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="claimsphere_–_ai_driven_claims_processing_automation",
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

solution_name = '''Solution 1: ClaimSphere – AI-driven Claims Processing Automation'''
solution_name_clean = '''claimsphere_–_ai_driven_claims_processing_automation'''
table_name = '''ICP_RECORDS'''
table_description = '''Consolidated table containing key claims processing data from Claims Management Systems, Policy Administration Systems, and Customer Relationship Management Systems'''
solution_content = '''Solution 1: ClaimSphere – AI-driven Claims Processing Automation**

* **Primary Business Challenge:** Manual claims processing is time-consuming, prone to errors, and leads to delayed settlements, resulting in poor customer satisfaction and increased operational costs.
* **Key Features:**
	+ Automated claims data extraction and validation
	+ AI-driven claims classification and routing
	+ Predictive analytics for claims outcome forecasting
	+ Integration with existing claims management systems
* **Data Sources:**
	+ Claims Management Systems: Guidewire, Duck Creek, Insurity
	+ Policy Administration Systems: Oracle, SAP, Insurity
	+ Customer Relationship Management (CRM): Salesforce, HubSpot, Zoho
* **Competitive Advantage:** ClaimSphere differentiates itself from traditional approaches by leveraging generative AI to automate claims processing, reducing manual errors, and improving claims settlement speed.
* **Key Stakeholders:** Claims managers, underwriters, customer service representatives, and the Chief Operating Officer (COO).
* **Technical Approach:** Generative AI models are trained on historical claims data to learn patterns and relationships, enabling the automation of claims processing tasks.
* **Expected Business Results:**
	+ 15% reduction in claims processing time
	+ 10% reduction in claims processing errors
	+ 12% increase in customer satisfaction ratings
	+ 8% reduction in operational costs
* **Calculations:**
	+ 15% reduction in claims processing time: **100,000 claims/year × 10 hours/claim × 15% reduction = 15,000 hours saved/year**
	+ 10% reduction in claims processing errors: **10,000 claims/year × 5% baseline error rate × 10% reduction = 500 fewer errors/year**
	+ 12% increase in customer satisfaction ratings: **10,000 customers/year × 80% baseline satisfaction rate × 12% increase = 960 additional satisfied customers/year**
	+ 8% reduction in operational costs: **$ 10,000,000 annual operational costs × 8% reduction = $ 800,000 savings/year**
* **Success Metrics:** Claims processing time, claims processing accuracy, customer satisfaction ratings, operational costs.
* **Risk Assessment:** Integration with existing systems, data quality issues, and potential bias in AI models. Mitigation strategies include thorough testing, data validation, and ongoing model monitoring.
* **Long-term Evolution:** ClaimSphere will continue to evolve by incorporating new data sources, improving AI models, and expanding to other insurance products and lines of business.

**'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Insurance</p>
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
            "challenge": "Claims managers manually review thousands of insurance claims daily, spending 3+ hours analyzing claim documents, validating information, and routing claims through complex approval workflows to ensure accurate settlements.",
            "solution": "Autonomous claims processing workflow that analyzes claim documents, validates policy information, and routes claims automatically with AI-driven classification, fraud detection, and settlement recommendations to accelerate processing and improve accuracy."
        },
        "Optimization Opportunities": {
            "challenge": "Claims processing teams spend 4+ hours daily manually identifying inefficiencies in claim routing, validation workflows, and settlement processes across diverse insurance product lines and customer segments.",
            "solution": "AI-powered claims optimization analysis that automatically detects processing bottlenecks, validation gaps, and routing inefficiencies with specific implementation recommendations for Guidewire, Duck Creek, and Insurity system integration."
        },
        "Financial Impact": {
            "challenge": "Insurance financial analysts manually calculate complex ROI metrics across claims operations and customer satisfaction, requiring 3+ hours of cost modeling to assess operational efficiency and claims settlement optimization.",
            "solution": "Automated insurance financial analysis that calculates comprehensive ROI, identifies operational cost reduction opportunities across claim types, and projects customer satisfaction benefits with detailed claims economics forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "Chief Operating Officers spend hours manually analyzing competitive positioning and developing strategic roadmaps for claims processing automation advancement and digital transformation initiatives.",
            "solution": "Strategic insurance intelligence workflow that analyzes competitive advantages against traditional manual claims processing, identifies AI and automation integration opportunities, and creates prioritized digital claims transformation roadmaps."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - Insurance Claims Processing focused version"""
    
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
        total_claims = len(data)
        key_metrics = ["claim_processing_time", "claim_processing_error_reduction", "customer_satisfaction_rating", "operational_cost"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced insurance data insights
        avg_processing_time = data['claim_processing_time'].mean() if 'claim_processing_time' in data.columns else 0
        avg_error_reduction = data['claim_processing_error_reduction'].mean() if 'claim_processing_error_reduction' in data.columns else 0
        claim_types = len(data['claim_type'].unique()) if 'claim_type' in data.columns else 0
        customer_segments = len(data['customer_segment'].unique()) if 'customer_segment' in data.columns else 0
        approved_claims = len(data[data['claim_outcome'] == 'Approved']) if 'claim_outcome' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Claims Processing Data Initialization", 15, f"Loading comprehensive insurance claims dataset with enhanced validation across {total_claims} claims and {claim_types} claim types", f"Connected to {len(available_metrics)} claims metrics across {len(data.columns)} total insurance data dimensions"),
                ("Claims Processing Performance Assessment", 35, f"Advanced calculation of claims processing indicators with settlement analysis (avg processing time: {avg_processing_time:.1f}h)", f"Computed claims metrics: {avg_processing_time:.1f}h avg processing time, {avg_error_reduction:.1f}% error reduction, {approved_claims} approved claims"),
                ("Insurance Pattern Recognition", 55, f"Sophisticated identification of claim outcome patterns with settlement correlation analysis across {claim_types} claim categories", f"Detected significant patterns in {len(data['claim_outcome'].unique()) if 'claim_outcome' in data.columns else 'N/A'} claim outcomes with processing efficiency analysis completed"),
                ("AI Claims Intelligence Processing", 75, f"Processing comprehensive insurance data through {model_name} with advanced reasoning for claims processing automation insights", f"Enhanced AI analysis of claims processing effectiveness across {total_claims} insurance claims completed"),
                ("Insurance Claims Report Compilation", 100, f"Professional claims processing analysis with evidence-based recommendations and actionable settlement insights ready", f"Comprehensive claims performance report with {len(available_metrics)} insurance metrics analysis and processing optimization recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            settlement_rate = (approved_claims / total_claims) * 100 if total_claims > 0 else 0
            
            steps = [
                ("Claims Optimization Data Preparation", 12, f"Advanced loading of insurance claims processing data with enhanced validation across {total_claims} claims for efficiency improvement identification", f"Prepared {claim_types} claim types, {customer_segments} customer segments for optimization analysis with {settlement_rate:.1f}% settlement rate"),
                ("Claims Processing Inefficiency Detection", 28, f"Sophisticated analysis of claim routing and validation workflows with evidence-based inefficiency identification", f"Identified optimization opportunities across {claim_types} claim categories with processing bottlenecks and routing gaps"),
                ("Insurance Correlation Analysis", 45, f"Enhanced examination of relationships between processing times, error rates, and customer satisfaction across insurance operations", f"Analyzed correlations between claims processing and customer satisfaction across {total_claims} insurance claims"),
                ("Claims System Integration Optimization", 65, f"Comprehensive evaluation of claims processing integration with existing Guidewire, Duck Creek, and Insurity management systems", f"Assessed integration opportunities across {len(data.columns)} data points and claims management system optimization needs"),
                ("AI Claims Optimization Intelligence", 85, f"Generating advanced claims processing recommendations using {model_name} with insurance reasoning and automation implementation strategies", f"AI-powered claims optimization strategy across {claim_types} claim categories and processing improvements completed"),
                ("Claims Strategy Finalization", 100, f"Professional claims optimization report with prioritized implementation roadmap and processing efficiency impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and claims implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            avg_claim_amount = data['claim_amount'].mean() if 'claim_amount' in data.columns else 0
            total_cost_reduction = data['operational_cost_reduction'].sum() if 'operational_cost_reduction' in data.columns else 0
            
            steps = [
                ("Insurance Financial Data Integration", 15, f"Advanced loading of claims financial data and insurance operational metrics with enhanced validation across {total_claims} claims", f"Integrated insurance financial data: ${avg_claim_amount:,.0f} avg claim amount, ${total_cost_reduction:,.0f} total cost reduction across claims portfolio"),
                ("Claims Financial Impact Calculation", 30, f"Sophisticated ROI metrics calculation with settlement cost analysis and operational efficiency enhancement", f"Computed comprehensive financial analysis: claims processing costs, settlement efficiency, and ${total_cost_reduction:,.0f} operational cost optimization"),
                ("Customer Satisfaction Financial Assessment", 50, f"Enhanced analysis of insurance revenue impact with customer retention metrics and claims satisfaction correlation analysis", f"Assessed financial implications: {avg_error_reduction:.1f}% error reduction with {approved_claims} successful claim settlements driving customer satisfaction"),
                ("Claims Portfolio Efficiency Analysis", 70, f"Comprehensive evaluation of resource allocation efficiency across claim types with settlement cost optimization", f"Analyzed claims efficiency: {claim_types} claim categories with processing cost reduction and settlement optimization opportunities identified"),
                ("AI Insurance Financial Modeling", 90, f"Advanced claims financial projections and operational ROI calculations using {model_name} with comprehensive insurance cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} insurance financial metrics completed"),
                ("Insurance Economics Report Generation", 100, f"Professional insurance financial impact analysis with detailed claims processing ROI calculations and operational cost forecasting ready", f"Comprehensive insurance financial report with ${total_cost_reduction:,.0f} cost optimization analysis and claims efficiency strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            automation_effectiveness_score = (100 - avg_processing_time) if avg_processing_time > 0 else 0
            
            steps = [
                ("Insurance Technology Assessment", 15, f"Advanced loading of claims processing digital context with competitive positioning analysis across {total_claims} claims and {claim_types} insurance products", f"Analyzed insurance technology landscape: {claim_types} claim categories, {customer_segments} customer segments, comprehensive claims automation assessment completed"),
                ("Claims Processing Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional manual claims processing with AI-powered automation effectiveness", f"Assessed competitive advantages: {automation_effectiveness_score:.1f}% automation effectiveness, {avg_error_reduction:.1f}% error reduction vs manual processing methods"),
                ("Advanced Claims Technology Integration", 50, f"Enhanced analysis of integration opportunities with fraud detection AI, customer interaction automation, and advanced analytics across {len(data.columns)} claims data dimensions", f"Identified strategic technology integration: AI fraud detection, automated customer communications, predictive claims analytics opportunities"),
                ("Digital Claims Strategy Development", 70, f"Comprehensive development of prioritized digital transformation roadmap with evidence-based claims automation adoption strategies", f"Created sequenced implementation plan across {claim_types} claims areas with advanced insurance technology integration opportunities"),
                ("AI Insurance Strategic Processing", 85, f"Advanced claims processing strategic recommendations using {model_name} with long-term competitive positioning and insurance industry analysis", f"Enhanced strategic analysis with claims processing competitive positioning and insurance transformation roadmap completed"),
                ("Digital Insurance Report Generation", 100, f"Professional digital insurance transformation roadmap with competitive analysis and claims automation implementation plan ready for COO executive review", f"Comprehensive strategic report with {claim_types}-category implementation plan and claims processing competitive advantage analysis generated")
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
    key_metrics = ["claim_processing_time", "claim_processing_error_reduction", "customer_satisfaction_rating", "operational_cost", "claim_processing_duration", "claim_amount", "operational_cost_reduction"]
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
    categorical_options = ["policy_id", "claim_id", "claim_status", "claim_type", "claim_outcome", "customer_segment", "claim_category", "claim_subcategory", "customer_name", "customer_id"]
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
        For the Overall Performance analysis of ClaimSphere:
        1. Provide a comprehensive analysis of the claims processing automation system's performance using processing times, error reduction, and customer satisfaction ratings
        2. Identify significant patterns in claim outcomes, processing efficiency, and operational costs
        3. Highlight 3-5 key insurance metrics that best indicate processing effectiveness (processing time reduction, error reduction, customer satisfaction)
        4. Discuss both operational strengths and areas for improvement in claims processing
        5. Include 3-5 actionable insights for improving claims processing based on the data
        
        Structure your response with these insurance-focused sections:
        - Claims Insights (5 specific insights with supporting data)
        - Processing Efficiency Trends (3-4 significant trends in claims handling)
        - Operational Recommendations (3-5 data-backed recommendations for improving processing)
        - Implementation Steps (3-5 concrete next steps for claims teams)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of ClaimSphere:
        1. Focus specifically on areas where claims processing can be improved
        2. Identify inefficiencies in claims routing, processing workflows, and customer interactions
        3. Analyze correlations between processing times, error rates, and customer satisfaction
        4. Prioritize optimization opportunities based on potential impact on error reduction and settlement speed
        5. Suggest specific technical or process improvements for integration with existing claims systems
        
        Structure your response with these insurance-focused sections:
        - Processing Optimization Priorities (3-5 areas with highest improvement potential)
        - Customer Impact Analysis (quantified benefits of addressing each opportunity)
        - Implementation Strategy (specific steps for claims staff to implement each optimization)
        - System Integration Recommendations (specific technical changes needed for seamless workflow)
        - Risk Assessment (potential challenges and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of ClaimSphere:
        1. Focus on cost-benefit analysis and ROI in insurance terms (operational cost vs. efficiency improvement)
        2. Quantify financial impacts through operational cost reduction, processing time savings, and error reduction
        3. Identify cost savings opportunities in claim settlement optimization and processing efficiency
        4. Analyze resource allocation efficiency across different claim types and categories
        5. Project future financial outcomes based on improved processing efficiency and reduced errors
        
        Structure your response with these insurance-focused sections:
        - Operational Cost Analysis (breakdown of processing costs and potential savings)
        - Revenue Impact (how improved processing affects insurance revenue)
        - ROI Calculation (specific calculations showing return on investment)
        - Cost Reduction Opportunities (specific areas to reduce operational costs)
        - Financial Forecasting (projections based on improved efficiency metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of ClaimSphere:
        1. Focus on long-term strategic implications for claims processing improvement
        2. Identify competitive advantages against traditional claims processing systems
        3. Suggest new directions for AI integration with claims data, customer interactions, and fraud detection
        4. Connect recommendations to broader insurance goals of reducing costs and improving customer satisfaction
        5. Provide an implementation roadmap with prioritized initiatives
        
        Structure your response with these insurance-focused sections:
        - Industry Context (how ClaimSphere fits into broader insurance industry transformation)
        - Competitive Advantage Analysis (how to maximize effectiveness compared to traditional systems)
        - Strategic Priorities (3-5 high-impact strategic initiatives)
        - Future Technology Vision (how to evolve ClaimSphere with additional AI capabilities over 1-3 years)
        - Implementation Roadmap (sequenced steps for integration and adoption)
        """
    }

    # Get the specific instructions for the selected focus area
    selected_focus_instructions = focus_area_instructions.get(focus_area, "")

    prompt = f'''
    You are an expert data analyst specializing in {focus_area.lower()} analysis for insurance claims processing.

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

categorical_cols = [col for col in ["policy_id", "claim_id", "claim_status", "claim_type", "claim_outcome", "customer_segment", "claim_category", "claim_subcategory", "customer_name", "customer_id"] if col in data.columns]
numeric_cols = [col for col in ["claim_processing_time", "claim_processing_error_reduction", "customer_satisfaction_rating", "operational_cost", "claim_processing_duration", "claim_amount", "operational_cost_reduction"] if col in data.columns]
date_cols = [col for col in ["claim_date", "claim_processing_start_date", "claim_processing_end_date", "policy_effective_date"] if col in data.columns]

sample_cols = data.columns.tolist()
numeric_candidates = [col for col in sample_cols if data[col].dtype in ['float64', 'int64'] and 'id' not in col.lower()]
date_candidates = [col for col in sample_cols if 'date' in col.lower() or 'timestamp' in col.lower()]
cat_candidates = [col for col in sample_cols if data[col].dtype == 'object' and data[col].nunique() < 1000]

# Four tabs - with Metrics as the first tab (Tab 0)
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics Tab (Tab 0)
with tabs[0]:
    st.header("Claims Processing Metrics")
    
    # Overview metrics row - 4 KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics from the data
    avg_processing_time = data['claim_processing_time'].mean() if 'claim_processing_time' in data.columns else 0
    avg_error_reduction = data['claim_processing_error_reduction'].mean() if 'claim_processing_error_reduction' in data.columns else 0
    avg_csat = data['customer_satisfaction_rating'].mean() if 'customer_satisfaction_rating' in data.columns else 0
    total_cost_reduction = data['operational_cost_reduction'].sum() if 'operational_cost_reduction' in data.columns else 0
    
    with col1:
        with st.container(border=True):
            st.metric(
                "Avg Processing Time (hours)", 
                f"{avg_processing_time:.2f}",
                f"{-15:.1f}%" if avg_processing_time > 0 else "0%",
                help="Average claim processing time in hours. Lower is better."
            )
    
    with col2:
        with st.container(border=True):
            st.metric(
                "Avg Error Reduction", 
                f"{avg_error_reduction:.2f}%",
                f"{10:.1f}%" if avg_error_reduction > 0 else "0%",
                help="Average reduction in processing errors. Higher is better."
            )
    
    with col3:
        with st.container(border=True):
            st.metric(
                "Avg Customer Satisfaction", 
                f"{avg_csat:.1f}/5",
                f"{12:.1f}%" if avg_csat > 3 else f"{(avg_csat - 3) / 3 * 100:.1f}%",
                help="Average customer satisfaction rating (1-5 scale). Higher is better."
            )
    
    with col4:
        with st.container(border=True):
            st.metric(
                "Total Cost Reduction", 
                f"${total_cost_reduction:,.2f}",
                f"{8:.1f}%" if total_cost_reduction > 0 else "0%",
                help="Total operational cost reduction across all claims"
            )
    
    # Financial Metrics Section - 3 Financial Metrics
    st.subheader("Financial Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            avg_operational_cost = data['operational_cost'].mean() if 'operational_cost' in data.columns else 0
            st.metric("Avg Operational Cost", f"${avg_operational_cost:,.2f}")
        
    with col2:
        with st.container(border=True):
            avg_claim_amount = data['claim_amount'].mean() if 'claim_amount' in data.columns else 0
            st.metric("Avg Claim Amount", f"${avg_claim_amount:,.2f}")
        
    with col3:
        with st.container(border=True):
            avg_duration = data['claim_processing_duration'].mean() if 'claim_processing_duration' in data.columns else 0
            st.metric("Avg Processing Duration (days)", f"{avg_duration:.1f}")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    # Claim Outcome Distribution
    with col1:
        st.subheader("Claim Outcome Distribution")
        
        if 'claim_outcome' in data.columns:
            outcome_counts = data['claim_outcome'].value_counts().reset_index()
            outcome_counts.columns = ['outcome', 'count']
            
            colors = {
                'Approved': '#52BE80',
                'Settled': '#5DADE2',
                'Pending': '#F4D03F',
                'In Progress': '#85C1E9',
                'Disputed': '#E59866',
                'Closed': '#7DCEA0',
                'Reopened': '#F5B041',
                'Withdrawn': '#E74C3C'
            }
            
            chart = alt.Chart(outcome_counts).mark_bar().encode(
                x=alt.X('outcome:N', title='Claim Outcome', sort='-y'),
                y=alt.Y('count:Q', title='Number of Claims'),
                color=alt.Color('outcome:N', scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())))
            )
            
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-15  # Increased space above bars
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Claim outcome data not available")
    
    # Claim Type Distribution
    with col2:
        st.subheader("Claim Type Distribution")
        
        if 'claim_type' in data.columns:
            type_counts = data['claim_type'].value_counts().reset_index()
            type_counts.columns = ['type', 'count']
            
            chart = alt.Chart(type_counts).mark_bar().encode(
                x=alt.X('type:N', title='Claim Type', sort='-y'),
                y=alt.Y('count:Q', title='Number of Claims'),
                color=alt.Color('type:N')
            )
            
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-15
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Claim type data not available")
    
    # Customer Satisfaction
    st.subheader("Customer Satisfaction Ratings")
    
    if 'customer_satisfaction_rating' in data.columns:
        satisfaction_counts = data['customer_satisfaction_rating'].value_counts().reset_index()
        satisfaction_counts.columns = ['rating', 'count']
        
        # Convert rating to string for better display
        satisfaction_counts['rating'] = satisfaction_counts['rating'].astype(str)
        
        # Define color scale for ratings
        color_scale = alt.Scale(domain=['1', '2', '3', '4', '5'], 
                             range=['#E74C3C', '#F39C12', '#F1C40F', '#2ECC71', '#27AE60'])
        
        chart = alt.Chart(satisfaction_counts).mark_bar().encode(
            x=alt.X('rating:N', title='Satisfaction Rating', sort='x', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count:Q', title='Number of Customers'),
            color=alt.Color('rating:N', scale=color_scale)
        )
        
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-15  # Increased space above bars
        ).encode(
            text='count:Q'
        )
        
        st.altair_chart((chart + text).properties(height=300), use_container_width=True)
    else:
        st.write("Customer satisfaction data not available")
    
    # Claims Processing Metrics Section
    st.subheader("Claims Processing Metrics")
    
    # Create 2 columns for category/subcategory metrics
    col1, col2 = st.columns(2)
    
    # Claim Categories
    with col1:
        st.subheader("Top Claim Categories")
        
        if 'claim_category' in data.columns:
            category_counts = data['claim_category'].value_counts().head(5).reset_index()
            category_counts.columns = ['category', 'count']
            
            chart = alt.Chart(category_counts).mark_bar().encode(
                y=alt.Y('category:N', title='Claim Category', sort='-x'),
                x=alt.X('count:Q', title='Number of Claims'),
                color=alt.Color('category:N', legend=None)
            )
            
            text = chart.mark_text(
                align='left',
                baseline='middle',
                dx=3  # Maintain horizontal spacing for these horizontal bar charts
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Claim category data not available")
    
    # Claim Subcategories
    with col2:
        st.subheader("Top Claim Subcategories")
        
        if 'claim_subcategory' in data.columns:
            subcategory_counts = data['claim_subcategory'].value_counts().head(5).reset_index()
            subcategory_counts.columns = ['subcategory', 'count']
            
            chart = alt.Chart(subcategory_counts).mark_bar().encode(
                y=alt.Y('subcategory:N', title='Claim Subcategory', sort='-x'),
                x=alt.X('count:Q', title='Number of Claims'),
                color=alt.Color('subcategory:N', legend=None)
            )
            
            text = chart.mark_text(
                align='left',
                baseline='middle',
                dx=3  # Maintain horizontal spacing for these horizontal bar charts
            ).encode(
                text='count:Q'
            )
            
            st.altair_chart((chart + text).properties(height=300), use_container_width=True)
        else:
            st.write("Claim subcategory data not available")
    
    # Customer Segments
    st.subheader("Claims by Customer Segment")
    
    if 'customer_segment' in data.columns:
        segment_counts = data['customer_segment'].value_counts().reset_index()
        segment_counts.columns = ['segment', 'count']
        
        chart = alt.Chart(segment_counts).mark_bar().encode(
            x=alt.X('segment:N', title='Customer Segment', sort='-y'),
            y=alt.Y('count:Q', title='Number of Claims'),
            color=alt.Color('segment:N')
        )
        
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-15  # Increased space above bars
        ).encode(
            text='count:Q'
        )
        
        st.altair_chart((chart + text).properties(height=300), use_container_width=True)
    else:
        st.write("Customer segment data not available")

# AI Insights tab
with tabs[1]:
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each claims processing analysis focus area**")
    
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
                st.success(f"🎉 {focus_area} Agent completed with real insurance claims data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real Insurance Claims Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Claims Processing Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Claims Processing Analysis</small><br>
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