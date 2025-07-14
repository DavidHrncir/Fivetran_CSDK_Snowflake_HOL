# PricePulse – AI-driven Dynamic Pricing

![PricePulse](images/PricePulse.png)

A Fivetran and Cortex-powered Streamlit in Snowflake data application for Retail with advanced AI Agent Workflows.

## Overview

PricePulse is an AI-driven dynamic pricing system that helps retailers maximize profits through real-time price optimization. This Streamlit in Snowflake data application helps pricing managers, inventory managers, and marketing teams respond quickly to market fluctuations, reducing overstocking and stockouts while increasing revenue and customer satisfaction.

The application features sophisticated AI Agent Workflows that provide transparent, step-by-step analysis of retail pricing data, transforming complex market insights into actionable pricing strategies and revenue optimization recommendations. Each analysis focus area operates through specialized mini-agents that simulate the decision-making process of experienced retail pricing professionals and merchandising specialists.

The application utilizes a synthetic retail dataset that simulates data from point of sale systems, customer relationship management platforms, and inventory management systems. This synthetic data is moved into Snowflake using a custom connector built with the Fivetran Connector SDK, enabling reliable and efficient data pipelines for retail analytics.

## AI Agent Workflows

### Agent Architecture Overview

PricePulse employs a sophisticated multi-agent architecture designed specifically for retail pricing analysis. Each focus area operates through specialized AI agents that break down complex pricing optimization tasks into transparent, sequential steps that mirror the thought processes of experienced retail pricing professionals and merchandising experts.

### Focus Area Agents

#### Overall Performance Agent
**Business Challenge**: Pricing managers manually review thousands of product prices and market conditions daily, spending 3+ hours analyzing competitor pricing, demand forecasts, and inventory levels to optimize pricing strategies and maximize revenue.

**Agent Solution**: Autonomous dynamic pricing workflow that analyzes real-time market data, customer behavior, and inventory levels to generate AI-driven price recommendations with revenue optimization, demand forecasting, and automated price adjustments across all retail channels.

**Agent Workflow Steps**:
1. **Retail Pricing Data Initialization** - Loading comprehensive retail pricing dataset with enhanced validation across products and product categories
2. **Dynamic Pricing Performance Assessment** - Advanced calculation of pricing optimization indicators with revenue analysis
3. **Retail Pattern Recognition** - Sophisticated identification of pricing effectiveness patterns with customer behavior correlation analysis
4. **AI Retail Intelligence Processing** - Processing comprehensive retail data through selected AI model with advanced reasoning
5. **Retail Performance Report Compilation** - Professional retail pricing analysis with evidence-based recommendations and actionable revenue optimization insights

#### Optimization Opportunities Agent
**Business Challenge**: Merchandising teams spend 4+ hours daily manually identifying inefficiencies in pricing strategies, inventory management, and customer segmentation across diverse product categories and sales channels.

**Agent Solution**: AI-powered retail optimization analysis that automatically detects pricing inefficiencies, inventory optimization opportunities, and customer segment targeting improvements with specific implementation recommendations for POS and inventory management system integration.

**Agent Workflow Steps**:
1. **Retail Optimization Data Preparation** - Advanced loading of retail pricing and inventory data with enhanced validation for efficiency improvement identification
2. **Pricing Strategy Inefficiency Detection** - Sophisticated analysis of price elasticity and customer segmentation with evidence-based inefficiency identification
3. **Retail Correlation Analysis** - Enhanced examination of relationships between price elasticity, customer segments, and purchasing behavior
4. **POS System Integration Optimization** - Comprehensive evaluation of dynamic pricing integration with existing Shopify, Square, and inventory management platforms
5. **AI Retail Optimization Intelligence** - Generating advanced pricing strategy recommendations using selected AI model with retail reasoning
6. **Retail Strategy Finalization** - Professional retail optimization report with prioritized implementation roadmap and pricing strategy impact analysis

#### Financial Impact Agent
**Business Challenge**: Retail financial analysts manually calculate complex ROI metrics across pricing strategies and inventory management, requiring 3+ hours of financial modeling to assess dynamic pricing impact on revenue growth and cost reduction.

**Agent Solution**: Automated retail financial analysis that calculates comprehensive ROI, identifies revenue optimization opportunities across product categories and customer segments, and projects pricing strategy benefits with detailed retail economics forecasting.

