import pymongo
import os
import requests
from datetime import datetime
from src.models.data_model_candle import Candle



class CandleScrapper:

    def __init__(self) -> None:
        client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
        database = client.get_database(os.environ.get("DATABASE"))
        self.candles_collection = database.get_collection("MinuteCandles")

    def insert_into_database(self, sorted_candles: list):
        # Insert into mongo database

        dict_sorted_candles = []
        candle: Candle
        for candle in sorted_candles:
            dict_sorted_candles.append(candle.dict())

        # Insert the document into the collection
        res = self.candles_collection.insert_many(dict_sorted_candles)

        # Print the document
        return len(res.inserted_ids)

    def fetch_historical_data(self, from_date: str, to_date: str, instrument: str = "NSE_INDEX|Nifty 50"):
        """
        Args:
            - `from_date`: 2023-10-17
            - `to_date`: 2023-10-17
        """

        headers = {
            "Api-Version": "2.0"
        }
        api_url =  f"https://api-v2.upstox.com/historical-candle/{instrument}/1minute/{from_date}/{to_date}"
        response = requests.get(api_url, headers=headers)
        historical_data = response.json().get("data")

        # Serialize data
        candles_list = []
        for candle in historical_data.get("candles"):
            temp = {
                "meta" : instrument,
                "ts" : datetime.fromisoformat(candle[0]),
                "open" : candle[1],
                "high" : candle[2],
                "low" : candle[3],
                "close" : candle[4],
                "volume" : candle[5],
            }
            candles_list.append(Candle(**temp))

        # Sort based on latest data
        sorted_candles = sorted(candles_list, key=lambda candle: candle.ts)

        # Insert into database
        self.insert_into_database(sorted_candles=sorted_candles)

    
    def clear_database(self):
        """
        Dangerous function. Use only when necessary
        """

        res = self.candles_collection.delete_many({})
        print(res.deleted_count)