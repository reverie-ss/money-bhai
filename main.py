from src.scrapper.instruments import InstrumentsScrapper
# from datetime import datetime
from src.scrapper.candles import CandleScrapper
from src.order.exit import ExitService
from src.scrapper.premium import PremiumScrapper


# CandleScrapper(instrument_key="NSE_FO|40742").fetch_historical_data(
#     start_date=datetime(
#         year=2023,
#         month=10,
#         day=1
#     )
# )

# InstrumentsScrapper().scrap_and_store_instruments()
# from src.scrapper.premium import PremiumScrapper


# PremiumScrapper().fill_tradebook_from_zerodha()

from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}
