import os
from dotenv import load_dotenv
import pandas as pd
from processing_tickers import process_tickers

from ml_models.scalars.normalization.min_max_scaling import MinMaxScaling
# from ml_models.feature_engineering.pca import PCAFeatureSelector
from ml_models.feature_selection.eighty_cummulative import CummulativeImportanceSelector
from ml_models.models_ml.random_forest import RandomForestModel
from ml_models.models_ml.xg_boost import XGBoostModel
from ml_models.target_engineering.five_category_division import FiveCategoryDivision
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split

# Import date configuration
from config import START_DATE, END_DATE, TRAIN_END_DATE, VAL_END_DATE

def main():
    load_dotenv()
    
    tickers_df = pd.read_csv("Tickers.csv")
    tickers = tickers_df["Symbol"].tolist()
    print("Total No of Stocks:", len(tickers))
    print("First few Stock Symbols:", tickers[:20])

    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env file.")

    merged_df = process_tickers(tickers, api_key, START_DATE, END_DATE)
    
    if not merged_df.empty:
        output_csv = "final_merged_factors.csv"
        merged_df.to_csv(output_csv, index=False)
        print(f"\nFinal merged factors saved to {output_csv}")

        target_engineer = FiveCategoryDivision()
        merged_df = target_engineer.create_target(merged_df)

        scaler = MinMaxScaling()
        scaled_df = scaler.transform(merged_df)
        # Feature selection using cumulative importance
        rf_model = RandomForestModel()
        X = scaled_df.drop(columns=['date', "Ticker", "target"], errors="ignore")
        y = scaled_df["target"].values
        rf_model.train(X, y)
        feature_selector = CummulativeImportanceSelector(rf_model.model, scaled_df.drop(columns=['date', "Ticker", "target"], errors="ignore"))
        selected_features = feature_selector.select_features()
        
        features_df = scaled_df[["date", "Ticker"] + selected_features + ["target"]]

        # Use the imported configuration dates to split the data
        train_df = features_df[features_df["date"] < TRAIN_END_DATE]
        val_df = features_df[(features_df["date"] >= TRAIN_END_DATE) & (features_df["date"] < VAL_END_DATE)]
        test_df = features_df[features_df["date"] >= VAL_END_DATE]

        X_train = train_df.drop(columns=["date", "Ticker", "target"], errors="ignore")
        y_train = train_df["target"]
        X_test = val_df.drop(columns=["date", "Ticker", "target"], errors="ignore")
        y_test = val_df["target"]

        xgb_model = XGBoostModel()
        xgb_model.train(X_train, y_train)
        predictions = xgb_model.predict(X_test)
        accuracy = accuracy_score(y_test, predictions)

        # Create the portfolio for the next quarter using test set
        test_new_df = test_df.drop(columns=["date", "Ticker", "target"], errors="ignore")
        predictions = xgb_model.predict(test_new_df)
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
