import numpy as np
from sklearn.ensemble import RandomForestClassifier


class RandomForestModel:
    """
    Random Forest classifier for stock selection.
    """

    def __init__(self, n_estimators: int = 100, random_state: int = 42):
        self.n_estimators = n_estimators
        self.random_state = random_state
        self.model = RandomForestClassifier(n_estimators=self.n_estimators,
                                            random_state=self.random_state)

    def train(self, X, y):
        """
        Train the Random Forest model.

        :param X: Feature set.
        :param y: Target labels.
        """
        self.model.fit(X, y)

    def predict(self, X) -> np.ndarray:
        """
        Predict using the trained model.

        :param X: Feature set.
        :return: Predictions.
        """
        return self.model.predict(X)
