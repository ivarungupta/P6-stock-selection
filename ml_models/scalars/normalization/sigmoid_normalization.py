import numpy as np
import pandas as pd


class SigmoidNormalization:
    """
    Applies sigmoid normalization to numeric features.
    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data using sigmoid function.

        :param data: DataFrame with numeric features.
        :return: Transformed DataFrame.
        """
        transformed_data = data.copy()
        numeric_cols = transformed_data.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            transformed_data[col] = 1 / (1 + np.exp(-transformed_data[col]))
        return transformed_data
