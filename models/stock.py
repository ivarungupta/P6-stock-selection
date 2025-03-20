import pandas as pd
import numpy as np

class Stock:
    """
    A class to calculate stock-related financial factors.
    
    Attributes:
        income_data (pd.DataFrame): Income statement data
        balance_data (pd.DataFrame): Balance sheet data
        cash_flow_data (pd.DataFrame): Cash flow statement data
        market_data (pd.DataFrame): Market data
    """
    def __init__(self, income_data, balance_data, cash_flow_data, market_data):
        self.income_data_master = income_data
        self.balance_data_master = balance_data
        self.cash_flow_data_master = cash_flow_data
        self.market_data_master = market_data
        self.required_columns = {
            'income': {'eps', 'weightedAverageShsOut'},
            'balance': {'totalStockholdersEquity', 'retainedEarnings'},
            'cash_flow': {'operatingCashFlow', 'freeCashFlow'},
            'market': {'close'},
        }
        self._validate_columns()

    def _validate_columns(self):
        missing_cols = []
        for df_name, columns in self.required_columns.items():
            df = getattr(self, f"{df_name}_data_master")
            for col in columns:
                if col not in df.columns:
                    missing_cols.append(f"{df_name}: {col}")
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    def calculate_net_asset_per_share(self):
        return self.balance_data['totalStockholdersEquity'].iloc[0] / self.income_data['weightedAverageShsOut'].iloc[0]

    def calculate_net_operate_cash_flow_per_share(self):
        return self.cash_flow_data['operatingCashFlow'].iloc[0] / self.income_data['weightedAverageShsOut'].iloc[0]

    def calculate_eps(self):
        return self.income_data['eps'].iloc[0]

    def calculate_retained_earnings_per_share(self):
        return self.balance_data['retainedEarnings'].iloc[0] / self.income_data['weightedAverageShsOut'].iloc[0]

    def calculate_cashflow_per_share(self):
        return self.cash_flow_data['freeCashFlow'].iloc[0] / self.income_data['weightedAverageShsOut'].iloc[0]

    def calculate_market_cap(self):
        return self.income_data['weightedAverageShsOut'].iloc[0] * self.market_data['close'].iloc[0]

    def calculate_all_factors(self):
        try:
            factors = []
            for i, income_row in self.income_data_master.iterrows():
                    date = income_row['date']
                    self.income_data = self.income_data_master[self.income_data_master['date'] == date]
                    self.balance_data = self.balance_data_master[self.balance_data_master['date'] == date]
                    self.cash_flow_data = self.cash_flow_data_master[self.cash_flow_data_master['date'] == date]
                    if date in self.market_data_master['date'].values:
                        self.market_data = self.market_data_master[self.market_data_master['date'] == date]
                    else:
                        prev_date = self.market_data_master[self.market_data_master['date'] < date]['date'].max()
                        if pd.isna(prev_date):
                            raise ValueError(f"No available market data for or before date: {date}")
                        self.market_data = self.market_data_master[self.market_data_master['date'] == prev_date]
                    factors.append({
                        'date': date,
                        'open': self.market_data['open'].iloc[0],
                        'high': self.market_data['high'].iloc[0],
                        'low': self.market_data['low'].iloc[0],
                        'close': self.market_data['close'].iloc[0],
                        'volume': self.market_data['volume'].iloc[0],
                        'net_asset_per_share': self.calculate_net_asset_per_share(),
                        'net_operate_cash_flow_per_share': self.calculate_net_operate_cash_flow_per_share(),
                        'eps': self.calculate_eps(),
                        'retained_earnings_per_share': self.calculate_retained_earnings_per_share(),
                        'cashflow_per_share': self.calculate_cashflow_per_share(),
                        'market_cap': self.calculate_market_cap()
                    })
            return pd.DataFrame(factors)
        
        except Exception as e:
            print(f"Error calculating stock factors: {e}")
            return {}
