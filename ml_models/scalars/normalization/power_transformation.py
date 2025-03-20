import pandas as pd
from sklearn.preprocessing import PowerTransformer


class PowerTransformation:
    """
    Applies power transformation to numeric features.
    """

    def __init__(self, method: str = 'yeo-johnson'):
        self.transformer = PowerTransformer(method=method)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data using power transformation.

        :param data: DataFrame with numeric features.
        :return: Transformed DataFrame.
        """
        transformed_data = data.copy()
        numeric_cols = transformed_data.select_dtypes(include=['number']).columns
        transformed_data[numeric_cols] = self.transformer.fit_transform(
            transformed_data[numeric_cols]
        )
        return transformed_data
