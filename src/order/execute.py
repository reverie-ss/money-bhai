"""
Executes order
"""
import json
import requests
from src.utilities.script import base_url, generate_header


class ExecuteOrder:
    """
    has functions to execute a trade
    """

    def __init__(self) -> None:
        pass

    def place_order(self, quantity: int, instrument_key: str, transaction_type: str):
        """
        Funciton is used to entry or exit orders
        """
        body = {
            "quantity": quantity,
            "product": "I",
            "validity": "DAY",
            "price": 0,
            "tag": "MoneyBhai",
            "instrument_token": instrument_key,
            "order_type": "MARKET",
            "transaction_type": transaction_type,
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        headers = generate_header(is_authorization_required=True)
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        api_url =  f"{base_url()}order/place"
        response = requests.post(api_url, headers=headers, timeout=60, data=json.dumps(body))
        print(response.text)
        return
