import pandas as pd
import numpy as np

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
        missing_cols = []
        for df_name, columns in self.required_columns.items():
            df = getattr(self, f"{df_name}_data")
            for col in columns:
                if col not in df.columns:
                    missing_cols.append(f"{df_name}: {col}")
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    def calculate_net_asset_per_share(self):
        return self.balance_data['totalStockholdersEquity'].iloc[0] / self.enterprise_data['numberOfShares'].iloc[0]

    def calculate_net_operate_cash_flow_per_share(self):
        return self.cash_flow_data['operatingCashFlow'].iloc[0] / self.enterprise_data['numberOfShares'].iloc[0]

    def calculate_eps(self):
        return self.income_data['eps'].iloc[0]

    def calculate_retained_earnings_per_share(self):
        return self.balance_data['retainedEarnings'].iloc[0] / self.enterprise_data['numberOfShares'].iloc[0]

    def calculate_cashflow_per_share(self):
        return self.cash_flow_data['freeCashFlow'].iloc[0] / self.enterprise_data['numberOfShares'].iloc[0]

    def calculate_market_cap(self):
        return self.enterprise_data['numberOfShares'].iloc[0] * self.enterprise_data['stockPrice'].iloc[0]

    def calculate_all_factors(self):
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
