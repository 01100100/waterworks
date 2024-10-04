import json
import pandas as pd
import requests
import time

# Define a custom User-Agent to abide by the Nominatim usage policy
USER_AGENT = "kreuzungen/1.0 (contact@kreuzungen.world)"


def fetch_nominatim_data(osm_id: int, max_retries: int = 5) -> dict:
    """
    Fetch data from the Nominatim API for a given OSM ID with exponential backoff.

    Args:
        osm_id (int): The OSM ID to fetch data for.
        max_retries (int): The maximum number of retries for the request.

    Returns:
        dict: The response data from the Nominatim API.
    """
    url = f"https://nominatim.openstreetmap.org/details.php?osmtype=R&osmid={osm_id}&format=json"
    headers = {"User-Agent": USER_AGENT}
    retries = 0
    while retries < max_retries:
        try:
            print(f"Trying to fetch data for OSM ID {osm_id}... 🌐")
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            print(f"Successfully fetched data for OSM ID {osm_id} ✅")
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 404:
                print(f"OSM ID {osm_id} not found. Check the relation at https://www.openstreetmap.org/relation/{osm_id} ❌")
                return {}
            else:
                retries += 1
                wait_time = 2**retries  # Exponential backoff
                print(
                    f"Error fetching data from Nominatim for OSM ID {osm_id}: {e}. Retrying in {wait_time} seconds... 🔄"
                )
                time.sleep(wait_time)
        except requests.RequestException as e:
            retries += 1
            wait_time = 2**retries  # Exponential backoff
            print(
                f"Error fetching data from Nominatim for OSM ID {osm_id}: {e}. Retrying in {wait_time} seconds... 🔄"
            )
            time.sleep(wait_time)
    print(
        f"Failed to fetch data from Nominatim for OSM ID {osm_id} after {max_retries} retries. ❌"
    )
    return {}


def model(dbt, session) -> pd.DataFrame:
    # Fetch OSM IDs from the new_relations table
    dbt.config(materialized="incremental")
    osm_relations = dbt.ref("osm_relations").df()
    osm_ids_to_fetch = []

    # Check if the DataFrame is empty or lacks the required columns
    if osm_relations.empty or "osm_id" not in osm_relations.columns:
        raise ValueError(
            "The DataFrame is empty or does not contain the required 'osm_id' column"
        )

    if dbt.is_incremental:
        # only new rows which don't exist in current table
        print("Incremental model: Fetching only new OSM IDs 🔄")
        already_processed_query = f"SELECT osm_id FROM {dbt.this}"
        already_processed_df = session.execute(already_processed_query).fetchall()
        print(f"Already processed {len(already_processed_df)} OSM relations 📋")
        already_processed_ids = [row[0] for row in already_processed_df]
        osm_ids_to_fetch = osm_relations[
            ~osm_relations["osm_id"].isin(already_processed_ids)
        ]["osm_id"].tolist()
    else:
        print("Full-refresh model: Fetching all OSM IDs 🔄")
        osm_ids_to_fetch = osm_relations["osm_id"].tolist()

    if not osm_ids_to_fetch:
        print("No new OSM IDs to fetch from Nominatim. 🖖")
        return pd.DataFrame(
            columns=["osm_id", "nominatim_response"]
        )  # Return an empty DataFrame with the required columns

    print(
        f"Fetching {len(osm_ids_to_fetch)} new relations from Nominatim. OSM IDs: {osm_ids_to_fetch} 📋"
    )

    nominatim_data = []
    start_time = time.time()
    for osm_id in osm_ids_to_fetch:
        data = fetch_nominatim_data(osm_id)
        nominatim_data.append(
            {"osm_id": osm_id, "nominatim_response": json.dumps(data)}
        )

        # Calculate elapsed time and sleep if necessary to maintain rate limit
        elapsed_time = time.time() - start_time
        if elapsed_time < len(nominatim_data):
            time.sleep(len(nominatim_data) - elapsed_time)

    df = pd.DataFrame(nominatim_data)
    print(f"Fetched data for {len(df)} OSM IDs. 📊")
    return df