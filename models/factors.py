import pandas as pd
import numpy as np
 
 
class Quality:
    """
    A class to calculate quality-related financial factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing the financial data
        required_columns (set): Set of required columns for calculations
    """
 
    def __init__(self, income_data, balance_data, cash_flow_data, prev_income_data=None):
        """
        Initialize Quality class with financial data.
 
        Args:
            income_data (pd.DataFrame): Income statement data
            balance_data (pd.DataFrame): Balance sheet data
            cash_flow_data (pd.DataFrame): Cash flow statement data
            prev_income_data (pd.DataFrame, optional): Previous period income data
        """
        self.income_data = income_data
        self.balance_data = balance_data
        self.cash_flow_data = cash_flow_data
        self.prev_income_data = prev_income_data
        self.required_columns = {
            'income': {'netIncome', 'revenue', 'grossProfit'},
            'balance': {'totalStockholdersEquity', 'totalAssets', 'totalLiabilities'},
            'cash_flow': {'operatingCashFlow'}
        }
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrames."""
        missing_cols = []
        for col in self.required_columns['income']:
            if col not in self.income_data.columns:
                missing_cols.append(f"Income: {col}")
        for col in self.required_columns['balance']:
            if col not in self.balance_data.columns:
                missing_cols.append(f"Balance: {col}")
        for col in self.required_columns['cash_flow']:
            if col not in self.cash_flow_data.columns:
                missing_cols.append(f"Cash Flow: {col}")
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
 
    def calculate_net_profit_to_revenue(self):
        """Calculate net profit to total revenue ratio."""
        return (self.income_data['netIncome'].iloc[0] / 
                self.income_data['revenue'].iloc[0])
 
    def calculate_decm(self):
        """Calculate Debt to Equity Capital Market ratio."""
        return (self.balance_data['totalLiabilities'].iloc[0] / 
                self.balance_data['totalAssets'].iloc[0])
 
    def calculate_roe(self):
        """Calculate Return on Equity (ROE)."""
        return (self.income_data['netIncome'].iloc[0] / 
                self.balance_data['totalStockholdersEquity'].iloc[0])
 
    def calculate_roa(self):
        """Calculate Return on Assets (ROA)."""
        return (self.income_data['netIncome'].iloc[0] / 
                self.balance_data['totalAssets'].iloc[0])
 
    def calculate_gmi(self):
        """Calculate Gross Margin Index (GMI)."""
        if self.prev_income_data is None:
            raise ValueError("Previous period income data required for GMI calculation")
        current_gross_margin = (self.income_data['grossProfit'].iloc[0] / 
                              self.income_data['revenue'].iloc[0])
        prev_gross_margin = (self.prev_income_data['grossProfit'].iloc[0] / 
                           self.prev_income_data['revenue'].iloc[0])
        return current_gross_margin - prev_gross_margin
 
    def calculate_acca(self):
        """Calculate Accruals (ACCA)."""
        return ((self.income_data['netIncome'].iloc[0] - 
                 self.cash_flow_data['operatingCashFlow'].iloc[0]) / 
                self.balance_data['totalAssets'].iloc[0])
 
    def calculate_all_factors(self):
        """
        Calculate all quality factors and return as dictionary.
 
        Returns:
            dict: Dictionary containing all calculated quality factors
        """
        try:
            factors = {
                'net_profit_to_total_revenue': self.calculate_net_profit_to_revenue(),
                'DECM': self.calculate_decm(),
                'ROE': self.calculate_roe(),
                'ROA': self.calculate_roa(),
                'ACCA': self.calculate_acca()
            }
            if self.prev_income_data is not None:
                factors['GMI'] = self.calculate_gmi()
            return factors
        except Exception as e:
            print(f"Error calculating quality factors: {e}")
            return {}

class Value:
    """
    A class to calculate value-related financial factors.
 
    Attributes:
        income_data (pd.DataFrame): Income statement data
        balance_data (pd.DataFrame): Balance sheet data
        cash_flow_data (pd.DataFrame): Cash flow statement data
        enterprise_data (pd.DataFrame): Enterprise value and market data
    """
 
    def __init__(self, income_data, balance_data, cash_flow_data, enterprise_data):
        """
        Initialize Value class with financial data.
 
        Args:
            income_data (pd.DataFrame): Income statement data
            balance_data (pd.DataFrame): Balance sheet data
            cash_flow_data (pd.DataFrame): Cash flow statement data
            enterprise_data (pd.DataFrame): Enterprise value and market data
        """
        self.income_data = income_data
        self.balance_data = balance_data
        self.cash_flow_data = cash_flow_data
        self.enterprise_data = enterprise_data
        self.required_columns = {
            'income': {'netIncome', 'revenue', 'eps', 'EBIT'},
            'balance': {
                'totalLiabilities', 'totalAssets', 'netReceivables',
                'inventory', 'totalStockholdersEquity'
            },
            'cash_flow': {'operatingCashFlow'},
            'enterprise': {'numberOfShares', 'stockPrice'}
        }
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrames."""
        missing_cols = []
        for df_name, columns in self.required_columns.items():
            df = getattr(self, f"{df_name}_data")
            for col in columns:
                if col not in df.columns:
                    missing_cols.append(f"{df_name}: {col}")
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
 
    def calculate_financial_liability(self):
        """Calculate total financial liabilities."""
        return self.balance_data['totalLiabilities'].iloc[0]
 
    def calculate_cash_flow_to_price(self):
        """Calculate cash flow to price ratio."""
        return ((self.cash_flow_data['operatingCashFlow'].iloc[0] / 
                 self.enterprise_data['numberOfShares'].iloc[0]) / 
                self.enterprise_data['stockPrice'].iloc[0])
 
    def calculate_net_profit(self):
        """Calculate net profit."""
        return self.income_data['netIncome'].iloc[0]
 
    def calculate_ebit(self):
        """Calculate EBIT."""
        return self.income_data['EBIT'].iloc[0]
 
    def calculate_price_to_sales(self):
        """Calculate Price to Sales ratio (P/S)."""
        return (self.enterprise_data['stockPrice'].iloc[0] / 
                (self.income_data['revenue'].iloc[0] / 
                 self.enterprise_data['numberOfShares'].iloc[0]))
 
    def calculate_price_to_earnings(self):
        """Calculate Price to Earnings ratio (P/E)."""
        return (self.enterprise_data['stockPrice'].iloc[0] / 
                self.income_data['eps'].iloc[0])
 
    def calculate_ltd_to_ta(self):
        """Calculate Long Term Debt to Total Assets ratio."""
        return (self.balance_data['totalLiabilities'].iloc[0] / 
                self.balance_data['totalAssets'].iloc[0])
 
    def calculate_working_capital_ratio(self):
        """Calculate Working Capital Ratio."""
        return (self.cash_flow_data['operatingCashFlow'].iloc[0] / 
                self.balance_data['totalAssets'].iloc[0])
 
    def calculate_quick_ratio(self):
        """Calculate Quick Ratio."""
        return ((self.balance_data['netReceivables'].iloc[0] + 
                 self.balance_data['inventory'].iloc[0]) / 
                self.income_data['revenue'].iloc[0])
 
    def calculate_ev_to_ocl(self):
        """Calculate Enterprise Value to Operating Cash Flow Liability ratio."""
        return (self.cash_flow_data['operatingCashFlow'].iloc[0] / 
                self.balance_data['totalLiabilities'].iloc[0])
 
    def calculate_debt_to_equity(self):
        """Calculate Debt to Equity ratio."""
        return (self.balance_data['totalLiabilities'].iloc[0] / 
                self.balance_data['totalStockholdersEquity'].iloc[0])
 
    def calculate_all_factors(self):
        """
        Calculate all value factors and return as dictionary.
 
        Returns:
            dict: Dictionary containing all calculated value factors
        """
        try:
            return {
                'financial_liability': self.calculate_financial_liability(),
                'cash_flow_to_price_ratio': self.calculate_cash_flow_to_price(),
                'net_profit': self.calculate_net_profit(),
                'EBIT': self.calculate_ebit(),
                'P/S': self.calculate_price_to_sales(),
                'P/E': self.calculate_price_to_earnings(),
                'LTD/TA': self.calculate_ltd_to_ta(),
                'WCR': self.calculate_working_capital_ratio(),
                'QR': self.calculate_quick_ratio(),
                'EV/OCL': self.calculate_ev_to_ocl(),
                'D/E': self.calculate_debt_to_equity()
            }
        except Exception as e:
            print(f"Error calculating value factors: {e}")
            return {}
        
