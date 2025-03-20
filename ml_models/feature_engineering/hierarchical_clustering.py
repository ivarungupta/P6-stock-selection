import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster


class HierarchicalClustering:
    """
    Performs feature selection using hierarchical clustering.
    """

    def __init__(self, method: str = 'ward', threshold: float = 1.0):
        """
        Initialize the HierarchicalClustering object.

        :param method: Linkage method to use.
        :param threshold: Threshold to cut the dendrogram.
        """
        self.method = method
        self.threshold = threshold

    def select_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Select a subset of features based on hierarchical clustering.

        :param data: DataFrame with numeric features.
        :return: DataFrame with selected features.
        """
        # Compute correlation-based distance
        corr_matrix = data.corr().abs()
        distance_matrix = 1 - corr_matrix
        Z = linkage(distance_matrix, method=self.method)
        clusters = fcluster(Z, t=self.threshold, criterion='distance')

        # Pick one feature per cluster
        feature_clusters = {}
        for feature, cluster_label in zip(data.columns, clusters):
            if cluster_label not in feature_clusters:
                feature_clusters[cluster_label] = feature

        selected_features = list(feature_clusters.values())
        return data[selected_features]
