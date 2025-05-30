import streamlit as st
from snowflake.snowpark.context import get_active_session
import pandas as pd
import time
import re

# Define available models as strings
MODELS = [
    "claude-4-sonnet", "claude-3-7-sonnet", "claude-3-5-sonnet", "llama3.1-8b", "llama3.1-70b", "llama4-maverick", "llama4-scout", "llama3.2-1b", "snowflake-llama-3.1-405b", "snowflake-llama-3.3-70b", "mistral-large2", "mistral-7b", "deepseek-r1", "snowflake-arctic", "reka-flash", "jamba-instruct", "gemma-7b"
]

QBR_TEMPLATES = ["Standard QBR", "Executive Summary Only", "Technical Deep Dive", "Customer Success Focus"]
VIEW_TYPES = ["Sales View", "Executive View", "Technical View", "Customer Success View"]

# Initialize Snowflake session
try:
    session = get_active_session()
except:
    st.error("Could not get active Snowflake session. Please check your connection.")
    st.stop()

def build_prompt(company_name, company_data, historical_data, template_type, view_type):
    """Builds a prompt for QBR generation with template modifications and view-specific emphasis."""

    template_instructions = {
        "Standard QBR": """
        This is a full Quarterly Business Review (QBR) covering all key aspects, including health score analysis, adoption metrics, customer satisfaction, and strategic recommendations.
        """,
        "Executive Summary Only": """
        This QBR should be concise and high-level, focusing only on key insights, major wins, critical challenges, and high-level recommendations.
        Exclude deep technical details, adoption trends, and granular product feature analysis.
        """,
        "Technical Deep Dive": """
        This QBR should focus on technical aspects such as system architecture, integrations, API usage, performance metrics, and technical challenges.
        Prioritize technical success metrics, potential optimizations, and engineering recommendations.
        Minimize business-level overviews and executive summaries.
        """,
        "Customer Success Focus": """
        This QBR should emphasize customer engagement, product adoption, support trends, and user satisfaction.
        Focus on training needs, adoption blockers, support ticket patterns, and customer success strategies.
        Minimize in-depth technical or executive-level details.
        """
    }

    view_type_instructions = {
        "Sales View": """
        This QBR should focus on revenue impact, upsell opportunities, contract value, expansion potential, and risk mitigation.
        Prioritize key financial metrics, deal health, and strategic recommendations for account growth.
        Minimize highly technical discussions unless relevant for deal positioning.
        """,
        "Executive View": """
        This QBR should provide a high-level strategic overview, emphasizing business outcomes, financial impact, and alignment with company goals.
        Keep details concise, use bullet points, and focus on key wins, challenges, and high-level recommendations.
        Minimize operational or highly technical details.
        """,
        "Technical View": """
        This QBR should provide a deep dive into system performance, architecture, integrations, and product adoption from a technical perspective.
        Prioritize API usage, reliability metrics, infrastructure considerations, and upcoming technical improvements.
        Minimize business-oriented insights unless relevant to product engineering.
        """,
        "Customer Success View": """
        This QBR should focus on customer satisfaction, adoption trends, support tickets, training needs, and customer engagement.
        Prioritize recommendations for improving retention, reducing churn, and addressing adoption blockers.
        Minimize purely financial or highly technical content unless relevant for success strategy.
        """
    }

    view_based_sections = {
        "Sales View": """
        1. Account Health Summary  
        2. Revenue & Expansion Opportunities  
        3. Usage Trends & Adoption Insights  
        4. Competitive Positioning  
        5. Strategic Sales Recommendations  
        """,
        "Executive View": """
        1. Key Business Outcomes  
        2. ROI & Financial Impact  
        3. Adoption & Customer Engagement  
        4. Strategic Roadmap Alignment  
        5. High-Level Recommendations  
        """,
        "Technical View": """
        1. System Performance & API Usage  
        2. Infrastructure & Security Considerations  
        3. Feature Adoption & Implementation Status  
        4. Engineering Challenges & Optimization Strategies  
        5. Technical Roadmap & Upcoming Enhancements  
        """,
        "Customer Success View": """
        1. Customer Engagement & Satisfaction Metrics  
        2. Product Adoption & User Retention  
        3. Support Trends & Resolution Efficiency  
        4. Training & Enablement Opportunities  
        5. Customer Success Strategy & Next Steps  
        """
    }

    # Format the company data as a dictionary
    if isinstance(company_data, pd.DataFrame) and not company_data.empty:
        company_data_dict = company_data.iloc[0].to_dict()
        
        # Format each key-value pair with proper formatting and handling for different data types
        formatted_lines = []
        
        # Order important metrics first
        priority_metrics = [
            "COMPANY_NAME", "INDUSTRY", "SIZE", "DEAL_STAGE", "QBR_QUARTER", "QBR_YEAR",
            "HEALTH_SCORE", "CONTRACT_VALUE", "CSAT_SCORE", "ACTIVE_USERS", 
            "FEATURE_ADOPTION_RATE", "RENEWAL_PROBABILITY", "TICKET_VOLUME",
            "CONTRACT_START_DATE", "CONTRACT_EXPIRATION_DATE"
        ]
        
        # Add priority metrics first
        for key in priority_metrics:
            if key in company_data_dict:
                value = company_data_dict[key]
                if pd.notna(value):
                    # Format values based on type
                    if key == "CONTRACT_VALUE" or key == "ESTIMATED_ROI_VALUE":
                        formatted_lines.append(f"{key}: ${value:,.2f}")
                    elif key == "HEALTH_SCORE" or key == "CSAT_SCORE" or key == "FEATURE_ADOPTION_RATE" or key == "RENEWAL_PROBABILITY" or key == "SLA_COMPLIANCE_RATE":
                        formatted_lines.append(f"{key}: {value:.2f}")
                    elif key == "CONTRACT_START_DATE" or key == "CONTRACT_EXPIRATION_DATE":
                        formatted_lines.append(f"{key}: {value}")
                    else:
                        formatted_lines.append(f"{key}: {value}")
        
        # Add remaining metrics
        for key, value in company_data_dict.items():
            if key not in priority_metrics and pd.notna(value):
                # Format values based on type
                if key == "CONTRACT_VALUE" or key == "ESTIMATED_ROI_VALUE":
                    formatted_lines.append(f"{key}: ${value:,.2f}")
                elif key == "HEALTH_SCORE" or key == "CSAT_SCORE" or key == "FEATURE_ADOPTION_RATE" or key == "RENEWAL_PROBABILITY" or key == "SLA_COMPLIANCE_RATE":
                    formatted_lines.append(f"{key}: {value:.2f}")
                elif key == "CONTRACT_START_DATE" or key == "CONTRACT_EXPIRATION_DATE":
                    formatted_lines.append(f"{key}: {value}")
                else:
                    formatted_lines.append(f"{key}: {value}")
        
        company_data_formatted = "\n".join(formatted_lines)
    else:
        company_data_formatted = "No company data available"

    qbr_type_instructions = template_instructions.get(template_type, "")
    view_specific_instructions = view_type_instructions.get(view_type, "")
    dynamic_sections = view_based_sections.get(view_type, "1. Executive Summary\n2. Business Impact\n3. Strategic Recommendations")

    # Create a more explicit prompt ensuring specific company focus
    prompt = f"""
    You are an expert business analyst creating a Quarterly Business Review (QBR) for {company_name}.
    Generate a {template_type} QBR ONLY for this specific company using the provided data.
    This QBR is for Q{company_data.iloc[0]['QBR_QUARTER']} {company_data.iloc[0]['QBR_YEAR']}.

    {qbr_type_instructions}

    {view_specific_instructions}

    Company Data for {company_name}:
    {company_data_formatted}

    Historical Data for {company_name}:
    {historical_data if historical_data else 'No historical data available for this specific company'}

    Structure the QBR based on {view_type}, prioritizing the most relevant insights for {company_name} specifically.
    
    Use the following section structure:
    {dynamic_sections}

    Format the QBR professionally with clear section headers and bullet points for key insights about {company_name}.
    
    Important instructions:
    1. All data, insights, and recommendations should be specific to {company_name} only.
    2. DO NOT include any generic or placeholder text like "[Insert Company Name]" or "[Insert QBR Quarter]".
    3. DO NOT include data about other companies or average data across all accounts.
    4. Use the actual metrics provided for {company_name} in the company data.
    5. In the header, clearly specify this is a Q{company_data.iloc[0]['QBR_QUARTER']} {company_data.iloc[0]['QBR_YEAR']} QBR for {company_name}.
    """

    return prompt

