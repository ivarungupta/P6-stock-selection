import pandas as pd
from sklearn.preprocessing import QuantileTransformer


class QuantileTransformation:
    """
    Applies quantile transformation to numeric features.
    """

    def __init__(self, output_distribution: str = 'uniform'):
        self.transformer = QuantileTransformer(output_distribution=output_distribution)

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data using quantile transformation.

        :param data: DataFrame with numeric features.
        :return: Transformed DataFrame.
        """
        transformed_data = data.copy()
        numeric_cols = transformed_data.select_dtypes(include=['number']).columns
        transformed_data[numeric_cols] = self.transformer.fit_transform(
            transformed_data[numeric_cols]
        )
        return transformed_data
