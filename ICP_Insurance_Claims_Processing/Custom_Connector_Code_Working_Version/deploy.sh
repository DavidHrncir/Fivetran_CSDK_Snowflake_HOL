#!/bin/bash

# Locate the root-level config.json file
ROOT_CONFIG="config.json"
CONFIG_PATH=$(pwd)
while [[ "$CONFIG_PATH" != "/" ]]; do
    if [[ -f "$CONFIG_PATH/$ROOT_CONFIG" ]]; then
        break
    fi
    CONFIG_PATH=$(dirname "$CONFIG_PATH")
done

# Validate the root config.json file exists
if [[ ! -f "$CONFIG_PATH/$ROOT_CONFIG" ]]; then
    echo "Error: Root config.json not found!"
    exit 1
fi

# Validate the local configuration.json file exists
if [[ ! -f "configuration.json" ]]; then
    echo "Error: Local configuration.json not found!"
    exit 1
fi

# Prompt for the Fivetran Account Name
read -p "Enter your Fivetran Account Name [MDS_SNOWFLAKE_HOL]: " ACCOUNT_NAME
ACCOUNT_NAME=${ACCOUNT_NAME:-"MDS_SNOWFLAKE_HOL"}

# Fetch the API key from config.json
API_KEY=$(jq -r ".fivetran.api_key" "$CONFIG_PATH/$ROOT_CONFIG")
if [[ "$API_KEY" == "null" ]]; then
    echo "Error: API key name not found in $ROOT_CONFIG!"
    exit 1
fi

# Fetch the dest name from config.json
DEST_NAME=$(jq -r ".fivetran.dest_name" "$CONFIG_PATH/$ROOT_CONFIG")
if [[ "$DEST_NAME" == "null" ]]; then
    echo "Error: Destination name not found in $ROOT_CONFIG!"
    exit 1
fi

# Prompt for the Fivetran Destination Name
read -p "Enter your Fivetran Destination Name [$DEST_NAME]: " DESTINATION_NAME
DESTINATION_NAME=${DESTINATION_NAME:-"$DEST_NAME"}

# Prompt for the Fivetran Connector Name
read -p "Enter a unique Fivetran Connection Name [my_new_fivetran_custom_connection]: " CONNECTION_NAME
CONNECTION_NAME=${CONNECTION_NAME:-"my_new_fivetran_custom_connection"}

# Deploy the connection using the configuration file
echo "Deploying connection..."
fivetran deploy --api-key "$API_KEY" --destination "$DESTINATION_NAME" --connection "$CONNECTION_NAME" --configuration configuration.json