class Stock:
    """
    A class to calculate stock-related financial factors.
 
    Attributes:
        income_data (pd.DataFrame): Income statement data
        balance_data (pd.DataFrame): Balance sheet data
        cash_flow_data (pd.DataFrame): Cash flow statement data
        enterprise_data (pd.DataFrame): Enterprise value and market data
    """
 
    def __init__(self, income_data, balance_data, cash_flow_data, enterprise_data):
        """
        Initialize Stock class with financial data.
 
        Args:
            income_data (pd.DataFrame): Income statement data
            balance_data (pd.DataFrame): Balance sheet data
            cash_flow_data (pd.DataFrame): Cash flow statement data
            enterprise_data (pd.DataFrame): Enterprise value and market data
        """
        self.income_data = income_data
        self.balance_data = balance_data
        self.cash_flow_data = cash_flow_data
        self.enterprise_data = enterprise_data
        self.required_columns = {
            'income': {'eps'},
            'balance': {'totalStockholdersEquity', 'retainedEarnings'},
            'cash_flow': {'operatingCashFlow', 'freeCashFlow'},
            'enterprise': {'numberOfShares', 'stockPrice'}
        }
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrames."""
        missing_cols = []
        for df_name, columns in self.required_columns.items():
            df = getattr(self, f"{df_name}_data")
            for col in columns:
                if col not in df.columns:
                    missing_cols.append(f"{df_name}: {col}")
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
 
    def calculate_net_asset_per_share(self):
        """Calculate net asset per share."""
        return (self.balance_data['totalStockholdersEquity'].iloc[0] / 
                self.enterprise_data['numberOfShares'].iloc[0])
 
    def calculate_net_operate_cash_flow_per_share(self):
        """Calculate net operating cash flow per share."""
        return (self.cash_flow_data['operatingCashFlow'].iloc[0] / 
                self.enterprise_data['numberOfShares'].iloc[0])
 
    def calculate_eps(self):
        """Get earnings per share."""
        return self.income_data['eps'].iloc[0]
 
    def calculate_retained_earnings_per_share(self):
        """Calculate retained earnings per share."""
        return (self.balance_data['retainedEarnings'].iloc[0] / 
                self.enterprise_data['numberOfShares'].iloc[0])
 
    def calculate_cashflow_per_share(self):
        """Calculate free cash flow per share."""
        return (self.cash_flow_data['freeCashFlow'].iloc[0] / 
                self.enterprise_data['numberOfShares'].iloc[0])
 
    def calculate_market_cap(self):
        """Calculate market capitalization."""
        return (self.enterprise_data['numberOfShares'].iloc[0] * 
                self.enterprise_data['stockPrice'].iloc[0])
 
    def calculate_all_factors(self):
        """
        Calculate all stock factors and return as dictionary.
 
        Returns:
            dict: Dictionary containing all calculated stock factors
        """
        try:
            return {
                'net_asset_per_share': self.calculate_net_asset_per_share(),
                'net_operate_cash_flow_per_share': self.calculate_net_operate_cash_flow_per_share(),
                'eps': self.calculate_eps(),
                'retained_earnings_per_share': self.calculate_retained_earnings_per_share(),
                'cashflow_per_share': self.calculate_cashflow_per_share(),
                'market_cap': self.calculate_market_cap()
            }
        except Exception as e:
            print(f"Error calculating stock factors: {e}")
            return {}
        
class Growth:
    """
    A class to calculate growth-related financial factors.
 
    Attributes:
        income_data (pd.DataFrame): Current income statement data
        balance_data (pd.DataFrame): Current balance sheet data
        cash_flow_data (pd.DataFrame): Current cash flow statement data
        prev_income_data (pd.DataFrame): Previous period income statement data
        prev_balance_data (pd.DataFrame): Previous period balance sheet data
        prev_cash_flow_data (pd.DataFrame): Previous period cash flow statement data
    """
 
    def __init__(self, income_data, balance_data, cash_flow_data,
                 prev_income_data, prev_balance_data, prev_cash_flow_data):
        """
        Initialize Growth class with current and previous period financial data.
 
        Args:
            income_data (pd.DataFrame): Current income statement data
            balance_data (pd.DataFrame): Current balance sheet data
            cash_flow_data (pd.DataFrame): Current cash flow statement data
            prev_income_data (pd.DataFrame): Previous period income statement data
            prev_balance_data (pd.DataFrame): Previous period balance sheet data
            prev_cash_flow_data (pd.DataFrame): Previous period cash flow statement data
        """
        self.income_data = income_data
        self.balance_data = balance_data
        self.cash_flow_data = cash_flow_data
        self.prev_income_data = prev_income_data
        self.prev_balance_data = prev_balance_data
        self.prev_cash_flow_data = prev_cash_flow_data
        self.required_columns = {
            'income': {'eps', 'netIncome', 'revenue'},
            'balance': {'totalStockholdersEquity'},
            'cash_flow': {'operatingCashFlow'}
        }
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in all DataFrames."""
        missing_cols = []
        for df_name, columns in self.required_columns.items():
            current_df = getattr(self, f"{df_name}_data")
            prev_df = getattr(self, f"prev_{df_name}_data")
            for col in columns:
                if col not in current_df.columns:
                    missing_cols.append(f"Current {df_name}: {col}")
                if col not in prev_df.columns:
                    missing_cols.append(f"Previous {df_name}: {col}")
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
 
    def calculate_peg(self):
        """Calculate Price/Earnings to Growth ratio."""
        return (self.income_data['eps'].iloc[0] / 
                self.prev_income_data['eps'].iloc[0])
 
    def calculate_net_profit_growth(self):
        """Calculate net profit growth rate."""
        return (self.income_data['netIncome'].iloc[0] / 
                self.prev_income_data['netIncome'].iloc[0])
 
    def calculate_revenue_growth(self):
        """Calculate total revenue growth rate."""
        return (self.income_data['revenue'].iloc[0] / 
                self.prev_income_data['revenue'].iloc[0])
 
    def calculate_net_asset_growth(self):
        """Calculate net asset growth rate."""
        return (self.balance_data['totalStockholdersEquity'].iloc[0] / 
                self.prev_balance_data['totalStockholdersEquity'].iloc[0])
 
    def calculate_operating_cashflow_growth(self):
        """Calculate net operating cash flow growth rate."""
        return ((self.cash_flow_data['operatingCashFlow'].iloc[0] / 
                 self.prev_cash_flow_data['operatingCashFlow'].iloc[0]) - 1)
 
    def calculate_all_factors(self):
        """
        Calculate all growth factors and return as dictionary.
 
        Returns:
            dict: Dictionary containing all calculated growth factors
        """
        try:
            return {
                'PEG': self.calculate_peg(),
                'net_profit_growth_rate': self.calculate_net_profit_growth(),
                'total_revenue_growth_rate': self.calculate_revenue_growth(),
                'net_asset_growth_rate': self.calculate_net_asset_growth(),
                'net_operate_cashflow_growth_rate': self.calculate_operating_cashflow_growth()
            }
        except Exception as e:
            print(f"Error calculating growth factors: {e}")
            return {}
        
