#!/usr/bin/env python
"""
equity_curve.py

This module computes and plots the cumulative equity curve using
the quarterly_predictions.csv file. It now also computes the S&P500 equity curve
(using '^GSPC' as the ticker) so that both curves are plotted together for comparison.
The S&P500 curve uses a base price from January 2020, and the strategy curve now also
includes an initial row at 2020-01-01 with equity set to 100.
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
    def __init__(self, predictions_csv, overall_end_date, api_key, initial_equity=100):
        self.predictions_csv = predictions_csv
        self.overall_end_date = pd.to_datetime(overall_end_date)
        self.api_key = api_key
        self.initial_equity = initial_equity
        self.fmp = FMPWrapper(api_key)
        self.predictions_df = self._load_predictions()

    def _load_predictions(self):
        try:
            df = pd.read_csv(self.predictions_csv)
            df['Quarter'] = pd.to_datetime(df['Quarter'])
            df['Top20_Tickers'] = df['Top20_Tickers'].apply(ast.literal_eval)
            df.sort_values('Quarter', inplace=True)
            df.reset_index(drop=True, inplace=True)
            return df
        except Exception as e:
            print(f"Error loading predictions CSV: {e}")
            return pd.DataFrame()

    def _get_price_on_date(self, ticker, target_date):
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
            record = df.sort_values('date').iloc[-1]
            price = record.get('adjClose', record.get('close'))
            return price
        except Exception as e:
            print(f"Error fetching price for {ticker} on {target_date.strftime('%Y-%m-%d')}: {e}")
            return None

    def compute_equity_curve(self, strategy_start_date="2020-01-01"):
        if self.predictions_df.empty:
            print("No prediction data available.")
            return pd.DataFrame()

        strategy_start = pd.to_datetime(strategy_start_date)
        equity = self.initial_equity
        curve = []
        
        # Prepend the starting row.
        curve.append({'QuarterEnd': strategy_start, 'Equity': equity})

        for i in range(len(self.predictions_df)):
            row = self.predictions_df.iloc[i]
            quarter_start = row['Quarter']
            if quarter_start < strategy_start:
                continue
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
        curve_df.sort_values('QuarterEnd', inplace=True, ignore_index=True)
        return curve_df

    def compute_sp500_curve(self, strategy_start_date="2020-01-01"):
        strategy_start = pd.to_datetime(strategy_start_date)
        pred_dates = sorted(self.predictions_df['Quarter'].tolist())
        timeline = []
        if strategy_start < pred_dates[0]:
            timeline.append(strategy_start)
        timeline.extend(pred_dates)
        if timeline[-1] != self.overall_end_date:
            timeline.append(self.overall_end_date)

        initial_sp500_price = self._get_price_on_date('^GSPC', strategy_start)
        if initial_sp500_price is None:
            print("Could not retrieve S&P500 price for the strategy start date.")
            return pd.DataFrame()

        sp500_curve = []
        for date in timeline:
            sp500_price = self._get_price_on_date('^GSPC', date)
            if sp500_price is None:
                print(f"Could not get S&P500 price for {date}. Skipping this date.")
                continue
            equity = (sp500_price / initial_sp500_price) * self.initial_equity
            sp500_curve.append({
                'QuarterEnd': date,
                'SP500_Equity': equity
            })

        sp500_df = pd.DataFrame(sp500_curve)
        sp500_df.sort_values('QuarterEnd', inplace=True, ignore_index=True)
        return sp500_df

    def plot_equity_comparison(self, equity_df, sp500_df):
        equity_df['QuarterEnd'] = pd.to_datetime(equity_df['QuarterEnd'])
        sp500_df['QuarterEnd'] = pd.to_datetime(sp500_df['QuarterEnd'])

        plt.figure(figsize=(10, 6))
        plt.plot(equity_df['QuarterEnd'], equity_df['Equity'], marker='o', linestyle='-', label='Strategy')
        plt.plot(sp500_df['QuarterEnd'], sp500_df['SP500_Equity'], marker='o', linestyle='-', label='S&P500')
        plt.xticks(equity_df['QuarterEnd'], equity_df['QuarterEnd'].dt.strftime('%Y-%m-%d'), rotation=45)
        plt.xlabel('Quarter End')
        plt.ylabel('Cumulative Equity')
        plt.title('Cumulative Equity Curve Comparison')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()


def main():
    predictions_file = 'quarterly_predictions.csv'
    overall_end_date = '2024-12-31'
    api_key = os.getenv('API_KEY')
    if not api_key:
        raise ValueError("API_KEY not found in environment variables.")

    equity_obj = EquityCurve(
        predictions_csv=predictions_file,
        overall_end_date=overall_end_date,
        api_key=api_key,
        initial_equity=100
    )

    strategy_equity_df = equity_obj.compute_equity_curve(strategy_start_date="2020-01-01")
    print("Strategy Equity Curve:")
    print(strategy_equity_df)

    sp500_equity_df = equity_obj.compute_sp500_curve(strategy_start_date="2020-01-01")
    print("S&P500 Equity Curve:")
    print(sp500_equity_df)

    equity_obj.plot_equity_comparison(strategy_equity_df, sp500_equity_df)


if __name__ == '__main__':
    main()
