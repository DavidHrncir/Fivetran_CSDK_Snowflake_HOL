import streamlit as st
import pandas as pd
import altair as alt
import time
import json
import re
from datetime import datetime
from snowflake.snowpark.context import get_active_session

st.set_page_config(
    page_title="materialmind_–_ai_powered_material_selection_and_optimization",
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

solution_name = '''Solution 2: MaterialMind – AI-powered Material Selection and Optimization'''
solution_name_clean = '''materialmind_–_ai_powered_material_selection_and_optimization'''
table_name = '''MSO_RECORDS'''
table_description = '''Consolidated table containing material properties, product lifecycle management, and CAD system data for material selection and optimization'''
solution_content = '''Solution 2: MaterialMind – AI-powered Material Selection and Optimization**

**Primary Business Challenge:** 
- Inefficient material selection and optimization leading to increased costs and reduced product performance.

**Key Features:**
- AI-driven material selection and optimization
- Integration with existing CAD systems
- Real-time material properties analysis

**Data Sources:**
- Material properties databases: MatWeb, Granta Design, Material Properties Database
- Product Lifecycle Management (PLM) systems: Siemens Teamcenter, PTC Windchill, Oracle Agile
- Computer-Aided Design (CAD) systems: Autodesk Inventor, SolidWorks, Siemens NX

**Competitive Advantage:**
- Optimizes material selection for improved product performance and reduced costs.

**Key Stakeholders:**
- Product Designers
- Materials Engineers
- Operations Directors
- Top C-level executive: Chief Operating Officer (COO)

**Technical Approach:**
- Generative AI algorithms (e.g., Generative Adversarial Networks (GANs)) to optimize material selection.
- Integration with CAD systems to enable seamless material selection.

**Expected Business Results:**
- 12% reduction in material costs
- 10% decrease in product weight
- 8% increase in product performance
- 15% reduction in material waste

**Calculations:**
- 12% reduction in material costs
  **$ 1,000,000 annual material costs × 12% reduction = $ 120,000 savings/year**
- 10% decrease in product weight
  **100 kg/unit × 10% reduction = 10 kg/unit saved**
- 8% increase in product performance
  **100 units/year × 8% increase = 8 additional units/year**
- 15% reduction in material waste
  **10,000 kg/year × 15% reduction = 1,500 kg saved/year**

**Success Metrics:**
- Material cost savings
- Product weight reduction
- Product performance improvement
- Material waste reduction

**Risk Assessment:**
- Integration challenges with existing CAD systems
- Data quality and availability
- Training and adoption by design teams

**Long-term Evolution:**
- Integration with emerging technologies (e.g., nanomaterials) for enhanced material selection and optimization.
- Expansion to other product development stages (e.g., prototyping, testing).

---

**'''

# Display logo and title inline
st.markdown(f'''
<div style="display:flex; align-items:center; margin-bottom:15px">
    <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
    <div>
        <h1 style="font-size:2.2rem; margin:0; padding:0">{solution_name_clean.replace('_', ' ').title()}</h1>
        <p style="font-size:1.1rem; color:gray; margin:0; padding:0">Fivetran and Cortex-powered Streamlit in Snowflake data application for Manufacturing</p>
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
            "challenge": "Product designers and materials engineers manually review hundreds of material properties and performance specifications daily, spending 4+ hours analyzing density, Young's modulus, and cost data to optimize material selection for weight reduction and performance improvement.",
            "solution": "Autonomous material optimization workflow that analyzes material properties databases, CAD system integration data, and performance metrics to generate AI-driven material recommendations with cost savings, weight reduction, and performance improvement predictions."
        },
        "Optimization Opportunities": {
            "challenge": "Materials engineers spend 3+ hours daily manually identifying inefficiencies in material selection processes, waste reduction opportunities, and CAD system integration gaps across diverse manufacturing product lines.",
            "solution": "AI-powered material optimization analysis that automatically detects material selection inefficiencies, waste reduction opportunities, and CAD integration improvements with specific implementation recommendations for Autodesk Inventor, SolidWorks, and Siemens NX systems."
        },
        "Financial Impact": {
            "challenge": "Manufacturing financial analysts manually calculate complex ROI metrics across material costs and product performance improvements, requiring 3+ hours of cost modeling to assess material optimization impact on production efficiency.",
            "solution": "Automated manufacturing financial analysis that calculates comprehensive ROI, identifies material cost reduction opportunities across product lifecycle stages, and projects performance improvement benefits with detailed manufacturing economics forecasting."
        },
        "Strategic Recommendations": {
            "challenge": "Chief Operating Officers spend hours manually analyzing advanced manufacturing trends and developing strategic roadmaps for material science innovation and next-generation manufacturing technology integration.",
            "solution": "Strategic manufacturing intelligence workflow that analyzes competitive advantages against traditional material selection methods, identifies emerging materials integration opportunities with nanomaterials, and creates prioritized advanced manufacturing transformation roadmaps."
        }
    }
    
    return focus_info.get(focus_area, {"challenge": "", "solution": ""})

def generate_insights_with_agent_workflow(data, focus_area, model_name, progress_placeholder=None):
    """Generate insights using AI agent workflow - Manufacturing Material Selection focused version"""
    
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
        total_materials = len(data)
        key_metrics = ["density", "youngs_modulus", "material_cost", "weight_reduction", "cost_savings", "performance_improvement"]
        available_metrics = [col for col in key_metrics if col in data.columns]
        
        # Calculate enhanced manufacturing data insights
        avg_weight_reduction = data['weight_reduction'].mean() if 'weight_reduction' in data.columns else 0
        avg_cost_savings = data['cost_savings'].mean() if 'cost_savings' in data.columns else 0
        lifecycle_stages = len(data['product_lifecycle_stage'].unique()) if 'product_lifecycle_stage' in data.columns else 0
        cad_systems = len(data['cad_system'].unique()) if 'cad_system' in data.columns else 0
        recommended_materials = len(data[data['material_selection_recommendation'] == 'Recommended']) if 'material_selection_recommendation' in data.columns else 0
        
        # Define enhanced agent workflows for each focus area
        if focus_area == "Overall Performance":
            steps = [
                ("Material Properties Data Initialization", 15, f"Loading comprehensive material properties dataset with enhanced validation across {total_materials} materials and {lifecycle_stages} product lifecycle stages", f"Connected to {len(available_metrics)} material metrics across {len(data.columns)} total manufacturing data dimensions"),
                ("Material Optimization Performance Assessment", 35, f"Advanced calculation of material selection indicators with weight and cost analysis (avg weight reduction: {avg_weight_reduction:.1f}%)", f"Computed material metrics: {avg_weight_reduction:.1f}% avg weight reduction, ${avg_cost_savings:.0f} avg cost savings, {recommended_materials} recommended materials"),
                ("Manufacturing Pattern Recognition", 55, f"Sophisticated identification of material performance patterns with CAD system correlation analysis across {cad_systems} CAD platforms", f"Detected significant patterns in {len(data['designer_skill_level'].unique()) if 'designer_skill_level' in data.columns else 'N/A'} designer skill levels with material optimization analysis completed"),
                ("AI Material Intelligence Processing", 75, f"Processing comprehensive manufacturing data through {model_name} with advanced reasoning for material selection optimization insights", f"Enhanced AI analysis of material selection effectiveness across {total_materials} manufacturing materials completed"),
                ("Manufacturing Optimization Report Compilation", 100, f"Professional material selection analysis with evidence-based recommendations and actionable optimization insights ready", f"Comprehensive material performance report with {len(available_metrics)} manufacturing metrics analysis and material selection recommendations generated")
            ]
            
        elif focus_area == "Optimization Opportunities":
            avg_waste_reduction = data['waste_reduction'].mean() if 'waste_reduction' in data.columns else 0
            
            steps = [
                ("Material Optimization Data Preparation", 12, f"Advanced loading of manufacturing material selection data with enhanced validation across {total_materials} materials for efficiency improvement identification", f"Prepared {lifecycle_stages} lifecycle stages, {cad_systems} CAD systems for optimization analysis with {avg_waste_reduction:.1f}% avg waste reduction"),
                ("Material Selection Inefficiency Detection", 28, f"Sophisticated analysis of material properties and CAD integration workflows with evidence-based inefficiency identification", f"Identified optimization opportunities across {lifecycle_stages} product stages with material selection gaps and CAD integration issues"),
                ("Manufacturing Correlation Analysis", 45, f"Enhanced examination of relationships between material properties, designer experience, and optimization outcomes", f"Analyzed correlations between material characteristics and selection success across {total_materials} manufacturing materials"),
                ("CAD System Integration Optimization", 65, f"Comprehensive evaluation of material selection integration with existing Autodesk Inventor, SolidWorks, and Siemens NX CAD platforms", f"Assessed integration opportunities across {len(data.columns)} data points and CAD system material optimization needs"),
                ("AI Manufacturing Optimization Intelligence", 85, f"Generating advanced material selection recommendations using {model_name} with manufacturing reasoning and CAD implementation strategies", f"AI-powered material optimization strategy across {lifecycle_stages} product stages and manufacturing improvements completed"),
                ("Material Strategy Finalization", 100, f"Professional material optimization report with prioritized implementation roadmap and manufacturing efficiency impact analysis ready", f"Comprehensive optimization strategy with {len(available_metrics)} performance improvement areas and manufacturing implementation plan generated")
            ]
            
        elif focus_area == "Financial Impact":
            avg_material_cost = data['material_cost'].mean() if 'material_cost' in data.columns else 0
            total_cost_savings = data['cost_savings'].sum() if 'cost_savings' in data.columns else 0
            
            steps = [
                ("Manufacturing Financial Data Integration", 15, f"Advanced loading of material cost data and manufacturing financial metrics with enhanced validation across {total_materials} materials", f"Integrated manufacturing financial data: ${avg_material_cost:.0f} avg material cost, ${total_cost_savings:,.0f} total cost savings across material portfolio"),
                ("Material Cost-Benefit Calculation", 30, f"Sophisticated ROI metrics calculation with weight reduction analysis and manufacturing efficiency enhancement", f"Computed comprehensive financial analysis: material costs, weight optimization benefits, and ${total_cost_savings:,.0f} manufacturing cost optimization"),
                ("Product Performance Financial Assessment", 50, f"Enhanced analysis of manufacturing revenue impact with performance improvement metrics and material cost correlation analysis", f"Assessed financial implications: {avg_weight_reduction:.1f}% weight reduction with {recommended_materials} optimized material selections driving cost efficiency"),
                ("Manufacturing Portfolio Efficiency Analysis", 70, f"Comprehensive evaluation of resource allocation efficiency across material types with lifecycle cost optimization", f"Analyzed manufacturing efficiency: {lifecycle_stages} product stages with material cost reduction and performance optimization opportunities identified"),
                ("AI Manufacturing Financial Modeling", 90, f"Advanced material cost projections and manufacturing ROI calculations using {model_name} with comprehensive manufacturing cost-benefit analysis", f"Enhanced financial impact analysis and forecasting across {len(available_metrics)} manufacturing financial metrics completed"),
                ("Manufacturing Economics Report Generation", 100, f"Professional manufacturing financial impact analysis with detailed material optimization ROI calculations and cost forecasting ready", f"Comprehensive manufacturing financial report with ${total_cost_savings:,.0f} cost optimization analysis and material selection strategy generated")
            ]
            
        elif focus_area == "Strategic Recommendations":
            optimization_effectiveness_score = (avg_weight_reduction + avg_cost_savings/10) if avg_weight_reduction > 0 else 0
            
            steps = [
                ("Manufacturing Technology Assessment", 15, f"Advanced loading of advanced manufacturing context with competitive positioning analysis across {total_materials} materials and {lifecycle_stages} product lifecycle stages", f"Analyzed manufacturing technology landscape: {lifecycle_stages} lifecycle stages, {cad_systems} CAD systems, comprehensive material science competitive assessment completed"),
                ("Material Science Competitive Advantage Analysis", 30, f"Sophisticated evaluation of competitive positioning against traditional material selection methods with AI-powered optimization effectiveness", f"Assessed competitive advantages: {optimization_effectiveness_score:.1f}% optimization effectiveness, {avg_cost_savings:.0f} cost savings vs traditional material selection methods"),
                ("Advanced Materials Technology Integration", 50, f"Enhanced analysis of integration opportunities with nanomaterials, advanced composites, and emerging manufacturing technologies across {len(data.columns)} material data dimensions", f"Identified strategic technology integration: nanomaterial applications, advanced composite materials, smart manufacturing opportunities"),
                ("Digital Manufacturing Strategy Development", 70, f"Comprehensive development of prioritized advanced manufacturing roadmap with evidence-based material science innovation adoption strategies", f"Created sequenced implementation plan across {lifecycle_stages} product development areas with emerging materials technology integration opportunities"),
                ("AI Manufacturing Strategic Processing", 85, f"Advanced material science strategic recommendations using {model_name} with long-term competitive positioning and advanced manufacturing analysis", f"Enhanced strategic analysis with material optimization competitive positioning and manufacturing transformation roadmap completed"),
                ("Advanced Manufacturing Report Generation", 100, f"Professional advanced manufacturing transformation roadmap with competitive analysis and material science innovation plan ready for COO executive review", f"Comprehensive strategic report with {lifecycle_stages}-stage implementation plan and material science competitive advantage analysis generated")
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
    key_metrics = ["density", "youngs_modulus", "poissons_ratio", "material_cost", "material_weight", "product_performance", "material_waste", "designer_experience", "material_selection_score", "material_optimization_score", "cost_savings", "weight_reduction", "performance_improvement", "waste_reduction"]
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
    categorical_options = ["material_id", "material_name", "product_id", "product_name", "product_description", "designer_id", "designer_name", "cad_system", "cad_file_name", "designer_skill_level", "product_lifecycle_stage", "product_lifecycle_status", "material_selection_recommendation", "material_optimization_recommendation"]
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
        For the Overall Performance analysis of MaterialMind:
        1. Provide a comprehensive analysis of the material selection and optimization system using weight reduction, cost savings, and performance improvement metrics
        2. Identify significant patterns in material properties (density, Young's modulus, Poisson's ratio) and their correlation with product performance
        3. Highlight 3-5 key manufacturing metrics that best indicate material optimization effectiveness (weight reduction percentages, cost savings, waste reduction)
        4. Discuss both strengths and areas for improvement in the AI-powered material selection process
        5. Include 3-5 actionable insights for improving material selection decisions based on the data
        
        Structure your response with these manufacturing-focused sections:
        - Material Optimization Insights (5 specific insights with supporting material property data)
        - Performance Optimization Trends (3-4 significant trends in weight reduction and performance improvement)
        - Material Selection Recommendations (3-5 data-backed recommendations for improving material choices)
        - Implementation Steps (3-5 concrete next steps for product designers and materials engineers)
        """,
        
        "Optimization Opportunities": """
        For the Optimization Opportunities analysis of MaterialMind:
        1. Focus specifically on areas where material selection accuracy can be improved
        2. Identify inefficiencies in material waste, underperforming material recommendations, and CAD system integration
        3. Analyze correlations between material properties, designer experience levels, and optimization outcomes
        4. Prioritize optimization opportunities based on potential impact on weight reduction and cost savings
        5. Suggest specific technical or process improvements for integration with existing CAD systems
        
        Structure your response with these manufacturing-focused sections:
        - Material Selection Optimization Priorities (3-5 areas with highest cost and weight reduction potential)
        - Engineering Impact Analysis (quantified benefits of addressing each opportunity in terms of performance metrics)
        - CAD Implementation Strategy (specific steps for design teams to implement each optimization)
        - CAD System Integration Recommendations (specific technical changes needed for seamless integration with Autodesk Inventor, SolidWorks, and Siemens NX)
        - Manufacturing Risk Assessment (potential challenges for production teams and how to mitigate them)
        """,
        
        "Financial Impact": """
        For the Financial Impact analysis of MaterialMind:
        1. Focus on cost-benefit analysis and ROI in manufacturing terms (material cost vs. performance gains)
        2. Quantify financial impacts through material cost savings, waste reduction, and performance improvements
        3. Identify cost savings opportunities across different product lifecycle stages
        4. Analyze resource allocation efficiency across different material types and properties
        5. Project future financial outcomes based on improved material selection accuracy and expanding to new materials
        
        Structure your response with these manufacturing-focused sections:
        - Material Cost Analysis (breakdown of material costs and potential savings by material type)
        - Production Efficiency Impact (how improved material selection affects manufacturing costs and throughput)
        - Manufacturing ROI Calculation (specific calculations showing return on investment in terms of material cost reduction)
        - Waste Reduction Opportunities (specific areas to reduce material waste and associated costs)
        - Production Cost Forecasting (projections based on improved material optimization metrics)
        """,
        
        "Strategic Recommendations": """
        For the Strategic Recommendations analysis of MaterialMind:
        1. Focus on long-term strategic implications for advanced manufacturing and material science
        2. Identify competitive advantages against traditional material selection approaches
        3. Suggest new directions for AI integration with emerging materials (e.g., nanomaterials) and production technologies
        4. Connect recommendations to broader manufacturing goals of reducing costs and improving product performance
        5. Provide a material innovation roadmap with prioritized initiatives
        
        Structure your response with these manufacturing-focused sections:
        - Manufacturing Technology Context (how MaterialMind fits into broader digital manufacturing transformation)
        - Engineering Competitive Advantage Analysis (how to maximize performance advantages compared to traditional material selection methods)
        - Material Science Strategic Priorities (3-5 high-impact strategic initiatives for improving material selection)
        - Advanced Materials Integration Vision (how to evolve MaterialMind with nanomaterials and other emerging materials over 1-3 years)
        - Product Development Transformation Roadmap (sequenced steps for expanding to other product development stages like prototyping and testing)
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

categorical_cols = [col for col in ["material_id", "material_name", "product_id", "product_name", "product_description", "designer_id", "designer_name", "cad_system", "cad_file_name", "designer_skill_level", "product_lifecycle_stage", "product_lifecycle_status", "material_selection_recommendation", "material_optimization_recommendation"] if col in data.columns]
numeric_cols = [col for col in ["density", "youngs_modulus", "poissons_ratio", "material_cost", "material_weight", "product_performance", "material_waste", "designer_experience", "material_selection_score", "material_optimization_score", "cost_savings", "weight_reduction", "performance_improvement", "waste_reduction"] if col in data.columns]
date_cols = [col for col in ["material_selection_date", "material_optimization_date"] if col in data.columns]

sample_cols = data.columns.tolist()
numeric_candidates = [col for col in sample_cols if data[col].dtype in ['float64', 'int64'] and 'id' not in col.lower()]
date_candidates = [col for col in sample_cols if 'date' in col.lower() or 'timestamp' in col.lower()]
cat_candidates = [col for col in sample_cols if data[col].dtype == 'object' and data[col].nunique() < 1000]

# Four tabs - with Metrics as the first tab (Tab 0)
tabs = st.tabs(["📊 Metrics", "✨ AI Insights", "📁 Insights History", "🔍 Data Explorer"])

# Metrics Tab (Tab 0)
with tabs[0]:
    st.header("Material Selection & Optimization Metrics")
    
    # Overview metrics row - 4 KPIs
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate metrics from the data
    avg_weight_reduction = data['weight_reduction'].mean() if 'weight_reduction' in data.columns else 0
    avg_cost_savings = data['cost_savings'].mean() if 'cost_savings' in data.columns else 0
    avg_performance_improvement = data['performance_improvement'].mean() if 'performance_improvement' in data.columns else 0
    avg_waste_reduction = data['waste_reduction'].mean() if 'waste_reduction' in data.columns else 0
    
    with col1:
        with st.container(border=True):
            st.metric(
                "Avg Weight Reduction", 
                f"{avg_weight_reduction:.2f}%",
                f"{(avg_weight_reduction - 10.0):.1f}pp" if avg_weight_reduction > 10.0 else f"{(avg_weight_reduction - 10.0):.1f}pp",
                help="Average percentage of weight reduction achieved. Target: 10%"
            )
    
    with col2:
        with st.container(border=True):
            st.metric(
                "Avg Cost Savings", 
                f"${avg_cost_savings:.2f}",
                f"{(avg_cost_savings - 120.0) / 120.0 * 100:.1f}%" if avg_cost_savings > 120.0 else f"{(avg_cost_savings - 120.0) / 120.0 * 100:.1f}%",
                help="Average cost savings per material selection. Target: $120.00"
            )
    
    with col3:
        with st.container(border=True):
            st.metric(
                "Avg Performance Improvement", 
                f"{avg_performance_improvement:.2f}%",
                f"{(avg_performance_improvement - 8.0):.1f}pp" if avg_performance_improvement > 8.0 else f"{(avg_performance_improvement - 8.0):.1f}pp",
                help="Average percentage of performance improvement. Target: 8%"
            )
    
    with col4:
        with st.container(border=True):
            st.metric(
                "Avg Waste Reduction", 
                f"{avg_waste_reduction:.2f}%",
                f"{(avg_waste_reduction - 15.0):.1f}pp" if avg_waste_reduction > 15.0 else f"{(avg_waste_reduction - 15.0):.1f}pp",
                help="Average percentage of material waste reduction. Target: 15%"
            )
    
    # Material Properties Section - 3 Material Metrics
    st.subheader("Material Properties")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container(border=True):
            avg_density = data['density'].mean() if 'density' in data.columns else 0
            st.metric("Avg Material Density", f"{avg_density:.2f} g/cm³")
        
    with col2:
        with st.container(border=True):
            avg_youngs_modulus = data['youngs_modulus'].mean() if 'youngs_modulus' in data.columns else 0
            st.metric("Avg Young's Modulus", f"{avg_youngs_modulus:.2f} MPa")
        
    with col3:
        with st.container(border=True):
            avg_poissons_ratio = data['poissons_ratio'].mean() if 'poissons_ratio' in data.columns else 0
            st.metric("Avg Poisson's Ratio", f"{avg_poissons_ratio:.4f}")
    
    # Create two columns for charts
    col1, col2 = st.columns(2)
    
    # Recommendation Status Distribution
    with col1:
        st.subheader("Recommendation Status Distribution")
        
        if 'material_selection_recommendation' in data.columns:
            status_counts = data['material_selection_recommendation'].value_counts().reset_index()
            status_counts.columns = ['status', 'count']
            
            # Status colors
            colors = {
                'Recommended': '#52BE80',  # Green
                'Not Recommended': '#E74C3C'   # Red
            }
            
            # Recommendation Status Distribution Chart
            chart = alt.Chart(status_counts).mark_bar().encode(
                x=alt.X('status:N', title='Material Selection Recommendation', axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Materials'),
                color=alt.Color('status:N', scale=alt.Scale(domain=list(colors.keys()), range=list(colors.values())))
            )
            
            text = chart.mark_text(
                align='center',
                baseline='bottom',
                dy=-15  # Increased space above bars
            ).encode(
                text='count:Q'
            )
            
            # Use the same approach for both charts
            st.altair_chart((chart + text).properties(height=300, width=500), use_container_width=True)
        else:
            st.write("Recommendation status data not available")
    
    # Material Optimization Distribution
    with col2:
        st.subheader("Material Optimization Distribution")
        
        if 'material_optimization_score' in data.columns:
            # Create bins for optimization scores
            bins = [0, 0.25, 0.5, 0.75, 1.0]
            labels = ['Low (0-0.25)', 'Medium-Low (0.25-0.5)', 'Medium-High (0.5-0.75)', 'High (0.75-1.0)']
            data['optimization_category'] = pd.cut(data['material_optimization_score'], bins=bins, labels=labels, include_lowest=True)
            
            optimization_counts = data['optimization_category'].value_counts().reset_index()
            optimization_counts.columns = ['category', 'count']
            
            # Material Optimization Distribution Chart
            chart = alt.Chart(optimization_counts).mark_bar().encode(
                x=alt.X('category:N', title='Optimization Score Level', sort=None, axis=alt.Axis(labelAngle=0)),
                y=alt.Y('count:Q', title='Number of Materials'),
                color=alt.Color('category:N', scale=alt.Scale(domain=labels, range=['#E74C3C', '#F4D03F', '#5DADE2', '#52BE80']))
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
            st.write("Material optimization score data not available")
    
    # Product Lifecycle Stage
    st.subheader("Product Lifecycle Stage Distribution")
    
    if 'product_lifecycle_stage' in data.columns:
        lifecycle_counts = data['product_lifecycle_stage'].value_counts().reset_index()
        lifecycle_counts.columns = ['stage', 'count']
        
        # Define lifecycle stage colors
        lifecycle_colors = {
            'Design': '#F4D03F',      # Yellow
            'Development': '#5DADE2', # Blue
            'Testing': '#52BE80',    # Green
            'Production': '#8E44AD'   # Purple
        }
        
        # Product Lifecycle Stage Chart
        chart = alt.Chart(lifecycle_counts).mark_bar().encode(
            x=alt.X('stage:N', title='Lifecycle Stage', axis=alt.Axis(labelAngle=0)),
            y=alt.Y('count:Q', title='Number of Products'),
            color=alt.Color('stage:N', scale=alt.Scale(domain=list(lifecycle_colors.keys()), range=list(lifecycle_colors.values())))
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
        st.write("Product lifecycle stage data not available")
    
    # Designer Metrics Section
    st.subheader("Designer Metrics")
    
    # Create 2 columns for designer metrics
    col1, col2 = st.columns(2)
    
    # Designer Skill Level Distribution
    with col1:
        st.subheader("Designer Skill Level Distribution")
        
        if 'designer_skill_level' in data.columns:
            skill_counts = data['designer_skill_level'].value_counts().reset_index()
            skill_counts.columns = ['skill_level', 'count']
            
            # Designer Skill Level Distribution Chart
            chart = alt.Chart(skill_counts).mark_bar().encode(
                y=alt.Y('skill_level:N', title='Skill Level', sort='-x'),
                x=alt.X('count:Q', title='Number of Designers'),
                color=alt.Color('skill_level:N', legend=None)
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
            st.write("Designer skill level data not available")
    
    # CAD System Distribution
    with col2:
        st.subheader("CAD System Distribution")
        
        if 'cad_system' in data.columns:
            cad_counts = data['cad_system'].value_counts().reset_index()
            cad_counts.columns = ['cad_system', 'count']
            
            # CAD System Distribution Chart
            chart = alt.Chart(cad_counts).mark_bar().encode(
                y=alt.Y('cad_system:N', title='CAD System', sort='-x'),
                x=alt.X('count:Q', title='Number of Users'),
                color=alt.Color('cad_system:N', legend=None)
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
            st.write("CAD system data not available")
    
    # Cost Savings vs Weight Reduction Quadrant Analysis
    st.subheader("Cost Savings vs Weight Reduction Quadrant Analysis")
    
    if 'cost_savings' in data.columns and 'weight_reduction' in data.columns:
        # Target values based on solution content
        target_cost_savings = 120.0
        target_weight_reduction = 10.0
        
        # Create a copy of the data with just the columns we need
        quadrant_data = data[['cost_savings', 'weight_reduction', 'material_name', 'material_selection_recommendation']].copy()
        
        # Calculate a performance score (optional, for coloring)
        quadrant_data['performance_score'] = (quadrant_data['cost_savings'] / target_cost_savings + 
                                             quadrant_data['weight_reduction'] / target_weight_reduction) / 2
        
        # Label quadrants
        quadrant_data['quadrant'] = 'Q3: Low savings, Low reduction'  # default
        
        # Q1: High savings, High reduction (optimal)
        mask_q1 = (quadrant_data['cost_savings'] >= target_cost_savings) & (quadrant_data['weight_reduction'] >= target_weight_reduction)
        quadrant_data.loc[mask_q1, 'quadrant'] = 'Q1: High savings, High reduction ✓'
        
        # Q2: Low savings, High reduction
        mask_q2 = (quadrant_data['cost_savings'] < target_cost_savings) & (quadrant_data['weight_reduction'] >= target_weight_reduction)
        quadrant_data.loc[mask_q2, 'quadrant'] = 'Q2: Low savings, High reduction'
        
        # Q4: High savings, Low reduction
        mask_q4 = (quadrant_data['cost_savings'] >= target_cost_savings) & (quadrant_data['weight_reduction'] < target_weight_reduction)
        quadrant_data.loc[mask_q4, 'quadrant'] = 'Q4: High savings, Low reduction'
        
        # Top performers - to highlight
        top_performers = quadrant_data.sort_values('performance_score', ascending=False).head(5)
        
        # Create reference lines for targets
        vline = alt.Chart(pd.DataFrame({'x': [target_cost_savings]})).mark_rule(
            color='gray', strokeDash=[5, 5]
        ).encode(x='x:Q')
        
        hline = alt.Chart(pd.DataFrame({'y': [target_weight_reduction]})).mark_rule(
            color='gray', strokeDash=[5, 5]
        ).encode(y='y:Q')
        
        # Annotations for quadrants
        text_data = pd.DataFrame({
            'cost_savings': [target_cost_savings/2, target_cost_savings*1.5, target_cost_savings/2, target_cost_savings*1.5],
            'weight_reduction': [target_weight_reduction*1.5, target_weight_reduction*1.5, target_weight_reduction/2, target_weight_reduction/2],
            'label': ['Q2', 'Q1 (Optimal)', 'Q3', 'Q4']
        })
        
        text_chart = alt.Chart(text_data).mark_text(
            align='center',
            baseline='middle',
            fontSize=14,
            opacity=0.7
        ).encode(
            x='cost_savings:Q',
            y='weight_reduction:Q',
            text='label:N'
        )
        
        # Main scatter plot with opacity to reduce visual clutter
        scatter = alt.Chart(quadrant_data).mark_circle(
            size=60,
            opacity=0.6
        ).encode(
            x=alt.X('cost_savings:Q', 
                   title='Cost Savings ($)',
                   scale=alt.Scale(domain=[0, max(quadrant_data['cost_savings'])*1.05])),
            y=alt.Y('weight_reduction:Q', 
                   title='Weight Reduction (%)',
                   scale=alt.Scale(domain=[0, max(quadrant_data['weight_reduction'])*1.05])),
            color=alt.Color('quadrant:N', 
                          legend=alt.Legend(title="Performance Quadrant")),
            tooltip=['material_name', 'cost_savings', 'weight_reduction', 
                    'material_selection_recommendation', 'quadrant']
        )
        
        # Highlight top performers
        highlight = alt.Chart(top_performers).mark_circle(
            size=100,
            stroke='black',
            strokeWidth=2
        ).encode(
            x='cost_savings:Q',
            y='weight_reduction:Q',
            tooltip=['material_name', 'cost_savings', 'weight_reduction', 
                   'material_selection_recommendation', 'performance_score']
        )
        
        # Target labels
        target_labels = alt.Chart(pd.DataFrame({
            'x': [target_cost_savings],
            'y': [0],
            'text': [f'Target: ${target_cost_savings}']
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
            'y': [target_weight_reduction],
            'text': [f'Target: {target_weight_reduction}%']
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
        q1_pct = (quadrant_data['quadrant'] == 'Q1: High savings, High reduction ✓').mean() * 100
        
        # Show chart and metrics
        st.altair_chart(chart, use_container_width=True)
        
        # Show quadrant distribution
        st.markdown(f"""
        **Quadrant Distribution:**
        - **Q1 (Optimal):** {q1_pct:.1f}% of materials achieve both target cost savings and weight reduction
        - **Top materials are highlighted with black outline**
        """)
        
        # Show top 5 materials in a small table
        st.subheader("Top 5 Materials by Overall Performance")
        top_display = top_performers[['material_name', 'cost_savings', 'weight_reduction', 'quadrant']].reset_index(drop=True)
        st.dataframe(top_display, hide_index=True)
        
    else:
        st.write("Cost savings or weight reduction data not available")

# AI Insights tab
with tabs[1]:
    st.subheader("✨ AI-Powered Insights with Agent Workflows")
    st.markdown("**Experience behind-the-scenes AI agent processing for each material selection analysis focus area**")
    
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
                st.success(f"🎉 {focus_area} Agent completed with real manufacturing data analysis!")
                
                # Show report in expandable section
                with st.expander(f"📋 Generated {focus_area} Report (Real Manufacturing Material Data)", expanded=True):
                    st.markdown(f"""
                    <div class="agent-report-header">
                        <strong>{focus_area} Report - AI-Generated Material Selection Analysis</strong><br>
                        <small>Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</small><br>
                        <small>Data Source: Live Snowflake Material Optimization Analysis</small><br>
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