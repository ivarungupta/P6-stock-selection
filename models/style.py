import pandas as pd
import numpy as np

class Style:
    """
    A class to calculate style-related market factors.
    
    Attributes:
        df (pd.DataFrame): DataFrame containing OHLCV market data
        sp500_returns (pd.DataFrame): DataFrame containing S&P 500 returns
        tickers (list): List of ticker symbols
    """
    def __init__(self, df, sp500_returns, tickers):
        self.df = df
        self.sp500_returns = sp500_returns
        self.tickers = tickers
        self.required_columns = {'close', 'volume'}
        self._validate_columns()

    def _validate_columns(self):
        """Validate required columns are present in the DataFrame"""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")

    def calculate_beta(self, window_size=62, step_size=62):
        """
        Calculate beta using rolling windows
        
        Args:
            window_size (int): Size of rolling window in days
            step_size (int): Step size for non-overlapping windows
        """
        style_factors = pd.DataFrame(index=self.df.index)
        
        for ticker in self.tickers:
            # Get stock returns
            stock_returns = self.df[['date','close']].copy()
            stock_returns['close'] = stock_returns['close'].pct_change()
            # Merge with market returns
            merged_df = pd.merge(
                stock_returns,
                self.sp500_returns,
                on='date',
                how='outer'
            )
            merged_df.fillna(0)
            merged_df.set_index('date', inplace=True)
            
            # Calculate rolling betas
            betas = []
            for start in range(0, len(merged_df) - window_size + 1, step_size):
                end = start + window_size
                stock_window = merged_df['close'].iloc[start:end]
                market_window = merged_df['changePercent'].iloc[start:end]
                
                # Compute beta for window
                beta = (np.cov(stock_window, market_window)[0, 1] / 
                       np.var(market_window)) if len(stock_window) > 1 else np.nan
                
                # Extend beta value for the whole window
                betas.extend([beta] * (end - start))
            
            # Adjust beta length to match DataFrame
            if len(merged_df) > len(betas):
                betas = np.append(betas, np.full((len(merged_df) - len(betas),), betas[-1]))
            elif len(merged_df) < len(betas):
                betas = betas[:len(merged_df)]
            
            # Assign betas to style factors
            style_factors['beta'] = betas
            
        return style_factors

    def calculate_liquidity(self, window=60):
        """Calculate liquidity using volume moving average"""
        style_factors = pd.DataFrame(index=self.df.index)
        
        for ticker in self.tickers:
            liquidity = (self.df['volume']
                        .rolling(window=window)
                        .mean())
            style_factors['liquidity'] = liquidity
            
        return style_factors

    def calculate_growth(self, window=60):
        """Calculate price growth over window"""
        style_factors = pd.DataFrame(index=self.df.index)
        
        for ticker in self.tickers:
            growth = (self.df['close']
                     .pct_change()
                     .rolling(window=window)
                     .sum())
            style_factors['growth'] = growth
            
        return style_factors

    def calculate_momentum(self, window=60):
        """Calculate price momentum"""
        style_factors = pd.DataFrame(index=self.df.index)
        
        for ticker in self.tickers:
            momentum = (self.df['close']
                       .pct_change()
                       .rolling(window=window)
                       .mean())
            style_factors['momentum'] = momentum
            
        return style_factors

    def calculate_all_factors(self):
        """Calculate all style factors"""
        try:
            # Initialize results DataFrame
            all_factors = pd.DataFrame(index=self.df.index)
                
                # Calculate individual factors
            beta_factors = self.calculate_beta()
            liquidity_factors = self.calculate_liquidity()
            growth_factors = self.calculate_growth()
            momentum_factors = self.calculate_momentum()
                
            # Combine all factors
            all_factors['date'] = self.df['date']
            all_factors['beta'] = beta_factors['beta']
            all_factors['liquidity'] = liquidity_factors['liquidity']
            all_factors['growth'] = growth_factors['growth']
            all_factors['momentum'] = momentum_factors['momentum']
                
            return all_factors
            
        except Exception as e:
            print(f"Error calculating style factors: {e}")
            return pd.DataFrame()