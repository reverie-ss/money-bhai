"""
Constantly checks for active orders and closes if conditions are met
"""
from datetime import datetime
import json
import time
import requests
from src.models.data_model_candle import Candle
from src.utilities.script import generate_header
from src.utilities.singleton import database_client


class ExitService:

    def __init__(self) -> None:
        self.candles_collection = database_client.get_collection("MinuteCandles")


    def fetch_latest_price(self, instrument_key: str):
        """
        Fetches the latest candle details from upstox api for one or more instruments
        
        Args:
            - `instruments_list` : list of all the instruments key values (for example, ["NSE|FO4437", "NSE|FO4438"])
        """

        # Convert the list into string separated by commas
        # query_instruments = ""
        # for instrument in instruments_list:
        #     query_instruments = query_instruments + instrument + ","
        # query_instruments = query_instruments[:-1]

        headers = generate_header(is_authorization_required=True)
        api_url =  f"https://api-v2.upstox.com/market-quote/quotes?symbol={instrument_key}"
        response = requests.get(api_url, headers=headers, timeout=60)
        print(response.text)
        if response.status_code == 200:
            result_dict = (json.loads(response.content)).get("data")
            for instrument_key in result_dict:
                return result_dict.get(instrument_key).get("last_price")
        return None
    
    def track_premium(self, instrument_key: str, stop_loss_percent: float, trailing_percent: float):
        """
        Tracks the instrument every second to check if exit conditions are met.
        """
        stop_loss: float = -1
        trailing_target: float = -1
        trailing_variation: float = 0
        last_price: float = 0
        total_time = 0
        counter = 0
        current_time = datetime.now()
        while True:
            last_price = self.fetch_latest_price(instrument_key=instrument_key)
            
            if last_price:

                if trailing_target == -1 or stop_loss == -1:
                    trailing_variation = last_price*(trailing_percent/100)
                    trailing_target = last_price + trailing_variation
                    stop_loss = last_price - last_price*(stop_loss_percent/100)

                # Exit if stoploss hits
                if last_price <= stop_loss:
                    print("Exit")
                    break
                
                # Exit before day ends
                if current_time.hour == 15:
                    print("Exit")
                    break

                
                # Trailing Stoploss
                if (last_price > trailing_target):
                    stop_loss = stop_loss + trailing_variation
                    trailing_target = trailing_target + trailing_variation
            counter = counter + 1
            time.sleep(1.8)
            if counter == 100:
                break

        total_time = total_time + (datetime.now() - current_time).seconds
        print("Average Time:" + str(total_time/counter))
        
        # while True:
        #     print(f"EXIT @{last_price} (stop_loss={stop_loss} and trailing_target={trailing_target})")

    
    def execute(self):
        """
        Intitates the process of exiting a position. 
        Here are the following steps:
        1. Get the latest order from order history API
        2. Take the premium and track it every second
        3. Track premium to exit when needed
        """

        self.track_premium(
            instrument_key="NSE_FO|40742",
            stop_loss_percent=10,
            trailing_percent=10
        )


