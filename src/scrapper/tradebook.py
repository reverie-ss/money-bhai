"""
Scraps the premiums which is most relevant to the nifty50 or banknifty prices
The idea is to fetch and store premiums which are near to the index funds
If Nifty50 is at 19250, pull 8 premiums which are multiple of 100 (4 from top and 4 from below)
"""
import pandas as pd
from pymongo.errors import BulkWriteError
from datetime import datetime

from src.models.data_model_candle import Instruments, Order
from src.utilities.singleton import database_client

class TradebookScrapper:
    """
    Scraps premium
    """
    def __init__(self) -> None:
        self.orders_collection = database_client.get_collection("orders")
        self.instruments_collection = database_client.get_collection("instruments")
        
    
    def fill_tradebook_from_zerodha(self):
        """
        Function that helps to fill the tradebook fromzerodha csv export
        """
        tradebook_df = pd.read_csv("tradebook2.csv")
        data_list = []
        for index, row in tradebook_df.iterrows(): # pylint: disable=unused-variable
            order: Order = Order(
                trading_symbol=row.get("symbol"),
                trade_date=row.get("trade_date"),
                trade_type=row.get("trade_type"),
                quantity=round(row.get("quantity")),
                price=row.get("price"),
                trade_id=row.get("trade_id"),
                order_id=row.get("order_id"),
                order_execution_time =row.get("order_execution_time"),
                expiry_date=row.get("expiry_date")
            )
            data_list.append(order.dict())

        try:
            db_res = self.orders_collection.insert_many(data_list, ordered=False)
            inserted_count = len(db_res.inserted_ids)
        except Exception as exc:
            if isinstance(exc, BulkWriteError):
                print(f"Skipping {len(exc.details.get('writeErrors'))} orders as these are duplicate")
                inserted_count = exc.details.get('nInserted')

        print("Successfuly inserted orders")
        print(f"Fetched orders: {len(data_list)}")
        print(f"Inserted orders: {inserted_count}")
        print(f"Ignored orders: {len(data_list) - inserted_count}")

        return "Successful", 200
         

    
    def fill_tradebook_from_upstox(self, order_list: list):
        """
        Function that helps to fill the tradebook from upstox API
        """
        
        data_list = []
        for index, order in enumerate(order_list): # pylint: disable=unused-variable
            
            if order.get("status") != "complete":
                continue

            order_time = datetime.strptime(order.get("order_timestamp"), "%Y-%m-%d %H:%M:%S")
            order_instrument: Instruments = Instruments(**self.instruments_collection.find_one({"instrument_key": order.get("instrument_token")}))

            order_obj: Order = Order(
                trading_symbol=order.get("trading_symbol"),
                trade_date=order_time.strftime("%Y-%m-%d"),
                trade_type=order.get("transaction_type").lower(),
                quantity=order.get("quantity"),
                price=order.get("average_price"),
                trade_id=order.get("exchange_order_id"),
                order_id=order.get("order_id"),
                order_execution_time=order_time,
                expiry_date=order_instrument.expiry,
                instrument_token=order.get("instrument_token")
            )
            data_list.append(order_obj.dict())

        try:
            db_res = self.orders_collection.insert_many(data_list, ordered=False)
            inserted_count = len(db_res.inserted_ids)
        except Exception as exc:
            if isinstance(exc, BulkWriteError):
                print(f"Skipping {len(exc.details.get('writeErrors'))} orders as these are duplicate")
                inserted_count = exc.details.get('nInserted')

        print("Successfuly inserted orders")
        print(f"Fetched orders: {len(data_list)}")
        print(f"Inserted orders: {inserted_count}")
        print(f"Ignored orders: {len(data_list) - inserted_count}")

        return "Successful", 200
    

    def fill_tradebook_from_upstox_csv(self):
        """
        Function that helps to fill the tradebook from upstox csv export
        """
        tradebook_df = pd.read_csv("tradebook_upstox_1.csv")
        data_list = []
        for index, row in tradebook_df.iterrows(): # pylint: disable=unused-variable
            
            order_time = datetime.strptime(row.get("Date") + " " + row.get("Trade Time"), "%d-%m-%Y %H:%M:%S")

            option_type = "CE"
            if row.get("Instrument Type") == "European Put":
                option_type = "PE"
            order_instrument = self.instruments_collection.find_one({
                "strike": row.get("Strike Price"),
                "expiry": (datetime.strptime(row.get("Expiry"), "%d-%m-%Y")).strftime("%Y-%m-%d"),
                "option_type": option_type
            })
            if order_instrument is None:
                print("Skipping this order as no data found in instruments collection", row)
                continue

            order_instrument: Instruments = Instruments(**order_instrument)
            
            order_obj: Order = Order(
                trading_symbol=order_instrument.trading_symbol,
                trade_date=order_time.strftime("%Y-%m-%d"),
                trade_type=row.get("Side").lower(),
                quantity=row.get("Quantity"),
                price=float(row.get("Price")[1:]),
                trade_id=row.get("Trade Num"),
                order_id=row.get("Trade Num"),
                order_execution_time=order_time,
                expiry_date=order_instrument.expiry,
                instrument_token=order_instrument.instrument_key
            )
            data_list.append(order_obj.dict())

        try:
            db_res = self.orders_collection.insert_many(data_list, ordered=False)
            inserted_count = len(db_res.inserted_ids)
        except Exception as exc:
            if isinstance(exc, BulkWriteError):
                print(f"Skipping {len(exc.details.get('writeErrors'))} orders as these are duplicate")
                inserted_count = exc.details.get('nInserted')

        print("Successfuly inserted orders")
        print(f"Fetched orders: {len(data_list)}")
        print(f"Inserted orders: {inserted_count}")
        print(f"Ignored orders: {len(data_list) - inserted_count}")

        return "Successful", 200
         