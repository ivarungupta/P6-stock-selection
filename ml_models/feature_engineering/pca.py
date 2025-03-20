import pandas as pd
from sklearn.decomposition import PCA


class PCAFeatureSelector:
    """
    Performs feature selection using Principal Component Analysis (PCA).
    """

    def __init__(self, n_components: int = 5):
        """
        Initialize the PCAFeatureSelector.

        :param n_components: Number of principal components to keep.
        """
        self.n_components = n_components
        self.pca = PCA(n_components=self.n_components)

    def select_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Transform the data using PCA and return the principal components as features.

        :param data: DataFrame with numeric features.
        :return: DataFrame with principal components.
        """
        numeric_data = data.select_dtypes(include=['number'])
        principal_components = self.pca.fit_transform(numeric_data)
        pc_columns = [f'PC{i+1}' for i in range(self.n_components)]
        return pd.DataFrame(principal_components, columns=pc_columns, index=data.index)
