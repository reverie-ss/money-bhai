import pymongo
import os
import requests
import time
from dateutil import parser
from datetime import datetime, timedelta
from dotenv import load_dotenv
from src.models.data_model_candle import Candle
from src.utilities.enums import InstrumentKey

load_dotenv()


class InstrumentsScrapper:

    def __init__(self) -> None:
        client = pymongo.MongoClient(os.environ.get("MONGO_URL"))
        database = client.get_database(os.environ.get("DATABASE"))
        self.candles_collection = database.get_collection("MinuteCandles")

        self.url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.csv.gz"

    def fetch_instruments(self):
        """
        Fetch the latest list of instruments from the upstox url and store it in the database
        """
        try:

            response = requests.get(self.url, timeout=60)

            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Specify the local file path where you want to save the downloaded file
                local_file_path = "downloaded_file.pdf"

                # Open the local file in binary write mode and write the content of the downloaded file
                with open(local_file_path, "wb") as file:
                    file.write(response.content)

                print(f"File downloaded and saved as {local_file_path}")
            else:
                print(f"Failed to download the file. Status code: {response.status_code}")
        except Exception as exc:
            print(exc)


