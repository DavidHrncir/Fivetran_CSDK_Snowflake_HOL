import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="livestock_health_guardian_–_ai_driven_livestock_health_monitoring",
    page_icon="https://i.imgur.com/Og6gFnB.png",
    layout="wide",
    initial_sidebar_state="expanded"
)

solution_name = '''Solution 1: Livestock Health Guardian – AI-driven Livestock Health Monitoring'''
solution_name_clean = '''livestock_health_guardian_–_ai_driven_livestock_health_monitoring'''
table_name = '''AGR_RECORDS'''
table_description = '''Integrated data from farm management software, livestock health records, and weather data for real-time monitoring and predictive analytics'''
solution_content = '''Solution 1: Livestock Health Guardian – AI-driven Livestock Health Monitoring**

### Business Challenge
The primary business challenge addressed by Livestock Health Guardian is the need for early detection and prevention of livestock health issues, reducing the risk of disease outbreaks and improving overall animal welfare.

### Key Features
• Real-time monitoring of vital signs and behavior
• Advanced predictive analytics for early disease detection
• Personalized health recommendations for each animal
• Integration with farm management software for seamless data exchange

### Data Sources
• Farm Management Software: Granular, Trimble Ag, Climate FieldView
• Livestock Health Records: Zoetis, Merck Animal Health, Elanco
• Weather Data: The Weather Company, AccuWeather, DTN

### Competitive Advantage
Livestock Health Guardian differentiates itself through its use of advanced generative AI algorithms, enabling early detection of health issues and personalized recommendations for each animal. This creates a competitive advantage by reducing the risk of disease outbreaks and improving animal welfare.

### Key Stakeholders
• Farm Managers
• Veterinarians
• Livestock Owners

### Top C-level Executive
CEO of the farm or agricultural company

### Technical Approach
Generative AI is used to analyze vast amounts of data from various sources, including farm management software, livestock health records, and weather data. This analysis enables the system to identify patterns and anomalies, predicting potential health issues before they become severe.

### Expected Business Results
• **300 fewer failed treatments per year**
  **10,000 animals × 3% baseline treatment failure rate × 10% reduction = 300 fewer failed treatments/year**
• **$ 1,200,000 in reduced veterinary costs annually**
  **$ 4,000,000 annual veterinary costs × 30% reduction = $ 1,200,000 savings/year**
• **20% increase in animal productivity**
  **80,000 animals × 20% baseline productivity rate × 20% improvement = 32,000 additional units/year**
• **15% reduction in antibiotic usage**
  **10,000 animals × 15% baseline antibiotic usage rate × 15% reduction = 1,500 fewer antibiotic treatments/year**

### Success Metrics
• Reduction in treatment failures
• Decrease in veterinary costs
• Increase in animal productivity
• Reduction in antibiotic usage

### Risk Assessment
Potential implementation challenges include data quality issues and the need for significant training data. Mitigation strategies include ensuring high-quality data sources and investing in data curation and annotation.

### Long-term Evolution
In the next 3-5 years, Livestock Health Guardian will evolve to incorporate more advanced generative AI techniques, such as multimodal learning and transfer learning, to further improve its predictive capabilities and adapt to new data sources and farm management practices.

---

**'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Agriculture</p>
    </div>
</div>
''', unsafe_allow_html=True)

