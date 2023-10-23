


from src.scrapper.script import CandleScrapper
from src.utilities.enums import InstrumentKey


CandleScrapper(instrument_key=InstrumentKey.NIFTY_50.value).fetch_missing_historical_data()