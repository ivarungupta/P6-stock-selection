import os
from dotenv import load_dotenv
import pandas as pd
from processing_tickers import process_tickers

# Import ML pipeline components
from ml_models.scalars.normalization.min_max_scaling import MinMaxScaling
from ml_models.feature_engineering.pca import PCAFeatureSelector
from ml_models.models_ml.random_forest import RandomForestModel
from ml_models.target_engineering.five_category_division import FiveCategoryDivision
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

def main():
    # Load environment variables
    load_dotenv()

    # Read tickers from CSV file
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

    # Process tickers using the dedicated processing_tickers module
    merged_df = process_tickers(tickers, api_key, start_date, end_date)
    
    if not merged_df.empty:
        output_csv = "final_merged_factors.csv"
        merged_df.to_csv(output_csv, index=False)
        print(f"\nFinal merged factors saved to {output_csv}")

        # Create target column using the FiveCategoryDivision class
        target_engineer = FiveCategoryDivision()
        merged_df = target_engineer.create_target(merged_df)

        # Apply scaling using MinMaxScaling
        scaler = MinMaxScaling()
        scaled_df = scaler.transform(merged_df)

        # Perform feature engineering using PCA
        pca_selector = PCAFeatureSelector(n_components=5)
        features_df = pca_selector.select_features(scaled_df)

        # Prepare features and target for ML model training
        X = features_df.drop(columns=["target"], errors="ignore")
        y = merged_df["target"]

        # Train Random Forest model
        model = RandomForestModel()
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model.train(X_train, y_train)
        predictions = model.predict(X_test)
        print("Predictions:", predictions)
        accuracy = accuracy_score(y_test, predictions)
        print("Model accuracy:", accuracy)
    else:
        print("No factors were successfully calculated.")

if __name__ == "__main__":
    main()
