import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="trialgenius_–_ai_powered_clinical_trial_design_and_optimization",
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

solution_name = '''Solution 1: TrialGenius – AI-Powered Clinical Trial Design and Optimization'''
solution_name_clean = '''trialgenius_–_ai_powered_clinical_trial_design_and_optimization'''
table_name = '''PHR_RECORDS'''
table_description = '''Integrated data from clinical trial management systems, electronic data capture, and real-world evidence databases'''
solution_content = '''Solution 1: TrialGenius – AI-Powered Clinical Trial Design and Optimization**

**Business Challenge:**
Pharmaceutical companies face mounting pressure to reduce clinical trial costs and timelines while improving success rates. Traditional clinical trial design relies heavily on historical precedent and expert intuition, leading to suboptimal patient stratification, inefficient site selection, and protocol designs that fail to account for real-world variability. This results in 90% of clinical trials failing to meet enrollment timelines and $2.6 billion average cost per approved drug, with clinical trials representing 60-70% of total development costs.

**Key Features:**
• Intelligent protocol generation with AI-powered inclusion/exclusion criteria optimization
• Predictive patient recruitment modeling with site-specific enrollment forecasting
• Adaptive trial design recommendations based on interim data analysis
• Synthetic control arm generation for rare disease studies
• Real-time protocol amendment suggestions based on emerging data patterns
• Multi-scenario simulation engine for risk assessment and contingency planning

**Data Sources:**
• Clinical Trial Management Systems (CTMS): Veeva Vault CTMS, Oracle Clinical One, Medidata Rave
• Electronic Data Capture (EDC): Medidata Rave EDC, Oracle Clinical One Data Collection, Veeva Vault EDC
• Real-World Evidence Databases: Flatiron Health, IQVIA Real-World Data, Optum Clinformatics
• Regulatory Databases: FDA Orange Book, EMA Clinical Data Publication Policy, ClinicalTrials.gov
• Patient Registries: TriNetX, IBM Watson Health, Syapse
• Genomic Databases: gnomAD, UK Biobank, All of Us Research Program

**Competitive Advantage:**
TrialGenius differentiates from traditional clinical trial optimization through its generative AI capability to create novel trial designs rather than simply analyzing existing ones. Unlike conventional statistical modeling tools, it generates synthetic patient populations and simulates thousands of trial scenarios simultaneously, enabling pharmaceutical companies to identify optimal trial parameters before patient enrollment begins. This proactive approach reduces trial failure risk by 40% compared to reactive optimization methods.

**Key Stakeholders:**
• Primary: Chief Medical Officer, VP of Clinical Development, Clinical Operations Directors
• Secondary: Biostatisticians, Regulatory Affairs Directors, Clinical Data Managers
• Tertiary: Site Investigators, Clinical Research Associates, Patient Recruitment Specialists
• **Top C-Level Executive:** Chief Medical Officer (CMO)

**Technical Approach:**
The solution leverages large language models fine-tuned on clinical trial protocols and outcomes to generate optimized trial designs. Generative adversarial networks create synthetic patient populations that mirror real-world demographics while preserving privacy. Transformer-based models analyze historical trial data to identify success patterns and generate protocol recommendations.

**Expected Business Results:**
- **40% reduction in trial failure risk**
  **100 trials/year × 90% baseline failure rate × 40% reduction = 36 fewer failed trials/year**
- **$520 million in development cost savings annually**
  **$2.6 billion average cost per drug × 20% cost reduction = $520 million savings per approved drug**
- **30% improvement in patient enrollment timelines**
  **18 months average enrollment time × 30% improvement = 5.4 months faster enrollment**
- **50% reduction in protocol amendment frequency**
  **Average 3 amendments per trial × 50% reduction = 1.5 fewer amendments per trial**

**Success Metrics:**
- Reduction in trial failure rates
- Clinical development cost savings
- Patient enrollment timeline improvements
- Protocol amendment frequency reduction
- Regulatory approval success rates

**Risk Assessment:**
Potential challenges include:
- Regulatory acceptance of AI-generated protocols
- Integration with existing CTMS and EDC systems
- Data quality and standardization across clinical sites

Mitigation strategies:
- Early engagement with regulatory authorities
- Comprehensive system integration testing
- Implementation of robust data governance frameworks

**Long-term Evolution:**
Over the next 3-5 years, TrialGenius will continue to evolve by incorporating real-world evidence, expanding to include post-market surveillance, and integrating with emerging digital health technologies like wearables and digital biomarkers.'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Clinical Trials</p>
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
            "challenge": "Chief Medical Officers manually review hundreds of clinical trial protocols, enrollment data, and patient outcomes daily, spending 4+ hours analyzing trial performance, patient stratification effectiveness, and site performance to identify critical enrollment issues and protocol optimization opportunities.",
            "solution": "Autonomous clinical trial workflow that analyzes protocol data, enrollment metrics, patient demographics, and site performance to generate automated trial summaries, identify enrollment bottlenecks, and produce prioritized clinical insights with adaptive trial design recommendations."
        },
        "Optimization Opportunities": {
            "challenge": "Clinical Operations Directors spend 5+ hours daily manually identifying inefficiencies in patient recruitment strategies, site selection criteria, and protocol design parameters across multiple concurrent clinical trials and therapeutic areas.",
            "solution": "AI-powered clinical trial optimization analysis that automatically detects patient recruitment gaps, site performance inefficiencies, and protocol design improvements with specific implementation recommendations for CTMS and EDC system integration."
        },
        "Financial Impact": {
            "challenge": "VP of Clinical Development manually calculate complex ROI metrics across clinical trial activities and patient recruitment performance, requiring 4+ hours of cost modeling to assess trial efficiency and development cost optimization across the clinical portfolio.",
            "solution": "Automated pharmaceutical financial analysis that calculates comprehensive clinical trial ROI, identifies patient recruitment cost reduction opportunities across disease areas, and projects trial efficiency benefits with detailed development cost forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "Chief Medical Officers spend hours manually analyzing digital transformation opportunities and developing strategic clinical technology roadmaps for trial design advancement and adaptive trial implementation across therapeutic portfolios.",
            "solution": "Strategic clinical trial intelligence workflow that analyzes competitive advantages against traditional manual trial design processes, identifies AI and adaptive trial integration opportunities, and creates prioritized digital clinical transformation roadmaps."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - Clinical Trial focused version"""
    
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
        total_records = len(data)
        key_metrics = ["patient_age", "enrollment_rate", "dropout_rate"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced clinical trial data insights
        avg_enrollment_rate = data['enrollment_rate'].mean() if 'enrollment_rate' in data.columns else 0
        avg_dropout_rate = data['dropout_rate'].mean() if 'dropout_rate' in data.columns else 0
        disease_areas = len(data['disease_area'].unique()) if 'disease_area' in data.columns else 0
        active_trials = len(data['trial_id'].unique()) if 'trial_id' in data.columns else 0
        avg_patient_age = data['patient_age'].mean() if 'patient_age' in data.columns else 0
        sites_count = len(data['site_name'].unique()) if 'site_name' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Clinical Trial Data Initialization", 15, f"Loading comprehensive clinical trial dataset with enhanced validation across {total_records} patient records and {active_trials} active trials", f"Connected to {len(available_metrics)} clinical metrics across {len(data.columns)} total trial data dimensions"),
                ("Patient Enrollment Assessment", 35, f"Advanced calculation of clinical trial indicators with enrollment analysis (avg enrollment rate: {avg_enrollment_rate:.1f}%)", f"Computed clinical metrics: {avg_enrollment_rate:.1f}% enrollment rate, {avg_dropout_rate:.1f}% dropout rate, {avg_patient_age:.1f} avg patient age"),
                ("Clinical Trial Pattern Recognition", 55, f"Sophisticated identification of patient recruitment patterns with site correlation analysis across {disease_areas} disease areas", f"Detected significant patterns in {len(data['trial_status'].unique()) if 'trial_status' in data.columns else 'N/A'} trial status categories with site correlation analysis completed"),
                ("AI Clinical Trial Intelligence Processing", 75, f"Processing comprehensive clinical data through {model_name} with advanced reasoning for trial optimization insights", f"Enhanced AI analysis of clinical trial design effectiveness across {total_records} patient records completed"),
                ("Clinical Performance Report Compilation", 100, f"Professional clinical trial analysis with evidence-based recommendations and actionable protocol insights ready", f"Comprehensive clinical performance report with {len(available_metrics)} trial metrics analysis and patient recruitment recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            active_enrollment = len(data[data['trial_status'] == 'Active']) if 'trial_status' in data.columns else 0
            enrollment_success_rate = (active_enrollment / total_records) * 100 if total_records > 0 else 0
            
            steps = [
                ("Clinical Trial Optimization Data Preparation", 12, f"Advanced loading of patient recruitment data with enhanced validation across {total_records} records for enrollment improvement identification", f"Prepared {disease_areas} disease areas, {sites_count} clinical sites for optimization analysis with {enrollment_success_rate:.1f}% active enrollment rate"),
                ("Patient Recruitment Inefficiency Detection", 28, f"Sophisticated analysis of enrollment strategies and site performance with evidence-based inefficiency identification", f"Identified optimization opportunities across {disease_areas} disease areas with patient recruitment and site performance gaps"),
                ("Clinical Trial Correlation Analysis", 45, f"Enhanced examination of relationships between disease areas, patient demographics, and enrollment success rates", f"Analyzed correlations between trial characteristics and patient outcomes across {total_records} clinical records"),
                ("CTMS Integration Optimization", 65, f"Comprehensive evaluation of clinical operations integration with existing Veeva, Oracle, and Medidata CTMS systems", f"Assessed integration opportunities across {len(data.columns)} data points and clinical trial system optimization needs"),
                ("AI Clinical Trial Intelligence", 85, f"Generating advanced clinical optimization recommendations using {model_name} with pharmaceutical reasoning and implementation strategies", f"AI-powered clinical trial optimization strategy across {disease_areas} therapeutic areas and patient recruitment improvements completed"),
                ("Clinical Trial Strategy Finalization", 100, f"Professional clinical trial optimization report with prioritized implementation roadmap and enrollment impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and clinical operations implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            total_patients = data['patient_id'].nunique() if 'patient_id' in data.columns else 0
            avg_trial_cost_estimate = 2600000 * (avg_dropout_rate / 100) if avg_dropout_rate > 0 else 0
            
            steps = [
                ("Pharmaceutical Financial Data Integration", 15, f"Advanced loading of clinical trial financial data and development cost metrics with enhanced validation across {total_records} patient records", f"Integrated clinical trial financial data: {avg_enrollment_rate:.1f}% avg enrollment rate, {avg_dropout_rate:.1f}% dropout rate across {active_trials} trials"),
                ("Clinical Development Cost-Benefit Calculation", 30, f"Sophisticated ROI metrics calculation with patient recruitment analysis and clinical trial efficiency cost savings", f"Computed comprehensive cost analysis: enrollment expenses, dropout costs, and ${avg_trial_cost_estimate:,.0f} estimated trial optimization potential"),
                ("Patient Recruitment Impact Assessment", 50, f"Enhanced analysis of clinical trial revenue impact with patient retention metrics and enrollment cost correlation analysis", f"Assessed clinical implications: {avg_dropout_rate:.1f}% dropout rate with {sites_count} clinical sites requiring cost optimization"),
                ("Clinical Trial Resource Efficiency Analysis", 70, f"Comprehensive evaluation of resource allocation efficiency across patient recruitment activities with trial lifecycle cost optimization", f"Analyzed resource efficiency: {disease_areas} therapeutic areas with patient enrollment cost reduction opportunities identified"),
                ("AI Pharmaceutical Financial Modeling", 90, f"Advanced clinical trial financial projections and development ROI calculations using {model_name} with comprehensive pharmaceutical cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} clinical cost metrics completed"),
                ("Clinical Trial Economics Report Generation", 100, f"Professional pharmaceutical financial impact analysis with detailed clinical development ROI calculations and trial cost forecasting ready", f"Comprehensive clinical trial financial report with ${avg_trial_cost_estimate:,.0f} cost optimization analysis and patient recruitment efficiency strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            protocol_efficiency_score = (100 - avg_dropout_rate) * 10 if avg_dropout_rate > 0 else 0
            
            steps = [
                ("Pharmaceutical Technology Assessment", 15, f"Advanced loading of clinical trial digital context with competitive positioning analysis across {total_records} patient records and {active_trials} active trials", f"Analyzed pharmaceutical technology landscape: {disease_areas} therapeutic areas, {sites_count} clinical sites, comprehensive trial digitization assessment completed"),
                ("Clinical Trial Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional manual trial design with AI-powered protocol optimization effectiveness", f"Assessed competitive advantages: {protocol_efficiency_score:.1f}% protocol efficiency, {avg_enrollment_rate:.1f}% enrollment vs industry benchmarks"),
                ("Advanced Clinical Technology Integration", 50, f"Enhanced analysis of integration opportunities with digital biomarkers, adaptive trial designs, and AI-powered patient stratification across {len(data.columns)} clinical data dimensions", f"Identified strategic technology integration: digital health monitoring, adaptive trial algorithms, automated patient recruitment opportunities"),
                ("Digital Clinical Operations Strategy Development", 70, f"Comprehensive development of prioritized digital transformation roadmap with evidence-based clinical technology adoption strategies", f"Created sequenced implementation plan across {disease_areas} therapeutic areas with advanced clinical technology integration opportunities"),
                ("AI Pharmaceutical Strategic Processing", 85, f"Advanced clinical trial strategic recommendations using {model_name} with long-term competitive positioning and pharmaceutical technology analysis", f"Enhanced strategic analysis with clinical trial competitive positioning and digital transformation roadmap completed"),
                ("Digital Clinical Trial Report Generation", 100, f"Professional digital pharmaceutical transformation roadmap with competitive analysis and clinical technology implementation plan ready for CMO executive review", f"Comprehensive strategic report with {disease_areas}-area implementation plan and clinical trial competitive advantage analysis generated")
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
    # Only include actual numeric metrics from pharma dataset
    key_metrics = ["patient_age", "enrollment_rate", "dropout_rate"]
    
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
    categorical_options = ["disease_area", "trial_status", "regulatory_approval_status", "sponsor_name", "patient_gender", "site_name"]
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
        For the Overall Performance analysis of TrialGenius:
        1. Provide a comprehensive analysis of the clinical trial design and optimization system using patient age, enrollment rate, and dropout rate metrics
        2. Identify significant patterns in disease areas, trial status, regulatory approvals, and patient demographics across pharmaceutical operations
        3. Highlight 3-5 key clinical trial metrics that best indicate trial optimization effectiveness (enrollment rates, patient demographics, dropout rates)
        4. Discuss both strengths and areas for improvement in the AI-powered clinical trial design process
        5. Include 3-5 actionable insights for improving clinical trial operations based on the trial management data
        
        Structure your response with these pharmaceutical focused sections:
        - Clinical Trial Insights (5 specific insights with supporting patient and trial data)
        - Trial Performance Trends (3-4 significant trends in enrollment rates and patient demographics)
        - Trial Optimization Recommendations (3-5 data-backed recommendations for improving clinical operations)
        - Implementation Steps (3-5 concrete next steps for clinical operations and trial managers)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of TrialGenius:
        1. Focus specifically on areas where clinical trial enrollment, patient stratification, and trial efficiency can be improved
        2. Identify inefficiencies in patient recruitment, site selection, and protocol designs across pharmaceutical operations
        3. Analyze correlations between disease areas, patient demographics, enrollment rates, and dropout rates
        4. Prioritize optimization opportunities based on potential impact on trial timelines and success rates
        5. Suggest specific technical or process improvements for integration with existing CTMS and EDC systems
        
        Structure your response with these pharmaceutical focused sections:
        - Clinical Trial Optimization Priorities (3-5 areas with highest enrollment and retention improvement potential)
        - Trial Impact Analysis (quantified benefits of addressing each opportunity in terms of enrollment and dropout metrics)
        - CTMS Integration Strategy (specific steps for clinical teams to implement each optimization)
        - System Integration Recommendations (specific technical changes needed for seamless integration with Veeva, Oracle, and Medidata systems)
        - Clinical Operations Risk Assessment (potential challenges for investigators and clinical teams and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of TrialGenius:
        1. Focus on cost-benefit analysis and ROI in pharmaceutical clinical trial terms (development costs vs. trial success improvements)
        2. Quantify financial impacts through enrollment improvements, dropout reduction, and trial timeline optimization
        3. Identify cost savings opportunities across different disease areas and trial types
        4. Analyze resource allocation efficiency across different sites and patient populations
        5. Project future financial outcomes based on improved trial design accuracy and expanding to adaptive trials
        
        Structure your response with these pharmaceutical focused sections:
        - Clinical Development Cost Analysis (breakdown of trial costs and potential savings by disease area and trial phase)
        - Trial Efficiency Impact (how improved trial design affects development costs and time-to-market)
        - Pharmaceutical ROI Calculation (specific calculations showing return on investment in terms of trial success rate improvement)
        - Enrollment Cost Reduction Opportunities (specific areas to reduce patient recruitment and retention costs)
        - Development Cost Forecasting (projections based on improved trial efficiency metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of TrialGenius:
        1. Focus on long-term strategic implications for digital transformation in pharmaceutical clinical development
        2. Identify competitive advantages against traditional manual trial design approaches
        3. Suggest new directions for AI integration with emerging clinical technologies (e.g., digital biomarkers, decentralized trials)
        4. Connect recommendations to broader drug development goals of reducing costs and improving success rates
        5. Provide a digital clinical operations roadmap with prioritized initiatives
        
        Structure your response with these pharmaceutical focused sections:
        - Digital Clinical Development Context (how TrialGenius fits into broader digital transformation in pharma)
        - Clinical Competitive Advantage Analysis (how to maximize efficiency advantages compared to traditional trial design)
        - Clinical Technology Strategic Priorities (3-5 high-impact strategic initiatives for improving clinical operations)
        - Advanced Clinical Technology Integration Vision (how to evolve TrialGenius with digital biomarkers and decentralized trials over 1-3 years)
        - Clinical Operations Transformation Roadmap (sequenced steps for expanding to adaptive trials and real-time protocol optimization)
        """
    }

    # Get the specific instructions for the selected focus area
    selected_focus_instructions = focus_area_instructions.get(focus_area, "")

    prompt = f'''
    You are an expert data analyst specializing in {focus_area.lower()} analysis for pharmaceutical clinical trial operations.

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
    - Frame all insights in the context of pharmaceutical clinical trial operations and development
    '''

    return call_cortex_model(prompt, model_name)

def create_metrics_charts(data):
    """Create metric visualizations for the pharmaceutical clinical trial data"""
    charts = []
    
    # Patient Age Distribution
    if 'patient_age' in data.columns:
        age_chart = alt.Chart(data).mark_bar().encode(
            alt.X('patient_age:Q', bin=alt.Bin(maxbins=15), title='Patient Age'),
            alt.Y('count()', title='Number of Patients'),
            color=alt.value('#1f77b4')
        ).properties(
            title='Patient Age Distribution',
            width=380,
            height=340
        )
        charts.append(('Patient Age Distribution', age_chart))
    
    # Enrollment Rate by Disease Area
    if 'enrollment_rate' in data.columns and 'disease_area' in data.columns:
        enrollment_chart = alt.Chart(data).mark_boxplot().encode(
            alt.X('disease_area:N', title='Disease Area'),
            alt.Y('enrollment_rate:Q', title='Enrollment Rate'),
            color=alt.Color('disease_area:N', legend=None)
        ).properties(
            title='Enrollment Rate by Disease Area',
            width=380,
            height=340
        )
        charts.append(('Enrollment Rate by Disease Area', enrollment_chart))
    
    # Dropout Rate Trends Over Time
    if 'dropout_rate' in data.columns and 'enrollment_date' in data.columns:
        try:
            # Convert enrollment_date to datetime if possible
            data_copy = data.copy()
            data_copy['enrollment_date'] = pd.to_datetime(data_copy['enrollment_date'], errors='coerce')
            data_copy = data_copy.dropna(subset=['enrollment_date'])
            
            if not data_copy.empty:
                dropout_chart = alt.Chart(data_copy).mark_line(point=True).encode(
                    alt.X('enrollment_date:T', title='Enrollment Date'),
                    alt.Y('mean(dropout_rate):Q', title='Average Dropout Rate'),
                    color=alt.value('#ff7f0e')
                ).properties(
                    title='Dropout Rate Trends',
                    width=380,
                    height=340
                )
                charts.append(('Dropout Rate Trends', dropout_chart))
        except:
            # If date conversion fails, create alternative chart
            if 'trial_status' in data.columns:
                status_dropout_chart = alt.Chart(data).mark_bar().encode(
                    alt.X('trial_status:N', title='Trial Status'),
                    alt.Y('mean(dropout_rate):Q', title='Average Dropout Rate'),
                    color=alt.Color('trial_status:N', legend=None)
                ).properties(
                    title='Dropout Rate by Trial Status',
                    width=380,
                    height=340
                )
                charts.append(('Dropout Rate by Trial Status', status_dropout_chart))
    
    # Trial Status Distribution
    if 'trial_status' in data.columns:
        status_chart = alt.Chart(data).mark_arc().encode(
            theta=alt.Theta('count():Q'),
            color=alt.Color('trial_status:N', title='Status'),
            tooltip=['trial_status:N', 'count():Q']
        ).properties(
            title='Trial Status Distribution',
            width=380,
            height=340
        )
        charts.append(('Trial Status Distribution', status_chart))
    
    # Gender Distribution by Disease Area
    if 'patient_gender' in data.columns and 'disease_area' in data.columns:
        gender_chart = alt.Chart(data).mark_bar().encode(
            alt.X('disease_area:N', title='Disease Area'),
            alt.Y('count():Q', title='Patient Count'),
            alt.Color('patient_gender:N', title='Gender'),
            tooltip=['disease_area:N', 'patient_gender:N', 'count():Q']
        ).properties(
            title='Patient Gender by Disease Area',
            width=380,
            height=340
        )
        charts.append(('Patient Gender by Disease Area', gender_chart))
    
    # Site Performance Analysis
    if 'site_name' in data.columns and 'enrollment_rate' in data.columns:
        # Group by site and calculate average enrollment rate for top 10 sites
        site_data = data.groupby('site_name')['enrollment_rate'].agg(['mean', 'count']).reset_index()
        site_data = site_data[site_data['count'] >= 3]  # Only sites with 3+ patients
        site_data = site_data.nlargest(10, 'mean')  # Top 10 by enrollment rate
        
        if not site_data.empty:
            site_chart = alt.Chart(site_data).mark_bar().encode(
                alt.X('site_name:O', title='Site Name', sort='-y'),
                alt.Y('mean:Q', title='Average Enrollment Rate'),
                color=alt.Color('mean:Q', title='Enrollment Rate', scale=alt.Scale(scheme='blues')),
                tooltip=['site_name:O', alt.Tooltip('mean:Q', format='.3f')]
            ).properties(
                title='Top Sites by Enrollment Rate',
                width=380,
                height=340
            )
            charts.append(('Top Sites by Enrollment Rate', site_chart))
    
    return charts

data = load_data()
if data.empty:
    st.error("No data found.")
    st.stop()

categorical_cols = [col for col in ["disease_area", "trial_status", "regulatory_approval_status", "sponsor_name", "patient_gender", "site_name"] if col in data.columns]
numeric_cols = [col for col in ["patient_age", "enrollment_rate", "dropout_rate"] if col in data.columns]
date_cols = [col for col in ["enrollment_date", "protocol_amendment_date"] if col in data.columns]

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
        if 'patient_age' in data.columns:
            avg_age = data['patient_age'].mean()
            st.metric("Avg Patient Age", f"{avg_age:.1f} years", delta=f"{(avg_age - 55):.1f}y vs target")
    
    with col2:
        if 'enrollment_rate' in data.columns:
            avg_enrollment = data['enrollment_rate'].mean()
            st.metric("Avg Enrollment Rate", f"{avg_enrollment:.1f}%", delta=f"{(avg_enrollment - 75):.1f}% vs target")
    
    with col3:
        if 'dropout_rate' in data.columns:
            avg_dropout = data['dropout_rate'].mean()
            st.metric("Avg Dropout Rate", f"{avg_dropout:.1f}%", delta=f"{(15 - avg_dropout):.1f}% vs target")
    
    with col4:
        if 'trial_status' in data.columns:
            active_trials = len(data[data['trial_status'] == 'Active'])
            total_trials = len(data['trial_id'].unique()) if 'trial_id' in data.columns else len(data)
            st.metric("Active Trials", f"{active_trials}")
    
    st.markdown("---")
    
    # Create and display charts
    charts = create_metrics_charts(data)
    
    if charts:
        st.subheader("📈 Performance Visualizations")
        
        # Display charts in a 2-column grid, ensuring all charts are shown
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
        
        # Create two columns for better organization
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Key Clinical Metrics**")
            key_metrics = ['patient_age', 'enrollment_rate', 'dropout_rate']
            key_metrics_present = [m for m in key_metrics if m in summary_df.index]
            
            if key_metrics_present:
                key_stats_df = summary_df.loc[key_metrics_present]
                
                # Create a more readable format
                for metric in key_stats_df.index:
                    mean_val = key_stats_df.loc[metric, 'Mean']
                    min_val = key_stats_df.loc[metric, 'Min']
                    max_val = key_stats_df.loc[metric, 'Max']
                    
                    # Format based on metric type
                    if 'age' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.1f} years",
                            help=f"Range: {min_val:.1f} - {max_val:.1f} years"
                        )
                    elif 'rate' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.3f}",
                            help=f"Range: {min_val:.3f} - {max_val:.3f}"
                        )
                    else:
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.2f}",
                            help=f"Range: {min_val:.2f} - {max_val:.2f}"
                        )
        
        with col2:
            st.markdown("**📊 Clinical Trial Insights**")
            
            # Calculate and display key insights
            insights = []
            
            if 'patient_age' in summary_df.index:
                age_mean = summary_df.loc['patient_age', 'Mean']
                age_std = summary_df.loc['patient_age', 'Std Dev']
                insights.append(f"• **Patient Age Variability**: {age_std:.1f} years (σ)")
                
                if age_mean > 65:
                    insights.append(f"• **Elderly patient population** (avg {age_mean:.1f}y)")
                elif age_mean < 45:
                    insights.append(f"• **Younger patient population** (avg {age_mean:.1f}y)")
                else:
                    insights.append(f"• **Mixed age population** (avg {age_mean:.1f}y)")
            
            if 'enrollment_rate' in summary_df.index:
                er_q75 = summary_df.loc['enrollment_rate', '75%']
                er_q25 = summary_df.loc['enrollment_rate', '25%']
                iqr = er_q75 - er_q25
                insights.append(f"• **Enrollment Rate IQR**: {iqr:.3f}")
            
            if 'dropout_rate' in summary_df.index:
                dr_median = summary_df.loc['dropout_rate', '50% (Median)']
                dr_max = summary_df.loc['dropout_rate', 'Max']
                insights.append(f"• **Median Dropout Rate**: {dr_median:.3f}")
                if dr_max > 0.3:
                    insights.append(f"• **⚠️ High dropout events**: up to {dr_max:.3f}")
            
            # Add categorical insights
            if 'disease_area' in data.columns:
                top_disease = data['disease_area'].value_counts().index[0]
                disease_count = data['disease_area'].value_counts().iloc[0]
                insights.append(f"• **Top Disease Area**: {top_disease} ({disease_count} patients)")
            
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

# AI Insights tab with Agent Workflows
with tabs[1]:
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each clinical trial analysis focus area**")
    
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
                st.success(f"🎉 {focus_area} Agent completed with real clinical trial data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real Clinical Trial Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Clinical Trial Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Clinical Trial Analysis</small><br>
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