**Agent Workflow Steps**:
1. **Retail Financial Data Integration** - Advanced loading of retail revenue data and pricing financial metrics with enhanced validation across products
2. **Revenue Impact Calculation** - Sophisticated ROI metrics calculation with pricing strategy analysis and customer lifetime value enhancement
3. **Customer Value Financial Assessment** - Enhanced analysis of retail revenue impact with customer satisfaction metrics and pricing elasticity correlation analysis
4. **Retail Portfolio Efficiency Analysis** - Comprehensive evaluation of resource allocation efficiency across product categories with inventory cost optimization
5. **AI Retail Financial Modeling** - Advanced retail revenue projections and pricing ROI calculations using selected AI model
6. **Retail Economics Report Generation** - Professional retail financial impact analysis with detailed pricing optimization ROI calculations and revenue forecasting

#### Strategic Recommendations Agent
**Business Challenge**: Chief Executive Officers spend hours manually analyzing competitive positioning and developing strategic roadmaps for retail technology advancement and omnichannel pricing transformation initiatives.

**Agent Solution**: Strategic retail intelligence workflow that analyzes competitive advantages against traditional fixed-pricing approaches, identifies emerging retail technology integration opportunities with IoT/AR, and creates prioritized omnichannel transformation roadmaps.

**Agent Workflow Steps**:
1. **Retail Technology Assessment** - Advanced loading of retail technology context with competitive positioning analysis across products and categories
2. **Retail Competitive Advantage Analysis** - Sophisticated evaluation of competitive positioning against traditional fixed-pricing retail approaches with AI-powered dynamic pricing effectiveness
3. **Advanced Retail Technology Integration** - Enhanced analysis of integration opportunities with IoT sensors, AR customer experiences, and omnichannel retail technologies across retail data dimensions
4. **Omnichannel Retail Strategy Development** - Comprehensive development of prioritized retail transformation roadmap with evidence-based dynamic pricing adoption strategies
5. **AI Retail Strategic Processing** - Advanced retail strategic recommendations using selected AI model with long-term competitive positioning
6. **Digital Retail Report Generation** - Professional digital retail transformation roadmap with competitive analysis and dynamic pricing implementation plan ready for CEO executive review

### Agent Execution Flow

1. **Agent Initialization** - User selects focus area and AI model, triggering specialized agent activation
2. **Data Context Loading** - Agent accesses pricing data, customer behavior metrics, and inventory performance indicators
3. **Step-by-Step Processing** - Agent executes sequential workflow steps with real-time progress visualization
4. **Retail Intelligence Integration** - Selected Snowflake Cortex model processes retail context with specialized prompting
5. **Results Compilation** - Agent generates comprehensive pricing analysis with actionable retail recommendations
6. **Report Delivery** - Professional retail report delivered with implementation roadmap and success metrics

## Data Sources

The application is designed to work with data from major retail systems and platforms:

### Retail Data Sources (Simulated)
- **Point of Sale (POS)**: 
  - Shopify
  - Square
  - Lightspeed
- **Customer Relationship Management (CRM)**: 
  - Salesforce
  - HubSpot
  - Zoho
- **Inventory Management**: 
  - Manhattan Associates
  - Oracle Retail
  - JDA Software

For demonstration and development purposes, we've created a synthetic dataset that approximates these data sources and combined them into a single table exposed through an API server. This approach allows for realistic retail analytics without using protected customer information.

## Key Features

- **AI Agent Workflows**: Transparent, step-by-step retail pricing analysis through specialized mini-agents for each focus area
- **Agent Progress Visualization**: Real-time display of agent processing steps with retail context and completion tracking
- **Focus Area Specialization**: Dedicated agents for Overall Performance, Optimization Opportunities, Financial Impact, and Strategic Recommendations
- **Retail Intelligence Integration**: Seamless integration with multiple Snowflake Cortex models for specialized retail analysis
- **Real-time market data analysis**: Analyzes sales data, market trends, and competitive information to inform pricing decisions
- **Predictive demand forecasting**: Predicts future demand based on historical data and market factors
- **Automated price optimization**: Automatically recommends optimal pricing for products based on multiple factors
- **Integration with synthetic retail data**: Simulates data from major POS, CRM, and inventory management systems
- **Comprehensive data application**: Visual representation of key metrics including revenue growth, stockout rates, overstock rates, and customer satisfaction
- **Custom Fivetran connector**: Utilizes a custom connector built with the Fivetran Connector SDK to reliably move data from the API server to Snowflake

