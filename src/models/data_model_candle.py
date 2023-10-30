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
    tradingsymbol: str
    name: str
    last_price: float
    expiry: str
    strike: float
    tick_size: float
    lot_size: float
    instrument_type: str
    option_type: str
    exchange: str
    created_at: datetime = datetime.now()
    