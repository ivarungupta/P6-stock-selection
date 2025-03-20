import numpy as np
from sklearn.linear_model import LogisticRegression


class LogisticRegressionModel:
    """
    Logistic Regression classifier for stock selection.
    """

    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = LogisticRegression(random_state=self.random_state, max_iter=1000)

    def train(self, X, y):
        """
        Train the Logistic Regression model.

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
