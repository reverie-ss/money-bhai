


from src.scrapper.script import CandleScrapper
from src.utilities.enums import InstrumentKey


res = CandleScrapper(instrument_key=InstrumentKey.NIFTY_50.value).fetch_historical_data_multiple_days()