import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="studentsuccess_–_ai_driven_freshman_retention_insights",
    page_icon="https://i.imgur.com/Og6gFnB.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

solution_name = '''Solution 1: StudentSuccess – AI-driven Freshman Retention Insights'''
solution_name_clean = '''studentsuccess_–_ai_driven_freshman_retention_insights'''
table_name = '''HED_RECORDS'''
table_description = '''Consolidated student retention data from multiple sources for StudentSuccess solution'''
solution_content = '''Solution 1: StudentSuccess – AI-driven Freshman Retention Insights

### Business Challenge
The primary business challenge addressed by StudentSuccess is the high freshman dropout rate and the difficulty in identifying at-risk students early in their academic journey. Traditional methods of tracking student performance rely on reactive measures rather than proactive interventions, leading to lost tuition revenue, decreased institutional reputation, and missed opportunities to support student success.

### Key Features
- AI-powered early warning system for at-risk student identification
- Real-time dashboard for tracking student engagement and academic performance
- Automated intervention recommendations based on multi-factor analysis
- Integration with existing Student Information Systems (SIS), Learning Management Systems (LMS), and academic support services

### Data Sources
- Student Information Systems: Banner, PeopleSoft, Colleague
- Learning Management Systems: Canvas, Blackboard, Moodle
- Academic Integrity Systems: Turnitin, SafeAssign
- Engagement Analytics: BrightBytes, Civitas Learning

### Competitive Advantage
StudentSuccess differentiates itself by leveraging advanced machine learning algorithms to predict student retention risk using a comprehensive dataset that includes academic performance, engagement metrics, financial aid status, and behavioral indicators. This holistic approach enables earlier and more accurate identification of at-risk students.

### Key Stakeholders
- Academic Advisors
- Student Success Coordinators
- Enrollment Management Teams
- C-level Executive: Provost and Vice President of Student Affairs

### Technical Approach
StudentSuccess utilizes ensemble machine learning models including random forests, gradient boosting, and neural networks to analyze student data patterns. The system incorporates natural language processing to analyze student communications and engagement patterns, providing comprehensive risk assessment and intervention recommendations.

### Expected Business Results
- **15% improvement in freshman retention rate**
  **1,000 freshman students × 85% baseline retention × 15% improvement = 127 additional retained students/year**
- **$2,500,000 in tuition revenue protection annually**
  **127 additional retained students × $20,000 average tuition = $2,540,000 revenue protection/year**
- **40% reduction in time to identify at-risk students**
  **Traditional 8-week identification → 5-week identification = 3-week earlier intervention**
- **90% accuracy in at-risk student prediction**
  **Improved from 65% manual identification accuracy to 90% AI-powered accuracy**

### Success Metrics
- Freshman retention rate improvement
- Early identification accuracy
- Intervention effectiveness
- Time to risk identification
- Revenue protection through retention

### Risk Assessment
Potential challenges include:
- Data privacy and FERPA compliance requirements
- Integration complexity with legacy systems
- Faculty and staff adoption resistance
- Model bias and fairness considerations

Mitigation strategies:
- Implement comprehensive data governance and privacy controls
- Conduct phased integration with thorough testing
- Provide extensive training and change management support
- Regular model auditing for bias and fairness

### Long-term Evolution
Over the next 3-5 years, StudentSuccess will expand to include predictive analytics for course success, degree completion forecasting, and personalized learning pathway recommendations. Integration with emerging technologies like natural language processing for sentiment analysis and IoT campus engagement tracking will further enhance prediction accuracy.'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Higher Education</p>
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
    # Only include actual numeric metrics, not ID columns
    key_metrics = ["current_gpa", "credit_hours_attempted", "credit_hours_earned", "financial_aid_amount", 
                  "total_course_views", "assignment_submissions", "discussion_posts", "avg_assignment_score", 
                  "course_completion_rate", "plagiarism_incidents", "writing_quality_score", 
                  "engagement_score", "intervention_count"]
    
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
    categorical_options = ["academic_standing", "major_code", "at_risk_flag"]
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
                correlation_info = "Top correlations between student metrics:\n"
                for col1, col2, _, corr_value in corr_pairs[:3]:
                    correlation_info += f"- {col1} and {col2}: r = {corr_value:.2f}\n"
        except Exception as e:
            correlation_info = "Could not calculate correlations between student metrics.\n"

    # Define specific instructions for each focus area
    focus_area_instructions = {
        "Overall Performance": """
        For the Overall Performance analysis of StudentSuccess:
        1. Provide a comprehensive analysis of freshman retention using GPA, credit hours, engagement scores, and at-risk indicators
        2. Identify significant patterns in academic performance, student engagement, and retention risk across different majors and academic standings
        3. Highlight 3-5 key academic metrics that best indicate student success likelihood (GPA trends, course completion rates, engagement scores)
        4. Discuss both strengths and areas for improvement in the AI-powered student success prediction system
        5. Include 3-5 actionable insights for improving freshman retention based on the student data
        
        Structure your response with these higher education focused sections:
        - Academic Performance Insights (5 specific insights with supporting GPA, credit hours, and engagement data)
        - Student Engagement Trends (3-4 significant trends in course views, assignments, and discussion participation)
        - Retention Risk Recommendations (3-5 data-backed recommendations for improving student success interventions)
        - Implementation Steps (3-5 concrete next steps for advisors and student success coordinators)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of StudentSuccess:
        1. Focus specifically on areas where student success interventions and retention efforts can be improved
        2. Identify inefficiencies in academic advising, student engagement tracking, and early warning systems
        3. Analyze correlations between engagement metrics, academic performance, and intervention effectiveness
        4. Prioritize optimization opportunities based on potential impact on retention rates and student outcomes
        5. Suggest specific technical or process improvements for integration with existing SIS and LMS systems
        
        Structure your response with these higher education focused sections:
        - Student Success Optimization Priorities (3-5 areas with highest retention improvement potential)
        - Academic Impact Analysis (quantified benefits of addressing each opportunity in terms of GPA and retention metrics)
        - Advising Strategy Enhancement (specific steps for academic advisors to implement each optimization)
        - System Integration Recommendations (specific technical changes needed for seamless integration with Banner, Canvas, and Turnitin)
        - Student Support Risk Assessment (potential challenges for students and advisors and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of StudentSuccess:
        1. Focus on cost-benefit analysis and ROI in higher education terms (tuition revenue protection vs. intervention costs)
        2. Quantify financial impacts through retention improvements, reduced dropout costs, and increased enrollment efficiency
        3. Identify revenue protection opportunities across different student populations and academic programs
        4. Analyze resource allocation efficiency across different advisors and intervention strategies
        5. Project future financial outcomes based on improved retention rates and expanding to other student populations
        
        Structure your response with these higher education focused sections:
        - Tuition Revenue Analysis (breakdown of revenue protection and potential gains by retention improvements)
        - Student Success Investment Impact (how improved early warning affects institutional costs and student outcomes)
        - Higher Education ROI Calculation (specific calculations showing return on investment in terms of retained tuition revenue)
        - Intervention Cost-Effectiveness (specific areas to optimize intervention spending for maximum retention impact)
        - Enrollment Revenue Forecasting (projections based on improved retention rate metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of StudentSuccess:
        1. Focus on long-term strategic implications for digital transformation in higher education student success
        2. Identify competitive advantages against traditional reactive advising approaches
        3. Suggest new directions for AI integration with emerging educational technologies (e.g., adaptive learning, predictive analytics)
        4. Connect recommendations to broader institutional goals of improving graduation rates and student satisfaction
        5. Provide a student success roadmap with prioritized initiatives
        
        Structure your response with these higher education focused sections:
        - Digital Student Success Context (how StudentSuccess fits into broader digital transformation in higher education)
        - Institutional Competitive Advantage Analysis (how to maximize retention advantages compared to traditional reactive methods)
        - Academic Technology Strategic Priorities (3-5 high-impact strategic initiatives for improving student outcomes)
        - Advanced Analytics Integration Vision (how to evolve StudentSuccess with predictive learning analytics over 1-3 years)
        - Student Success Transformation Roadmap (sequenced steps for expanding to degree completion prediction and personalized learning pathways)
        """
    }

    # Get the specific instructions for the selected focus area
    selected_focus_instructions = focus_area_instructions.get(focus_area, "")

    prompt = f'''
    You are an expert data analyst specializing in {focus_area.lower()} analysis for higher education student success and retention.

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
    - Frame all insights in the context of higher education student success and freshman retention
    '''

    return call_cortex_model(prompt, model_name)

def create_metrics_charts(data):
    """Create metric visualizations for the higher education data"""
    charts = []
    
    # GPA Distribution
    if 'current_gpa' in data.columns:
        gpa_chart = alt.Chart(data).mark_bar().encode(
            alt.X('current_gpa:Q', bin=alt.Bin(maxbins=20), title='Current GPA'),
            alt.Y('count()', title='Number of Students'),
            color=alt.value('#1f77b4')
        ).properties(
            title='GPA Distribution',
            width=380,
            height=280
        )
        charts.append(('GPA Distribution', gpa_chart))
    
    # Engagement Score by Academic Standing
    if 'engagement_score' in data.columns and 'academic_standing' in data.columns:
        engagement_chart = alt.Chart(data).mark_boxplot().encode(
            alt.X('academic_standing:N', title='Academic Standing'),
            alt.Y('engagement_score:Q', title='Engagement Score'),
            color=alt.Color('academic_standing:N', legend=None)
        ).properties(
            title='Engagement by Standing',
            width=380,
            height=280
        )
        charts.append(('Engagement by Standing', engagement_chart))
    
    # Course Completion Rate Trends
    if 'course_completion_rate' in data.columns and 'enrollment_date' in data.columns:
        completion_chart = alt.Chart(data).mark_line(point=True).encode(
            alt.X('month(enrollment_date):O', title='Enrollment Month'),
            alt.Y('mean(course_completion_rate):Q', title='Avg Completion Rate'),
            color=alt.value('#ff7f0e')
        ).properties(
            title='Completion Rate Trends',
            width=380,
            height=280
        )
        charts.append(('Completion Rate Trends', completion_chart))
    
    # At-Risk Student Distribution
    if 'at_risk_flag' in data.columns:
        risk_chart = alt.Chart(data).mark_arc().encode(
            theta=alt.Theta('count():Q'),
            color=alt.Color('at_risk_flag:N', title='At Risk', scale=alt.Scale(range=['#2ca02c', '#d62728'])),
            tooltip=['at_risk_flag:N', 'count():Q']
        ).properties(
            title='At-Risk Distribution',
            width=380,
            height=280
        )
        charts.append(('At-Risk Distribution', risk_chart))
    
    # Financial Aid vs GPA Correlation
    if 'financial_aid_amount' in data.columns and 'current_gpa' in data.columns:
        aid_chart = alt.Chart(data).mark_circle(size=80).encode(
            alt.X('financial_aid_amount:Q', title='Financial Aid Amount ($)'),
            alt.Y('current_gpa:Q', title='Current GPA'),
            color=alt.Color('engagement_score:Q', title='Engagement', scale=alt.Scale(scheme='viridis')),
            tooltip=['financial_aid_amount:Q', 'current_gpa:Q', 'engagement_score:Q']
        ).properties(
            title='Aid vs GPA Correlation',
            width=380,
            height=280
        )
        charts.append(('Aid vs GPA Correlation', aid_chart))
    
    # Major Performance Analysis
    if 'major_code' in data.columns and 'current_gpa' in data.columns:
        # Group by major and calculate average GPA
        major_data = data.groupby('major_code')['current_gpa'].mean().reset_index()
        major_data = major_data.head(12).sort_values('current_gpa', ascending=False)  # Top 12 performing majors
        
        major_chart = alt.Chart(major_data).mark_bar().encode(
            alt.X('major_code:O', title='Major Code', sort='-y'),
            alt.Y('current_gpa:Q', title='Average GPA'),
            color=alt.Color('current_gpa:Q', title='Avg GPA', scale=alt.Scale(scheme='blues')),
            tooltip=['major_code:O', alt.Tooltip('current_gpa:Q', format='.2f')]
        ).properties(
            title='Major Performance',
            width=380,
            height=280
        )
        charts.append(('Major Performance', major_chart))
    
    return charts

data = load_data()
if data.empty:
    st.error("No data found.")
    st.stop()

categorical_cols = [col for col in ["academic_standing", "major_code", "advisor_id"] if col in data.columns]
numeric_cols = [col for col in ["current_gpa", "credit_hours_attempted", "credit_hours_earned", "financial_aid_amount", 
                               "total_course_views", "assignment_submissions", "discussion_posts", "avg_assignment_score", 
                               "course_completion_rate", "plagiarism_incidents", "writing_quality_score", 
                               "engagement_score", "intervention_count"] if col in data.columns]
date_cols = [col for col in ["enrollment_date", "last_login_date", "last_updated"] if col in data.columns]

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
        if 'current_gpa' in data.columns:
            avg_gpa = data['current_gpa'].mean()
            st.metric("Average GPA", f"{avg_gpa:.2f}", delta=f"{(avg_gpa - 3.0):.2f} vs 3.0 target")
    
    with col2:
        if 'course_completion_rate' in data.columns:
            avg_completion = data['course_completion_rate'].mean()
            st.metric("Avg Completion Rate", f"{avg_completion:.1%}", delta=f"{(avg_completion - 0.85):.1%} vs 85% target")
    
    with col3:
        if 'engagement_score' in data.columns:
            avg_engagement = data['engagement_score'].mean()
            st.metric("Avg Engagement Score", f"{avg_engagement:.1f}", delta=f"{(avg_engagement - 70):.1f} vs 70 target")
    
    with col4:
        if 'at_risk_flag' in data.columns:
            at_risk_pct = data['at_risk_flag'].mean()
            st.metric("At-Risk Students", f"{at_risk_pct:.1%}", delta=f"{(at_risk_pct - 0.30):.1%} vs 30% baseline")
    
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
        
        # Create three columns for better organization
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎯 Key Academic Metrics**")
            key_metrics = ['current_gpa', 'course_completion_rate', 'engagement_score', 'avg_assignment_score']
            key_metrics_present = [m for m in key_metrics if m in summary_df.index]
            
            if key_metrics_present:
                key_stats_df = summary_df.loc[key_metrics_present]
                
                # Create a more readable format
                for metric in key_stats_df.index:
                    mean_val = key_stats_df.loc[metric, 'Mean']
                    min_val = key_stats_df.loc[metric, 'Min']
                    max_val = key_stats_df.loc[metric, 'Max']
                    
                    # Format based on metric type
                    if 'gpa' in metric.lower() or 'score' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.2f}",
                            help=f"Range: {min_val:.2f} - {max_val:.2f}"
                        )
                    elif 'rate' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.1%}",
                            help=f"Range: {min_val:.1%} - {max_val:.1%}"
                        )
                    else:
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.1f}",
                            help=f"Range: {min_val:.1f} - {max_val:.1f}"
                        )
        
        with col2:
            st.markdown("**📊 Distribution Insights**")
            
            # Calculate and display key insights
            insights = []
            
            if 'current_gpa' in summary_df.index:
                gpa_mean = summary_df.loc['current_gpa', 'Mean']
                gpa_std = summary_df.loc['current_gpa', 'Std Dev']
                insights.append(f"• **GPA Variability**: {gpa_std:.2f} (σ)")
                
                if gpa_mean < 2.5:
                    insights.append(f"• **⚠️ Low average GPA** ({gpa_mean:.2f})")
                else:
                    insights.append(f"• **Acceptable GPA performance** ({gpa_mean:.2f})")
            
            if 'financial_aid_amount' in summary_df.index:
                aid_q75 = summary_df.loc['financial_aid_amount', '75%']
                aid_q25 = summary_df.loc['financial_aid_amount', '25%']
                iqr = aid_q75 - aid_q25
                insights.append(f"• **Financial Aid IQR**: ${iqr:,.0f}")
            
            if 'engagement_score' in summary_df.index:
                eng_median = summary_df.loc['engagement_score', '50% (Median)']
                eng_min = summary_df.loc['engagement_score', 'Min']
                insights.append(f"• **Median Engagement**: {eng_median:.1f}")
                if eng_min < 20:
                    insights.append(f"• **⚠️ Low engagement detected**: as low as {eng_min:.1f}")
            
            if 'plagiarism_incidents' in summary_df.index:
                plag_mean = summary_df.loc['plagiarism_incidents', 'Mean']
                insights.append(f"• **Avg Plagiarism Incidents**: {plag_mean:.1f}")
            
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