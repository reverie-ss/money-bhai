"""
Constantly checks for active orders and closes if conditions are met
"""
from datetime import datetime
import json
from src.models.data_model_candle import Instruments
from src.models.trades import TradeEntry
from src.order.exit import ExitService
from src.order.order_manager import ManageOrder
from src.utilities.enums import HTTP_Method, UpstoxEndpoint
from src.utilities.script import execute_api
from src.utilities.singleton import database_client


class EntryService:
    """
    Has logic to tell which premium to enter with
    1. Fetch the latest price of nifty, banknifty and finnifty
    2. Figure out the upcoming expiry date
    2. Find the closest strike price from instruments collection
    3. Choose the instrument and place order
    """

    def __init__(self, trade_entry: TradeEntry) -> None:
        self.instruments_collection = database_client.get_collection("instruments")
        self.trade_entry = trade_entry

    def fetch_latest_price_of_premiums(self):
        """
        Fetches the latest candle details from upstox api for all 3 premiums NIFTY, BANKNIFTY, FINNIFTY
        
        Args:
            - `instruments_list` : list of all the instruments key values (for example, ["NSE|FO4437", "NSE|FO4438"])
        """
        NIFTY_INTRUMENT = "NSE_INDEX|Nifty 50"
        BANKNIFTY_INTRUMENT = "NSE_INDEX|Nifty Bank"
        query_params = "symbol=NSE_INDEX|Nifty 50,NSE_INDEX|Nifty Bank"

        response = execute_api(
            method=HTTP_Method.GET,
            endpoint=UpstoxEndpoint.FETCH_QUOTES,
            query_params=query_params,
            is_authorization_required=True
        )

        if response.status_code == 200:
            result_dict: dict = (json.loads(response.content)).get("data")
            return result_dict.get(NIFTY_INTRUMENT.replace("|", ":")).get("last_price"), result_dict.get(BANKNIFTY_INTRUMENT.replace("|", ":")).get("last_price"),
    
        return response

    def find_upcoming_expiry(self):
        """
        """
        current_date = datetime.now()
        current_date = current_date.strftime("%Y-%m-%d")
        query = [
            {
                '$match': {
                    'expiry': {
                        '$gte': current_date
                    }, 
                    'trading_symbol': {
                        '$regex': '^' + self.trade_entry.market_index
                    },
                }
            }, {
                '$sort': {
                    'expiry': 1
                }
            },  {
                '$limit': 1
            }
        ]
        db_response = list(self.instruments_collection.aggregate(query))
        
        return db_response[0].get("expiry")

    def fetch_relevant_premium(self, strike: int):
        """
        query from instruments collection
        """
        expiry = self.find_upcoming_expiry()
        query = [
            {
                '$match': {
                    'instrument_type': 'OPTIDX', 
                    'option_type': self.trade_entry.option_type, 
                    'expiry': expiry, 
                    'trading_symbol': {
                        '$regex': '^' + self.trade_entry.market_index
                    }
                }
            }, {
                '$addFields': {
                    'differnece': {
                        '$abs': {
                            '$subtract': [
                                '$strike', strike
                            ]
                        }
                    }
                }
            }, {
                '$sort': {
                    'differnece': 1
                }
            }
        ]
        instruments_list = list(self.instruments_collection.aggregate(query))
        return Instruments(**instruments_list[0])

    def execute(self):
        """
        Logix starts here
        """
        nifty50, bank_nifty = self.fetch_latest_price_of_premiums()
        print(f"Indexes @ NIFTY:{nifty50} and BANKNIFTY:{bank_nifty}")

        strike = bank_nifty
        if self.trade_entry.market_index == "NIFTY":
            strike = nifty50

        instrument: Instruments = self.fetch_relevant_premium(strike=strike)
        print("Found strike at" + instrument.instrument_key)
        print(instrument.dict())

        response = ManageOrder(instrument=instrument).buy()
        if response.status_code == 200:
            print(f"Placed order for {instrument.instrument_key}")
            exit_response: bool = ExitService(
                stop_loss_percent=10,
                trailing_percent=5
            ).start_trailing()
            
        return response
    
    def buy_specific_strike(self, strike: int):

        instrument: Instruments = self.fetch_relevant_premium(strike=strike)
        print("Found strike at" + instrument.instrument_key)
        print(instrument.dict())

        response = ManageOrder(instrument=instrument).buy()
        if response.status_code == 200:
            print(f"Placed order for {instrument.instrument_key}")
            exit_response: bool = ExitService(
                stop_loss_percent=10,
                trailing_percent=5
            ).start_trailing()
        
        return response
    
    
            