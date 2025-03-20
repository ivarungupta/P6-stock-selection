import numpy as np
from sklearn.naive_bayes import GaussianNB


class NaiveBayesModel:
    """
    Naive Bayes classifier for stock selection.
    """

    def __init__(self):
        self.model = GaussianNB()

    def train(self, X, y):
        """
        Train the Naive Bayes model.

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
