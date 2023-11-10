"""
Executes order
"""
from src.models.data_model_candle import Instruments
from src.utilities.enums import HTTP_Method, UpstoxEndpoint
from src.utilities.script import execute_api


class ManageOrder:
    """
    has functions to execute a trade
    """

    def __init__(self, instrument: Instruments) -> None:
        self.instrument = instrument

    def place_order(self, transaction_type: str):
        """
        Funciton is used to entry or exit orders
        """
        body = {
            "quantity": self.instrument.lot_size,
            "product": "I",
            "validity": "DAY",
            "price": 0,
            "tag": "MoneyBhai",
            "instrument_token": self.instrument.instrument_key,
            "order_type": "MARKET",
            "transaction_type": transaction_type,
            "disclosed_quantity": 0,
            "trigger_price": 0,
            "is_amo": False
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        response = execute_api(
            method=HTTP_Method.POST,
            endpoint=UpstoxEndpoint.PLACE_ORDER,
            is_authorization_required=True,
            body=body,
            headers=headers
        )
        print(response.text)
        return response

    def buy(self):
        return self.place_order(
            transaction_type="BUY"
        )

    def sell(self):
        return self.place_order(
            transaction_type="SELL"
        )