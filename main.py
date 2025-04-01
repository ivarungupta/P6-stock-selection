import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
import ast
from processing_tickers import process_tickers, get_sp500_tickers
from ml_models.scalars.normalization.min_max_scaling import MinMaxScaling
from ml_models.feature_selection.eighty_cummulative import CummulativeImportanceSelector
from ml_models.models_ml.random_forest import RandomForestModel
from ml_models.models_ml.xg_boost import XGBoostModel
from ml_models.target_engineering.five_category_division import FiveCategoryDivision
from sklearn.metrics import accuracy_score
from ml_models.hyperparameter_tuning.hyper_parameter_tuning import HyperparameterTuner
from config import START_DATE, END_DATE, TRAIN_END_DATE

def generate_quarterly_dates(start_date, end_date):
    start_dt = pd.to_datetime(start_date)
    end_dt = pd.to_datetime(end_date)
    quarterly_dates = pd.date_range(start=start_dt, end=end_dt, freq='QS').to_list()
    if start_dt not in quarterly_dates:
        quarterly_dates.insert(0, start_dt)
    return [dt.strftime('%Y-%m-%d') for dt in quarterly_dates]

def main():
    load_dotenv()
    
    # Check if the combined factors file already exists.
    if os.path.exists("final_merged_factors.csv"):
        print("Loading existing final_merged_factors.csv...")
        merged_df = pd.read_csv("final_merged_factors.csv")
    else:
        print("final_merged_factors.csv not found. Processing tickers to generate factors...")
        api_key = os.getenv("API_KEY")
        if not api_key:
            raise ValueError("API_KEY not found in .env file.")
        
        # Fetch the S&P 500 tickers using our helper function.
        tickers = get_sp500_tickers(api_key)
        # print(tickers)
        if not tickers:
            print("No S&P 500 tickers found.")
            return

        merged_df = process_tickers(tickers, api_key, START_DATE, END_DATE)

        if merged_df.empty:
            print("No factors were successfully calculated.")
            return
        
        merged_df.to_csv("final_merged_factors.csv", index=False)
        print("Saved final_merged_factors.csv")
    
    # Load the S&P 500 constituents timeline (used later for predictions).
    try:
        timeline_df = pd.read_csv("sp500_constituents_timeline.csv")
        timeline_df["date"] = pd.to_datetime(timeline_df["date"])
        timeline_df["constituents"] = timeline_df["constituents"].apply(lambda x: ast.literal_eval(x))
    except Exception as e:
        print(f"Error loading sp500_constituents_timeline.csv: {e}")
        return

    # Clean the merged factors data.
    merged_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    merged_df.fillna(method="ffill", inplace=True)
    merged_df.fillna(method="bfill", inplace=True)
    merged_df.fillna(0, inplace=True)
    
    try:
        target_engineer = FiveCategoryDivision()
        merged_df = target_engineer.create_target(merged_df)
    except Exception as e:
        print(f"Error creating target variable: {e}")
        return

    scaler = MinMaxScaling()
    try:
        scaled_df = scaler.transform(merged_df)
    except Exception as e:
        print(f"Error during scaling: {e}")
        return

    scaled_df["date"] = pd.to_datetime(scaled_df["date"])
    train_data = scaled_df[scaled_df["date"] < pd.to_datetime(TRAIN_END_DATE)].copy()
    test_data = scaled_df[scaled_df["date"] >= pd.to_datetime(TRAIN_END_DATE)].copy()
    
    X_tune = train_data.drop(columns=["date", "Ticker", "target"], errors="ignore")
    y_tune = train_data["target"]

    xgb_model = XGBoostModel()
    estimator = xgb_model.model
    param_grid = {
        'n_estimators': [50, 100, 200],
        'learning_rate': [0.01],
        'max_depth': [3]
    }
    tuner = HyperparameterTuner(estimator, param_grid, scoring='accuracy', cv=3, n_jobs=-1)
    _, best_score, best_params = tuner.tune_with_grid_search(X_tune, y_tune)
    print("Hyperparameter Tuning (Grid Search) - Best Score:", best_score)
    print("Hyperparameter Tuning (Grid Search) - Best Params:", best_params)
    xgb_model.model.set_params(**best_params)

    quarters = generate_quarterly_dates(TRAIN_END_DATE, END_DATE)
    predictions = []
    
    for i, quarter in enumerate(quarters):
        current_quarter = pd.to_datetime(quarter)
        print(f"\nProcessing quarter: {quarter}")
        
        active_rows = timeline_df[timeline_df["date"] == current_quarter]
        if not active_rows.empty:
            active_constituents = active_rows["constituents"].iloc[0]
        else:
            past = timeline_df[timeline_df["date"] < current_quarter]
            if not past.empty:
                active_constituents = past.sort_values("date").iloc[-1]["constituents"]
            else:
                active_constituents = []
        
        train_active = train_data[train_data["Ticker"].isin(active_constituents)].copy()
        if train_active.empty:
            print(f"No training data available for active constituents in quarter {quarter}. Skipping.")
            continue
        
        if i < len(quarters) - 1:
            next_quarter = pd.to_datetime(quarters[i+1])
            test_quarter = test_data[(test_data["date"] >= current_quarter) & (test_data["date"] < next_quarter)].copy()
        else:
            test_quarter = test_data[test_data["date"] >= current_quarter].copy()
        
        test_active = test_quarter[test_quarter["Ticker"].isin(active_constituents)].copy()
        if test_active.empty:
            print(f"No test data available for active constituents in quarter {quarter}. Skipping.")
            continue
        
        X_train = train_active.drop(columns=["date", "Ticker", "target"], errors="ignore")
        y_train = train_active["target"]
        rf_model = RandomForestModel()
        try:
            rf_model.train(X_train, y_train)
            feature_selector = CummulativeImportanceSelector(rf_model.model, X_train)
            selected_features = feature_selector.select_features()
        except Exception as e:
            print(f"Error in feature selection for quarter {quarter}: {e}")
            continue
        
        try:
            X_train_sel = X_train[selected_features]
            X_test_sel = test_active.drop(columns=["date", "Ticker", "target"], errors="ignore")[selected_features]
            y_test = test_active["target"]
        except Exception as e:
            print(f"Error preparing training/test sets for quarter {quarter}: {e}")
            continue
        
        try:
            xgb_model.train(X_train_sel, y_train)
            pred = xgb_model.predict(X_test_sel)
            acc = accuracy_score(y_test, pred)
            pred_proba = xgb_model.predict_proba(X_test_sel)
        except Exception as e:
            print(f"Error training/predicting XGBoost for quarter {quarter}: {e}")
            continue
        
        test_active["target_pred_proba"] = pred_proba
        test_active["target_pred"] = pred
        test_active = test_active.sort_values(by=["target_pred", "target_pred_proba"], ascending=[False, False])
        top20 = test_active["Ticker"].head(20).tolist()
        
        predictions.append(pd.DataFrame({"Quarter": [quarter], "Top20_Tickers": [top20]}))
        
        print(f"Accuracy for {quarter}: {acc}")
        print(f"Top 20 stocks for {quarter}: {top20}")
        
        train_data = train_data[train_data["Ticker"].isin(active_constituents)].copy()
        train_data = pd.concat([train_data, test_active], ignore_index=True)
    
    if predictions:
        all_predictions = pd.concat(predictions, ignore_index=True)
        try:
            all_predictions.to_csv("quarterly_predictions.csv", index=False)
            print("Saved quarterly_predictions.csv")
        except Exception as e:
            print(f"Error saving quarterly predictions: {e}")
    else:
        print("No quarterly predictions were generated.")

if __name__ == "__main__":
    main()
