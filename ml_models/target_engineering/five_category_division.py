import pandas as pd


class FiveCategoryDivision:
    """
    Performs target engineering on stock data.
    This class creates a target column by categorizing the percentage change of the 'close'
    price into five baskets. The target is then shifted one period back to serve as the prediction target.
    """

    def __init__(self, bins=None, labels=None):
        """
        Initialize the FiveCategoryDivision with specific bins and labels.

        :param bins: List of bin edges for categorizing the percentage change.
                     Default is [-inf, -10, 0, 5, 10, inf].
        :param labels: List of labels for each bin.
                       Default is [0, 1, 2, 3, 4].
        """
        if bins is None:
            bins = [-float("inf"), -10, 0, 5, 10, float("inf")]
        if labels is None:
            labels = [0, 1, 2, 3, 4]
        self.bins = bins
        self.labels = labels

    def create_target(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create a target column based on the percentage change in the 'close' price.
        The target is shifted one period back to align with prediction needs.

        :param df: DataFrame containing at least the 'close' column.
        :return: DataFrame with a new 'target' column.
        """
        df = df.copy()
        if "close" in df.columns:
            # Calculate percentage change in the close price
            df["close_change"] = df["close"].pct_change() * 100
            # Categorize the percentage change into bins
            df["target"] = pd.cut(df["close_change"], bins=self.bins, labels=self.labels)
            df.drop(columns=["close_change"], inplace=True)
        else:
            print("Column 'close' not found in DataFrame. Creating a default target column with value 0.")
            df["target"] = 0

        # Shift the target variable one timestamp back
        df["target"] = df["target"].shift(-1)
        # Drop rows with NaN target values after shifting
        df.dropna(subset=["target"], inplace=True)
        return df