class Emotional:
    """
    A class to calculate emotional/sentiment-related market factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing market data with OHLCV columns
    """
 
    def __init__(self, df):
        """
        Initialize Emotional class with market data.
 
        Args:
            df (pd.DataFrame): DataFrame containing market data
                Required columns: ['close', 'high', 'low', 'volume']
        """
        self.df = df
        self.required_columns = {'close', 'high', 'low', 'volume'}
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrame."""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
 
    def calculate_volume_volatility(self, window=20):
        """
        Calculate rolling standard deviation of returns (VOL20).
        Args:
            window (int): Rolling window size, defaults to 20
        """
        self.df['VOL20'] = self.df['close'].pct_change().rolling(window=window).std()
        return self.df
 
    def calculate_volume_ma(self, window=20):
        """
        Calculate rolling mean of volume (DAVOL20).
        Args:
            window (int): Rolling window size, defaults to 20
        """
        self.df['DAVOL20'] = self.df['volume'].rolling(window=window).mean()
        return self.df
 
    def calculate_volume_oscillator(self):
        """Calculate Volume Oscillator (VOSC)."""
        volume_ma = self.df['volume'].rolling(window=60).mean()
        self.df['VOSC'] = self.df['volume'] - volume_ma
        return self.df
 
    def calculate_volume_macd(self):
        """Calculate Volume MACD."""
        fast_ma = self.df['volume'].ewm(span=36).mean()
        slow_ma = self.df['volume'].ewm(span=78).mean()
        self.df['VMACD'] = fast_ma - slow_ma
        return self.df
 
    def calculate_atr(self, window=14):
        """
        Calculate Average True Range (ATR14).
        Args:
            window (int): Rolling window size, defaults to 14
        """
        self.df['ATR14'] = (self.df['high'] - self.df['low']).rolling(window=window).mean()
        return self.df
 
    def calculate_all_factors(self):
        """
        Calculate all emotional factors.
 
        Returns:
            pd.DataFrame: DataFrame with all calculated emotional factors
        """
        try:
            self.calculate_volume_volatility()
            self.calculate_volume_ma()
            self.calculate_volume_oscillator()
            self.calculate_volume_macd()
            self.calculate_atr()
            # Return only the calculated factors
            emotional_columns = ['VOL20', 'DAVOL20', 'VOSC', 'VMACD', 'ATR14']
            return self.df[emotional_columns]
        except Exception as e:
            print(f"Error calculating emotional factors: {e}")
            return pd.DataFrame()
        
class Style:
    """
    A class to calculate style-related market factors.
 
    Attributes:
        combined_data (pd.DataFrame): Combined market data
        sp500_returns (pd.DataFrame): S&P 500 returns data
        tickers (list): List of stock tickers
    """
 
    def __init__(self, combined_data, sp500_returns, tickers):
        """
        Initialize Style class with market data.
 
        Args:
            combined_data (pd.DataFrame): Combined market data with multi-index (Date, Ticker)
            sp500_returns (pd.DataFrame): S&P 500 returns data
            tickers (list): List of stock tickers
        """
        self.combined_data# filepath: /home/mayanksony/2cents/models/factors.py
 
class Risk:
    """
    A class to calculate risk-related market factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing market data
        risk_free_rate_20 (float): 20-day risk-free rate
        risk_free_rate_60 (float): 60-day risk-free rate
    """
 
    def __init__(self, df, risk_free_rate_20=0.02, risk_free_rate_60=0.02):
        """
        Initialize Risk class with market data and risk-free rates.
 
        Args:
            df (pd.DataFrame): DataFrame containing market data
                Required columns: ['close']
            risk_free_rate_20 (float): 20-day risk-free rate, defaults to 0.02
            risk_free_rate_60 (float): 60-day risk-free rate, defaults to 0.02
        """
        self.df = df
        self.risk_free_rate_20 = risk_free_rate_20
        self.risk_free_rate_60 = risk_free_rate_60
        self.required_columns = {'close'}
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrame."""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
 
    def calculate_variance(self, window=60):
        """
        Calculate return variance over specified window.
 
        Args:
            window (int): Rolling window size, defaults to 60
        """
        self.df['Variance60'] = (
            self.df['close'].pct_change().rolling(window=window).var()
        )
        return self.df
 
    def calculate_sharpe_ratio_20(self):
        """Calculate 20-day Sharpe ratio."""
        returns = self.df['close'].pct_change()
        self.df['sharpe_ratio_20'] = (
            (returns.rolling(window=20).mean() - self.risk_free_rate_20) /
            returns.rolling(window=20).std()
        )
        return self.df
 
    def calculate_kurtosis(self, window=60):
        """
        Calculate return kurtosis over specified window.
 
        Args:
            window (int): Rolling window size, defaults to 60
        """
        self.df['Kurtosis60'] = (
            self.df['close'].pct_change().rolling(window=window).kurt()
        )
        return self.df
 
    def calculate_skewness(self, window=60):
        """
        Calculate return skewness over specified window.
 
        Args:
            window (int): Rolling window size, defaults to 60
        """
        self.df['Skewness60'] = (
            self.df['close'].pct_change().rolling(window=window).skew()
        )
        return self.df
 
    def calculate_sharpe_ratio_60(self):
        """Calculate 60-day Sharpe ratio."""
        returns = self.df['close'].pct_change()
        self.df['sharpe_ratio_60'] = (
            (returns.rolling(window=60).mean() - self.risk_free_rate_60) /
            returns.rolling(window=60).std()
        )
        return self.df
 
    def calculate_all_factors(self):
        """
        Calculate all risk factors.
 
        Returns:
            pd.DataFrame: DataFrame containing all calculated risk factors
        """
        try:
            self.calculate_variance()
            self.calculate_sharpe_ratio_20()
            self.calculate_kurtosis()
            self.calculate_skewness()
            self.calculate_sharpe_ratio_60()
           
            # Return only the calculated factors
            risk_columns = [
                'Variance60', 'sharpe_ratio_20', 'Kurtosis60',
                'Skewness60', 'sharpe_ratio_60'
            ]
            return self.df[risk_columns]
           
        except Exception as e:
            print(f"Error calculating risk factors: {e}")
            return pd.DataFrame()
    """
    A class to calculate momentum-related market factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing OHLCV market data
    """
 
    def __init__(self, df):
        """
        Initialize Momentum class with market data.
 
        Args:
            df (pd.DataFrame): DataFrame containing market data
                Required columns: ['close', 'volume']
        """
        self.df = df
        self.required_columns = {'close', 'volume'}
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrame."""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
 
    def calculate_rate_of_change(self, window=60):
        """
        Calculate Rate of Change (ROC60).
 
        Args:
            window (int): Look-back period, defaults to 60
        """
        self.df['ROC60'] = (
            (self.df['close'] - self.df['close'].shift(window)) / 
            self.df['close'].shift(window)
        )
        return self.df
 
    def calculate_volume_quarterly(self, window=60):
        """
        Calculate Quarterly Volume (Volume1Q).
 
        Args:
            window (int): Rolling window size, defaults to 60 days
        """
        self.df['Volume1Q'] = self.df['volume'].rolling(window=window).sum()
        return self.df
 
    def calculate_trix(self, span=30):
        """
        Calculate Triple Exponential Average (TRIX30).
 
        Args:
            span (int): Exponential moving average span, defaults to 30
        """
        triple_ema = (
            self.df['close']
            .ewm(span=span).mean()
            .ewm(span=span).mean()
            .ewm(span=span).mean()
        )
        self.df['TRIX30'] = triple_ema.pct_change(periods=1)
        return self.df
 
    def calculate_price_quarterly(self, window=60):
        """
        Calculate Quarterly Price Change (Price1Q).
 
        Args:
            window (int): Look-back period, defaults to 60 days
        """
        self.df['Price1Q'] = self.df['close'] - self.df['close'].shift(window)
        return self.df
 
    def calculate_price_level_ratio(self, window=36):
        """
        Calculate Price Level Ratio Change (PLRC36).
 
        Args:
            window (int): Rolling window size, defaults to 36
        """
        self.df['PLRC36'] = (
            self.df['close'].rolling(window=window).mean() / 
            self.df['close'].shift(window) - 1
        )
        return self.df
 
    def calculate_all_factors(self):
        """
        Calculate all momentum factors.
 
        Returns:
            pd.DataFrame: DataFrame containing all calculated momentum factors
        """
        try:
            self.calculate_rate_of_change()
            self.calculate_volume_quarterly()
            self.calculate_trix()
            self.calculate_price_quarterly()
            self.calculate_price_level_ratio()
            # Return only the calculated factors
            momentum_columns = [
                'ROC60', 'Volume1Q', 'TRIX30', 'Price1Q', 'PLRC36'
            ]
            return self.df[momentum_columns]
        except Exception as e:
            print(f"Error calculating momentum factors: {e}")
            return pd.DataFrame()
    """
    A class to calculate momentum-related market factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing OHLCV market data
    """
 
    def __init__(self, df):
        """
        Initialize Momentum class with market data.
 
        Args:
            df (pd.DataFrame): DataFrame containing market data
                Required columns: ['close', 'volume']
        """
        self.df = df
        self.required_columns = {'close', 'volume'}
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrame."""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
 
    def calculate_rate_of_change(self, window=60):
        """
        Calculate Rate of Change (ROC60).
 
        Args:
            window (int): Look-back period, defaults to 60
        """
        self.df['ROC60'] = (
            (self.df['close'] - self.df['close'].shift(window)) / 
            self.df['close'].shift(window)
        )
        return self.df
 
    def calculate_volume_quarterly(self, window=60):
        """
        Calculate Quarterly Volume (Volume1Q).
 
        Args:
            window (int): Rolling window size, defaults to 60 days
        """
        self.df['Volume1Q'] = self.df['volume'].rolling(window=window).sum()
        return self.df
 
    def calculate_trix(self, span=30):
        """
        Calculate Triple Exponential Average (TRIX30).
 
        Args:
            span (int): Exponential moving average span, defaults to 30
        """
        triple_ema = (
            self.df['close']
            .ewm(span=span).mean()
            .ewm(span=span).mean()
            .ewm(span=span).mean()
        )
        self.df['TRIX30'] = triple_ema.pct_change(periods=1)
        return self.df
 
    def calculate_price_quarterly(self, window=60):
        """
        Calculate Quarterly Price Change (Price1Q).
 
        Args:
            window (int): Look-back period, defaults to 60 days
        """
        self.df['Price1Q'] = self.df['close'] - self.df['close'].shift(window)
        return self.df
 
    def calculate_price_level_ratio(self, window=36):
        """
        Calculate Price Level Ratio Change (PLRC36).
 
        Args:
            window (int): Rolling window size, defaults to 36
        """
        self.df['PLRC36'] = (
            self.df['close'].rolling(window=window).mean() / 
            self.df['close'].shift(window) - 1
        )
        return self.df
 
    def calculate_all_factors(self):
        """
        Calculate all momentum factors.
 
        Returns:
            pd.DataFrame: DataFrame containing all calculated momentum factors
        """
        try:
            self.calculate_rate_of_change()
            self.calculate_volume_quarterly()
            self.calculate_trix()
            self.calculate_price_quarterly()
            self.calculate_price_level_ratio()
            # Return only the calculated factors
            momentum_columns = [
                'ROC60', 'Volume1Q', 'TRIX30', 'Price1Q', 'PLRC36'
            ]
            return self.df[momentum_columns]
        except Exception as e:
            print(f"Error calculating momentum factors: {e}")
            return pd.DataFrame()
    """
    A class to calculate technical market factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing OHLCV market data
    """
 
    def __init__(self, df):
        """
        Initialize Technical class with market data.
 
        Args:
            df (pd.DataFrame): DataFrame containing market data
                Required columns: ['close', 'high', 'low', 'volume']
        """
        self.df = df
        self.required_columns = {'close', 'high', 'low', 'volume'}
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrame."""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
 
    def calculate_mac(self):
        """
        Calculate Moving Average Convergence (MAC60).
        Uses 36-period and 78-period exponential moving averages.
        """
        fast_ma = self.df['close'].ewm(span=36).mean()
        slow_ma = self.df['close'].ewm(span=78).mean()
        self.df['MAC60'] = fast_ma - slow_ma
        return self.df
 
    def calculate_bollinger_bands(self, window=60, num_std=2):
        """
        Calculate Bollinger Bands.
 
        Args:
            window (int): Rolling window size, defaults to 60
            num_std (int): Number of standard deviations, defaults to 2
        """
        rolling_mean = self.df['close'].rolling(window=window).mean()
        rolling_std = self.df['close'].rolling(window=window).std()
        self.df['boll_up'] = rolling_mean + (rolling_std * num_std)
        self.df['boll_down'] = rolling_mean - (rolling_std * num_std)
        return self.df
 
    def calculate_mfi(self, window=42):
        """
        Calculate Money Flow Index (MFI42).
 
        Args:
            window (int): Rolling window size, defaults to 42
        """
        # Calculate typical price
        typical_price = (self.df['close'] + 
                        self.df['high'] + 
                        self.df['low']) / 3
        # Calculate raw money flow
        raw_money_flow = typical_price * self.df['volume']
        # Calculate positive and negative flow
        positive_flow = raw_money_flow.where(
            typical_price > typical_price.shift(1), 0)
        negative_flow = raw_money_flow.where(
            typical_price < typical_price.shift(1), 0)
        # Calculate money flow ratio
        positive_flow_sum = positive_flow.rolling(window=window).sum()
        negative_flow_sum = negative_flow.rolling(window=window).sum()
        money_flow_ratio = positive_flow_sum / negative_flow_sum
        # Calculate MFI
        self.df['MFI42'] = 100 - (100 / (1 + money_flow_ratio))
        return self.df
 
    def calculate_all_factors(self):
        """
        Calculate all technical factors.
 
        Returns:
            pd.DataFrame: DataFrame containing all calculated technical factors
        """
        try:
            self.calculate_mac()
            self.calculate_bollinger_bands()
            self.calculate_mfi()
            # Return only the calculated factors
            technical_columns = ['MAC60', 'boll_up', 'boll_down', 'MFI42']
            return self.df[technical_columns]
        except Exception as e:
            print(f"Error calculating technical factors: {e}")
            return pd.DataFrame()

class Momentum:
    """
    A class to calculate momentum-related market factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing OHLCV market data
    """
 
    def __init__(self, df):
        """
        Initialize Momentum class with market data.
 
        Args:
            df (pd.DataFrame): DataFrame containing market data
                Required columns: ['close', 'volume']
        """
        self.df = df
        self.required_columns = {'close', 'volume'}
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrame."""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
 
    def calculate_rate_of_change(self, window=60):
        """
        Calculate Rate of Change (ROC60).
 
        Args:
            window (int): Look-back period, defaults to 60
        """
        self.df['ROC60'] = (
            (self.df['close'] - self.df['close'].shift(window)) / 
            self.df['close'].shift(window)
        )
        return self.df
 
    def calculate_volume_quarterly(self, window=60):
        """
        Calculate Quarterly Volume (Volume1Q).
 
        Args:
            window (int): Rolling window size, defaults to 60 days
        """
        self.df['Volume1Q'] = self.df['volume'].rolling(window=window).sum()
        return self.df
 
    def calculate_trix(self, span=30):
        """
        Calculate Triple Exponential Average (TRIX30).
 
        Args:
            span (int): Exponential moving average span, defaults to 30
        """
        triple_ema = (
            self.df['close']
            .ewm(span=span).mean()
            .ewm(span=span).mean()
            .ewm(span=span).mean()
        )
        self.df['TRIX30'] = triple_ema.pct_change(periods=1)
        return self.df
 
    def calculate_price_quarterly(self, window=60):
        """
        Calculate Quarterly Price Change (Price1Q).
 
        Args:
            window (int): Look-back period, defaults to 60 days
        """
        self.df['Price1Q'] = self.df['close'] - self.df['close'].shift(window)
        return self.df
 
    def calculate_price_level_ratio(self, window=36):
        """
        Calculate Price Level Ratio Change (PLRC36).
 
        Args:
            window (int): Rolling window size, defaults to 36
        """
        self.df['PLRC36'] = (
            self.df['close'].rolling(window=window).mean() / 
            self.df['close'].shift(window) - 1
        )
        return self.df
 
    def calculate_all_factors(self):
        """
        Calculate all momentum factors.
 
        Returns:
            pd.DataFrame: DataFrame containing all calculated momentum factors
        """
        try:
            self.calculate_rate_of_change()
            self.calculate_volume_quarterly()
            self.calculate_trix()
            self.calculate_price_quarterly()
            self.calculate_price_level_ratio()
            # Return only the calculated factors
            momentum_columns = [
                'ROC60', 'Volume1Q', 'TRIX30', 'Price1Q', 'PLRC36'
            ]
            return self.df[momentum_columns]
        except Exception as e:
            print(f"Error calculating momentum factors: {e}")
            return pd.DataFrame()
