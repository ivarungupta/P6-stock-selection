"""
sp500_constituents.py

This module retrieves and processes the current S&P 500 constituent data
using the FMPWrapper from fmp.py. The new endpoint returns an array of constituent records,
each with a "dateFirstAdded" field indicating when the company was added.
This module builds a quarterly timeline of S&P 500 constituents based on their addition dates,
recording snapshots only for quarters from the output_start_year onward.
"""

import pandas as pd
from datetime import datetime
from data_sources.fmp import FMPWrapper

class SP500Constituents:
    def __init__(self, api_key, output_start_year=2004, end_year=2024):
        """
        Initialize with the API key and desired output year range.
        Although the API data starts earlier, snapshots will be recorded
        only for quarters from the output_start_year onward.
        """
        self.api_key = api_key
        self.output_start_year = output_start_year
        self.end_year = end_year
        self.fmp = FMPWrapper(api_key)
    
    def fetch_historical_data(self):
        """
        Fetch the current S&P 500 constituent data using FMPWrapper.
        Returns:
            List of constituent records (each a dict).
        """
        data = self.fmp.get_sp500_constituent()
        return data

    def generate_quarterly_dates(self, start_date, end_date):
        """
        Generate a list of quarterly boundary dates (as Timestamps) between start_date and end_date.
        """
        quarterly_dates = pd.date_range(start=pd.to_datetime(start_date), end=pd.to_datetime(end_date), freq='QS').to_list()
        return quarterly_dates

    def process_quarterly_changes(self, changes):
        """
        Process constituent records to build a quarterly timeline.
        Each record is expected to include:
            - "dateFirstAdded": The effective date the constituent was added.
            - "symbol": The ticker symbol.
        Returns:
            A dictionary mapping quarterly boundary dates (as strings) to sorted lists of constituent tickers.
        """
        # Convert each record's "dateFirstAdded" to a datetime field.
        for record in changes:
            if "dateFirstAdded" in record:
                try:
                    record["date_dt"] = pd.to_datetime(record["dateFirstAdded"])
                except Exception as e:
                    print(f"Error parsing date in record {record}: {e}")
                    record["date_dt"] = pd.NaT
            else:
                record["date_dt"] = pd.NaT
        
        # Sort records chronologically.
        changes_sorted = sorted(changes, key=lambda x: x["date_dt"] if pd.notnull(x["date_dt"]) else datetime.min)
        
        quarterly_dates = self.generate_quarterly_dates(f"{self.output_start_year}-01-01", f"{self.end_year}-12-31")
        timeline = {}
        current_constituents = set()
        change_index = 0
        num_changes = len(changes_sorted)
        
        for q_date in quarterly_dates:
            # Apply all addition events up to (and including) the current quarterly date.
            while change_index < num_changes and changes_sorted[change_index]["date_dt"] <= q_date:
                record = changes_sorted[change_index]
                if "symbol" in record and record["symbol"]:
                    current_constituents.add(record["symbol"])
                change_index += 1
            
            # Record snapshot if the quarter is within our output range.
            if q_date.year >= self.output_start_year:
                timeline[q_date.strftime("%Y-%m-%d")] = sorted(list(current_constituents))
        
        return timeline

    def get_quarterly_constituents_timeline(self):
        """
        Retrieves constituent data using FMPWrapper and returns a quarterly timeline of S&P 500 constituents.
        Returns:
            A dictionary where keys are quarterly boundary dates (as strings) and values are sorted lists of tickers.
        """
        data = self.fetch_historical_data()
        timeline = self.process_quarterly_changes(data)
        return timeline

if __name__ == "__main__":
    # Example usage:
    API_KEY = "bEiVRux9rewQy16TXMPxDqBAQGIW8UBd"  # Replace with your API key if needed.
    sp500 = SP500Constituents(API_KEY, output_start_year=2005, end_year=2025)
    timeline = sp500.get_quarterly_constituents_timeline()
    
    # Convert the timeline dictionary into a DataFrame and save as CSV.
    timeline_df = pd.DataFrame(list(timeline.items()), columns=["date", "constituents"])
    timeline_df = timeline_df.sort_values(by="date")
    timeline_df.to_csv("sp500_constituents_timeline.csv", index=False)
    print("Saved sp500_constituents_timeline.csv")