# Define available models as strings
MODELS = [
    "llama3.1-8b", "snowflake-llama-3.3-70b", "mistral-large2", "llama3.1-70b", "llama4-maverick", "llama4-scout", "claude-3-5-sonnet", "snowflake-llama3.1-405b", "deepseek-r1"
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
    key_metrics = ["age", "weight", "temperature", "humidity", "precipitation", "predicted_health_risk"]
    
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
    categorical_options = ["species", "breed", "health_status", "vaccination_history", "medication_history", "weather_data", "recommended_action"]
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
        For the Overall Performance analysis of Livestock Health Guardian:
        1. Provide a comprehensive analysis of the livestock health monitoring system using animal health metrics, environmental conditions, and predictive health risk scores
        2. Identify significant patterns in animal health status, vaccination coverage, and environmental factors across different species and breeds
        3. Highlight 3-5 key livestock metrics that best indicate overall herd health and productivity (health status distribution, vaccination compliance, weight patterns, health risk predictions)
        4. Discuss both strengths and areas for improvement in the AI-powered livestock health monitoring process
        5. Include 3-5 actionable insights for improving farm operations and animal welfare based on the livestock data
        
        Structure your response with these agriculture-focused sections:
        - Livestock Health Insights (5 specific insights with supporting animal health and environmental data)
        - Animal Welfare Performance Trends (3-4 significant trends in health status, vaccination rates, and risk predictions)
        - Farm Management Recommendations (3-5 data-backed recommendations for improving livestock operations)
        - Implementation Steps (3-5 concrete next steps for farm managers and veterinarians)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of Livestock Health Guardian:
        1. Focus specifically on areas where livestock health monitoring and farm management efficiency can be improved
        2. Identify inefficiencies in vaccination schedules, health interventions, and environmental management across different animal species and farms
        3. Analyze correlations between environmental conditions, animal characteristics, and health risk predictions
        4. Prioritize optimization opportunities based on potential impact on animal welfare, veterinary costs, and farm productivity
        5. Suggest specific technical or process improvements for integration with existing farm management software and veterinary systems
        
        Structure your response with these agriculture-focused sections:
        - Livestock Management Optimization Priorities (3-5 areas with highest potential for improving animal health and reducing costs)
        - Health Intervention Impact Analysis (quantified benefits of addressing each opportunity in terms of animal welfare metrics)
        - Farm Management Integration Strategy (specific steps for farm managers to implement each optimization)
        - Veterinary System Integration Recommendations (specific technical changes needed for seamless integration with farm management software)
        - Animal Welfare Risk Assessment (potential challenges for livestock health and farm operations and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of Livestock Health Guardian:
        1. Focus on cost-benefit analysis and ROI in agriculture terms (veterinary costs vs. animal productivity gains and disease prevention)
        2. Quantify financial impacts through reduced veterinary expenses, improved animal productivity, and decreased treatment failures
        3. Identify cost savings opportunities across different animal species, health interventions, and farm operations
        4. Analyze resource allocation efficiency across different farms, veterinarians, and livestock management practices
        5. Project future financial outcomes based on improved health prediction accuracy and expanding to preventive care
        
        Structure your response with these agriculture-focused sections:
        - Veterinary Cost Analysis (breakdown of veterinary expenses and potential savings by animal species and treatment type)
        - Animal Productivity Impact (how improved health monitoring affects livestock productivity and farm revenue)
        - Agriculture ROI Calculation (specific calculations showing return on investment in terms of reduced veterinary costs and improved productivity)
        - Disease Prevention Opportunities (specific areas to reduce disease outbreaks and associated costs)
        - Farm Economics Forecasting (projections based on improved animal health metrics and productivity)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of Livestock Health Guardian:
        1. Focus on long-term strategic implications for digital transformation in agriculture and livestock management
        2. Identify competitive advantages against traditional manual livestock health monitoring approaches
        3. Suggest new directions for AI integration with emerging agricultural technologies (e.g., IoT sensors, precision agriculture, automated feeding systems)
        4. Connect recommendations to broader agricultural goals of sustainable farming, animal welfare improvement, and farm profitability
        5. Provide a digital agriculture roadmap with prioritized initiatives
        
        Structure your response with these agriculture-focused sections:
        - Digital Agriculture Context (how Livestock Health Guardian fits into broader digital transformation in farming)
        - Farm Management Competitive Advantage Analysis (how to maximize efficiency advantages compared to traditional manual monitoring)
        - Agricultural Technology Strategic Priorities (3-5 high-impact strategic initiatives for improving livestock operations)
        - Advanced Agricultural Technology Integration Vision (how to evolve with IoT sensors, precision agriculture, and automated systems over 1-3 years)
        - Farm Operations Transformation Roadmap (sequenced steps for expanding to real-time monitoring and predictive veterinary care)
        """
    }

    # Get the specific instructions for the selected focus area
    selected_focus_instructions = focus_area_instructions.get(focus_area, "")

    prompt = f'''
    You are an expert data analyst specializing in {focus_area.lower()} analysis for agriculture and livestock operations.

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
    - Frame all insights in the context of livestock health monitoring and farm management
    '''

    return call_cortex_model(prompt, model_name)

def create_metrics_charts(data):
    """Create metric visualizations for the agriculture data"""
    charts = []
    
    # Animal Weight Distribution
    if 'weight' in data.columns:
        weight_chart = alt.Chart(data).mark_bar().encode(
            alt.X('weight:Q', bin=alt.Bin(maxbins=20), title='Animal Weight (lbs)'),
            alt.Y('count()', title='Number of Animals'),
            color=alt.value('#2E8B57')
        ).properties(
            title='Weight Distribution',
            width=380,
            height=280
        )
        charts.append(('Weight Distribution', weight_chart))
    
    # Health Risk by Species
    if 'predicted_health_risk' in data.columns and 'species' in data.columns:
        risk_chart = alt.Chart(data).mark_boxplot().encode(
            alt.X('species:N', title='Animal Species'),
            alt.Y('predicted_health_risk:Q', title='Predicted Health Risk'),
            color=alt.Color('species:N', legend=None)
        ).properties(
            title='Health Risk by Species',
            width=380,
            height=280
        )
        charts.append(('Health Risk by Species', risk_chart))
    
    # Environmental Temperature Trends
    if 'temperature' in data.columns:
        temp_chart = alt.Chart(data).mark_area(opacity=0.7).encode(
            alt.X('temperature:Q', bin=alt.Bin(maxbins=15), title='Temperature (°F)'),
            alt.Y('count()', title='Frequency'),
            color=alt.value('#FF6B6B')
        ).properties(
            title='Temperature Distribution',
            width=380,
            height=280
        )
        charts.append(('Temperature Distribution', temp_chart))
    
    # Health Status Distribution
    if 'health_status' in data.columns:
        status_chart = alt.Chart(data).mark_arc().encode(
            theta=alt.Theta('count():Q'),
            color=alt.Color('health_status:N', title='Health Status'),
            tooltip=['health_status:N', 'count():Q']
        ).properties(
            title='Health Status Distribution',
            width=380,
            height=280
        )
        charts.append(('Health Status Distribution', status_chart))
    
    # Weight vs Health Risk Correlation
    if 'weight' in data.columns and 'predicted_health_risk' in data.columns:
        correlation_chart = alt.Chart(data).mark_circle(size=80).encode(
            alt.X('weight:Q', title='Animal Weight (lbs)'),
            alt.Y('predicted_health_risk:Q', title='Predicted Health Risk'),
            color=alt.Color('age:Q', title='Age (years)', scale=alt.Scale(scheme='viridis')),
            tooltip=['weight:Q', 'predicted_health_risk:Q', 'age:Q', 'species:N']
        ).properties(
            title='Weight vs Health Risk',
            width=380,
            height=280
        )
        charts.append(('Weight vs Health Risk', correlation_chart))
    
    # Vaccination Status by Breed
    if 'vaccination_history' in data.columns and 'breed' in data.columns:
        # Group by breed and vaccination status
        vacc_data = data.groupby(['breed', 'vaccination_history']).size().reset_index(name='count')
        # Limit to top 10 breeds by total count
        top_breeds = data['breed'].value_counts().head(10).index
        vacc_data_filtered = vacc_data[vacc_data['breed'].isin(top_breeds)]
        
        vacc_chart = alt.Chart(vacc_data_filtered).mark_bar().encode(
            alt.X('breed:O', title='Breed', sort='-y'),
            alt.Y('count:Q', title='Number of Animals'),
            color=alt.Color('vaccination_history:N', title='Vaccination Status'),
            tooltip=['breed:O', 'vaccination_history:N', 'count:Q']
        ).properties(
            title='Vaccination Status by Breed',
            width=380,
            height=280
        )
        charts.append(('Vaccination Status by Breed', vacc_chart))
    
    return charts

data = load_data()
if data.empty:
    st.error("No data found.")
    st.stop()

categorical_cols = [col for col in ["species", "breed", "health_status", "vaccination_history", "medication_history", "weather_data", "recommended_action"] if col in data.columns]
numeric_cols = [col for col in ["age", "weight", "temperature", "humidity", "precipitation", "predicted_health_risk"] if col in data.columns]
date_cols = [col for col in [] if col in data.columns]

sample_cols = data.columns.tolist()
numeric_candidates = [col for col in sample_cols if data[col].dtype in ['float64', 'int64'] and 'id' not in col.lower()]
date_candidates = [col for col in sample_cols if 'date' in col.lower() or 'timestamp' in col.lower()]
cat_candidates = [col for col in sample_cols if data[col].dtype == 'object' and data[col].nunique() < 1000]

# Four tabs - Metrics tab first, then AI Insights
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics tab (first)
with tabs[0]:
    st.subheader("📊 Key Performance Metrics")
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if 'predicted_health_risk' in data.columns:
            avg_risk = data['predicted_health_risk'].mean()
            st.metric("Avg Health Risk", f"{avg_risk:.3f}", delta=f"{(avg_risk - 0.5)*100:.1f}% vs baseline")
    
    with col2:
        if 'weight' in data.columns:
            avg_weight = data['weight'].mean()
            st.metric("Avg Animal Weight", f"{avg_weight:,.0f} lbs", delta=f"{(avg_weight - 1500):,.0f} vs target")
    
    with col3:
        if 'age' in data.columns:
            avg_age = data['age'].mean()
            st.metric("Avg Animal Age", f"{avg_age:.1f} years", delta=f"{(avg_age - 6):.1f} vs target")
    
    with col4:
        if 'temperature' in data.columns:
            avg_temp = data['temperature'].mean()
            st.metric("Avg Temperature", f"{avg_temp:.1f}°F", delta=f"{(avg_temp - 70):.1f}°F vs optimal")
    
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
            st.markdown("**🎯 Key Livestock Metrics**")
            key_metrics = ['age', 'weight', 'temperature', 'humidity', 'precipitation', 'predicted_health_risk']
            key_metrics_present = [m for m in key_metrics if m in summary_df.index]
            
            if key_metrics_present:
                # Create a more readable format
                for metric in key_metrics_present:
                    mean_val = summary_df.loc[metric, 'Mean']
                    min_val = summary_df.loc[metric, 'Min']
                    max_val = summary_df.loc[metric, 'Max']
                    
                    # Format based on metric type
                    if 'weight' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:,.0f} lbs",
                            help=f"Range: {min_val:,.0f} - {max_val:,.0f} lbs"
                        )
                    elif 'risk' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.3f}",
                            help=f"Range: {min_val:.3f} - {max_val:.3f}"
                        )
                    elif 'temperature' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.1f}°F",
                            help=f"Range: {min_val:.1f}°F - {max_val:.1f}°F"
                        )
                    elif 'humidity' in metric.lower() or 'precipitation' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.1f}%",
                            help=f"Range: {min_val:.1f}% - {max_val:.1f}%"
                        )
                    elif 'age' in metric.lower():
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.1f} years",
                            help=f"Range: {min_val:.1f} - {max_val:.1f} years"
                        )
                    else:
                        st.metric(
                            label=metric.replace('_', ' ').title(),
                            value=f"{mean_val:.2f}",
                            help=f"Range: {min_val:.2f} - {max_val:.2f}"
                        )
        
        with col2:
            st.markdown("**📊 Distribution Insights**")
            
            # Calculate and display key insights
            insights = []
            
            if 'predicted_health_risk' in summary_df.index:
                hr_mean = summary_df.loc['predicted_health_risk', 'Mean']
                hr_std = summary_df.loc['predicted_health_risk', 'Std Dev']
                insights.append(f"• **Health Risk Variability**: {hr_std:.3f} (σ)")
                
                if hr_mean > 0.5:
                    insights.append(f"• **⚠️ Elevated health risk** ({hr_mean:.1%})")
                else:
                    insights.append(f"• **Good health status** ({hr_mean:.1%} avg risk)")
            
            if 'weight' in summary_df.index:
                wt_q75 = summary_df.loc['weight', '75%']
                wt_q25 = summary_df.loc['weight', '25%']
                iqr = wt_q75 - wt_q25
                insights.append(f"• **Weight IQR**: {iqr:,.0f} lbs")
            
            if 'age' in summary_df.index:
                age_median = summary_df.loc['age', '50% (Median)']
                age_max = summary_df.loc['age', 'Max']
                insights.append(f"• **Median Age**: {age_median:.1f} years")
                if age_max > 10:
                    insights.append(f"• **Mature animals present**: up to {age_max:.1f} years")
            
            if 'temperature' in summary_df.index:
                temp_mean = summary_df.loc['temperature', 'Mean']
                temp_std = summary_df.loc['temperature', 'Std Dev']
                insights.append(f"• **Avg Environmental Temp**: {temp_mean:.1f}°F")
                if temp_std > 15:
                    insights.append(f"• **Variable conditions** (σ = {temp_std:.1f}°F)")
            
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

# AI Insights tab (second)
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

# Insights History tab
with tabs[2]:
    st.subheader("📁 Insights History")
    if st.session_state.insights_history:
        for i, item in enumerate(reversed(st.session_state.insights_history)):
            with st.expander(f"{item['timestamp']} - {item['focus']} ({item['model']})", expanded=False):
                st.markdown(item["insights"])
    else:
        st.info("No insights generated yet. Go to the AI Insights tab to generate some insights.")

# Data Explorer tab (fourth)
with tabs[3]:
    st.subheader("🔍 Data Explorer")
    rows_per_page = st.slider("Rows per page", 5, 50, 10)
    page = st.number_input("Page", min_value=1, value=1)
    start = (page - 1) * rows_per_page
    end = min(start + rows_per_page, len(data))
    st.dataframe(data.iloc[start:end], use_container_width=True)
    st.caption(f"Showing rows {start + 1}–{end} of {len(data)}")