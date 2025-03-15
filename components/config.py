import finnhub
import os
import dotenv
import datetime
dotenv.load_dotenv()
# ---------------------------------------
# Replace with your actual Finnhub API key
# ---------------------------------------
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
FINNCLIENT = finnhub.Client(api_key=FINNHUB_API_KEY)
STARTDATE ="2021-01-01"