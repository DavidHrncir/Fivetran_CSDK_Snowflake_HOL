import requests
import time
import json
from fivetran_connector_sdk import Connector
from fivetran_connector_sdk import Operations as op
from fivetran_connector_sdk import Logging as log

def schema(configuration: dict):
    """Define the minimal table schema for Fivetran"""
    # Validate configuration
    api_key = configuration.get('api_key')
    if not api_key:
        log.severe("API key is missing from configuration")
        return []

    # Only table name and primary key, as per API spec
    # The API spec states 'record_id' is the primary key for hed_records
    return [
        {
            "table": "hed_records",
            "primary_key": ["record_id"]  # record_id uniquely identifies each record
        }
    ]

def update(configuration: dict, state: dict):
    """Extract data from the hed_data endpoint and yield operations"""
    api_key = configuration.get('api_key')
    if not api_key:
        log.severe("API key is missing from configuration")
        return

    base_url = configuration.get('base_url')
    if not base_url:
        log.severe("Base URL is missing from configuration")
        return

    page_size = int(configuration.get('page_size', '100'))

    headers = {"x-api-key": api_key}
    session = requests.Session()
    session.headers.update(headers)

    next_cursor = state.get('next_cursor')
    url = f"{base_url}/hed_data"
    params = {"page_size": page_size}
    if next_cursor:
        params["cursor"] = next_cursor
        log.info(f"Starting sync from cursor: {next_cursor}")
    else:
        log.info("Starting initial sync")

    record_count = 0
    has_more = True
    iteration = 0

    try:
        while has_more:
            if iteration >= 200:
                yield op.checkpoint({"next_cursor": next_cursor})
                log.warning("Maximum iteration limit (200) reached. Checkpoint saved, exiting sync.")
                break

            try:
                for attempt in range(3):
                    try:
                        response = session.get(url, params=params)
                        response.raise_for_status()
                        break
                    except requests.exceptions.RequestException as e:
                        if attempt == 2:
                            raise
                        log.warning(f"Request failed (attempt {attempt + 1}/3): {str(e)}")
                        time.sleep(2 ** attempt)

                data = response.json()
                records = data.get("hed_records", [])
                for record in records:
                    if 'record_id' in record:
                        yield op.upsert("hed_records", record)
                        record_count += 1
                    else:
                        log.warning(f"Skipping record without ID: {record}")

                next_cursor = data.get("next_cursor")
                has_more = data.get("has_more", False)

                yield op.checkpoint({"next_cursor": next_cursor})
                log.info(f"Checkpoint at {record_count} records, cursor: {next_cursor}")

                if next_cursor:
                    params["cursor"] = next_cursor

                log.info(f"Processed batch: {len(records)} records, has_more: {has_more}")
                iteration += 1

            except requests.exceptions.HTTPError as e:
                status = e.response.status_code
                if status == 401:
                    log.severe("Authentication failed - check API key")
                    return
                elif status == 429:
                    log.warning("Rate limit hit, waiting 60 seconds")
                    time.sleep(60)
                    continue
                else:
                    log.severe(f"HTTP error: {status} - {e.response.text}")
                    break
            except requests.exceptions.RequestException as e:
                log.severe(f"API request failed: {str(e)}")
                break
            except Exception as e:
                log.severe(f"Unexpected error processing response: {str(e)}")
                break

        if next_cursor:
            yield op.checkpoint({"next_cursor": next_cursor})
            log.info(f"Final checkpoint: {record_count} total records, cursor: {next_cursor}")
        else:
            log.info(f"Sync completed: {record_count} total records")

    except Exception as e:
        log.severe(f"Unexpected error in update function: {str(e)}")

connector = Connector(update=update, schema=schema)

if __name__ == "__main__":
    with open("configuration.json", "r") as f:
        configuration = json.load(f)
    connector.debug(configuration=configuration)