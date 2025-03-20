import pandas as pd
import concurrent.futures
from data_sources.fmp import FMPWrapper
from models.factors import FactorsWrapper

def process_ticker(ticker, api_key, start_date, end_date):
    try:
        fmp = FMPWrapper(api_key)
        factors_wrapper = FactorsWrapper(ticker, fmp, start_date, end_date)
        factors = factors_wrapper.calculate_all_factors()

        # Extract the quality factors DataFrame to use its date columns as the reference
        quality_factors = factors.get("quality", pd.DataFrame())
        if quality_factors.empty:
            print(f"No quality factors found for {ticker}. Skipping.")
            return pd.DataFrame()

        # Initialize the final merged DataFrame with the date column from quality factors
        merged_factors = quality_factors[["date"]].copy()
        merged_factors['Ticker'] = ticker

        # Iterate through all factor categories and merge them based on the date column
        for factor_category, factor_values in factors.items():
            if isinstance(factor_values, pd.DataFrame) and "date" in factor_values.columns:
                # Sort the factor DataFrame by date to ensure proper alignment
                factor_values = factor_values.sort_values(by="date")

                # Forward fill missing values to handle dates without specific factor values
                factor_values = factor_values.ffill()

                # Ensure all dates in the quality factors are present in the factor DataFrame
                factor_values = pd.merge(
                    merged_factors[["date"]],
                    factor_values,
                    on="date",
                    how="outer"
                ).ffill()

                # Merge the factor DataFrame with the merged_factors DataFrame on the date column
                merged_factors = pd.merge(
                    merged_factors,
                    factor_values,
                    on="date",
                    how="left",
                )
            else:
                print(f"Skipping {factor_category} for {ticker} as it does not contain a valid DataFrame with a 'date' column.")

        # Filter the merged factors DataFrame based on the start_date and end_date
        merged_factors = merged_factors[
            (merged_factors["date"] >= start_date) & (merged_factors["date"] <= end_date)
        ]

        return merged_factors

    except Exception as e:
        print(f"Error processing {ticker}: {e}")
        return pd.DataFrame()

def main():
    # Read tickers
    tickers_df = pd.read_csv('Tickers.csv')
    tickers = tickers_df['Symbol'].tolist()

    print("Total No of Stocks:", len(tickers))
    print("First few Stock Symbols:", tickers[:20])

    api_key = "bEiVRux9rewQy16TXMPxDqBAQGIW8UBd"
    start_date = "2022-01-01"
    end_date = "2023-12-31"

    # List to store results from all tickers
    merged_factors_list = []

    # Use ProcessPoolExecutor for parallel processing
    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {
            executor.submit(process_ticker, ticker, api_key, start_date, end_date): ticker
            for ticker in tickers[:20]  # Limit to first 10 tickers for testing
        }
        for future in concurrent.futures.as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                result = future.result()
                if not result.empty:
                    merged_factors_list.append(result)
            except Exception as e:
                print(f"Error processing {ticker}: {e}")

    # Combine all results into a single DataFrame
    if merged_factors_list:

        master_df = pd.concat(merged_factors_list, ignore_index=True)

        # Save the final merged DataFrame to a CSV file
        output_csv = "final_merged_factors.csv"
        master_df.to_csv(output_csv, index=False)
        print(f"\nFinal merged factors saved to {output_csv}")
    else:
        print("No factors were successfully calculated.")


    # print(merged_factors)
if __name__ == "__main__":
    main()


