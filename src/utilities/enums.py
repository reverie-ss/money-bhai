from enum import Enum

class InstrumentKey(Enum):
    NIFTY_50 = "NSE_INDEX|Nifty 50"
    BANK_NIFTY = "NSE_INDEX|Nifty Bank"
    BANKNIFTY23O1844400CE = "NSE_FO|48237"
    NIFTY23N0219600CE = "NSE_FO|50112"
    NIFTY23O1919500CE = "NSE_FO|44452"
    BANKNIFTY23O1844200CE = "NSE_FO|48233"
    NIFTY23OCT19550PE = "NSE_FO|67303"

class HTTP_Method(Enum): # pylint: disable=invalid-name
    GET = "GET"
    PUT = "PUT"
    POST = "POST"

class UpstoxEndpoint(Enum):
    PLACE_ORDER="/order/place" # API to place an order
    FETCH_ORDERS="/order/retrieve-all" # API to retrieve the list of a orders placed for the current day
    FETCH_QUOTES="/market-quote/quotes"