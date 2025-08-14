# Fivetran Connector SDK Hands on Lab with Snowflake 2025: Oil and Gas Field Technician Summarization

## Overview
In this hands on lab, you'll build a **custom Fivetran connector** using the **Fivetran Connector SDK** and the **LLM service of your choice** to integrate data from a custom REST API into Snowflake. You'll then create a **Streamlit (in Snowflake)** application with various tools and dashboards powering key metrics as well as a **Snowflake Cortex AI-driven** feature to drive even deeper analytics, descriptive, and prescriptive insights.

The Oil and Gas FTS custom connector should fetch field technician records from a REST API and load them into a single table called `fts_records` in your Snowflake database. The connector should deliver detailed information about field operations, maintenance activities, and technician log summarization for oil and gas operations, including properties like failure rates, maintenance costs, downtime hours, and summarization time savings. It should handle authentication, pagination, error handling, and maintain state between sync runs using a cursor-based approach.

## Lab Steps - Quick Access

- [Step 1: Set up the Development Environment](#step-1-set-up-the-development-environment)
- [Step 2: Create a Custom Fivetran Connector](#step-2-create-a-custom-fivetran-connector)
- [Step 3: Start Data Sync in Fivetran](#step-3-start-data-sync-in-fivetran)
- [Step 4: Create a Streamlit Application in Snowflake](#step-4-create-a-streamlit-application-in-snowflake)

## Web Locations
- Browser tabs (leave them open throughout the lab):
  - Tab 1: GitHub Lab Repo: This Lab Guide (stays on lab guide)
  - Tab 2: GitHub Lab Repo: This Lab Guide (expands folders and opens files) 
  - Tab 3: [Fivetran: Automated Data Movement Platform](https://www.fivetran.com/login)
  - Tab 4: [Snowflake: Data and AI Platform](https://aa67604.us-central1.gcp.snowflakecomputing.com/console/login#/)
  - Tab 5: [Fivetran Connector SDK Docs](https://fivetran.com/docs/connector-sdk)

***PAUSE: Let's quickly walk through the GitHub interface.***

## Step 1: Set up the Development Environment
1. Create the project directory. On a Windows or Mac, create the **fts** folder in a folder that does not reside under a system folder such as "My Documents".

2. Download the project files from the git repo (easiest way):
   - **fts_manual.env**: Environment variables loading file
   - **configuration.json**: Configure your API credentials and settings
   - **connector.py**: Our connector code for this vertical
   - **requirements.txt**: Python requirements file
3. Once the above files are downloaded copy/move them to the newly created **fts** folder
4. Open this folder in your development IDE or in a terminal window
5. **Activate your Python virtual environment in your terminal window**

6. Set up our environment variables.
   - Edit the **fts_manual.env** file.  These values will become environment variables in your current terminal session (meaning if you close the terminal by accident, you will need to re-apply these environment variables). NOTE: If these environment variables are not present, you will be prompted to enter them manually during debugging and deployment (added complexity).  Note that the **FIVETRAN_CONFIGURATION** and **FIVETRAN_PYTHON_VERSION** values are already set.  We need to update the first 3 values now.
      - **FIVETRAN_API_KEY**: We need to be in our Fivetran UI, then click your name in the lower left nav panel, then click API Key, and click Generate New API Key.  Copy the ***base64 encoded key***, remove the default text including the brackets and paste that value. If you make a mistake, you can generate a new key as it will overwrite the previous one.
      - **FIVETRAN_DESTINATION_NAME**:  The instructor will place the value in the webinar chat area.  Copy and paste from there.
      - **FIVETRAN_CONNECTION_NAME**: This must be all lower case letters, numbers, and underscores.  Since we are sharing a common environment, the <ins>connection names must be unique</ins>.  An option that works well here is, your initials followed by your birth month and day followed by fts.  Example: **dh0816fts** This value will be the connector name in Fivetran as well as the schema name in Snowflake.  Ensure you save the **fts_manual.env** file.
7. Copy all 5 values from the fts_manual.env file and paste them into your terminal and press enter/return.
   - To view/verify the values are applied in Windows:
   ```bash
   set
   ```
   - To view/verify the values are applied in Mac:
   ```bash
   env
   ```

## Step 2: Create a Custom Fivetran Connector

### 2.1 Install the Fivetran Connector SDK Package
Let's install the Fivetran Connector SDK package. We will directly use version 1.7.0. In your terminal with your Python environment already activated, run the following command:
```bash
pip install fivetran-connector-sdk==1.7.0
```

### 2.2 Debug the Custom Connector Locally
1. Let's debug our code in the terminal by running the following commands. **fivetran reset** tells your local SDK system that all files and temporary databases should be reset for a brand new run. **fivetran debug** tells your local SDK system that it should mimic locally what Fivetran would be doing in Fivetran's environment.  You will notice that you must pass in the **--configuration configuration.json** parameter for the debug command since you could be testing multiple types of configurations during a development/testing cycle.
```bash
fivetran reset
```
```bash
fivetran debug --configuration configuration.json
```

2. (Optional-Instructor will demo) Once debug completes, you are able to open a tool like dBeaver and open the DuckDB in the projects **files** folder and inspect the contents.  **Ensure you disconnect** the tool from the database when done since most tools will lock the database while open.

3. If you let the code run to the end, you should see a statement that 600 rows were replicated/upserted.

***PAUSE: Let's analyze what is happening behind the scenes.***

### 2.3 Deploy the Custom Connector to Fivetran
Let's deploy this code into Fivetran. This is the portion where all of the environment variables will be utilized.  Let's run the following command.  This command will prompt you for parameters, but you will notice that the command takes our environment variables and presents them as defaults.  You can just press enter/return through those.  **Note that only a portion of the Fivetran API key will be shown.**
```bash
fivetran deploy --configuration configuration.json
```

You should receive a message stating the connection was deployed successfully along with the Python version and the Connection ID value. At this point, we are done with developing our connection.  Let's move some data!

## Step 3: Start Data Sync in Fivetran

1. Switch to the Fivetran tab in your browser.
2. Ensure you are in the **Connections** page and refresh the page to find your newly created connection.  If you enter your initials in the search, it should filter directly to your connection.
3. Click on the connection to open the **Status** page.
4. Click the **Start Initial Sync** button.
5. You should see a status message indicating that the sync is **Active** and that it is the first time syncing data for this connection.
6. Once your sync completes, you will see a message "Next sync will run in x hours" and if you click on the **1 HOUR** selection on the right side, you will see some sync metrics.  <ins>You may need to refresh the UI to see updated sync progress and logs in the UI. </ins>
7. Once your sync completes, you will see a message "Next sync will run in x hours" and if you click on the **1 HOUR** selection on the right side, you will see some sync metrics.

***PAUSE: Recap.***

## Step 4: Create a Streamlit Application in Snowflake

### 4.1 Copy the Streamlit Data App Code
Open the **Streamlit_App** folder in this git repo on the other GitHub browser tab.  Click the **app-agent.py** file and click the copy icon in the upper right.

### 4.2 Create and Deploy the Streamlit in Snowflake Gen AI Data App
1. Switch to the Snowflake tab in your browser.
2. Click on **Projects** in the left navigation panel.
3. Click on **Streamlit**.
4. Click the refresh icon in your browser to refresh the schemas.
5. Click the **+ Streamlit App** blue button in the upper right corner.
6. Configure your app:
   - App title: **[your initials]-LogLynx**
   - Database: Select **HOL_DATABASE_1**
   - Schema: Select your schema which is the same name as your connector (example: dh0816fts) the schema created by your Fivetran connector.
7. In the Streamlit Editor that appears (left side of the Streamlit UI), select all text (Command+A or Control+A) and delete it.
8. Paste the copied Streamlit application code into the empty editor (Command+V or Control+V).
9. Click the blue **Run** button in the upper right corner.
10. Close the editor by clicking the middle icon in the bottom left navigation.

## 4.3 Explore the Streamlit in Snowflake Gen AI Data App
The LogLynx data app should now be running with the following sections:
- **Metrics**: View failure rates, maintenance costs, downtime hours, and time savings metrics with operational visualizations
- **AI Insights**: Generate AI-powered analysis of the oil and gas field operations data across four focus areas
- **Insights History**: Access previously generated AI insights
- **Data Explorer**: Browse the underlying field technician and maintenance data

## Done!
You've successfully:
1. Created a custom Fivetran connector using the Fivetran Connector SDK
2. Deployed the connector to sync oil and gas field technician summarization data into Snowflake
3. Built a Streamlit in Snowflake data app to visualize and analyze the data using Snowflake Cortex

## Next Steps
Consider how you might adapt this solution for your own use:
- Integration with field operations systems like SAP, Oracle, or Microsoft Dynamics
- Adding real-time equipment monitoring from CMMS systems like IBM Maximo or Infor EAM
- Implementing machine learning models for more sophisticated predictive maintenance algorithms
- Customizing the Streamlit app for specific oil and gas operational processes

## Resources
- Fivetran Connector SDK Documentation: [https://fivetran.com/docs/connectors/connector-sdk](https://fivetran.com/docs/connectors/connector-sdk)  
- Fivetran Connector SDK Examples: [https://fivetran.com/docs/connector-sdk/examples](https://fivetran.com/docs/connector-sdk/examples)
- API Connector Reference: [https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fts_api_spec](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/fts_api_spec)
- Snowflake Cortex Documentation: [https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- Snowflake Streamlit Documentation: [https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)