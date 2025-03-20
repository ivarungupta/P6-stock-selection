import pandas as pd
from sklearn.manifold import TSNE

try:
    import umap
except ImportError:
    umap = None


class TSNEUMAPFeatureSelector:
    """
    Performs dimensionality reduction using t-SNE or UMAP.
    """

    def __init__(self, n_components: int = 2, method: str = 'tsne'):
        """
        Initialize the TSNEUMAPFeatureSelector.

        :param n_components: Number of dimensions to reduce to.
        :param method: Dimensionality reduction method ('tsne' or 'umap').
        """
        self.n_components = n_components
        self.method = method.lower()
        if self.method == 'tsne':
            self.reducer = TSNE(n_components=self.n_components)
        elif self.method == 'umap':
            if umap is None:
                raise ImportError("UMAP is not installed. Please install umap-learn.")
            self.reducer = umap.UMAP(n_components=self.n_components)
        else:
            raise ValueError("Method must be 'tsne' or 'umap'.")

    def select_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Reduce the dimensionality of the data.

        :param data: DataFrame with numeric features.
        :return: DataFrame with reduced dimensions.
        """
        numeric_data = data.select_dtypes(include=['number'])
        reduced = self.reducer.fit_transform(numeric_data)
        columns = [f'{self.method.upper()}_{i+1}' for i in range(self.n_components)]
        return pd.DataFrame(reduced, columns=columns, index=data.index)
