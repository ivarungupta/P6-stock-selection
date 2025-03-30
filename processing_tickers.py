import os
import pandas as pd
import concurrent.futures
from data_sources.fmp import FMPWrapper
from models.factors import FactorsWrapper
from sp500_constituents import SP500Constituents

def process_ticker(ticker, api_key, start_date, end_date):
    """
    Processes a single ticker:
      - Instantiates FMPWrapper and FactorsWrapper.
      - Calculates all factors and merges them (using the quality factors’ dates as a base).
      - Filters the merged data by the given date range.
    """
    try:
        fmp = FMPWrapper(api_key)
        factors_wrapper = FactorsWrapper(ticker, fmp, start_date, end_date)
        factors = factors_wrapper.calculate_all_factors()

        quality_factors = factors.get("quality", pd.DataFrame())
        if quality_factors.empty:
            print(f"No quality factors found for {ticker}. Skipping.")
            return pd.DataFrame()

        merged_factors = quality_factors[["date"]].copy()
        merged_factors["Ticker"] = ticker

        for factor_category, factor_values in factors.items():
            if isinstance(factor_values, pd.DataFrame) and "date" in factor_values.columns:
                factor_values = factor_values.sort_values(by="date").ffill()
                factor_values = pd.merge(
                    merged_factors[["date"]],
                    factor_values,
                    on="date",
                    how="outer"
                ).ffill()
                merged_factors = pd.merge(
                    merged_factors,
                    factor_values,
                    on="date",
                    how="left",
                )
            else:
                print(f"Skipping {factor_category} for {ticker} as it does not contain a valid DataFrame with a 'date' column.")

        merged_factors = merged_factors[(merged_factors["date"] >= start_date) & (merged_factors["date"] <= end_date)]
        return merged_factors

    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return pd.DataFrame()

def process_tickers(tickers, api_key, start_date, end_date, max_workers=10):
    """
    Processes multiple tickers concurrently and concatenates the results.
    """
    merged_factors_list = []
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
        future_to_ticker = {
            executor.submit(process_ticker, ticker, api_key, start_date, end_date): ticker
            for ticker in tickers
        }
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                if not result.empty:
                    merged_factors_list.append(result)
            except Exception as e:
                print(f"Error processing {ticker}: {e}")
                
    if merged_factors_list:
        return pd.concat(merged_factors_list, ignore_index=True)
    else:
        return pd.DataFrame()

def get_sp500_tickers(api_key):
    """
    Uses the SP500Constituents class to fetch the quarterly timeline of constituents,
    and returns the latest quarter’s ticker list.
    """
    sp500 = SP500Constituents(api_key)
    timeline = sp500.get_quarterly_constituents_timeline()
    if timeline:
        latest_date = max(timeline.keys())
        return timeline[latest_date]
    else:
        return []

# if __name__ == "__main__":
#     import argparse

#     parser = argparse.ArgumentParser(
#         description="Process S&P 500 tickers and generate merged factors."
#     )
#     parser.add_argument("--start_date", type=str, default="2022-01-01", help="Start date for processing.")
#     parser.add_argument("--end_date", type=str, default="2023-12-31", help="End date for processing.")
#     args = parser.parse_args()

#     api_key = os.getenv("API_KEY")
#     if not api_key:
#         raise ValueError("API_KEY not found in .env file.")

#     tickers = get_sp500_tickers(api_key)

#     if not tickers:
#         print("No S&P 500 tickers found.")
#         exit(1)

#     merged_df = process_tickers(tickers, api_key, args.start_date, args.end_date)
#     if not merged_df.empty:
#         output_csv = "final_merged_factors.csv"
#         merged_df.to_csv(output_csv, index=False)
#         print(f"Final merged factors saved to {output_csv}")
#     else:
#         print("No factors were successfully calculated.")
