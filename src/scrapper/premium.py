"""
Scraps the premiums which is most relevant to the nifty50 or banknifty prices
The idea is to fetch and store premiums which are near to the index funds
If Nifty50 is at 19250, pull 8 premiums which are multiple of 100 (4 from top and 4 from below)
"""
import os
import pandas as pd
import pymongo
from pymongo.errors import BulkWriteError

from src.models.data_model_candle import Order

class PremiumScrapper:
    """
    Scraps premium
    """
    def __init__(self) -> None:
        client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
        database = client.get_database(os.environ.get("DATABASE"))
        self.orders_collection = database.get_collection("orders")
    

    def execute(self):
        """
        1. Get the current price of index funds of nifty and bankfity
        2. Figure out the strike prices based on the above prices
        3. Pull instrument keys from the database for the chosen strike prices
        4. Fetch historical data from upstox for the given strike prices
        """
        
        
    
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
         