# Fivetran Connector SDK Hands on Lab at Big Data London 2025: Higher Education Freshman Retention

## Overview
In this hands on lab, you'll build a **custom Fivetran connector** using the **Fivetran Connector SDK** and the **LLM service of your choice** to integrate data from a custom REST API into Snowflake. You'll then create a **Streamlit (in Snowflake)** application with various tools and dashboards powering key metrics as well as a **Snowflake Cortex AI-driven** feature to drive even deeper analytics, descriptive, and prescriptive insights.

The Higher Education HED custom connector should fetch student academic and engagement records from a REST API and load them into a single table called `hed_records` in your Snowflake database. The connector should deliver detailed information about student academic and enagement details, including properties like enrollment date, academic standing, current gpa, avg assignment score, engagement score, and at risk flags. It should handle authentication, pagination, error handling, and maintain state between sync runs using a cursor-based approach.

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
1. Create the project directory. On a Windows or Mac, create the **hed** folder in a folder that does not reside under a system folder such as "My Documents".

2. Download the project files from the git repo (easiest way):
   - **hed_manual.env**: Environment variables loading file
   - **configuration.json**: Configure your API credentials and settings
   - **connector.py**: Our connector code for this vertical
   - **requirements.txt**: Python requirements file
3. Once the above files are downloaded copy/move them to the newly created **hed** folder
4. Open this folder in your development IDE or in a terminal window
5. **Activate your Python virtual environment in your terminal window**

6. Set up our environment variables.
   - Edit the **hed_manual.env** file.  These values will become environment variables in your current terminal session (meaning if you close the terminal by accident, you will need to re-apply these environment variables). NOTE: If these environment variables are not present, you will be prompted to enter them manually during debugging and deployment (added complexity).  Note that the **FIVETRAN_CONFIGURATION** and **FIVETRAN_PYTHON_VERSION** values are already set.  We need to update the first 3 values now.
      - **FIVETRAN_API_KEY**: We need to be in our Fivetran UI, then click your name in the lower left nav panel, then click API Key, and click Generate New API Key.  Copy the ***base64 encoded key***, remove the default text including the brackets and paste that value. If you make a mistake, you can generate a new key as it will overwrite the previous one.
      - **FIVETRAN_DESTINATION_NAME**:  The instructor will place the value in the webinar chat area.  Copy and paste from there.
      - **FIVETRAN_CONNECTION_NAME**: This must be all lower case letters, numbers, and underscores.  Since we are sharing a common environment, the <ins>connection names must be unique</ins>.  An option that works well here is, your initials followed by your birth month and day followed by hed.  Example: **dh0816hed** This value will be the connector name in Fivetran as well as the schema name in Snowflake.  Ensure you save the **hed_manual.env** file.
7. Copy all 5 values from the hed_manual.env file and paste them into your terminal and press enter/return.
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
   - App title:  **[your initials]-StudentSuccess**
   - Database: Select **HOL_DATABASE_1**
   - Schema: Select your schema which is the same name as your connector (example: dh0816hed) the schema created by your Fivetran connector.
7. In the Streamlit Editor that appears (left side of the Streamlit UI), select all text (Command+A) and delete it
8. Paste the copied Streamlit application code into the empty editor (Command+V):
9. Click the blue **Run** button in the upper right corner
10. Close the editor by clicking the middle icon in the bottom left navigation

### 3.3 Explore the Streamlit in Snowflake Gen AI Data App
The StudentSuccess data app should now be running with the following sections:
- **Metrics**: View key performance metrics, gpa distribution, academic standing, at risk distribution, aid vs gpa correlation, and more
- **AI Insights**: Generate AI-powered analysis of the student academic and engagement data across four focus areas
- **Insights History**: Access previously generated AI insights
- **Data Explorer**: Browse the underlying data

# 5 (Optional) Use GenAI to Build Our Code
This step completely optional, but if you would like to see how we generated the code for this connection, follow the below steps. The **system_prompt.txt** contains the generic prompt info that fits all the endpoints/verticals in this repo. The **user_prompt.txt** contains specific information about the API endpoint that is used for this vertical.
1. From the **Prompts** folder in this vertical, copy the **system_prompt.txt** text and paste directly into your model.  <ins>Note, if you are using a model which has the system and user prompts separated, like Anthropic Claude, you can paste the text into the system prompt area and possibly save the system prompt to be used as the basis for other connection builds in the future.</ins>
2. Next, from the **Prompts** folder in this vertical, copy the **user_prompt.txt** text and paste directly after the system prompt.  Again, if your interface has a separate section for the user prompt, paste it there.
3. Execute the prompts.
4. Copy and paste the results overwriting all of the code in the **connector.py** file.
5. Run step **2.2** above to debug and step **2.3** to deploy your generated version.

Instructor tidbits on using GenAI. Most LLMs work flawlessly with the prompts in this repo. The prompts are created for the source API used for this lab. If there is an error, copy and paste the error back into the LLM and ask it to review and fix the code.  If no errors, but the code does not work, that requires good-ole debugging. Most of the time when this happens, there is only a small bug like incorrect API key name, table name, or the use of the **has_more** flag. For the most part, the code should be complete and only minor tweaks may be needed.

## Done!
You've successfully:
1. Created a custom Fivetran connector using the Fivetran Connector SDK
2. Deployed the connector to sync higher education student academic and engagement data into Snowflake
3. Built a Streamlit in Snowflake data app to visualize and analyze the data using Snowflake Cortex

## Next Steps
Consider how you might adapt this solution for your own use:
- Integration with student information systems like Banner, PeopleSoft, or Colleague for comprehensive academic record management
- Adding real-time student engagement monitoring from learning management systems like Canvas, Blackboard, or Moodle
- Implementing machine learning models for more sophisticated at-risk student identification and intervention routing
- Customizing the Streamlit app for specific academic programs, student populations, or institutional retention goals

## Resources
- Fivetran Connector SDK Documentation: [https://fivetran.com/docs/connectors/connector-sdk](https://fivetran.com/docs/connectors/connector-sdk)  
- Fivetran Connector SDK Examples: [https://fivetran.com/docs/connector-sdk/examples](https://fivetran.com/docs/connector-sdk/examples)
- API Connector Reference: [https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/hed_api_spec](https://sdk-demo-api-dot-internal-sales.uc.r.appspot.com/hed_api_spec)
- Snowflake Cortex Documentation: [https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)
- Snowflake Streamlit Documentation: [https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)