import pymongo
import os
import requests
from datetime import datetime, timedelta
from src.models.data_model_candle import Candle



class CandleScrapper:

    def __init__(self, instrument_key: str) -> None:
        client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
        database = client.get_database(os.environ.get("DATABASE"))
        self.candles_collection = database.get_collection("MinuteCandles")

        self.instrument_key = "NSE_INDEX|Nifty 50"
        if instrument_key:
            self.instrument_key = instrument_key

    def insert_into_database(self, sorted_candles: list[Candle]) -> int:
        # Insert into mongo database

        dict_sorted_candles = []
        candle: Candle
        for candle in sorted_candles:
            dict_sorted_candles.append(candle.dict())

        # Insert the document into the collection
        res = self.candles_collection.insert_many(dict_sorted_candles)

        # Print the document
        return len(res.inserted_ids)
    
    def serialize_candle_data(self, historical_data: list) -> list[Candle]:
        # Serialize data
        candles_list = []
        for candle in historical_data.get("candles"):
            temp = {
                "meta" : self.instrument_key,
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
        return sorted_candles


    def fetch_historical_data(self, date: str):
        """
        Fetches data for a single day
        Args:
            - `from_date`: 2023-10-17
            - `to_date`: 2023-10-17
        """

        headers = {
            "Api-Version": "2.0"
        }
        api_url =  f"https://api-v2.upstox.com/historical-candle/{self.instrument_key}/1minute/{date}/{date}"
        response = requests.get(api_url, headers=headers)
        historical_data = response.json().get("data")

        return historical_data

    def fetch_historical_data_multiple_days(self, from_date: str, to_date: str, instrument: str = "NSE_INDEX|Nifty 50"):
        """
        Upstox has the following rate limit:

        Time Duration	Request Limit
        Per Second	    25 requests
        Per Minute	    250 requests
        Per 30 Minutes	1000 requests

        So, we are adding a delay of 2 seconds for data since Jan 1, 2023
        Sample Format: 2023-10-17
        """

        start_date = datetime(
            year=2023,
            month=1,
            day=1
        )
        end_date = datetime.now() - timedelta(days=1)

        for index in range(300):
            if start_date<end_date:

                date = start_date.strftime("YYYY-mm-dd")
                historical_data = self.fetch_historical_data(date=date)

                # Serialize data and sort it
                sorted_historical_data: list[Candle] = self.serialize_candle_data(historical_data=historical_data)

                # Insert into database
                inserted_count = self.insert_into_database(sorted_candles=sorted_historical_data)

                print(f"Historical data for {date} inserted with {inserted_count} documents")
            
            start_date = start_date + timedelta(days=1)

    
    def clear_database(self):
        """
        Dangerous function. Use only when necessary
        """

        res = self.candles_collection.delete_many({})
        print(res.deleted_count)