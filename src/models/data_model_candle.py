from datetime import datetime
from pydantic import BaseModel

class Candle(BaseModel):
    ts: datetime
    meta: str
    open: float
    high: float
    low: float
    close: float
    volume: float


class Instruments(BaseModel):
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
    