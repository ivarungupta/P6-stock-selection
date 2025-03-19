# # main.py

# import pandas as pd
# from data_sources.fmp import FMPWrapper
# from models.factors import FactorsWrapper

# def main():
#     # Read tickers from your CSV file (make sure 'Tickers.csv' is in your project root)
#     tickers_df = pd.read_csv('Tickers.csv')
#     tickers = tickers_df['Symbol'].tolist()
    
#     print("Total No of Stocks:", len(tickers))
#     print("First few Stock Symbols:", tickers[:10])
    
#     # Initialize the FMPWrapper with your API key (you could also import this from credentials.py)
#     api_key = "bEiVRux9rewQy16TXMPxDqBAQGIW8UBd"
#     fmp = FMPWrapper(api_key)
    
#     # This list will store a merged dictionary of factors for each ticker.
#     merged_factors_list = []
    
#     # Process each ticker (you could modify this to process a subset if desired)
#     for ticker in tickers:
#         print(f"\nProcessing ticker: {ticker}")
#         try:
#             # Instantiate the FactorsWrapper for the ticker.
#             factors_wrapper = FactorsWrapper(ticker, fmp)
            
#             # Calculate all factors (returned as a dictionary grouped by category).
#             factors = factors_wrapper.calculate_all_factors()
            
#             # Merge the results from each category into a single dictionary.
#             merged_factors = {"Ticker": ticker}
#             for category, factor_values in factors.items():
#                 if isinstance(factor_values, dict):
#                     merged_factors.update(factor_values)
#                 elif hasattr(factor_values, "to_dict"):
#                     try:
#                         # Assuming a one-row DataFrame, convert it to a dictionary.
#                         row = factor_values.to_dict("records")[0]
#                         merged_factors.update(row)
#                     except Exception as e:
#                         merged_factors[category] = f"Error converting DataFrame: {e}"
#                 else:
#                     merged_factors[category] = factor_values
            
#             merged_factors_list.append(merged_factors)
#         except Exception as e:
#             print(f"Error processing ticker {ticker}: {e}")
    
#     # Create a DataFrame from the list of merged dictionaries.
#     merged_df = pd.DataFrame(merged_factors_list)
    
#     # Save the DataFrame to a CSV file.
#     output_csv = "merged_factors.csv"
#     merged_df.to_csv(output_csv, index=False)
    
#     print(f"\nMerged factors saved to {output_csv}")
#     print(merged_df.head())

# if __name__ == "__main__":
#     main()

# main.py

import pandas as pd
from data_sources.fmp import FMPWrapper
from models.factors import FactorsWrapper

def main():
    # Read tickers from your CSV file (make sure 'Tickers.csv' is in your project root)
    tickers_df = pd.read_csv('Tickers.csv')
    tickers = tickers_df['Symbol'].tolist()
    
    # Process only the first two tickers
    tickers = tickers[:2]
    
    print("Processing the following tickers:", tickers)
    
    # Initialize the FMPWrapper with your API key.
    api_key = "bEiVRux9rewQy16TXMPxDqBAQGIW8UBd"
    fmp = FMPWrapper(api_key)
    
    # This list will store a merged dictionary of factors for each ticker.
    merged_factors_list = []
    
    for ticker in tickers:
        print(f"\nProcessing ticker: {ticker}")
        try:
            # Instantiate the FactorsWrapper for the ticker.
            factors_wrapper = FactorsWrapper(ticker, fmp)
            
            # Calculate all factors (returned as a dictionary grouped by category).
            factors = factors_wrapper.calculate_all_factors()
            
            # Merge the results from each category into a single dictionary.
            merged_factors = {"Ticker": ticker}
            for category, factor_values in factors.items():
                if isinstance(factor_values, dict):
                    merged_factors.update(factor_values)
                elif hasattr(factor_values, "to_dict"):
                    try:
                        # Assuming a one-row DataFrame, convert it to a dictionary.
                        row = factor_values.to_dict("records")[0]
                        merged_factors.update(row)
                    except Exception as e:
                        merged_factors[category] = f"Error converting DataFrame: {e}"
                else:
                    merged_factors[category] = factor_values
            
            merged_factors_list.append(merged_factors)
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")
    
    # Create a DataFrame from the list of merged dictionaries.
    merged_df = pd.DataFrame(merged_factors_list)
    
    # Save the DataFrame to a CSV file.
    output_csv = "merged_factors.csv"
    merged_df.to_csv(output_csv, index=False)
    
    print(f"\nMerged factors saved to {output_csv}")
    print(merged_df.head())

if __name__ == "__main__":
    main()

