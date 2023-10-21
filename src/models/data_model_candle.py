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