## Streamlit Data App Sections

### Metrics
- **Key Performance Indicators**: Track revenue growth, overstock rates, stockout rates, and customer satisfaction
- **Pricing Performance Metrics**: Monitor product prices, order values, and price elasticity
- **Price Optimization Results Distribution**: Visualize the success rate of price optimization recommendations
- **Customer Segment Distribution**: Analyze customer distribution across segments
- **Product Category Analysis**: Explore product categories and subcategories
- **Revenue Growth vs Customer Satisfaction Quadrant Analysis**: Map products by revenue growth and satisfaction performance
- **Price Elasticity vs Inventory Turnover Analysis**: Understand the relationship between price sensitivity and inventory efficiency
- **Order Status Distribution**: Monitor order fulfillment and cancellation rates
- **Inventory Management Summary**: Track stockout rates, overstock rates, and inventory turnover

### AI Insights with Agent Workflows
Generate AI-powered insights through transparent agent workflows with different focus areas:
- **Overall Performance**: Comprehensive analysis of the dynamic pricing system through autonomous dynamic pricing workflow
- **Optimization Opportunities**: Areas where pricing optimization can be improved via AI-powered retail optimization analysis
- **Financial Impact**: Cost-benefit analysis and ROI in retail terms through automated retail financial analysis
- **Strategic Recommendations**: Long-term strategic implications for improvement via strategic retail intelligence workflow

Each focus area includes:
- **Business Challenge Description**: Detailed explanation of the specific retail problem being addressed
- **Agent Solution Overview**: Description of how the AI agent workflow solves the challenge
- **Real-time Progress Tracking**: Step-by-step visualization of agent processing with retail context
- **Agent Execution Controls**: Start/stop controls for managing agent workflow execution
- **Professional Retail Reports**: Comprehensive analysis reports with implementation roadmaps

### Insights History
Access previously generated agent-driven insights for reference and comparison, including agent execution details and model selection.

### Data Explorer
Explore the underlying data with pagination controls.

## Setup Instructions

1. Within Snowflake, click on **Projects**
2. Click on **Streamlit**
3. Click the blue box in the upper right to create a new Streamlit application
4. On the next page:
   - Name your application
   - **IMPORTANT:** Set the database context
   - **IMPORTANT:** Set the schema context

### Fivetran Data Movement Setup

1. Ensure the API server hosting the synthetic retail data is operational
2. Configure the custom Fivetran connector (built with Fivetran Connector SDK) to connect to the API server - debug and deploy
3. Start the Fivetran sync in the Fivetran UI to move data into an `RDP_RECORDS` table in your Snowflake instance
4. Verify data is being loaded correctly by checking the table in Snowflake

## Data Flow

1. **Synthetic Data Creation**: A synthetic dataset approximating real retail data sources has been created and exposed via an API server:
   - Point of Sale: Shopify, Square, Lightspeed
   - Customer Relationship Management: Salesforce, HubSpot, Zoho
   - Inventory Management: Manhattan Associates, Oracle Retail, JDA Software

2. **Custom Data Integration**: A custom connector built with the Fivetran Connector SDK communicates with the API server to extract the synthetic retail data

3. **Automated Data Movement**: Fivetran manages the orchestration and scheduling of data movement from the API server into Snowflake

4. **Data Loading**: The synthetic retail data is loaded into Snowflake as an `RDP_RECORDS` table in a structured format ready for analysis

5. **Agent Workflow Execution**: AI agents process the retail pricing data through specialized workflows, providing transparent step-by-step analysis

6. **Data Analysis**: Snowpark for Python and Snowflake Cortex analyze the data to generate insights through agent-driven processes

7. **Data Visualization**: Streamlit in Snowflake presents the analyzed data in an interactive data application with agent workflow visualization

## Data Requirements

The application expects a table named `RDP_RECORDS` which contains synthetic data simulating various retail systems. This data is retrieved from an API server using a custom Fivetran connector built with the Fivetran Connector SDK:

