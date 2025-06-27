#!/bin/bash

# Colors and formatting
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'
BOLD='\033[1m'

# Display banner
echo -e "${BLUE}${BOLD}===========================================================${NC}"
echo -e "${BLUE}${BOLD}            Fivetran Connector Deployment Script          ${NC}"
echo -e "${BLUE}${BOLD}===========================================================${NC}"
echo

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
    echo -e "${YELLOW}Error: Root config.json not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found root config.json at: $CONFIG_PATH/$ROOT_CONFIG${NC}"

# Validate the local configuration.json file exists
if [[ ! -f "configuration.json" ]]; then
    echo -e "${YELLOW}Error: Local configuration.json not found!${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Found local configuration.json${NC}"
echo

# Prompt for the Fivetran Account Name
read -p "Enter your Fivetran Account Name [MDS_SNOWFLAKE_HOL]: " ACCOUNT_NAME
ACCOUNT_NAME=${ACCOUNT_NAME:-"MDS_SNOWFLAKE_HOL"}

# Fetch the API key from config.json
API_KEY=$(jq -r ".fivetran.api_key" "$CONFIG_PATH/$ROOT_CONFIG")
if [[ "$API_KEY" == "null" ]]; then
    echo -e "${YELLOW}Error: API key name not found in $ROOT_CONFIG!${NC}"
    exit 1
fi

# Fetch the dest name from config.json
DEST_NAME=$(jq -r ".fivetran.dest_name" "$CONFIG_PATH/$ROOT_CONFIG")
if [[ "$DEST_NAME" == "null" ]]; then
    echo -e "${YELLOW}Error: Destination name not found in $ROOT_CONFIG!${NC}"
    exit 1
fi

# Prompt for the Fivetran Destination Name
read -p "Enter your Fivetran Destination Name [$DEST_NAME]: " DESTINATION_NAME
DESTINATION_NAME=${DESTINATION_NAME:-"$DEST_NAME"}

# Prompt for the Fivetran Connector Name
read -p "Enter a unique Fivetran Connection Name [my_new_fivetran_custom_connection]: " CONNECTION_NAME
CONNECTION_NAME=${CONNECTION_NAME:-"my_new_fivetran_custom_connection"}

echo
echo -e "${BOLD}Deployment Configuration:${NC}"
echo -e "  Account: ${CYAN}$ACCOUNT_NAME${NC}"
echo -e "  Destination: ${CYAN}$DESTINATION_NAME${NC}"
echo -e "  Connection: ${CYAN}$CONNECTION_NAME${NC}"
echo

# Deploy the connection using the configuration file
echo -e "${BOLD}Deploying connection...${NC}"
echo -e "${CYAN}Running command:${NC} fivetran deploy --configuration configuration.json"
fivetran deploy --api-key "$API_KEY" --destination "$DESTINATION_NAME" --connection "$CONNECTION_NAME" --configuration configuration.json

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}${BOLD}✓ Deployment completed successfully!${NC}"
else
    echo -e "\n${YELLOW}⚠ Deployment encountered issues. Check the output above.${NC}"
    exit 1
fi