def get_company_data(company_name):
    """Retrieve company data from Snowflake."""
    try:
        metrics_query = """
        SELECT 
            COMPANY_NAME,
            COMPANY_ID,
            INDUSTRY,
            SIZE,
            QBR_QUARTER,
            QBR_YEAR,
            DEAL_STAGE,
            HEALTH_SCORE,
            CONTRACT_VALUE,
            CSAT_SCORE,
            ACTIVE_USERS,
            FEATURE_ADOPTION_RATE,
            TICKET_VOLUME,
            RENEWAL_PROBABILITY,
            CONTRACT_START_DATE,
            CONTRACT_EXPIRATION_DATE,
            PAIN_POINTS_DOCUMENTED,
            SUCCESS_CRITERIA_DEFINED,
            AVG_RESOLUTION_TIME_HOURS,
            SLA_COMPLIANCE_RATE,
            CHAMPION_IDENTIFIED,
            CHAMPION_LEVEL,
            CHAMPION_ENGAGEMENT_SCORE,
            ECONOMIC_BUYER_IDENTIFIED,
            EXECUTIVE_SPONSOR_ENGAGED,
            DECISION_MAKER_LEVEL,
            DECISION_TIMELINE_CLEAR,
            DECISION_PROCESS_DOCUMENTED,
            UPSELL_OPPORTUNITY,
            ESTIMATED_ROI_VALUE,
            ROI_CALCULATED,
            URGENCY_LEVEL,
            PAIN_IMPACT_LEVEL,
            COMPETITIVE_SITUATION,
            COMPETITIVE_POSITION,
            CUSTOM_INTEGRATIONS,
            PENDING_FEATURE_REQUESTS,
            SUCCESS_METRICS_DEFINED,
            TECHNICAL_CRITERIA_MET,
            BUSINESS_CRITERIA_MET,
            NEXT_STEPS_DEFINED
        FROM QBR_RECORDS
        WHERE COMPANY_NAME = ?
        """
        return session.sql(metrics_query, params=[company_name]).to_pandas()
    except Exception as e:
        st.error(f"Error retrieving company data: {str(e)}")
        return None

