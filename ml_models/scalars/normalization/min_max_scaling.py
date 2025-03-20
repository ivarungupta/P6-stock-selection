import pandas as pd
from sklearn.preprocessing import MinMaxScaler as SklearnMinMaxScaler


class MinMaxScaling:
    """
    Applies Min-Max scaling to numeric features.
    """

    def __init__(self):
        self.scaler = SklearnMinMaxScaler()

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Scale the data using Min-Max scaling.

        :param data: DataFrame with numeric features.
        :return: Scaled DataFrame.
        """
        scaled_data = data.copy()
        numeric_cols = scaled_data.select_dtypes(include=['number']).columns
        scaled_data[numeric_cols] = self.scaler.fit_transform(scaled_data[numeric_cols])
        return scaled_data
