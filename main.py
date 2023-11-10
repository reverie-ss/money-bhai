"""
Main module. This is where it all starts.
TODO: Move the routes to it's respective modules
"""
import json
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from src.auth.authorization import UpstoxAuthorization
from src.order.entry import EntryService
from src.scrapper.candles import CandleScrapper
from src.order.exit import ExitService
from src.scrapper.tradebook import TradebookScrapper
from src.scrapper.instruments import InstrumentsScrapper

load_dotenv()

app = FastAPI()


@app.post("/scrapper/instruments")
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

@app.get("/trade/entry/{market_index}/{option_type}")
def trade_entry(market_index: str, option_type: str):
    """
    Route used to scrap all the instruments and store in database
    """
    response = EntryService(market_index=market_index, option_type=option_type).execute()
    return response

@app.get("/authorize/upstox")
def authorize(code: str):
    """
    Route used to scrap all the instruments and store in database
    """
    response = UpstoxAuthorization().generate_access_token(code=code)
    return JSONResponse(content=json.loads(response.text), status_code=response.status_code)