### Order and Customer Data
- `order_id`
- `order_date`
- `order_total`
- `order_status`
- `customer_id`
- `customer_segment`
- `customer_ltv`
- `order_frequency`
- `average_order_value`

### Product Data
- `product_id`
- `product_category`
- `product_subcategory`
- `product_price`
- `product_rating`
- `product_review_count`

### Pricing Metrics
- `price_elasticity`
- `price_optimization_date`
- `price_optimization_result`
- `price_optimization_recommendation`

### Inventory Data
- `inventory_level`
- `inventory_turnover`
- `stockout_rate`
- `overstock_rate`
- `demand_forecast`

### Performance Metrics
- `revenue_growth_rate`
- `customer_satisfaction_rate`

## Benefits

- 8% increase in revenue: $800,000 additional revenue/year
- 12% reduction in overstocking: $60,000 savings/year
- 10% decrease in stockouts: $20,000 savings/year
- 5% improvement in customer satisfaction: 4% increase in customer satisfaction
- **Enhanced Pricing Transparency**: Agent workflows provide clear visibility into pricing analysis reasoning and decision-making processes
- **Accelerated Market Response**: Automated agent processing reduces manual analysis time from hours to minutes for complex pricing assessments

## Technical Details

This application uses:
- **AI Agent Workflow Engine**: Custom agent orchestration system for transparent, step-by-step retail pricing analysis
- **Multi-Agent Architecture**: Specialized agents for different retail focus areas with domain-specific processing
- **Agent Progress Visualization**: Real-time display of agent execution steps with retail context and completion tracking
- **Streamlit in Snowflake** for the user interface with enhanced agent workflow displays
- **Snowflake Cortex** for AI-powered insights generation through agent-managed prompting
- **Multiple AI models** including Claude 4 Sonnet, Claude 3.5 Sonnet, Llama 3.1/3.3, Mistral, DeepSeek, and more for agent intelligence
- **Snowpark for Python** for data processing within agent workflows
- **Fivetran Connector SDK** for building a custom connector to retrieve synthetic retail data from an API server
- **Custom Fivetran connector** for automated, reliable data movement into Snowflake

## Success Metrics

- Revenue growth
- Overstocking reduction
- Stockout decrease
- Customer satisfaction improvement
- **Agent Workflow Efficiency**: Time reduction from manual retail analysis to automated agent-driven insights
- **Pricing Strategy Transparency Score**: User confidence in retail recommendations through visible agent reasoning
- **Retail Analysis Accuracy**: Improvement in pricing decision quality through systematic agent processing

## Key Stakeholders

- Pricing Manager
- Inventory Manager
- Marketing Manager
- Chief Executive Officer (CEO)
- **Retail Data Analysts**: Professionals who benefit from transparent agent workflow visibility
- **Merchandising Teams**: Staff who implement agent-recommended pricing strategies

## Competitive Advantage

PricePulse's real-time analysis and predictive capabilities with transparent agent workflows enable retailers to respond quickly to market changes, maximizing profits and minimizing losses. The agent-based architecture provides unprecedented visibility into pricing analysis reasoning, building trust and confidence in AI-driven retail decisions. This creates a competitive advantage by delivering optimal pricing strategies while maintaining complete transparency in the decision-making process.

## Long-term Evolution

In the next 3-5 years, PricePulse will evolve to incorporate more advanced generative AI techniques and sophisticated agent architectures, including:

- **Multi-modal Agent Learning**: Agents that can process customer behavior data, market imagery, and competitive intelligence from diverse retail channels
- **Collaborative Agent Networks**: Multiple agents working together to solve complex pricing challenges across different product categories
- **Adaptive Agent Intelligence**: Self-improving agents that learn from market outcomes and refine their analytical approaches
- **Advanced Agent Orchestration**: Sophisticated workflow management for complex, multi-step pricing analysis processes
- **Integration with Emerging Retail Technologies**: Agent connectivity with IoT sensors for real-time inventory tracking, AR customer experience platforms, and omnichannel pricing synchronization for comprehensive retail optimization

The system will expand to include integration with emerging technologies like IoT and AR to enhance customer experience and improve supply chain efficiency, all orchestrated through advanced agent workflows that provide complete transparency and control over the retail pricing analysis process.