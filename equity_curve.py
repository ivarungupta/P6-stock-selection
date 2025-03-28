#!/usr/bin/env python
"""
equity_curve.py

This module computes and plots the cumulative equity curve using
the quarterly_predictions.csv file. The CSV file should have two columns:
"Quarter" (in YYYY-MM-DD format) and "Top5_Tickers" (a string representation
of a list of tickers for that quarter).

For each quarter, the module pulls the market data for the recommended stocks
at the quarter start and at the next quarter's start (or a provided overall
end date for the last quarter), computes the average return, and then builds
the cumulative equity curve. Finally, it plots the curve, ensuring that
all quarters are labeled on the x-axis.
"""

import os
import ast
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from dotenv import load_dotenv
from data_sources.fmp import FMPWrapper

# Load environment variables from .env file
load_dotenv()


class EquityCurve:
    """
    A class to compute and plot the cumulative equity curve using the quarterly
    predictions from a CSV file.
    """

    def __init__(self, predictions_csv, overall_end_date, api_key, initial_equity=100):
        """
        Initialize the EquityCurve instance.

        Args:
            predictions_csv (str): Path to the quarterly_predictions.csv file.
            overall_end_date (str): End date for the last quarter (YYYY-MM-DD).
            api_key (str): API key for accessing market data.
            initial_equity (float, optional): Starting equity value. Defaults to 100.
        """
        self.predictions_csv = predictions_csv
        self.overall_end_date = pd.to_datetime(overall_end_date)
        self.api_key = api_key
        self.initial_equity = initial_equity
        self.fmp = FMPWrapper(api_key)
        self.predictions_df = self._load_predictions()

    def _load_predictions(self):
        """
        Load and preprocess the quarterly predictions CSV file.

        Returns:
            pd.DataFrame: DataFrame with 'Quarter' (datetime) and 'Top5_Tickers' (list) columns.
        """
        try:
            df = pd.read_csv(self.predictions_csv)
            # Convert Quarter column to datetime
            df['Quarter'] = pd.to_datetime(df['Quarter'])
            # Convert Top5_Tickers column from string representation of list to actual list
            df['Top5_Tickers'] = df['Top5_Tickers'].apply(ast.literal_eval)
            # Sort by Quarter ascending
            df.sort_values('Quarter', inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception as e:
            print(f"Error loading predictions CSV: {e}")
            return pd.DataFrame()

    def _get_price_on_date(self, ticker, target_date):
        """
        Retrieve the closing price for a given ticker on or before the target date.

        If the market is closed on the target date, the method uses a buffer period
        to search for the most recent available price.

        Args:
            ticker (str): Stock ticker.
            target_date (datetime): The target date.

        Returns:
            float or None: The closing price if available, otherwise None.
        """
        buffer_days = 10
        search_start = (target_date - timedelta(days=buffer_days)).strftime('%Y-%m-%d')
        search_end = target_date.strftime('%Y-%m-%d')
        try:
            df = self.fmp.get_historical_price(ticker, search_start, search_end)
            if df.empty:
                return None
            df['date'] = pd.to_datetime(df['date'])
            df = df[df['date'] <= target_date]
            if df.empty:
                return None
            # Get the latest available record
            record = df.sort_values('date').iloc[-1]
            # Use adjusted close if available, otherwise use close
            price = record.get('adjClose', record.get('close'))
            return price
        except Exception as e:
            print(f"Error fetching price for {ticker} on {target_date.strftime('%Y-%m-%d')}: {e}")
            return None

    def compute_equity_curve(self):
        """
        Compute the cumulative equity curve using the quarterly predictions.

        For each quarter, the method computes the average return across the recommended
        stocks (by comparing the price at the quarter start and at the quarter end) and
        compounds the returns.

        Returns:
            pd.DataFrame: DataFrame with columns 'QuarterEnd' and 'Equity'.
        """
        if self.predictions_df.empty:
            print("No prediction data available.")
            return pd.DataFrame()

        equity = self.initial_equity
        curve = []

        # Iterate over each row; use the current Quarter as the start date
        # and the next row's Quarter as the end date, or overall_end_date for the last row.
        for i in range(len(self.predictions_df)):
            row = self.predictions_df.iloc[i]
            quarter_start = row['Quarter']
            if i < len(self.predictions_df) - 1:
                quarter_end = self.predictions_df.iloc[i + 1]['Quarter']
            else:
                quarter_end = self.overall_end_date

            returns = []
            for ticker in row['Top5_Tickers']:
                price_start = self._get_price_on_date(ticker, quarter_start)
                price_end = self._get_price_on_date(ticker, quarter_end)
                if price_start is not None and price_end is not None and price_start != 0:
                    ret = (price_end / price_start) - 1
                    returns.append(ret)
            avg_return = np.mean(returns) if returns else 0
            equity *= (1 + avg_return)
            curve.append({
                'QuarterEnd': quarter_end,
                'Equity': equity
            })

        curve_df = pd.DataFrame(curve)
        # Sort by QuarterEnd ascending, just in case
        curve_df.sort_values('QuarterEnd', inplace=True, ignore_index=True)
        return curve_df

    def plot_equity_curve(self, equity_df):
        """
        Plot the cumulative equity curve.

        Args:
            equity_df (pd.DataFrame): DataFrame with columns 'QuarterEnd' and 'Equity'.
        """
        # Ensure QuarterEnd is a datetime
        equity_df['QuarterEnd'] = pd.to_datetime(equity_df['QuarterEnd'])

        # Sort by date in case it's out of order
        equity_df.sort_values('QuarterEnd', inplace=True, ignore_index=True)

        plt.figure(figsize=(10, 6))
        plt.plot(equity_df['QuarterEnd'], equity_df['Equity'], marker='o', linestyle='-')

        # Force the x-axis to show all QuarterEnd labels
        plt.xticks(equity_df['QuarterEnd'], equity_df['QuarterEnd'].dt.strftime('%Y-%m-%d'), rotation=45)

        plt.xlabel('Quarter End')
        plt.ylabel('Cumulative Equity')
        plt.title('Cumulative Equity Curve')
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def main():
    predictions_file = 'quarterly_predictions.csv'
    overall_end_date = '2024-12-31'  # Adjust as needed
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in environment variables.")

    equity_obj = EquityCurve(
        predictions_csv=predictions_file,
        overall_end_date=overall_end_date,
        api_key=api_key,
        initial_equity=100
    )

    equity_df = equity_obj.compute_equity_curve()
    print(equity_df)
    equity_obj.plot_equity_curve(equity_df)


if __name__ == '__main__':
    main()
