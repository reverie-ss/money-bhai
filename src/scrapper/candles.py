"""
Candle Scrapper is used to fetch all the prices by minute level and store in database
"""
import os
import time
from datetime import datetime, timedelta
from dateutil import parser

import requests
import pymongo
from dotenv import load_dotenv

from src.models.data_model_candle import Candle
from src.utilities.enums import InstrumentKey
from src.utilities.singleton import database_client

load_dotenv()


class CandleScrapper:
    """
    Class is used to fetch all the price actions of a given instrument and store it in database
    """

    def __init__(self, instrument_key: str) -> None:
        self.candles_collection = database_client.get_collection("MinuteCandles")

        self.instrument_key = instrument_key

    def insert_into_database(self, sorted_candles: list[Candle]) -> int:
        """
        Inserts into mongo database
        """

        dict_sorted_candles = []
        candle: Candle
        for candle in sorted_candles:
            dict_sorted_candles.append(candle.dict())

        # Insert the document into the collection
        res = self.candles_collection.insert_many(dict_sorted_candles)
        timedelta(hours=5, minutes=30)

        return len(res.inserted_ids)

    def serialize_candle_data(self, historical_data: dict) -> list[Candle]:
        """
        Convert from api response into valid data model
        """

        print("Total data fetched: ", len(historical_data.get("candles")))
        # Serialize data
        candles_list = []
        for candle in historical_data.get("candles"):
            temp = {
                "meta" : self.instrument_key,
                "ts" : parser.parse(candle[0]).replace(tzinfo=None),
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


    def fetch_upstox_date(self, date: str):
        """
        Fetches data for a single day
        Args:
            - `from_date`: 2023-10-17
            - `to_date`: 2023-10-17
        """

        headers = {
            "Api-Version": "2.0",
        }
        api_url =  f"https://api-v2.upstox.com/historical-candle/{self.instrument_key}/1minute/{date}/{date}"
        response = requests.get(api_url, headers=headers, timeout=60)
        historical_data = response.json().get("data")

        if response.status_code == 200:
            return historical_data
        else:
            print("Upstox API failed", api_url)
            print(response.status_code, response.text)
            exit(0)

    def fetch_historical_data(self, start_date: datetime = None, end_date: datetime = None):
        """
        Upstox has the following rate limit:

        Time Duration	Request Limit
        Per Second	    25 requests
        Per Minute	    250 requests
        Per 30 Minutes	1000 requests

        So, we are adding a delay of 2 seconds for data since Jan 1, 2023
        Sample Format: 2023-10-17
        """

        # Set the upstox start date
        default_start_date = datetime(
            year=2023,
            month=4,
            day=15
        )
        default_end_date = datetime.now() - timedelta(days=1)

        if start_date is None:
            start_date = default_start_date

        if end_date is None:
            end_date = default_end_date

        while start_date<end_date:
            start_date = start_date + timedelta(days=1)
            print(f"Checking for date {start_date} {start_date.weekday()}")

            # Excluding weekends
            if start_date.weekday() > 4:
                continue

            date = start_date.strftime("%Y-%m-%d")
            historical_data = self.fetch_upstox_date(date=date)

            # Serialize data and sort it
            sorted_historical_data: list[Candle] = self.serialize_candle_data(historical_data=historical_data)

            if len(sorted_historical_data) != 0: # Day is holiday if no result returned

                # Insert into database
                inserted_count = self.insert_into_database(sorted_candles=sorted_historical_data)

                print(f"Historical data for {date} inserted with {inserted_count} documents")

            time.sleep(1) # To avoid rate limit

        print("Successfully completed scraping")
        return True

    def fetch_missing_historical_data(self):
        """
        This function will check the last date entry in database for the given instrument. It will then continue from that day.
        """
        res = list(self.candles_collection.find({"meta": self.instrument_key}).sort("_id", -1).limit(1))
        if len(res) == 0:
            print("Database is empty")
            return

        last_inserted_candle: Candle = Candle(**res[0])

        self.fetch_historical_data(start_date=last_inserted_candle.ts)
