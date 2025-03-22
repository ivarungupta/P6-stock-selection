import numpy as np
import pandas as pd

class CummulativeImportanceSelector:
    """
    Selects features from a stocks DataFrame based on cumulative importance.
    It supports models with `feature_importances_` or `coef_` attributes.
    """

    def __init__(self, model, df, threshold=0.80):
        """
        Initialize the FeatureImportanceSelector instance.

        :param model: Trained model with 'feature_importances_' or 'coef_' attribute.
        :param df: pandas DataFrame containing stocks data where columns correspond to features.
        :param threshold: Cumulative importance threshold (default is 0.80).
        """
        self.model = model
        self.df = df
        self.threshold = threshold
        self._validate_inputs()

    def _validate_inputs(self):
        """
        Validate the inputs provided to the instance.

        Raises:
            AttributeError: If the model does not have a recognized importance attribute.
            ValueError: If threshold is not between 0 and 1, or if the number of features
                        does not match the number of importance scores.
        """
        if hasattr(self.model, "feature_importances_"):
            self.importance_type = "feature_importances_"
        elif hasattr(self.model, "coef_"):
            self.importance_type = "coef_"
        else:
            raise AttributeError(
                "The provided model does not have 'feature_importances_' or 'coef_' attribute."
            )

        if not (0 < self.threshold <= 1):
            raise ValueError("Threshold must be between 0 and 1.")

        features = self.df.columns.tolist()
        if self.importance_type == "feature_importances_":
            importances = self.model.feature_importances_
        else:
            # For coef_, take absolute values and average if multi-dimensional.
            importances = np.abs(self.model.coef_)
            if importances.ndim > 1:
                importances = importances.mean(axis=0)
        if len(importances) != len(features):
            raise ValueError("Mismatch between number of features and importance scores.")

    def select_features(self):
        """
        Select features based on cumulative feature importance.

        Returns:
            list: A list of feature names that cumulatively contribute to at least the
                  specified threshold of the total importance.
        """
        features = self.df.columns.tolist()

        if self.importance_type == "feature_importances_":
            importances = self.model.feature_importances_
        else:
            importances = np.abs(self.model.coef_)
            if importances.ndim > 1:
                importances = importances.mean(axis=0)

        total_importance = np.sum(importances)
        # Normalize importance scores if they do not sum to 1.
        if not np.isclose(total_importance, 1.0):
            importances = importances / total_importance

        # Pair each feature with its importance and sort in descending order.
        feature_importance_pairs = sorted(
            zip(features, importances), key=lambda x: x[1], reverse=True
        )

        selected_features = []
        cumulative_importance = 0.0

        for feature, importance in feature_importance_pairs:
            selected_features.append(feature)
            cumulative_importance += importance
            if cumulative_importance >= self.threshold:
                break

        return selected_features

# Example usage:
if __name__ == "__main__":
    from sklearn.linear_model import LogisticRegression

    # Create a dummy stocks dataframe with some factor columns.
    data = {
        'factor1': [0.1, 0.2, 0.3, 0.4],
        'factor2': [0.4, 0.3, 0.2, 0.1],
        'factor3': [0.2, 0.2, 0.2, 0.2],
        'factor4': [0.3, 0.3, 0.3, 0.3]
    }
    df = pd.DataFrame(data)
    X = df.values
    y = [0, 1, 0, 1]

    # Train a simple logistic regression model.
    model = LogisticRegression(random_state=42, max_iter=1000)
    model.fit(X, y)

    # Use FeatureImportanceSelector to obtain features with cumulative importance >= 80%.
    selector = CummulativeImportanceSelector(model, df, threshold=0.80)
    selected_features = selector.select_features()
    print("Selected features:", selected_features)