class Technical:
    """
    A class to calculate technical market factors.
 
    Attributes:
        df (pd.DataFrame): DataFrame containing OHLCV market data
    """
 
    def __init__(self, df):
        """
        Initialize Technical class with market data.
 
        Args:
            df (pd.DataFrame): DataFrame containing market data
                Required columns: ['close', 'high', 'low', 'volume']
        """
        self.df = df
        self.required_columns = {'close', 'high', 'low', 'volume'}
        self._validate_columns()
 
    def _validate_columns(self):
        """Validate if required columns are present in DataFrame."""
        missing_cols = self.required_columns - set(self.df.columns)
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
 
    def calculate_mac(self, fast_span=36, slow_span=78):
        """
        Calculate Moving Average Convergence (MAC60).
 
        Args:
            fast_span (int): Fast EMA period, defaults to 36
            slow_span (int): Slow EMA period, defaults to 78
        """
        fast_ma = self.df['close'].ewm(span=fast_span).mean()
        slow_ma = self.df['close'].ewm(span=slow_span).mean()
        self.df['MAC60'] = fast_ma - slow_ma
        return self.df
 
    def calculate_bollinger_bands(self, window=60, num_std=2):
        """
        Calculate Bollinger Bands.
 
        Args:
            window (int): Rolling window size, defaults to 60
            num_std (int): Number of standard deviations, defaults to 2
        """
        rolling_mean = self.df['close'].rolling(window=window).mean()
        rolling_std = self.df['close'].rolling(window=window).std()
       
        self.df['boll_up'] = rolling_mean + (rolling_std * num_std)
        self.df['boll_down'] = rolling_mean - (rolling_std * num_std)
        return self.df
 
    def calculate_mfi(self, window=42):
        """
        Calculate Money Flow Index (MFI42).
 
        Args:
            window (int): Rolling window size, defaults to 42
        """
        # Calculate typical price
        typical_price = (
            self.df['close'] +
            self.df['high'] +
            self.df['low']
        ) / 3
       
        # Calculate raw money flow
        raw_money_flow = typical_price * self.df['volume']
       
        # Calculate positive and negative flow
        positive_flow = raw_money_flow.where(
            typical_price > typical_price.shift(1), 0)
        negative_flow = raw_money_flow.where(
            typical_price < typical_price.shift(1), 0)
       
        # Calculate money flow ratio
        positive_flow_sum = positive_flow.rolling(window=window).sum()
        negative_flow_sum = negative_flow.rolling(window=window).sum()
        money_flow_ratio = positive_flow_sum / negative_flow_sum
       
        # Calculate MFI
        self.df['MFI42'] = 100 - (100 / (1 + money_flow_ratio))
        return self.df
 
    def calculate_all_factors(self):
        """
        Calculate all technical factors.
 
        Returns:
            pd.DataFrame: DataFrame containing all calculated technical factors
        """
        try:
            self.calculate_mac()
            self.calculate_bollinger_bands()
            self.calculate_mfi()
           
            # Return only the calculated factors
            technical_columns = ['MAC60', 'boll_up', 'boll_down', 'MFI42']
            return self.df[technical_columns]
           
        except Exception as e:
            print(f"Error calculating technical factors: {e}")
            return pd.DataFrame()