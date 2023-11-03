"""
This module is used to fetch instruments data from upstox and store it in the database.
Instruments have information about each premium or index. These ids are required to fetch price or place order
"""
import gzip
import os
import pymongo
import requests
import pandas as pd
from dotenv import load_dotenv
from pymongo.errors import BulkWriteError
from src.models.data_model_candle import Instruments
from src.utilities.script import convert_model_to_dict

load_dotenv()


class InstrumentsScrapper:
    """
    Class that has all the functionalities to fetch, filter and store data
    """

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

                df = pd.read_csv(self.local_csv_file_path)
                os.remove(self.local_csv_file_path)
                return df
            else:
                print(f"Failed to download the PDF. Status code: {response.status_code}")

        except Exception as exc:
            print(exc)

        return None

    def filter_instruments(self, instruments_df: pd.DataFrame) -> list[Instruments]:
        """
        The instruments file has a lot of data, we just need to filter out the premiums of nifty and  banknifty
        """

        valid_instrument_type = "OPTIDX"
        valid_index = ["NSE_INDEX|Nifty 50", "NSE_INDEX|Nifty Bank"]

        valid_instruments_list: list[Instruments] = []
        for index, row in instruments_df.iterrows(): # pylint: disable=unused-variable
            instrument: Instruments = Instruments(**row)
            if instrument.instrument_type == valid_instrument_type and \
                (instrument.trading_symbol.startswith("NIFTY") or instrument.trading_symbol.startswith("BANKNIFTY")):
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

        if instruments_df is not None:
            valid_instruments_list: list[Instruments] = self.filter_instruments(instruments_df=instruments_df)

            # Convert the data model into dict so that it can be inserted into database
            valid_instruments_list = convert_model_to_dict(list_data_raw=valid_instruments_list)

            # Update/Insert the instruments into the database
            inserted_count: int = 0
            try:
                db_res = self.instruments_collection.insert_many(valid_instruments_list, ordered=False)
                inserted_count = len(db_res.inserted_ids)
            except Exception as exc:
                if isinstance(exc, BulkWriteError):
                    print(f"Skipping {len(exc.details.get('writeErrors'))} instruments as these are duplicate")
                    inserted_count = exc.details.get('nInserted')

            print("Successfuly completed scraping and storing instruments")
            print(f"Fetched instruments: {len(valid_instruments_list)}")
            print(f"Inserted instruments: {inserted_count}")
            print(f"Ignored instruments: {len(valid_instruments_list) - inserted_count}")
        else:
            print("Failed to fetch instruments from upstox")
