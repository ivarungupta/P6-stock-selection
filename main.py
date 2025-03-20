import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

import pandas as pd
import concurrent.futures
from data_sources.fmp import FMPWrapper
from models.factors import FactorsWrapper

# Import ML pipeline components
from ml_models.scalars.normalization.min_max_scaling import MinMaxScaling
from ml_models.feature_engineering.pca import PCAFeatureSelector
from ml_models.models_ml.random_forest import RandomForestModel
from ml_models.target_engineering.five_category_division import FiveCategoryDivision
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def process_ticker(ticker, api_key, start_date, end_date):
    try:
        fmp = FMPWrapper(api_key)
        factors_wrapper = FactorsWrapper(ticker, fmp, start_date, end_date)
        factors = factors_wrapper.calculate_all_factors()

        # Extract quality factors for a common date reference
        quality_factors = factors.get("quality", pd.DataFrame())
        if quality_factors.empty:
            print(f"No quality factors found for {ticker}. Skipping.")
            return pd.DataFrame()

        merged_factors = quality_factors[["date"]].copy()
        merged_factors["Ticker"] = ticker

        for factor_category, factor_values in factors.items():
            if isinstance(factor_values, pd.DataFrame) and "date" in factor_values.columns:
                factor_values = factor_values.sort_values(by="date")
                factor_values = factor_values.ffill()
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


def main():
    # Read tickers from CSV
    tickers_df = pd.read_csv("Tickers.csv")
    tickers = tickers_df["Symbol"].tolist()

    print("Total No of Stocks:", len(tickers))
    print("First few Stock Symbols:", tickers[:20])

    # Get API key from the environment variable
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env file.")

    start_date = "2022-01-01"
    end_date = "2023-12-31"

    merged_factors_list = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {
            executor.submit(process_ticker, ticker, api_key, start_date, end_date): ticker
            for ticker in tickers[:20]  # Limited for testing
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
        master_df = pd.concat(merged_factors_list, ignore_index=True)

        output_csv = "final_merged_factors.csv"
        master_df.to_csv(output_csv, index=False)
        print(f"\nFinal merged factors saved to {output_csv}")

        # Use the FiveCategoryDivision class to create a target column
        target_engineer = FiveCategoryDivision()
        master_df = target_engineer.create_target(master_df)

        # ML pipeline processing
        scaler = MinMaxScaling()
        scaled_df = scaler.transform(master_df)

        # Feature engineering using PCA
        pca_selector = PCAFeatureSelector(n_components=5)
        features_df = pca_selector.select_features(scaled_df)

        # Prepare features and target
        X = features_df.drop(columns=["target"], errors="ignore")
        y = master_df["target"]

        # Train Random Forest model
        model = RandomForestModel()
        # Perform train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model.train(X_train, y_train)
        predictions = model.predict(X_test)
        # Calculate accuracy
        print("Predictions:", predictions)
        accuracy = accuracy_score(y_test, predictions)
        print("Model accuracy:", accuracy)
    else:
        print("No factors were successfully calculated.")


if __name__ == "__main__":
    main()
