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
The solution leverages large language models fine-tuned on clinical trial protocols and outcomes to generate optimized trial designs. Generative adversarial networks create synthetic patient populations that mirror real-world demographics while preserving privacy. Transformer-based models analyze historical trial data to identify success patterns and generate protocol recommend...'''

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

# AI Insights tab (now second)
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
                    "model": selected_model,
                    "insights": insights
                })
                st.download_button("Download Insights", insights, file_name=f"{solution_name.replace(' ', '_').lower()}_insights.md")
            else:
                st.error("No insights returned.")

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