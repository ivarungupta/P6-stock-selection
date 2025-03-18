# Import the FMPWrapper class
import pandas as pd
import numpy as np
from data_sources.fmp import FMPWrapper

# Initialize the FMPWrapper with your API key
api_key = "bEiVRux9rewQy16TXMPxDqBAQGIW8UBd"
fmp = FMPWrapper(api_key)

# Step 1: Read the tickers from your Tickers.csv file
tickers_df = pd.read_csv('Tickers.csv')
tickers = tickers_df['Symbol'].tolist()

# Step 2: Display the number of tickers and the first few tickers
print("Total No of Stocks:", len(tickers))
print("First few Stock Symbols:", tickers[:10])

# Example: Fetch historical price data for the first ticker
historical_data = fmp.get_historical_price(tickers[0], start_date="2021-01-01", end_date="2021-01-10")
print(historical_data)