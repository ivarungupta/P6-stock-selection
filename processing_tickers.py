import os
import pandas as pd
import concurrent.futures
from data_sources.fmp import FMPWrapper
from models.factors import FactorsWrapper

def process_ticker(ticker, api_key, start_date, end_date):
    """
    Processes a single ticker:
      - Creates an instance of FMPWrapper and FactorsWrapper.
      - Calculates all factors.
      - Merges quality factors with all other factors by matching on the date.
      - Filters the merged dataframe by the specified date range.
    Returns a DataFrame containing the processed factors for the ticker.
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
                # Merge using outer join to ensure all dates are captured
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

        merged_factors = merged_factors[
            (merged_factors["date"] >= start_date) & (merged_factors["date"] <= end_date)
        ]
        return merged_factors

    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return pd.DataFrame()


def process_tickers(tickers, api_key, start_date, end_date, max_workers=10):
    """
    Processes multiple tickers concurrently:
      - Uses a ProcessPoolExecutor with a maximum of max_workers.
      - Only the first 20 tickers in the provided list are processed.
      - Collects the individual processed DataFrames and concatenates them.
    Returns a single merged DataFrame for all tickers.
    """
    # tickers = tickers[:20]
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


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Process tickers and generate merged factors."
    )
    parser.add_argument(
        "--tickers_file",
        type=str,
        default="Tickers.csv",
        help="Path to the CSV file containing tickers.",
    )
    parser.add_argument(
        "--start_date", type=str, default="2022-01-01", help="Start date for processing."
    )
    parser.add_argument(
        "--end_date", type=str, default="2023-12-31", help="End date for processing."
    )
    args = parser.parse_args()

    tickers_df = pd.read_csv(args.tickers_file)
    tickers = tickers_df["Symbol"].tolist()

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env file.")

    merged_df = process_tickers(tickers, api_key, args.start_date, args.end_date)
    if not merged_df.empty:
        output_csv = "final_merged_factors.csv"
        merged_df.to_csv(output_csv, index=False)
        print(f"Final merged factors saved to {output_csv}")
    else:
        print("No factors were successfully calculated.")
