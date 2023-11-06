from src.scrapper.instruments import InstrumentsScrapper
# from datetime import datetime
from src.scrapper.candles import CandleScrapper
from src.order.exit import ExitService
from src.scrapper.tradebook import PremiumScrapper, TradebookScrapper


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


@app.get("/scrapper/instruments")
def scrap_instruments():
    """
    Route used to scrap all the instruments and store in database
    """
    response = InstrumentsScrapper().scrap_and_store_instruments()
    return response


@app.get("/scrapper/tradebook")
def scrap_tradebook():
    """
    Route used to scrap all the instruments and store in database
    """
    response = TradebookScrapper().fill_tradebook_from_zerodha()
    return response
