import numpy as np
import pandas as pd


class LogTransformation:
    """
    Applies log transformation to numeric features.
    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data using log transformation.

        :param data: DataFrame with numeric features.
        :return: Transformed DataFrame.
        """
        transformed_data = data.copy()
        for column in transformed_data.select_dtypes(include=['number']).columns:
            transformed_data[column] = np.log(transformed_data[column] + 1e-6)
        return transformed_data
