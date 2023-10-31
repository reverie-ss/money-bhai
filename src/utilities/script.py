"""
Scripts module that contains functions that can be used across all modules
"""
from pydantic import BaseModel # pylint: disable=no-name-in-module


def convert_model_to_dict(list_data_raw: list[BaseModel]):
    """
    This function helps to convert a list of custom data models into list of dicts
    """
    list_data_formatted: list[dict] = []

    for data in list_data_raw:
        list_data_formatted.append(data.dict())

    return list_data_formatted
