"""
Constantly checks for active orders and closes if conditions are met
"""
from datetime import datetime
import json
import time
import requests
from src.utilities.enums import HTTP_Method, UpstoxEndpoint
from src.utilities.script import execute_api
from src.utilities.singleton import database_client


class EntryService:
    """
    Has logic to tell which premium to enter with
    1. Fetch the latest price of nifty, banknifty and finnifty
    2. Find the closest strike price from instruments collection
    3. Choose the strike price and place order
    """

    def __init__(self, instrument_key) -> None:
        self.candles_collection = database_client.get_collection("MinuteCandles")
        self.instrument_key = instrument_key

    def fetch_latest_price_of_premiums(self):
        """
        Fetches the latest candle details from upstox api for all 3 premiums NIFTY, BANKNIFTY, FINNIFTY
        
        Args:
            - `instruments_list` : list of all the instruments key values (for example, ["NSE|FO4437", "NSE|FO4438"])
        """
        NIFTY_INTRUMENT = "NSE_INDEX|Nifty 50"
        BANKNIFTY_INTRUMENT = "NSE_INDEX|Nifty Bank"
        query_params = "NSE_INDEX|Nifty 50,NSE_INDEX|Nifty Bank"

        response = execute_api(
            method=HTTP_Method.GET,
            endpoint=UpstoxEndpoint.FETCH_QUOTES,
            query_params=query_params
        )

        if response.status_code == 200:
            result_dict: dict = (json.loads(response.content)).get("data")
            return result_dict.get(NIFTY_INTRUMENT).get("last_price"), result_dict.get(BANKNIFTY_INTRUMENT).get("last_price"),
    
        return response

    def execute(self):
        """
        Logix starts here
        """
        res = self.fetch_latest_price_of_premiums()
        print(res)