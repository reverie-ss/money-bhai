"""
Constantly checks for active orders and closes if conditions are met
"""
from datetime import datetime
import time
import json

from requests import Response
from src.models.data_model_candle import Instruments
from src.order.order_manager import ManageOrder
from src.utilities.singleton import database_client
from src.utilities.enums import HTTP_Method, UpstoxEndpoint
from src.utilities.script import execute_api


class ExitService:
    """
    Has logic to tell when to exit
    """

    def __init__(self, stop_loss_percent: float, trailing_percent: float) -> None:
        self.candles_collection = database_client.get_collection("MinuteCandles")
        self.instruments_collection = database_client.get_collection("instruments")
        self.stop_loss_percent = stop_loss_percent
        self.trailing_percent = trailing_percent

    def fetch_current_posiitons(self):
        """
        This function helps to fetch the list of current day active/inactive positions in market.
        1. If the "quantity" is more than zero, it means the order is active (not sold yet)
        2. It also has the last_price, so we do not have to call another api to get latest price
        """

        response = execute_api(
            method=HTTP_Method.GET,
            endpoint=UpstoxEndpoint.FETCH_POSITIONS,
            is_authorization_required=True
        )
        print(response)
        return response

    def get_active_order(self, last_price_response: Response):
        """
        Get currently active order
        """

        if last_price_response.status_code != 200:
            return None
        
        order_list = json.loads(last_price_response.text).get("data")
        for order in order_list:
            if order.get("quantity") > 0:
                return order
        return None

    def fetch_instrument(self, instrument_key):
        """
        Fetches data for a particular instrument
        """

        instrument: Instruments = Instruments(**self.instruments_collection.find_one({"instrument_key": instrument_key}))
        return instrument

    def start_trailing(self) -> bool:
        """
        Tracks the instrument every second to check if exit conditions are met.
        """
        stop_loss: float = -1
        trailing_target: float = -1
        trailing_variation: float = 0
        last_price: float = 0
        quantity: int = 0
        total_time = 0
        counter = 1
        current_time = datetime.now()
        while True:
            last_price_response = self.fetch_current_posiitons()
            print(last_price, stop_loss, trailing_target)
            
            if last_price_response.status_code == 200:
                active_order = self.get_active_order(last_price_response=last_price_response)
                
                if active_order:
                    last_price = active_order.get("last_price")
                    quantity = active_order.get("quantity")
                else:
                    break

                if trailing_target == -1 or stop_loss == -1:
                    trailing_variation = last_price*(self.trailing_percent/100)
                    trailing_target = last_price + trailing_variation
                    stop_loss = last_price - last_price*(self.stop_loss_percent/100)

                # Exit if stoploss hits
                if last_price <= stop_loss:
                    print("Exit")
                    break
                
                # Exit before day ends
                # if current_time.hour == 15:
                #     print("Exit")
                #     break

                
                # Trailing Stoploss
                if (last_price > trailing_target):
                    stop_loss = stop_loss + trailing_variation
                    trailing_target = trailing_target + trailing_variation
            counter = counter + 1
            time.sleep(1.8)

        total_time = total_time + (datetime.now() - current_time).seconds
        print("Average Time:" + str(total_time/counter))
        print(f"EXIT @{last_price} (stop_loss={stop_loss} and trailing_target={trailing_target})")  
        instrument_key = active_order.get("instrument_token")

        ManageOrder(instrument=self.fetch_instrument(instrument_key=instrument_key), quantity=quantity).sell()

        return True
            