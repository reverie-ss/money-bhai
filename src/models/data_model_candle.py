"""
This module has the datamodels required for this project
"""
from datetime import datetime
from pydantic import BaseModel # pylint: disable=no-name-in-module

class Candle(BaseModel):
    """
    Data model for the candle fetched from Upstox. This is also the schema for Candles collection
    """
    ts: datetime
    meta: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class Instruments(BaseModel):
    """
    Data Model for the instruments fetched from Upstox.  This is also the schema for instruments collection
    """
    instrument_key: str
    exchange_token: float
    name: str
    last_price: float
    instrument_type: str
    exchange: str
    expiry: str
    option_type: str = None
    strike: float = None
    tick_size: float = None
    lot_size: float = None
    trading_symbol: str = None
    created_at: datetime = datetime.now()
    
class Order(BaseModel):
    """
    Data model created ion accordance with orders placed on Kite
    """
    trading_symbol: str
    trade_date: str
    trade_type: str
    quantity: int
    price: float
    trade_id: int
    order_id: int
    order_execution_time: datetime
    expiry_date: str
    instrument_token: str