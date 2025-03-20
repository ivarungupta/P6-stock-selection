import numpy as np
from sklearn.ensemble import GradientBoostingClassifier


class GradientBoostModel:
    """
    Gradient Boosting classifier for stock selection.
    """

    def __init__(self, n_estimators: int = 100, learning_rate: float = 0.1,
                 random_state: int = 42):
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.random_state = random_state
        self.model = GradientBoostingClassifier(n_estimators=self.n_estimators,
                                                learning_rate=self.learning_rate,
                                                random_state=self.random_state)

    def train(self, X, y):
        """
        Train the Gradient Boosting model.

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
