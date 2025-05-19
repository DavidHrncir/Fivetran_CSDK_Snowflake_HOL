#!/bin/bash

# Locate the root-level config.json file
ROOT_CONFIG="ft_accounts_config.json"
CONFIG_PATH="${FT_CONFIG_KEY_PATH}"

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

# Load the account name.
ACCOUNT_NAME="MDS_SNOWFLAKE_HOL"

# Fetch the API key from the configuration file.
API_KEY=$(jq -r ".fivetran.account.$ACCOUNT_NAME.api_key" "$CONFIG_PATH/$ROOT_CONFIG")
if [[ "$API_KEY" == "null" ]]; then
    echo "Error: API key not found in $ROOT_CONFIG!"
    exit 1
fi

# Fetch the destination name from the configuration file.
DESTINATION_NAME=$(jq -r ".fivetran.account.$ACCOUNT_NAME.dest_name" "$CONFIG_PATH/$ROOT_CONFIG")
if [[ "$DESTINATION_NAME" == "null" ]]; then
    echo "Error: Destination name not found in $ROOT_CONFIG!"
    exit 1
fi

# Prompt for the Fivetran Connection Name
read -p "Enter a unique Fivetran Connection Name [my_new_fivetran_custom_connection]: " CONNECTION_NAME
CONNECTION_NAME=${CONNECTION_NAME:-"custom_connection"}

# Deploy the connection using the configuration file
echo "Deploying connection..."
fivetran deploy --api-key "$API_KEY" --destination "$DESTINATION_NAME" --connection "$CONNECTION_NAME" --configuration configuration.json