def get_historical_data(company_name):
    """Get historical QBR data for the company."""
    try:
        # Get previous QBRs for this company
        query = """
        SELECT 
            QBR_QUARTER,
            QBR_YEAR,
            HEALTH_SCORE,
            CONTRACT_VALUE, 
            CSAT_SCORE,
            ACTIVE_USERS,
            FEATURE_ADOPTION_RATE,
            TICKET_VOLUME,
            RENEWAL_PROBABILITY,
            DEAL_STAGE
        FROM QBR_RECORDS
        WHERE COMPANY_NAME = ?
        AND (
            QBR_YEAR < (SELECT MAX(QBR_YEAR) FROM QBR_RECORDS WHERE COMPANY_NAME = ?) 
            OR (
                QBR_YEAR = (SELECT MAX(QBR_YEAR) FROM QBR_RECORDS WHERE COMPANY_NAME = ?) 
                AND QBR_QUARTER < (SELECT MAX(QBR_QUARTER) FROM QBR_RECORDS WHERE COMPANY_NAME = ? AND QBR_YEAR = (SELECT MAX(QBR_YEAR) FROM QBR_RECORDS WHERE COMPANY_NAME = ?))
            )
        )
        ORDER BY QBR_YEAR DESC, QBR_QUARTER DESC
        LIMIT 2
        """
        
        results = session.sql(query, params=[company_name, company_name, company_name, company_name, company_name]).to_pandas()
        
        if results.empty:
            return None
        
        # Format results into context
        historical_data = []
        for _, row in results.iterrows():
            historical_info = [f"Previous QBR (Q{row['QBR_QUARTER']} {row['QBR_YEAR']}):"]
            for col in results.columns:
                if col not in ['QBR_QUARTER', 'QBR_YEAR'] and pd.notna(row[col]):
                    if col == 'CONTRACT_VALUE':
                        historical_info.append(f"  - {col}: ${row[col]:,.2f}")
                    elif col in ['HEALTH_SCORE', 'CSAT_SCORE', 'FEATURE_ADOPTION_RATE', 'RENEWAL_PROBABILITY']:
                        historical_info.append(f"  - {col}: {row[col]:.2f}")
                    else:
                        historical_info.append(f"  - {col}: {row[col]}")
            
            historical_data.append("\n".join(historical_info))
        
        return "\n\n".join(historical_data)
        
    except Exception as e:
        st.error(f"Error retrieving historical data: {str(e)}")
        return None

