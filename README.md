# P6-stock-selection

## File-Structure 
```
├── data_sources/
│   ├── data_sources.txt
│   └── fmp.py
├── ml_models/
│   ├── ml.txt
│   ├── feature_engineering/
│   │   ├── hierarchical_clustering.py
│   │   ├── pca.py
│   │   └── t-SNE_UMAP.py
│   ├── models-ml/
│   │   ├── ada_boost.py
│   │   ├── cat_boost.py
│   │   ├── gradient_boost.py
│   │   ├── light_boost.py
│   │   ├── logistic_regression.py
│   │   ├── naive_bayes.py
│   │   ├── random_forest.py
│   │   ├── svc.py
│   │   └── xg_boost.py
│   ├── scalars/
│   │   ├── normalization/
│   │   │   ├── box-cox_yeo-johnson.py
│   │   │   ├── log_transformation.py
│   │   │   ├── mean_normalization.py
│   │   │   ├── min_max_scaling.py
│   │   │   ├── power_transformation.py
│   │   │   ├── quantile_transformation.py
│   │   │   ├── sigmoid_normalization.py
│   │   │   └── tanh_normalization.py
│   │   └── standardization/
│   │       ├── robust_scaling.py
│   │       └── zscore_scaling.py
│   ├── feature_engineering/
│   │   └── eighty_cummulative.py
│   ├── target_engineering/
│   │   └── five_category_division.py
│   └── ml.txt
├── models/
│   ├── factors.py
│   ├── emotional.py
│   ├── growth.py
│   ├── momentum.py
│   ├── quality.py
│   ├── risk.py
│   ├── stock.py
│   ├── style.py
│   ├── technical.py
│   └── value.py
├── optimization/
│   └── opt.txt
├── .env
├── .gitignore
├── config.py
├── main.py
├── sp500_constituents.py
├── equity_curve.py
├── sp500_constituents_timeline.csv
├── main.txt
├── final_merged_factors.csv
├── readme.md
└── tickers.csv

```
