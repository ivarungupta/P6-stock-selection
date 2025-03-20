import numpy as np
from sklearn.svm import SVC


class SVCModel:
    """
    Support Vector Classifier for stock selection.
    """

    def __init__(self, kernel: str = 'rbf', probability: bool = True, random_state: int = 42):
        self.kernel = kernel
        self.random_state = random_state
        self.model = SVC(kernel=self.kernel, probability=probability, random_state=self.random_state)

    def train(self, X, y):
        """
        Train the SVC model.

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
