import os
from dotenv import load_dotenv
import pandas as pd
import ast
from processing_tickers import process_tickers

from ml_models.scalars.normalization.min_max_scaling import MinMaxScaling
from ml_models.feature_selection.eighty_cummulative import CummulativeImportanceSelector
from ml_models.models_ml.random_forest import RandomForestModel
from ml_models.models_ml.xg_boost import XGBoostModel
from ml_models.target_engineering.five_category_division import FiveCategoryDivision
from sklearn.metrics import accuracy_score

# Import date configuration
from config import START_DATE, END_DATE, TRAIN_END_DATE

def generate_quarterly_dates(start_date, end_date):
    """
    Generate a list of quarterly boundary dates (formatted as YYYY-MM-DD)
    between start_date and end_date.
    """
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    quarterly_dates = pd.date_range(start=start_dt, end=end_dt, freq='QS').to_list()
    if start_dt not in quarterly_dates:
        quarterly_dates.insert(0, start_dt)
    return [dt.strftime('%Y-%m-%d') for dt in quarterly_dates]

def main():
    load_dotenv()
    
    # Load the S&P 500 constituents timeline CSV.
    # This file contains rows with "date" and "constituents" (a string representation of a list).
    timeline_df = pd.read_csv("sp500_constituents_timeline.csv")
    timeline_df["date"] = pd.to_datetime(timeline_df["date"])
    timeline_df["constituents"] = timeline_df["constituents"].apply(lambda x: ast.literal_eval(x))
    
    # Derive the ticker universe from the timeline.
    ticker_set = set()
    for constituents in timeline_df["constituents"]:
        ticker_set.update(constituents)
    # For now, limit to 20 tickers (alphabetically sorted)
    universe = sorted(list(ticker_set))[:20]
    print("Derived Ticker Universe (20 tickers):", universe)
    
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise ValueError("API_KEY not found in .env file.")
    
    # Process tickers (the derived universe) over the full period.
    merged_df = process_tickers(universe, api_key, START_DATE, END_DATE)
    if merged_df.empty:
        print("No factors were successfully calculated.")
        return
    merged_df.to_csv("final_merged_factors.csv", index=False)
    print("Saved final_merged_factors.csv")
    
    # Create target variable and scale the data.
    target_engineer = FiveCategoryDivision()
    merged_df = target_engineer.create_target(merged_df)
    scaler = MinMaxScaling()
    scaled_df = scaler.transform(merged_df)
    scaled_df["date"] = pd.to_datetime(scaled_df["date"])
    
    # Define training and test splits.
    train_data = scaled_df[scaled_df["date"] < pd.to_datetime(TRAIN_END_DATE)].copy()
    test_data = scaled_df[scaled_df["date"] >= pd.to_datetime(TRAIN_END_DATE)].copy()
    
    # Generate quarterly dates for the prediction period.
    quarters = generate_quarterly_dates(TRAIN_END_DATE, END_DATE)
    
    predictions = []
    xgb_model = XGBoostModel()
    
    # Loop through each quarter in the prediction period.
    for i, quarter in enumerate(quarters):
        current_quarter = pd.to_datetime(quarter)
        print(f"\nProcessing quarter: {quarter}")
        
        # Determine active constituents for the current quarter from the timeline.
        active_rows = timeline_df[timeline_df["date"] == current_quarter]
        if not active_rows.empty:
            active_constituents = active_rows["constituents"].iloc[0]
        else:
            past = timeline_df[timeline_df["date"] < current_quarter]
            if not past.empty:
                active_constituents = past.sort_values("date").iloc[-1]["constituents"]
            else:
                active_constituents = []
        
        # Filter training data: retain only records whose tickers are active in this quarter.
        train_active = train_data[train_data["Ticker"].isin(active_constituents)].copy()
        if train_active.empty:
            print(f"No training data available for active constituents in quarter {quarter}. Skipping.")
            continue
        
        # Define test data for the current quarter.
        if i < len(quarters) - 1:
            next_quarter = pd.to_datetime(quarters[i+1])
            test_quarter = test_data[(test_data["date"] >= current_quarter) & (test_data["date"] < next_quarter)].copy()
        else:
            test_quarter = test_data[test_data["date"] >= current_quarter].copy()
        # Filter test data to only include active tickers.
        test_active = test_quarter[test_quarter["Ticker"].isin(active_constituents)].copy()
        if test_active.empty:
            print(f"No test data available for active constituents in quarter {quarter}. Skipping.")
            continue
        
        # Re-run feature selection on the current active training data.
        X_train = train_active.drop(columns=["date", "Ticker", "target"], errors="ignore")
        y_train = train_active["target"]
        rf_model = RandomForestModel()
        rf_model.train(X_train, y_train)
        feature_selector = CummulativeImportanceSelector(rf_model.model, X_train)
        selected_features = feature_selector.select_features()
        
        # Prepare datasets using selected features.
        X_train_sel = X_train[selected_features]
        X_test_sel = test_active.drop(columns=["date", "Ticker", "target"], errors="ignore")[selected_features]
        y_test = test_active["target"]
        
        # Train XGBoost model and predict on current quarter.
        xgb_model.train(X_train_sel, y_train)
        pred = xgb_model.predict(X_test_sel)
        acc = accuracy_score(y_test, pred)
        pred_proba = xgb_model.predict_proba(X_test_sel)
        
        test_active["target_pred_proba"] = pred_proba
        test_active["target_pred"] = pred
        test_active = test_active.sort_values(by=["target_pred", "target_pred_proba"], ascending=[False, False])
        top5 = test_active["Ticker"].head(5).tolist()
        
        predictions.append(pd.DataFrame({"Quarter": [quarter], "Top5_Tickers": [top5]}))
        
        print(f"Accuracy for {quarter}: {acc}")
        print(f"Top 5 stocks for {quarter}: {top5}")
        
        # Update training data for next quarter: keep only active tickers and append current quarter's test data.
        train_data = train_data[train_data["Ticker"].isin(active_constituents)].copy()
        train_data = pd.concat([train_data, test_active], ignore_index=True)
    
    # Save the quarterly predictions.
    if predictions:
        all_predictions = pd.concat(predictions, ignore_index=True)
        all_predictions.to_csv("quarterly_predictions.csv", index=False)
        print("Saved quarterly_predictions.csv")
    else:
        print("No quarterly predictions were generated.")

if __name__ == "__main__":
    main()
