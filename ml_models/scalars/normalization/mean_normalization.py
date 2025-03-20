import pandas as pd


class MeanNormalization:
    """
    Applies mean normalization to numeric features.
    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Mean normalize the data.

        :param data: DataFrame with numeric features.
        :return: Normalized DataFrame.
        """
        normalized_data = data.copy()
        numeric_cols = normalized_data.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            col_mean = normalized_data[col].mean()
            col_range = normalized_data[col].max() - normalized_data[col].min()
            if col_range != 0:
                normalized_data[col] = (normalized_data[col] - col_mean) / col_range
        return normalized_data
