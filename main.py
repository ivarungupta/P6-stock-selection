import os
from dotenv import load_dotenv
import pandas as pd
from processing_tickers import process_tickers

# Import ML pipeline components
from ml_models.scalars.normalization.min_max_scaling import MinMaxScaling
# from ml_models.feature_engineering.pca import PCAFeatureSelector
from ml_models.feature_selection.eighty_cummulative import CummulativeImportanceSelector
from ml_models.models_ml.random_forest import RandomForestModel
from ml_models.models_ml.xg_boost import XGBoostModel
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
        # print(scaled_df.shape)
        #feature selection, taking top 80% cummulative feature 
        rf_model = RandomForestModel()
        X = scaled_df.drop(columns=['date',"Ticker","target"], errors="ignore")
        y = scaled_df["target"].values
        rf_model.train(X, y)
        feature_selector = CummulativeImportanceSelector(rf_model.model, scaled_df.drop(columns=['date',"Ticker","target"], errors="ignore"))
        selected_features = feature_selector.select_features()
        # print("Total features:", len(scaled_df.columns)-3)
        # print("Selected features:", selected_features)
        # print("Total features selected:", len(selected_features))
        features_df = scaled_df[["date","Ticker"]+selected_features + ["target"]]

        #  making a 75% train test split
        train_df = features_df[features_df["date"] < "2023-04-01"]
        val_df = features_df[(features_df["date"] >= "2023-04-01") & (features_df["date"] < "2023-10-01")]
        test_df = features_df[features_df["date"] >= "2023-10-01"]
        # Prepare features and target for ML model training
        X_train = train_df.drop(columns=["date","Ticker","target"], errors="ignore")
        y_train = train_df["target"]
        X_test = val_df.drop(columns=["date","Ticker","target"], errors="ignore")
        y_test = val_df["target"]

        xgb_model = XGBoostModel()
        xgb_model.train(X_train, y_train)
        predictions = xgb_model.predict(X_test)
        # print("Predictions:", predictions)
        accuracy = accuracy_score(y_test, predictions)
        # print("Model accuracy:", accuracy)

        # creating the portfolio for the next quarter
        test_new_df = test_df.drop(columns=["date","Ticker","target"], errors="ignore")
        predictions = xgb_model.predict(test_new_df)
        # print("Predictions:", predictions)
        # print("Predictions shape:", type(predictions))
        pred_proba = xgb_model.predict_proba(test_new_df)
        test_df["target_pred_proba"] = pred_proba
        test_df["target_pred"] = predictions
        # Sort test_df by target_pred and then by target_pred_proba in descending order
        test_df = test_df.sort_values(by=["target_pred", "target_pred_proba"], ascending=[False, False])
        print("Top 5 stocks for next quarter:")
        print(test_df['Ticker'].head(5))

    else:
        print("No factors were successfully calculated.")

if __name__ == "__main__":
    main()

'''
Optimizing the ML parameters
Optimizing the factors
'''