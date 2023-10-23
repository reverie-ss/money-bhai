

from datetime import datetime
from src.scrapper.script import CandleScrapper
from src.utilities.enums import InstrumentKey


CandleScrapper(instrument_key=InstrumentKey.NIFTY23OCT19550PE.value).fetch_historical_data(
    start_date=datetime(
        year=2023,
        month=10,
        day=1
    )
)