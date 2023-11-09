"""
Scripts module that contains functions that can be used across all modules
"""
import json
import os
from pydantic import BaseModel # pylint: disable=no-name-in-module
import requests

from src.utilities.enums import HTTP_Method, UpstoxEndpoint # pylint: disable=no-name-in-module


def convert_model_to_dict(list_data_raw: list[BaseModel]):
    """
    This function helps to convert a list of custom data models into list of dicts
    """
    list_data_formatted: list[dict] = []

    for data in list_data_raw:
        list_data_formatted.append(data.dict())

    return list_data_formatted

def base_url():
    """
    Returns the base url of upstox
    """
    return os.environ.get("UPSTOX_BASE_URL")

def execute_api(
        method: HTTP_Method, 
        endpoint: UpstoxEndpoint, 
        is_authorization_required: bool = False, 
        body: dict = None,
        headers: dict = None,
        query_params: str = None
    ):
    """
    Function used to execute APIs. Helps forming the headers and authorization
    """
    if not headers:
        headers = {}
        
    headers["Api-Version"] = "2.0"

    if is_authorization_required:
        headers["Authorization"] = "Bearer " + os.environ.get("ACCESS_TOKEN")

    api_url =  os.environ.get("UPSTOX_BASE_URL") + endpoint.value

    if query_params:
        api_url = api_url + "?" + query_params

    if method == HTTP_Method.GET:
        return requests.get(api_url, headers=headers, timeout=60)
    if method == HTTP_Method.POST:
        return requests.post(api_url, headers=headers, timeout=60, data=json.loads(body))
    return None
