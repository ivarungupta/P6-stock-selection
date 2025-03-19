import pandas as pd
import numpy as np

class Quality:
    """
    A class to calculate quality-related financial factors.
    
    Attributes:
        income_data (pd.DataFrame): Income statement data
        balance_data (pd.DataFrame): Balance sheet data
        cash_flow_data (pd.DataFrame): Cash flow statement data
        prev_income_data (pd.DataFrame, optional): Previous period income data
    """
    def __init__(self, income_data, balance_data, cash_flow_data, prev_income_data=None):
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
        return self.income_data['netIncome'].iloc[0] / self.income_data['revenue'].iloc[0]

    def calculate_decm(self):
        return self.balance_data['totalLiabilities'].iloc[0] / self.balance_data['totalAssets'].iloc[0]

    def calculate_roe(self):
        return self.income_data['netIncome'].iloc[0] / self.balance_data['totalStockholdersEquity'].iloc[0]

    def calculate_roa(self):
        return self.income_data['netIncome'].iloc[0] / self.balance_data['totalAssets'].iloc[0]

    def calculate_gmi(self):
        if self.prev_income_data is None:
            raise ValueError("Previous period income data required for GMI calculation")
        current_gross_margin = self.income_data['grossProfit'].iloc[0] / self.income_data['revenue'].iloc[0]
        prev_gross_margin = self.prev_income_data['grossProfit'].iloc[0] / self.prev_income_data['revenue'].iloc[0]
        return current_gross_margin - prev_gross_margin

    def calculate_acca(self):
        return ((self.income_data['netIncome'].iloc[0] - self.cash_flow_data['operatingCashFlow'].iloc[0]) /
                self.balance_data['totalAssets'].iloc[0])

    def calculate_all_factors(self):
        try:
            factors = pd.DataFrame([{
                'net_profit_to_total_revenue': self.calculate_net_profit_to_revenue(),
                'DECM': self.calculate_decm(),
                'ROE': self.calculate_roe(),
                'ROA': self.calculate_roa(),
                'ACCA': self.calculate_acca()
            }])
            if self.prev_income_data is not None:
                factors['GMI'] = self.calculate_gmi()
            return factors
        except Exception as e:
            print(f"Error calculating quality factors: {e}")
            return {}
