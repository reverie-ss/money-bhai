import pandas as pd
import pymongo
import gzip
import os
import requests
from typing import Dict
from dateutil import parser
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.models.data_model_candle import Candle, Instruments
from src.utilities.enums import InstrumentKey

load_dotenv()


class InstrumentsScrapper:

    def __init__(self) -> None:
        client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
        database = client.get_database(os.environ.get("DATABASE"))
        self.candles_collection = database.get_collection("MinuteCandles")
        self.instruments_collection = database.get_collection("instruments")
        self.local_csv_file_path = "instruments_file.csv"

        self.url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"

    def fetch_instruments(self):
        """
        Fetch the latest list of instruments from the upstox url and store it in the database
        """
        try:

            response = requests.get(self.url, timeout=60)

            if response.status_code == 200:

                # Decompress the GZ file and save the decompressed content to a local file
                with open(self.local_csv_file_path, 'wb') as local_csv_file:
                    decompressed_content = gzip.decompress(response.content)
                    local_csv_file.write(decompressed_content)


                return pd.read_csv(self.local_csv_file_path)
            else:
                print(f"Failed to download the PDF. Status code: {response.status_code}")

        except Exception as exc:
            print(exc)

        return None

    def filter_instruments(self, instruments_df: pd.DataFrame) -> list[Instruments]:
        """
        The instruments file has a lot of data, we just need to filter out the premiums of nifty and  banknifty
        """

        valid_instrument_type = ["INDEX", "OPTIDX"]
        valid_exchange = ["NSE_INDEX", "NSE_FO"]
        valid_index = ["NSE_INDEX|Nifty 50", "NSE_INDEX|Nifty Bank"]

        valid_instruments_list: list[Instruments] = []
        for index, row in instruments_df.iterrows():
            instrument: Instruments = Instruments(**row)
            if instrument.instrument_type in valid_instrument_type and \
                instrument.exchange in valid_exchange and \
                (instrument.tradingsymbol.startswith("NIFTY") or instrument.tradingsymbol.startswith("BANKNIFTY")):
                valid_instruments_list.append(instrument)

            if instrument.instrument_key in valid_index:
                valid_instruments_list.append(instrument)

        return valid_instruments_list

    def update_instruments_in_db(self, latest_instruments_list: list[Instruments]):
        """
        Update/Insert the instruments into the database 
        """
        self.instruments_collection.insert_many(latest_instruments_list, ordered=False)

    def scrap_and_store_instruments(self):
        """
        Scraps the data from upstox, filters and stores it in the database
        """
        instruments_df = self.fetch_instruments()

        if instruments_df:
            valid_instruments_list: list[Instruments] = self.filter_instruments(instruments_df=instruments_df)

            # Update/Insert the instruments into the database 
            db_res = self.instruments_collection.insert_many(valid_instruments_list, ordered=False)
            print("Successfuly completed scraping and storing instruments")
            print(f"Fetched instruments: {len(valid_instruments_list)}")
            print(f"Inserted instruments: {len(db_res.inserted_ids)}")
            print(f"Ignored instruments: {len(valid_instruments_list) - len(db_res.inserted_ids)}")
        else:
            print("Failed to fetch instruments from upstox")
