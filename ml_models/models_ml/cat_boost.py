import numpy as np
from catboost import CatBoostClassifier


class CatBoostModel:
    """
    CatBoost classifier for stock selection.
    """

    def __init__(self, iterations: int = 100, random_state: int = 42, verbose: bool = False):
        self.iterations = iterations
        self.random_state = random_state
        self.verbose = verbose
        self.model = CatBoostClassifier(iterations=self.iterations,
                                        random_state=self.random_state,
                                        verbose=self.verbose)

    def train(self, X, y):
        """
        Train the CatBoost model.

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
