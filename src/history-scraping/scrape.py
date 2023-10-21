import pymongo
import os
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
        print(res.inserted_ids)