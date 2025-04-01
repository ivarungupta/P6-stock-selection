# config.py

# Date range for processing tickers
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"

# Date boundaries for splitting the data into training, validation, and test sets
TRAIN_END_DATE = "2023-01-01"  # training data: dates before this date
VAL_END_DATE = "2024-10-01"    # validation data: dates from TRAIN_END_DATE (inclusive) to VAL_END_DATE (exclusive)
