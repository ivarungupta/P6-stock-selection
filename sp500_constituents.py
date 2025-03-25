"""
sp500_constituents.py

This module retrieves and processes the historical S&P 500 constituent changes
using the FMPWrapper from fmp.py. It constructs a quarterly timeline of the S&P 500 constituents
from a given output start year onward. It uses all historical changes (starting before 2005)
to build the cumulative membership but outputs snapshots only for quarters from the output start year.
"""

import pandas as pd
from datetime import datetime
from data_sources.fmp import FMPWrapper  # Adjust the import path if needed (e.g., from data_sources.fmp import FMPWrapper)
import ast

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
        Fetch the historical S&P 500 constituent change data using FMPWrapper.
        Returns:
            List of change records (each a dict).
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
        Process change records to build a quarterly timeline.
        All events (even those before 2005) are applied cumulatively.
        Only snapshots for quarters from the output_start_year onward are recorded.
        
        Each change record is expected to include:
            - "date": The effective date of the change (e.g., "2005-03-23").
            - "symbol": The ticker being added.
            - "removedTicker": (optional) The ticker being removed.
        Returns:
            A dictionary mapping quarterly boundary dates (as strings) to sorted lists of constituent tickers.
        """
        # Convert change records: add a datetime field.
        for change in changes:
            if "date" in change:
                try:
                    change["date_dt"] = pd.to_datetime(change["date"])
                except Exception as e:
                    print(f"Error parsing date in record {change}: {e}")
                    change["date_dt"] = pd.NaT
            else:
                change["date_dt"] = pd.NaT
        
        # Sort changes chronologically.
        changes_sorted = sorted(changes, key=lambda x: x["date_dt"] if x["date_dt"] is not pd.NaT else datetime.min)
        
        quarterly_dates = self.generate_quarterly_dates(f"{self.output_start_year}-01-01", f"{self.end_year}-12-31")
        timeline = {}
        current_constituents = set()
        change_index = 0
        num_changes = len(changes_sorted)
        
        for q_date in quarterly_dates:
            # Apply all change events up to (and including) the current quarterly date.
            while change_index < num_changes and changes_sorted[change_index]["date_dt"] <= q_date:
                change = changes_sorted[change_index]
                # Remove ticker if specified.
                if "removedTicker" in change and change["removedTicker"]:
                    current_constituents.discard(change["removedTicker"])
                # Add ticker (from the "symbol" field).
                if "symbol" in change and change["symbol"]:
                    current_constituents.add(change["symbol"])
                change_index += 1
            
            # Record snapshot if q_date is in our output range.
            if q_date.year >= self.output_start_year:
                timeline[q_date.strftime("%Y-%m-%d")] = sorted(list(current_constituents))
        
        return timeline

    def get_quarterly_constituents_timeline(self):
        """
        Retrieves historical data using FMPWrapper and returns a quarterly timeline of S&P 500 constituents.
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
