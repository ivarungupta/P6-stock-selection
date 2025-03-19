import pandas as pd
import numpy as np

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
        return self.income_data['eps'].iloc[0] / self.prev_income_data['eps'].iloc[0]

    def calculate_net_profit_growth(self):
        return self.income_data['netIncome'].iloc[0] / self.prev_income_data['netIncome'].iloc[0]

    def calculate_revenue_growth(self):
        return self.income_data['revenue'].iloc[0] / self.prev_income_data['revenue'].iloc[0]

    def calculate_net_asset_growth(self):
        return self.balance_data['totalStockholdersEquity'].iloc[0] / self.prev_balance_data['totalStockholdersEquity'].iloc[0]

    def calculate_operating_cashflow_growth(self):
        return (self.cash_flow_data['operatingCashFlow'].iloc[0] / self.prev_cash_flow_data['operatingCashFlow'].iloc[0]) - 1

    def calculate_all_factors(self):
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
