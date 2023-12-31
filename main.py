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
from src.order.order_manager import ManageOrder
from src.scrapper.candles import CandleScrapper, SyncInstrumentCandles
from src.order.exit import ExitService
from src.scrapper.tradebook import TradebookScrapper
from src.scrapper.instruments import InstrumentsScrapper
from src.models.trades import TradeEntry

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

@app.get("/scrapper/sync-order-instruments")
def scrap_sync_order_instruments():
    """
    Route used to scrap all the instruments and store in database
    """
    SyncInstrumentCandles().fetch_all_order_instruments()
    return JSONResponse(content="Synced Successfully", status_code=200)

@app.get("/scrapper/sync-indexes")
def scrap_sync_index_instruments():
    """
    Route used to scrap all the instruments and store in database
    """
    SyncInstrumentCandles().scrap_index_candles()
    return JSONResponse(content="Synced Successfully", status_code=200)


@app.get("/scrapper/candle/{instrument_key}")
def scrap_candles(instrument_key: str):
    """
    Route used to scrap all the instruments and store in database
    """
    response = CandleScrapper(instrument_key=instrument_key).fetch_missing_historical_data()
    return JSONResponse(content=json.loads(response.text), status_code=response.status_code)

@app.get("/trade/exit/")
def trade_exit():
    """
    Route used to scrap all the instruments and store in database
    """
    ExitService(
        stop_loss_percent=5,
        trailing_percent=3
    ).start_trailing()
    return "Successful", 200

@app.post("/trade/entry")
def trade_enter(trade_entry: TradeEntry):
    """
    Route used to scrap all the instruments and store in database
    """
    response = EntryService(trade_entry=trade_entry).execute()
    return JSONResponse(content=json.loads(response.text), status_code=response.status_code)

@app.get("/order/sync-history")
def fetch_order_history():
    """
    Route used to scrap all the orders for the day and store in database
    """
    response = ManageOrder().fetch_current_day_orders()
    return JSONResponse(content=json.loads(response.text), status_code=response.status_code)

@app.get("/authorize/upstox")
def authorize(code: str):
    """
    Route used to scrap all the instruments and store in database
    """
    response = UpstoxAuthorization().generate_access_token(code=code)
    return JSONResponse(content=json.loads(response.text), status_code=response.status_code)