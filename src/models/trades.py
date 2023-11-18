from pydantic import BaseModel

class TradeEntry(BaseModel):
    option_type: str
    market_index: str
    quantity: int
    strike: int = None
    instrument: float = None