def generate_qbr_content(company_name, company_data, historical_data, template_type, view_type, selected_model):
    """Generate QBR content using Snowflake Cortex."""
    try:
        prompt = build_prompt(company_name, company_data, historical_data, template_type, view_type)
        cortex_query = """
        SELECT SNOWFLAKE.CORTEX.COMPLETE(
            ?,
            ?
        ) as response
        """
        response = session.sql(cortex_query, params=[selected_model, prompt]).collect()[0][0]
        return response
    except Exception as e:
        st.error(f"Error generating QBR content: {str(e)}")
        return None

def display_metrics_dashboard(metrics_df):
    """Display simplified metrics dashboard with only the top row"""
    # Only show the top row of metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Health Score", 
            f"{metrics_df['HEALTH_SCORE'].iloc[0]:.1f}",
            delta=None
        )
    
    with col2:
        st.metric(
            "Contract Value", 
            f"${metrics_df['CONTRACT_VALUE'].iloc[0]:,.2f}",
            delta=None
        )
    
    with col3:
        st.metric(
            "CSAT Score", 
            f"{metrics_df['CSAT_SCORE'].iloc[0]:.1f}",
            delta=None
        )
    
    with col4:
        st.metric(
            "Active Users", 
            f"{int(metrics_df['ACTIVE_USERS'].iloc[0])}",
            delta=None
        )

def query_data(query, params=None):
    """Execute a query against Snowflake."""
    try:
        if params:
            return session.sql(query, params=params).to_pandas()
        else:
            return session.sql(query).to_pandas()
    except Exception as e:
        st.error(f"Error executing query: {str(e)}")
        return pd.DataFrame()

