import pandas as pd
from sklearn.preprocessing import StandardScaler


class ZScoreScaling:
    """
    Applies Z-score standardization to numeric features.
    """

    def __init__(self):
        self.scaler = StandardScaler()

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Standardize the data using Z-score scaling.

        :param data: DataFrame with numeric features.
        :return: Standardized DataFrame.
        """
        scaled_data = data.copy()
        numeric_cols = scaled_data.select_dtypes(include=['number']).columns
        scaled_data[numeric_cols] = self.scaler.fit_transform(scaled_data[numeric_cols])
        return scaled_data
