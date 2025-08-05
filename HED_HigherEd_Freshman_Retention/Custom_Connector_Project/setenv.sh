#!/bin/zsh

# This script loads environment variables from a specified .env file.
# It skips comments and empty lines, and handles single/double quotes around values.

# IMPORTANT: To make the variables available in your current terminal session,
# you MUST source this script, e.g.:
#   source ./load_env.zsh <path_to_env_file>
# Or the shorthand:
#   . ./load_env.zsh <path_to_env_file>

# Capture the script's name at the very beginning of execution.
# This ensures $SCRIPT_NAME always holds the actual script file name.
SCRIPT_NAME="$0"

# --- Function to display usage information ---
show_usage() {
  echo "Usage: source $SCRIPT_NAME <path_to_env_file>"
  echo "       (or . $SCRIPT_NAME <path_to_env_file>)"
  echo ""
  echo "Loads environment variables from the specified .env file into the current Zsh session."
  echo "  - Skips lines starting with '#' (comments)."
  echo "  - Skips empty lines."
  echo "  - Handles values enclosed in single or double quotes."
  echo "Example: source $SCRIPT_NAME .env.development"
}

# --- Function to trim leading/trailing whitespace from a string ---
# Takes a string as an argument and echoes the trimmed string.
trim() {
  local input_string="$1"
  # Use sed to remove leading and trailing whitespace characters
  echo "$input_string" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//'
}

# --- Main script logic ---

# Check if an environment file path was provided as an argument
if [[ -z "$1" ]]; then
  echo "Error: No environment file specified."
  show_usage
  return 1 # Use 'return' instead of 'exit' when sourcing to avoid exiting the parent shell
fi

ENV_FILE="$1"

# Check if the specified file exists and is readable
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Error: Environment file '$ENV_FILE' not found or is not a regular file."
  return 1 # Use 'return' instead of 'exit' when sourcing
fi

echo "--- Loading environment variables from '$ENV_FILE' ---"

# Read the file line by line using a while loop
# IFS= prevents word splitting on spaces/tabs
# read -r prevents backslash escapes from being interpreted
while IFS= read -r line; do
  # 1. Trim leading/trailing whitespace from the line using the new trim function
  trimmed_line=$(trim "$line")

  # 2. Skip empty lines or lines that are comments (start with '#')
  if [[ -z "$trimmed_line" || "$trimmed_line" =~ ^# ]]; then
    continue # Go to the next line
  fi

  # 3. Check if the line contains an '=' sign
  if [[ "$trimmed_line" =~ = ]]; then
    # Split the line at the first '=' to get key and value
    # Zsh's parameter expansion:
    #   ${parameter%%=*} - Remove longest suffix pattern from parameter (everything from the first '=')
    #   ${parameter#*=} - Remove shortest prefix pattern from parameter (everything up to and including the first '=')
    key="${trimmed_line%%=*}"   # Extracts everything before the first '='
    value="${trimmed_line#*=}"  # Extracts everything after the first '='

    # 4. Remove surrounding quotes from the value if present
    #    This regex matches a string that starts and ends with either ' or "
    #    The (.*) captures the content inside the quotes into the 'match' array.
    if [[ "$value" =~ ^[\'\"](.*)[\'\"]$ ]]; then
      value="${match[1]}" # Use the captured group (content inside quotes)
    fi

    # 5. Check if the variable already exists and unset it before exporting
    #    ${(P)key} performs indirect parameter expansion, using the value of 'key' as a variable name.
    if [[ -n "${(P)key}" ]]; then
      unset "$key"
      echo "  Unset existing: $key"
    fi

    # 6. Export the variable
    #    The syntax 'export VAR="value"' is used to set and export in one step.
    export "$key=$value"
    echo "  Exported: $key"
  else
    # Inform about lines that don't look like key=value pairs
    echo "  Skipping malformed line (no '=' found): $trimmed_line"
  fi

done < "$ENV_FILE" # Redirect the file content as input to the while loop

echo "--- Environment variable loading complete ---"

# --- Optional: Provide instructions for verification ---
echo ""
echo "To verify variables, you can use 'echo \$VARIABLE_NAME' or 'env | grep VARIABLE_NAME'."
echo "Example: echo \$MY_APP_NAME"