def main():
    st.set_page_config(layout="wide", page_title="Enterprise QBR Generator")
    
    # Initialize session state
    if 'qbr_history' not in st.session_state:
        st.session_state.qbr_history = []
    if 'page_number' not in st.session_state:
        st.session_state.page_number = 1
    if 'rows_per_page' not in st.session_state:
        st.session_state.rows_per_page = 10
    
    # Title and Description
    st.markdown(f'''
    <div style="display:flex; align-items:center; margin-bottom:15px">
        <img src="https://i.imgur.com/Og6gFnB.png" width="100" style="margin-right:15px">
        <div>
            <h1 style="font-size:2.2rem; margin:0; padding:0">Enterprise QBR Generator</h1>
            <p style="font-size:0.9rem; color:gray; margin:0; padding:0">Generate comprehensive, data-driven Quarterly Business Reviews using Fivetran and Snowflake Cortex. 
            This Streamlit in Snowflake Gen AI Data App combines sales data, support data, product data, 
            current metrics, and predictive insights to create instant, standardized, and actionable QBRs.</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    # Sidebar Configuration
    with st.sidebar:
        st.header("QBR Configuration")
        
        # Business Settings
        st.subheader("Business Settings")
        
        # Company Selection
        company_query = """
        SELECT DISTINCT COMPANY_NAME
        FROM QBR_RECORDS
        ORDER BY COMPANY_NAME
        """
        companies_df = session.sql(company_query).to_pandas()
        selected_company = st.selectbox(
            "Select Company",
            options=[""] + companies_df['COMPANY_NAME'].tolist(),
            help="Type to search for a specific company"
        )
        
        # Template Selection
        template_type = st.selectbox(
            "QBR Template",
            QBR_TEMPLATES
        )
        
        view_type = st.selectbox(
            "View Type",
            VIEW_TYPES
        )
        
        # Admin Settings
        st.subheader("Admin Settings")
        
        # Model Selection
        selected_model = st.selectbox(
            "Select Snowflake Cortex Model:",
            MODELS,
            help="Choose the LLM model for QBR generation"
        )
        
        # Advanced Options
        with st.expander("Advanced Options"):
            use_historical = st.checkbox(
                "Include Historical Data",
                help="Use previous QBRs for enhanced insights"
            )
            
            include_validation = st.checkbox(
                "Enable Data Validation",
                help="Add validation steps to the QBR process"
            )

        # Add spacing before branding text
        for _ in range(2):
            st.write("")

        # Branding Text (Above the logo)
        st.markdown(
            "<h4 style='text-align: center; font-weight: normal;'>Fivetran | Snowflake</h4>", 
            unsafe_allow_html=True
        )

        # Add spacing before logo
        for _ in range(1):
            st.write("")

        # Correct logo URL
        logo_url = "https://i.imgur.com/9lS8Y34.png"

        st.markdown(
            f"""
            <div style="display: flex; justify-content: center;">
                <img src="{logo_url}" width="150">
            </div>
            """,
            unsafe_allow_html=True
        )
    
    # Main Content Area
    tabs = st.tabs(["QBR Generation", "Historical QBRs", "Settings"])
    
    with tabs[0]:
        if selected_company:
            # Get and display company metrics
            company_data = get_company_data(selected_company)
            if company_data is not None and not company_data.empty:
                display_metrics_dashboard(company_data)
                
                # QBR Generation Button
                if st.button("Generate QBR"):
                    with st.spinner("Generating QBR..."):
                        # Get historical data if enabled
                        historical_data = None
                        if use_historical:
                            historical_data = get_historical_data(selected_company)
                        
                        # Generate QBR content with explicit company name
                        qbr_content = generate_qbr_content(
                            selected_company,  # Pass company name explicitly
                            company_data,
                            historical_data,
                            template_type,
                            view_type,
                            selected_model
                        )
                        
                        if qbr_content:
                            # Display generated QBR
                            st.header(f"Quarterly Business Review: {selected_company}")
                            st.write(qbr_content)
                            
                            # Add download button
                            st.download_button(
                                label="Download QBR",
                                data=qbr_content,
                                file_name=f"QBR_{selected_company}_{pd.Timestamp.now().strftime('%Y%m%d')}.md",
                                mime="text/markdown"
                            )
                            
                            # Save to history
                            st.session_state.qbr_history.append({
                                'company': selected_company,
                                'date': pd.Timestamp.now(),
                                'content': qbr_content,
                                'template': template_type,
                                'view_type': view_type,
                                'model': selected_model
                            })
            else:
                st.warning(f"No data available for {selected_company}. Please select another company.")
    
    with tabs[1]:
        if st.session_state.qbr_history:
            for qbr in reversed(st.session_state.qbr_history):
                template_type = qbr.get('template', 'Standard QBR')  # Default to "Standard QBR" if not found
                model_name = qbr.get('model', '')  # Get model name
                with st.expander(f"{qbr['company']} - {template_type} - {qbr['date'].strftime('%Y-%m-%d %H:%M')} ({model_name})"):
                    st.write(qbr['content'])
        else:
            st.info("No QBR history available")
    
    with tabs[2]:
        st.write("QBR Generation Settings")
        
        st.subheader("Snowflake Settings")
        # Get current session information
        try:
            # Get the current context information
            context_query = "SELECT CURRENT_DATABASE(), CURRENT_SCHEMA()"
            context_result = session.sql(context_query).collect()
            current_db = context_result[0][0] if context_result else "Not available"
            current_schema = context_result[0][1] if context_result else "Not available"
            
            st.write(f"**Database:** {current_db}")
            st.write(f"**Schema:** {current_schema}")
            st.write(f"**Table:** QBR_RECORDS")
            st.write(f"**Model:** {selected_model}")
        except Exception as e:
            st.error(f"Error retrieving Snowflake context: {str(e)}")
        
        # Data Explorer (replacing Test Company Search)
        st.subheader("🔍 Data Explorer")
        
        # Pagination controls
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.rows_per_page = st.slider("Rows per page", 5, 50, st.session_state.rows_per_page)
        
        with col2:
            st.session_state.page_number = st.number_input("Page", min_value=1, value=st.session_state.page_number)
        
        # Column selection
        with st.expander("Column Selection"):
            # Get all columns from the table
            all_columns_query = """
            SELECT COLUMN_NAME
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_NAME = 'QBR_RECORDS'
            ORDER BY ORDINAL_POSITION
            """
            columns_df = query_data(all_columns_query)
            
            if not columns_df.empty:
                all_columns = columns_df['COLUMN_NAME'].tolist()
                default_columns = [
                    "COMPANY_NAME", "INDUSTRY", "SIZE", "DEAL_STAGE", 
                    "HEALTH_SCORE", "CONTRACT_VALUE", "CSAT_SCORE", 
                    "ACTIVE_USERS", "QBR_QUARTER", "QBR_YEAR"
                ]
                # Find which default columns actually exist in all_columns
                default_columns = [col for col in default_columns if col in all_columns]
                
                selected_columns = st.multiselect(
                    "Select columns to display",
                    all_columns,
                    default=default_columns
                )
            else:
                selected_columns = []
                st.warning("Could not retrieve column information.")
        
        # Filtering options
        with st.expander("Filtering"):
            filter_options = st.multiselect(
                "Filter by",
                ["INDUSTRY", "SIZE", "DEAL_STAGE", "QBR_QUARTER", "QBR_YEAR"],
                default=[]
            )
            
            filter_conditions = []
            filter_params = []
            
            for filter_option in filter_options:
                if filter_option in all_columns:
                    # Get unique values for the filter
                    unique_values_query = f"""
                    SELECT DISTINCT {filter_option}
                    FROM QBR_RECORDS
                    ORDER BY {filter_option}
                    """
                    unique_values = query_data(unique_values_query)
                    
                    if not unique_values.empty:
                        filter_value = st.selectbox(
                            f"Select {filter_option}",
                            ["All"] + unique_values[filter_option].tolist()
                        )
                        
                        if filter_value != "All":
                            filter_conditions.append(f"{filter_option} = ?")
                            filter_params.append(filter_value)
        
        # Build and execute query
        if selected_columns:
            # Calculate pagination
            start = (st.session_state.page_number - 1) * st.session_state.rows_per_page
            
            # Build the query
            columns_str = ", ".join(selected_columns)
            query = f"SELECT {columns_str} FROM QBR_RECORDS"
            
            # Add filtering if conditions exist
            if filter_conditions:
                query += " WHERE " + " AND ".join(filter_conditions)
            
            # Add pagination
            query += f" LIMIT {st.session_state.rows_per_page} OFFSET {start}"
            
            # Get the count of all records (for pagination info)
            count_query = "SELECT COUNT(*) as count FROM QBR_RECORDS"
            if filter_conditions:
                count_query += " WHERE " + " AND ".join(filter_conditions)
            
            count_result = query_data(count_query, filter_params)
            total_records = count_result['COUNT'].iloc[0] if not count_result.empty else 0
            
            # Execute the main query
            results = query_data(query, filter_params)
            
            if not results.empty:
                st.dataframe(results, use_container_width=True)
                
                end = min(start + st.session_state.rows_per_page, total_records)
                st.caption(f"Showing {start+1} to {end} of {total_records} records")
                
                # Add navigation buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.session_state.page_number > 1:
                        if st.button("← Previous Page"):
                            st.session_state.page_number -= 1
                            st.experimental_rerun()
                
                with col2:
                    if end < total_records:
                        if st.button("Next Page →"):
                            st.session_state.page_number += 1
                            st.experimental_rerun()
            else:
                st.info("No records found matching the criteria.")
        else:
            st.warning("Please select at least one column to display.")

if __name__ == "__main__":
    main()