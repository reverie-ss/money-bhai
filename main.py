"""
Main module. This is where it all starts.
TODO: Move the routes to it's respective modules
"""
from datetime import datetime
from fastapi import FastAPI
from src.scrapper.candles import CandleScrapper
from src.order.exit import ExitService
from src.scrapper.tradebook import TradebookScrapper
from src.scrapper.instruments import InstrumentsScrapper

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


@app.get("/scrapper/candle/{instrument_key}")
def scrap_candles(instrument_key: str):
    """
    Route used to scrap all the instruments and store in database
    """
    response = CandleScrapper(instrument_key=instrument_key).fetch_missing_historical_data()
    return response

@app.get("/trade/exit/{instrument_key}")
def trade_exit(instrument_key: str):
    """
    Route used to scrap all the instruments and store in database
    """
    ExitService(instrument_key=instrument_key).start_trailing()
    return "Successful", 200