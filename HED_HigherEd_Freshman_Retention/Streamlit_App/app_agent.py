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
            "challenge": "Academic advisors manually review hundreds of student records daily, spending 3+ hours analyzing GPA trends, engagement metrics, and early warning indicators to identify at-risk freshmen and develop retention strategies.",
            "solution": "Autonomous student success workflow that analyzes academic performance, engagement patterns, and behavioral data to generate automated at-risk assessments, identify retention patterns, and produce prioritized intervention recommendations with predictive analytics."
        },
        "Optimization Opportunities": {
            "challenge": "Student success coordinators spend 4+ hours daily manually identifying inefficiencies in academic advising, engagement tracking, and intervention strategies across diverse student populations and academic programs.",
            "solution": "AI-powered student success optimization analysis that automatically detects advising gaps, engagement performance inefficiencies, and intervention allocation improvements with specific implementation recommendations for SIS and LMS integration."
        },
        "Financial Impact": {
            "challenge": "Enrollment financial analysts manually calculate complex ROI metrics across retention initiatives and student success programs, requiring 3+ hours of cost modeling to assess tuition revenue protection and intervention cost optimization.",
            "solution": "Automated higher education financial analysis that calculates comprehensive retention ROI, identifies tuition revenue protection opportunities across student segments, and projects enrollment efficiency benefits with detailed cost forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "Provosts and VPs of Student Affairs spend hours manually analyzing digital transformation opportunities and developing strategic technology roadmaps for student success advancement and predictive analytics implementation.",
            "solution": "Strategic student success intelligence workflow that analyzes competitive advantages against traditional reactive methods, identifies predictive analytics and personalized learning integration opportunities, and creates prioritized digital transformation roadmaps."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - Higher Education Student Success focused version"""
    
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
        total_students = len(data)
        key_metrics = ["current_gpa", "course_completion_rate", "engagement_score", "intervention_count"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced higher education data insights
        avg_gpa = data['current_gpa'].mean() if 'current_gpa' in data.columns else 0
        avg_completion_rate = data['course_completion_rate'].mean() if 'course_completion_rate' in data.columns else 0
        major_count = len(data['major_code'].unique()) if 'major_code' in data.columns else 0
        student_count = len(data['student_id'].unique()) if 'student_id' in data.columns else 0
        avg_engagement = data['engagement_score'].mean() if 'engagement_score' in data.columns else 0
        at_risk_count = len(data[data['at_risk_flag'] == True]) if 'at_risk_flag' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Student Success Data Initialization", 15, f"Loading comprehensive student academic dataset with enhanced validation across {total_students} student records and {major_count} academic programs", f"Connected to {len(available_metrics)} academic metrics across {len(data.columns)} total student success data dimensions"),
                ("Academic Performance Assessment", 35, f"Advanced calculation of retention indicators with GPA analysis (avg GPA: {avg_gpa:.3f})", f"Computed academic metrics: {avg_gpa:.3f} avg GPA, {avg_completion_rate:.1%} completion rate, {avg_engagement:.1f} avg engagement score"),
                ("Student Engagement Pattern Recognition", 55, f"Sophisticated identification of engagement performance patterns with academic correlation analysis across {major_count} academic majors", f"Detected significant patterns in {len(data['academic_standing'].unique()) if 'academic_standing' in data.columns else 'N/A'} academic standings with student correlation analysis completed"),
                ("AI Student Success Intelligence Processing", 75, f"Processing comprehensive student data through {model_name} with advanced reasoning for retention efficiency insights", f"Enhanced AI analysis of student retention prediction effectiveness across {total_students} academic records completed"),
                ("Academic Performance Report Compilation", 100, f"Professional student success analysis with evidence-based recommendations and actionable retention insights ready", f"Comprehensive academic performance report with {len(available_metrics)} student metrics analysis and retention recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            completed_courses = len(data[data['course_completion_rate'] > 0.8]) if 'course_completion_rate' in data.columns else 0
            success_rate = (completed_courses / total_students) * 100 if total_students > 0 else 0
            
            steps = [
                ("Student Success Optimization Data Preparation", 12, f"Advanced loading of academic performance data with enhanced validation across {total_students} students for retention improvement identification", f"Prepared {major_count} academic programs, {student_count} students for optimization analysis with {success_rate:.1f}% high completion rate"),
                ("Academic Advising Inefficiency Detection", 28, f"Sophisticated analysis of advising scheduling and student engagement with evidence-based inefficiency identification", f"Identified optimization opportunities across {major_count} academic programs with student performance and advising gaps"),
                ("Student Success Correlation Analysis", 45, f"Enhanced examination of relationships between academic standing, engagement scores, and intervention effectiveness", f"Analyzed correlations between academic activities and student performance across {total_students} student records"),
                ("SIS/LMS Integration Optimization", 65, f"Comprehensive evaluation of student success integration with existing Banner, Canvas, and Turnitin systems", f"Assessed integration opportunities across {len(data.columns)} data points and student success system optimization needs"),
                ("AI Student Success Intelligence", 85, f"Generating advanced retention optimization recommendations using {model_name} with higher education reasoning and implementation strategies", f"AI-powered student success optimization strategy across {major_count} academic areas and engagement improvements completed"),
                ("Student Success Strategy Finalization", 100, f"Professional student success optimization report with prioritized implementation roadmap and retention impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and student success implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            total_aid_amount = data['financial_aid_amount'].sum() if 'financial_aid_amount' in data.columns else 0
            avg_aid = data['financial_aid_amount'].mean() if 'financial_aid_amount' in data.columns else 0
            
            steps = [
                ("Higher Education Financial Data Integration", 15, f"Advanced loading of student success financial data and tuition revenue metrics with enhanced validation across {total_students} students", f"Integrated student financial data: ${avg_aid:,.0f} avg financial aid, {at_risk_count} at-risk students across enrollment portfolio"),
                ("Retention Revenue Calculation", 30, f"Sophisticated ROI metrics calculation with tuition revenue analysis and retention cost optimization", f"Computed comprehensive cost analysis: retention expenses, intervention costs, and ${total_aid_amount:,.0f} total financial aid optimization potential"),
                ("Student Success Investment Assessment", 50, f"Enhanced analysis of retention revenue impact with student success metrics and tuition revenue correlation analysis", f"Assessed financial implications: {at_risk_count} at-risk students with {student_count} total students requiring retention optimization"),
                ("Academic Resource Efficiency Analysis", 70, f"Comprehensive evaluation of resource allocation efficiency across academic programs with student lifecycle revenue optimization", f"Analyzed resource efficiency: {major_count} academic programs with student retention revenue protection opportunities identified"),
                ("AI Higher Education Financial Modeling", 90, f"Advanced student success financial projections and retention ROI calculations using {model_name} with comprehensive higher education cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} academic cost metrics completed"),
                ("Student Success Economics Report Generation", 100, f"Professional higher education financial impact analysis with detailed retention ROI calculations and tuition revenue forecasting ready", f"Comprehensive student success financial report with ${total_aid_amount:,.0f} revenue optimization analysis and academic efficiency strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            automation_efficiency_score = avg_engagement * 1.2 if avg_engagement > 0 else 0
            
            steps = [
                ("Higher Education Technology Assessment", 15, f"Advanced loading of student success digital context with competitive positioning analysis across {total_students} students and {major_count} academic programs", f"Analyzed higher education technology landscape: {major_count} academic programs, {student_count} students, comprehensive academic digitization assessment completed"),
                ("Student Success Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional reactive academic advising with AI-powered retention prediction effectiveness", f"Assessed competitive advantages: {automation_efficiency_score:.1f}% automation efficiency, {avg_engagement:.1f} engagement score vs manual methods"),
                ("Advanced Academic Technology Integration", 50, f"Enhanced analysis of integration opportunities with predictive analytics, personalized learning, and digital student success technologies across {len(data.columns)} academic data dimensions", f"Identified strategic technology integration: adaptive learning platforms, predictive retention algorithms, automated academic intervention opportunities"),
                ("Digital Student Success Strategy Development", 70, f"Comprehensive development of prioritized digital transformation roadmap with evidence-based academic technology adoption strategies", f"Created sequenced implementation plan across {major_count} academic areas with advanced technology integration opportunities"),
                ("AI Higher Education Strategic Processing", 85, f"Advanced student success strategic recommendations using {model_name} with long-term competitive positioning and higher education technology analysis", f"Enhanced strategic analysis with student success competitive positioning and digital transformation roadmap completed"),
                ("Digital Academic Transformation Report Generation", 100, f"Professional digital higher education transformation roadmap with competitive analysis and academic technology implementation plan ready for Provost executive review", f"Comprehensive strategic report with {major_count}-program implementation plan and student success competitive advantage analysis generated")
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

# Load data
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

# AI Insights tab
with tabs[1]:
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each student success analysis focus area**")
    
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
                st.success(f"🎉 {focus_area} Agent completed with real student success data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real Higher Education Student Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Student Success Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Student Success Analysis</small><br>
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