import pandas as pd 
from data_sources.fmp import FMPWrapper
from models.factors import FactorsWrapper

def main():
    tickers_df = pd.read_csv('Tickers.csv')
    tickers = tickers_df['Symbol'].tolist()
    
    print("Total No of Stocks:", len(tickers))
    print("First few Stock Symbols:", tickers[:2])
    
    api_key = "bEiVRux9rewQy16TXMPxDqBAQGIW8UBd"
    fmp = FMPWrapper(api_key)
        
    start_date = "2021-01-01"  
    end_date = "2022-12-31"    
    master_df = pd.DataFrame()
    for ticker in tickers[:10]:
        # print(f"\nProcessing ticker: {ticker}")
        factors_wrapper = FactorsWrapper(ticker, fmp, start_date, end_date)
        # merged_factors = pd.DataFrame()
        factors = factors_wrapper.calculate_all_factors()
        # Extract the quality factors DataFrame to use its date columns as the reference
        quality_factors = factors.get("quality", pd.DataFrame())
        if quality_factors.empty:
            print("No quality factors found. Exiting.")
            return

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
                print(f"Skipping {factor_category} as it does not contain a valid DataFrame with a 'date' column.")
        
        # Filter the merged factors DataFrame based on the start_date and end_date
        merged_factors = merged_factors[
            (merged_factors["date"] >= start_date) & (merged_factors["date"] <= end_date)
        ]

        # Print the final merged DataFrame
        print("\n--- FINAL MERGED FACTORS ---")
        print(merged_factors.head())
    
        # Append the merged factors for the current ticker to the master DataFrame
        master_df = pd.concat([master_df, merged_factors], ignore_index=True)

    # Save the final merged DataFrame to a CSV file
    output_csv = "final_merged_factors.csv"
    master_df.to_csv(output_csv, index=False)
    print(f"\nFinal merged factors saved to {output_csv}")

    # print(merged_factors)
if __name__ == "__main__":
    main()


