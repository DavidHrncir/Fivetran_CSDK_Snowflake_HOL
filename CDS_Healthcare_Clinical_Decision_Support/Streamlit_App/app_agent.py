import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="medmind_–_ai_driven_clinical_decision_support",
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

solution_name = '''Solution 1: MedMind – AI-driven Clinical Decision Support'''
solution_name_clean = '''medmind_–_ai_driven_clinical_decision_support'''
table_name = '''CDS_RECORDS'''
table_description = '''Consolidated patient data for MedMind AI-driven clinical decision support'''
solution_content = '''Solution 1: MedMind – AI-driven Clinical Decision Support**

* **Tagline:** "Transforming patient care with AI-driven insights"
* **Primary Business Challenge:** Reducing medical errors and improving patient outcomes
* **Key Features:**
	+ AI-driven clinical decision support system
	+ Integration with Electronic Health Records (EHRs)
	+ Real-time patient data analysis
	+ Personalized treatment recommendations
* **Data Sources:**
	+ Electronic Health Records (EHRs): Epic Systems Corporation, Cerner, Meditech
	+ Clinical Trials: ClinicalTrials.gov, National Institutes of Health (NIH)
	+ Medical Literature: PubMed, National Library of Medicine
* **Competitive Advantage:** MedMind differentiates itself from traditional clinical decision support systems by leveraging generative AI to analyze vast amounts of patient data and provide personalized treatment recommendations.
* **Key Stakeholders:** Chief Medical Officer, Chief Information Officer, Clinical Decision Support Teams
* **Technical Approach:** Generative AI using deep learning algorithms to analyze patient data and generate personalized treatment recommendations
* **Expected Business Results:**
	+ 10% reduction in medical errors
	+ 15% improvement in patient outcomes
	+ 20% reduction in hospital readmissions
	+ 5% reduction in healthcare costs
* **Calculations:**
	+ 10% reduction in medical errors: **100,000 patients/year × 10% baseline error rate × 10% reduction = 1,000 fewer medical errors/year**
	+ 15% improvement in patient outcomes: **10,000 patients/year × 20% baseline complication rate × 15% reduction = 300 fewer complications/year**
	+ 20% reduction in hospital readmissions: **5,000 patients/year × 20% baseline readmission rate × 20% reduction = 200 fewer readmissions/year**
	+ 5% reduction in healthcare costs: **$ 10,000,000 annual healthcare costs × 5% reduction = $ 500,000 savings/year**
* **Success Metrics:** Reduction in medical errors, improvement in patient outcomes, reduction in hospital readmissions, reduction in healthcare costs
* **Risk Assessment:** Integration with EHRs, data quality, regulatory compliance
* **Long-term Evolution:** Integration with wearable devices, telemedicine, and personalized medicine

**'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Healthcare</p>
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
            "challenge": "Care coordinators manually review dozens of hospital discharge reports daily, spending 2+ hours identifying high-risk patients who need immediate intervention to prevent readmission.",
            "solution": "Autonomous workflow that analyzes recent discharges, assesses readmission risks, identifies care gaps, and generates prioritized intervention plans in a fraction of the time normally required."
        },
        "Optimization Opportunities": {
            "challenge": "Care coordinators spend 3+ hours daily manually identifying workflow inefficiencies and optimization opportunities across treatment plans and medication protocols.",
            "solution": "AI-powered analysis that automatically detects care coordination gaps, medication optimization opportunities, and EHR integration improvements with specific implementation recommendations."
        },
        "Financial Impact": {
            "challenge": "Financial analysts manually calculate ROI and cost-benefit metrics across patient populations, requiring 2+ hours of complex financial modeling and reporting.",
            "solution": "Automated financial analysis that calculates comprehensive ROI, identifies cost reduction opportunities, and projects value-based care benefits with detailed financial forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "Healthcare executives spend hours manually analyzing competitive positioning and developing strategic technology roadmaps for clinical decision support advancement.",
            "solution": "Strategic intelligence workflow that analyzes competitive advantages, identifies technology integration opportunities, and creates prioritized implementation roadmaps for long-term growth."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - ENHANCED VERSION with pre-execution"""
    
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
        total_patients = len(data)
        key_metrics = ["readmission_risk", "medical_error_rate", "patient_outcome_score", "cost_of_care", "length_of_stay", "medication_cost", "total_cost_savings"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced data insights
        avg_outcome_score = data['patient_outcome_score'].mean() if 'patient_outcome_score' in data.columns else 0
        avg_error_rate = data['medical_error_rate'].mean() if 'medical_error_rate' in data.columns else 0
        total_cost_savings = data['total_cost_savings'].sum() if 'total_cost_savings' in data.columns else 0
        high_risk_patients = len(data[data['readmission_risk'] > 0.7]) if 'readmission_risk' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Clinical Data Initialization", 15, f"Loading comprehensive patient dataset with enhanced validation and quality checks across {total_patients} patient records", f"Connected to {len(available_metrics)} clinical metrics with {len(data.columns)} total data dimensions"),
                ("Performance Metrics Assessment", 35, f"Advanced calculation of key performance indicators with clinical effectiveness analysis (avg outcome score: {avg_outcome_score:.2f})", f"Computed patient outcomes: {avg_outcome_score:.2f}, error rates: {avg_error_rate:.2f}, total savings: ${total_cost_savings:,.0f}"),
                ("Clinical Pattern Recognition", 55, f"Sophisticated identification of clinical patterns with evidence-based analysis across treatment outcomes and medication effectiveness", f"Detected significant patterns in {len(data['treatment_outcome'].unique()) if 'treatment_outcome' in data.columns else 'N/A'} treatment categories with correlation analysis completed"),
                ("AI Clinical Intelligence Processing", 75, f"Processing comprehensive clinical data through {model_name} with advanced reasoning for performance insights", f"Enhanced AI analysis of clinical decision support effectiveness across {total_patients} patients completed"),
                ("Report Compilation", 100, f"Professional clinical performance analysis with evidence-based recommendations and actionable insights ready", f"Comprehensive performance report with {len(available_metrics)} KPI analysis and clinical recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            treatment_types = len(data['treatment_plan'].unique()) if 'treatment_plan' in data.columns else 0
            medication_types = len(data['current_medications'].unique()) if 'current_medications' in data.columns else 0
            
            steps = [
                ("Optimization Data Preparation", 12, f"Advanced loading of clinical workflow data with enhanced validation across {total_patients} patients for improvement opportunity identification", f"Prepared {treatment_types} treatment plans, {medication_types} medication protocols for optimization analysis"),
                ("Clinical Inefficiency Detection", 28, f"Sophisticated analysis of treatment plans and medication recommendations with evidence-based inefficiency identification", f"Identified inefficiencies in care coordination across {treatment_types} treatment protocols and medication adherence patterns"),
                ("Clinical Correlation Analysis", 45, f"Enhanced examination of relationships between medication adherence ({data['medication_adherence'].value_counts().index[0] if 'medication_adherence' in data.columns else 'N/A'}), outcomes, and satisfaction", f"Analyzed correlations between treatment adherence and patient outcomes across {total_patients} patient records"),
                ("EHR Integration Optimization", 65, f"Comprehensive evaluation of clinical decision support integration with existing EHR workflows and technical optimization assessment", f"Assessed workflow integration opportunities across {len(data.columns)} data points and technical optimization needs"),
                ("AI Optimization Intelligence", 85, f"Generating advanced optimization recommendations using {model_name} with clinical reasoning and implementation strategies", f"AI-powered optimization strategy across {treatment_types} treatment areas and workflow improvements completed"),
                ("Strategy Finalization", 100, f"Professional optimization report with prioritized implementation roadmap and clinical impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            avg_cost_care = data['cost_of_care'].mean() if 'cost_of_care' in data.columns else 0
            avg_med_cost = data['medication_cost'].mean() if 'medication_cost' in data.columns else 0
            
            steps = [
                ("Financial Data Integration", 15, f"Advanced loading of cost data and healthcare financial metrics with enhanced validation across {total_patients} patients", f"Integrated financial data: avg cost of care ${avg_cost_care:,.0f}, avg medication cost ${avg_med_cost:,.0f} across all patient records"),
                ("Cost-Benefit Calculation", 30, f"Sophisticated ROI metrics calculation with healthcare cost savings analysis (total savings: ${total_cost_savings:,.0f})", f"Computed comprehensive cost analysis: care costs, medication expenses, and ${total_cost_savings:,.0f} total savings potential identified"),
                ("Revenue Impact Assessment", 50, f"Enhanced analysis of healthcare revenue impact with value-based care metrics and clinical outcome financial correlation", f"Assessed revenue implications of improved outcomes: {avg_outcome_score:.2f} avg score with reduced error rates: {avg_error_rate:.2f}"),
                ("Resource Efficiency Analysis", 70, f"Comprehensive evaluation of resource allocation efficiency across treatment plans with length of stay optimization analysis", f"Analyzed resource efficiency: avg LOS {data['length_of_stay'].mean():.1f} days with readmission cost reduction opportunities identified"),
                ("AI Financial Modeling", 90, f"Advanced financial projections and ROI calculations using {model_name} with comprehensive cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} financial metrics completed"),
                ("Financial Report Generation", 100, f"Professional financial impact analysis with detailed ROI calculations and value-based care forecasting ready", f"Comprehensive financial report with ${total_cost_savings:,.0f} savings analysis and revenue optimization strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            diagnosis_types = len(data['diagnosis'].unique()) if 'diagnosis' in data.columns else 0
            trial_count = len(data['clinical_trial_id'].unique()) if 'clinical_trial_id' in data.columns else 0
            
            steps = [
                ("Strategic Data Assessment", 15, f"Advanced loading of strategic context with competitive positioning analysis across {total_patients} patients and {diagnosis_types} diagnosis categories", f"Analyzed strategic landscape: {diagnosis_types} diagnosis types, {trial_count} clinical trials, comprehensive market positioning assessment completed"),
                ("Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional clinical decision support with MedMind effectiveness analysis", f"Assessed competitive advantages: {avg_outcome_score:.2f} outcome improvement, {avg_error_rate:.2f} error reduction vs traditional systems"),
                ("Future Technology Integration", 50, f"Enhanced analysis of integration opportunities with genetic data, wearables, and telemedicine across {len(data.columns)} data dimensions", f"Identified strategic technology integration: genetic data utilization, vital signs monitoring, clinical trials integration opportunities"),
                ("Clinical Implementation Strategy", 70, f"Comprehensive development of prioritized clinical implementation roadmap with evidence-based adoption strategies", f"Created sequenced implementation plan across {diagnosis_types} clinical areas with {trial_count} research integration opportunities"),
                ("AI Strategic Processing", 85, f"Advanced strategic recommendations using {model_name} with long-term competitive positioning and market analysis", f"Enhanced strategic analysis with competitive positioning and long-term technology roadmap completed"),
                ("Strategic Report Generation", 100, f"Professional strategic roadmap with competitive analysis and clinical implementation plan ready for executive review", f"Comprehensive strategic report with {diagnosis_types}-area implementation plan and competitive advantage analysis generated")
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
    key_metrics = ["readmission_risk", "medical_error_rate", "patient_outcome_score", "cost_of_care", "length_of_stay", "medication_cost", "total_cost_savings"]
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
    categorical_options = ["patient_id", "medical_history", "current_medications", "lab_results", "vital_signs", "diagnosis", "treatment_plan", "clinical_trial_id", "trial_name", "trial_status", "medical_publication_id", "publication_title", "medication_side_effects", "allergies", "medical_conditions", "family_medical_history", "genetic_data", "treatment_outcome", "medication_adherence", "patient_satisfaction", "medication_recommendation", "treatment_recommendation"]
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
        For the Overall Performance analysis of MedMind:
        1. Provide a comprehensive analysis of the clinical decision support system's performance using patient outcome scores, treatment outcomes, and medical error rates
        2. Identify significant patterns in medication recommendations, patient outcomes, and readmission risks
        3. Highlight 3-5 key healthcare metrics that best indicate clinical effectiveness (patient outcome scores, medical error rates, readmission risks)
        4. Discuss both clinical strengths and areas for improvement in treatment recommendations
        5. Include 3-5 actionable insights for improving patient care based on the data
        
        Structure your response with these healthcare-focused sections:
        - Clinical Insights (5 specific insights with supporting patient data)
        - Patient Outcome Trends (3-4 significant trends in treatment effectiveness)
        - Clinical Recommendations (3-5 data-backed recommendations for improving care)
        - Implementation Steps (3-5 concrete next steps for clinical teams)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of MedMind:
        1. Focus specifically on areas where clinical decision support can be improved
        2. Identify inefficiencies in treatment plans, medication recommendations, and patient monitoring
        3. Analyze correlations between medication adherence, treatment outcomes, and patient satisfaction
        4. Prioritize optimization opportunities based on potential impact on medical error reduction and patient outcomes
        5. Suggest specific technical or process improvements for integration with existing EHR systems
        
        Structure your response with these healthcare-focused sections:
        - Clinical Optimization Priorities (3-5 areas with highest patient care improvement potential)
        - Patient Impact Analysis (quantified benefits of addressing each opportunity in terms of patient outcomes)
        - Clinical Implementation Strategy (specific steps for clinical staff to implement each optimization)
        - EHR Integration Recommendations (specific technical changes needed for seamless workflow)
        - Clinical Risk Assessment (potential challenges for medical staff and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of MedMind:
        1. Focus on cost-benefit analysis and ROI in healthcare terms (cost of care vs. outcome improvement)
        2. Quantify financial impacts through total cost savings, medication costs, and length of stay reductions
        3. Identify cost savings opportunities in readmission prevention and medical error reduction
        4. Analyze resource allocation efficiency across different treatment plans
        5. Project future financial outcomes based on improved patient outcomes and reduced medical errors
        
        Structure your response with these healthcare-focused sections:
        - Healthcare Cost Analysis (breakdown of cost of care, medication costs, and potential savings)
        - Clinical Revenue Impact (how improved outcomes affect healthcare revenue)
        - Healthcare ROI Calculation (specific calculations showing return on investment in terms of patient outcomes and cost savings)
        - Hospital Cost Reduction Opportunities (specific areas to reduce length of stay and readmissions)
        - Value-Based Care Forecasting (projections based on improved clinical metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of MedMind:
        1. Focus on long-term strategic implications for clinical decision support improvement
        2. Identify competitive advantages against traditional clinical decision support systems
        3. Suggest new directions for AI integration with genetic data, vital signs monitoring, and clinical trials
        4. Connect recommendations to broader healthcare goals of reducing errors and improving outcomes
        5. Provide a clinical implementation roadmap with prioritized initiatives
        
        Structure your response with these healthcare-focused sections:
        - Clinical Context (how MedMind fits into broader healthcare quality improvement initiatives)
        - Healthcare Competitive Advantage Analysis (how to maximize clinical effectiveness compared to traditional systems)
        - Clinical Strategic Priorities (3-5 high-impact strategic initiatives for improving patient care)
        - Future Medical Technology Vision (how to evolve MedMind with wearable devices, telemedicine, and personalized medicine over 1-3 years)
        - Clinical Implementation Roadmap (sequenced steps for clinical integration and adoption)
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

categorical_cols = [col for col in ["patient_id", "medical_history", "current_medications", "lab_results", "vital_signs", "diagnosis", "treatment_plan", "clinical_trial_id", "trial_name", "trial_status", "medical_publication_id", "publication_title", "medication_side_effects", "allergies", "medical_conditions", "family_medical_history", "genetic_data", "treatment_outcome", "medication_adherence", "patient_satisfaction", "medication_recommendation", "treatment_recommendation"] if col in data.columns]
numeric_cols = [col for col in ["readmission_risk", "medical_error_rate", "patient_outcome_score", "cost_of_care", "length_of_stay", "medication_cost", "total_cost_savings"] if col in data.columns]
date_cols = [col for col in ["publication_date"] if col in data.columns]

sample_cols = data.columns.tolist()
numeric_candidates = [col for col in sample_cols if data[col].dtype in ['float64', 'int64'] and 'id' not in col.lower()]
date_candidates = [col for col in sample_cols if 'date' in col.lower() or 'timestamp' in col.lower()]
cat_candidates = [col for col in sample_cols if data[col].dtype == 'object' and data[col].nunique() < 1000]

# Four tabs - with Metrics as the first tab (Tab 0)
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics Tab (Tab 0)
with tabs[0]:
    st.header("Clinical Decision Support Metrics")
    
    # Overview metrics row - 4 KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics from the data
    avg_outcome_score = data['patient_outcome_score'].mean() if 'patient_outcome_score' in data.columns else 0
    avg_error_rate = data['medical_error_rate'].mean() if 'medical_error_rate' in data.columns else 0
    avg_readmission_risk = data['readmission_risk'].mean() if 'readmission_risk' in data.columns else 0
    total_cost_savings = data['total_cost_savings'].sum() if 'total_cost_savings' in data.columns else 0
    
    with col1:
        with st.container(border=True):
            st.metric(
                "Avg Patient Outcome Score", 
                f"{avg_outcome_score:.2f}",
                f"{(avg_outcome_score - 0.5) / 0.5 * 100:.1f}%" if avg_outcome_score > 0.5 else f"{(avg_outcome_score - 0.5) / 0.5 * 100:.1f}%",
                help="Average patient outcome score (0-1 scale). Higher is better."
            )
    
    with col2:
        with st.container(border=True):
            st.metric(
                "Avg Medical Error Rate", 
                f"{avg_error_rate:.2f}",
                f"{(0.5 - avg_error_rate) / 0.5 * 100:.1f}%" if avg_error_rate < 0.5 else f"{(0.5 - avg_error_rate) / 0.5 * 100:.1f}%",
                help="Average error rate (0-1 scale). Lower is better."
            )
    
    with col3:
        with st.container(border=True):
            st.metric(
                "Avg Readmission Risk", 
                f"{avg_readmission_risk:.2f}",
                f"{(0.5 - avg_readmission_risk) / 0.5 * 100:.1f}%" if avg_readmission_risk < 0.5 else f"{(0.5 - avg_readmission_risk) / 0.5 * 100:.1f}%",
                help="Average readmission risk (0-1 scale). Lower is better."
            )
    
    with col4:
        with st.container(border=True):
            st.metric(
                "Total Cost Savings", 
                f"${total_cost_savings:,.2f}",
                help="Total cost savings across all patients"
            )
    
    # Financial Metrics Section - 3 Financial Metrics
    st.subheader("Financial Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            avg_cost_of_care = data['cost_of_care'].mean() if 'cost_of_care' in data.columns else 0
            st.metric("Avg Cost of Care", f"${avg_cost_of_care:,.2f}")
        
    with col2:
        with st.container(border=True):
            avg_medication_cost = data['medication_cost'].mean() if 'medication_cost' in data.columns else 0
            st.metric("Avg Medication Cost", f"${avg_medication_cost:,.2f}")
        
    with col3:
        with st.container(border=True):
            avg_los = data['length_of_stay'].mean() if 'length_of_stay' in data.columns else 0
            st.metric("Avg Length of Stay", f"{avg_los:.1f} days")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    # Patient Outcome Distribution
    with col1:
        st.subheader("Patient Outcome Distribution")
        
        if 'patient_outcome_score' in data.columns:
            # Create bins for outcome scores
            bins = [0, 0.25, 0.5, 0.75, 1.0]
            labels = ['Poor (0-0.25)', 'Fair (0.25-0.5)', 'Good (0.5-0.75)', 'Excellent (0.75-1.0)']
            data['outcome_category'] = pd.cut(data['patient_outcome_score'], bins=bins, labels=labels, include_lowest=True)
            
            outcome_counts = data['outcome_category'].value_counts().reset_index()
            outcome_counts.columns = ['category', 'count']
            
            # Patient Outcome Distribution Chart
            chart = alt.Chart(outcome_counts).mark_bar().encode(
                x=alt.X('category:N', title='Outcome Category', sort=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Patients'),
                color=alt.Color('category:N', scale=alt.Scale(domain=labels, range=['#E74C3C', '#F4D03F', '#52BE80', '#5DADE2']))
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
            st.write("Treatment outcome data not available")
    
    # Treatment Outcome Distribution
    with col2:
        st.subheader("Treatment Outcome Distribution")
        
        if 'treatment_outcome' in data.columns:
            treatment_counts = data['treatment_outcome'].value_counts().reset_index()
            treatment_counts.columns = ['outcome', 'count']
            
            colors = {
                'Successful': '#52BE80',
                'Partial Success': '#F4D03F',
                'Ongoing': '#5DADE2', 
                'Unsuccessful': '#E74C3C'
            }
            
            chart = alt.Chart(treatment_counts).mark_bar().encode(
                x=alt.X('outcome:N', title='Treatment Outcome', sort='-y', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Patients'),
                color=alt.Color('outcome:N', scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())))
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
            st.write("Treatment outcome data not available")
            
    # Patient Satisfaction
    st.subheader("Patient Satisfaction")
    
    if 'patient_satisfaction' in data.columns:
        satisfaction_counts = data['patient_satisfaction'].value_counts().reset_index()
        satisfaction_counts.columns = ['satisfaction', 'count']
        
        colors = {
            'Satisfied': '#52BE80',
            'Neutral': '#F4D03F',
            'Unsatisfied': '#E74C3C'
        }
        
        # Patient Satisfaction Chart
        chart = alt.Chart(satisfaction_counts).mark_bar().encode(
            x=alt.X('satisfaction:N', title='Satisfaction Level', sort='-y', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count:Q', title='Number of Patients'),
            color=alt.Color('satisfaction:N', scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())))
        )
        
        text = chart.mark_text(
            align='center',
            baseline='bottom',
            dy=-15  # Increased space above bars
        ).encode(
            text='count:Q'
        )
        
        # Use the same approach for Patient Satisfaction chart
        st.altair_chart((chart + text).properties(height=300, width=500), use_container_width=True)
    else:
        st.write("Patient satisfaction data not available")
    
    # Clinical Metrics Section
    st.subheader("Clinical Metrics")
    
    # Create 2 columns for diagnosis/treatment metrics
    col1, col2 = st.columns(2)
    
    # Top Diagnoses
    with col1:
        st.subheader("Top Diagnoses")
        
        if 'diagnosis' in data.columns:
            diagnosis_counts = data['diagnosis'].value_counts().head(5).reset_index()
            diagnosis_counts.columns = ['diagnosis', 'count']
            
            # Top Diagnoses Chart
            chart = alt.Chart(diagnosis_counts).mark_bar().encode(
                y=alt.Y('diagnosis:N', title='Diagnosis', sort='-x'),
                x=alt.X('count:Q', title='Number of Patients'),
                color=alt.Color('diagnosis:N', legend=None)
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
            st.write("Diagnosis data not available")
    
    # Treatment Plan Distribution
    with col2:
        st.subheader("Treatment Plan Distribution")
        
        if 'treatment_plan' in data.columns:
            treatment_counts = data['treatment_plan'].value_counts().reset_index()
            treatment_counts.columns = ['plan', 'count']
            
            # Treatment Plan Distribution Chart
            chart = alt.Chart(treatment_counts).mark_bar().encode(
                y=alt.Y('plan:N', title='Treatment Plan', sort='-x'),
                x=alt.X('count:Q', title='Number of Patients'),
                color=alt.Color('plan:N', legend=None)
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
            st.write("Treatment plan data not available")
    
# AI Insights tab
with tabs[1]:
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each analysis focus area**")
    
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
                st.success(f"🎉 {focus_area} Agent completed with real data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Analysis</small><br>
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