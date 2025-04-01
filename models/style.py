import pandas as pd
import numpy as np

class Style:
    """
    A class to calculate style-related market factors.
    """
    def __init__(self, df, sp500_returns, tickers):
        self.df = df.copy()
        self.sp500_returns = sp500_returns.copy()
        self.tickers = tickers
        self.required_columns = {'close', 'volume', 'date'}
        self._validate_columns()

    def _validate_columns(self):
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    def calculate_beta(self, window_size=62):
        # Compute stock returns from self.df.
        stock_returns = self.df[['date', 'close']].copy()
        stock_returns['stock_return'] = stock_returns['close'].pct_change()
        # Ensure sp500_returns has a 'date' column and a 'market_return' column.
        market_returns = self.sp500_returns.copy()
        if 'changePercent' in market_returns.columns:
            market_returns = market_returns.rename(columns={'changePercent': 'market_return'})
        # Merge on date.
        merged_df = pd.merge(stock_returns, market_returns, on='date', how='left')
        merged_df.fillna(0, inplace=True)
        merged_df.set_index('date', inplace=True)
        # Compute rolling beta.
        def calc_beta(window):
            market_var = np.var(window['market_return'])
            if market_var == 0:
                return np.nan
            return np.cov(window['stock_return'], window['market_return'])[0, 1] / market_var
        beta_series = merged_df[['stock_return','market_return']].rolling(window=window_size).apply(
            lambda x: calc_beta(pd.DataFrame(x.reshape(-1, 2), columns=['stock_return','market_return'])),
            raw=True
        )
        # Use the stock_return column as beta; reindex to self.df dates.
        beta_series = beta_series['stock_return']
        beta_series = beta_series.reindex(self.df['date']).ffill()
        return beta_series

    # to be changed
    # def calculate_liquidity(self, window=60):
    #     return self.df['volume'].rolling(window=window).mean()

    # to be changed
    def calculate_growth(self, window=252):
        """
        Calculate growth as the cumulative log return over the window.
        This is computed as: log(close) - log(close.shift(window)).
        """
        return np.log(self.df['close']) - np.log(self.df['close'].shift(window))

    # to be changed
    def calculate_momentum(self, window=252):
        """
        Calculate momentum as the percentage change from 'window' days ago.
        This is computed as: (close / close.shift(window)) - 1.
        """
        return self.df['close'].pct_change(periods=window)

    def calculate_all_factors(self):
        try:
            all_factors = self.df[['date']].copy()
            all_factors['beta'] = self.calculate_beta()
            all_factors['growth'] = self.calculate_growth()
            all_factors['momentum'] = self.calculate_momentum()
            return all_factors
        except Exception as e:
            print(f"Error calculating style factors: {e}")
            return pd.DataFrame()
