import os

import requests


def trigger_pipeline(api_key: str, pipeline_id: str, log_data: dict) -> dict:
    """
    Trigger a pipeline on the nadhi-server running in the Docker network.

    Args:
        pipeline_id (str): The ID of the pipeline to trigger.
        log_data (dict): The log data to send to the pipeline.

    Returns:
        dict: The JSON response from the nadhi-server.

    Raises:
        RuntimeError: If the API key is not set or the request fails.
    """

    # Use the Docker container name as the hostname
    nadhi_server_host = os.getenv("NADHI_SERVER_HOST", "http://data-nadhi-server")
    url = f"{nadhi_server_host}:5000/api/pipeline/trigger"
    headers = {"x-datanadhi-api-key": api_key, "Content-Type": "application/json"}
    payload = {"pipeline_id": pipeline_id, "log_data": log_data}
    response = requests.post(url, headers=headers, json=payload, timeout=10)
    response.raise_for_status()
    return response.json()
