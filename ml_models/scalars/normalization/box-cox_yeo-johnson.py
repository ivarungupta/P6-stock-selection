import numpy as np
import pandas as pd
from scipy.stats import boxcox
from sklearn.preprocessing import PowerTransformer


class BoxCoxYeoJohnsonScaler:
    """
    Applies Box-Cox transformation if data is positive, otherwise applies Yeo-Johnson.
    """

    def transform(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data using Box-Cox or Yeo-Johnson transformation.

        :param data: DataFrame with numeric features.
        :return: Transformed DataFrame.
        """
        transformed_data = data.copy()
        for column in transformed_data.select_dtypes(include=['number']).columns:
            if (transformed_data[column] > 0).all():
                transformed_data[column] = boxcox(transformed_data[column] + 1e-6)[0]
            else:
                pt = PowerTransformer(method='yeo-johnson')
                transformed_data[column] = pt.fit_transform(
                    transformed_data[[column]]
                ).flatten()
        return transformed_data
