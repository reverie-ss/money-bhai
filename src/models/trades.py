"""
Data Model for entry requirements
"""
from pydantic import BaseModel # pylint: disable=no-name-in-module

class TradeEntry(BaseModel):
    option_type: str
    market_index: str
    quantity: int
    strike: int = None
    instrument: float = None
