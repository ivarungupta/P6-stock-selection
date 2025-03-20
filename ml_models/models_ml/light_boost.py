import numpy as np
import lightgbm as lgb


class LightBoostModel:
    """
    LightGBM classifier for stock selection.
    """

    def __init__(self, params: dict = None, num_boost_round: int = 100,
                 random_state: int = 42):
        if params is None:
            params = {
                'objective': 'binary',
                'learning_rate': 0.1,
                'num_leaves': 31,
                'metric': 'binary_logloss'
            }
        self.params = params
        self.num_boost_round = num_boost_round
        self.random_state = random_state
        self.model = None

    def train(self, X, y):
        """
        Train the LightGBM model.

        :param X: Feature set.
        :param y: Target labels.
        """
        train_data = lgb.Dataset(X, label=y)
        self.model = lgb.train(self.params, train_data, num_boost_round=self.num_boost_round)

    def predict(self, X) -> np.ndarray:
        """
        Predict using the trained model.

        :param X: Feature set.
        :return: Predictions.
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet.")
        preds = self.model.predict(X)
        return (preds > 0.5).astype(int)
