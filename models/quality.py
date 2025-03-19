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
    def __init__(self, income_data, balance_data, cash_flow_data):
        self.income_data_master = income_data
        self.balance_data_master = balance_data
        self.cash_flow_data_master = cash_flow_data
        self.required_columns = {
            'income': {'netIncome', 'revenue', 'grossProfit'},
            'balance': {'totalStockholdersEquity', 'totalAssets', 'totalLiabilities'},
            'cash_flow': {'operatingCashFlow'}
        }
        self._validate_columns()

    def _validate_columns(self):
        missing_cols = []
        for col in self.required_columns['income']:
            if col not in self.income_data_master.columns:
                missing_cols.append(f"Income: {col}")
        for col in self.required_columns['balance']:
            if col not in self.balance_data_master.columns:
                missing_cols.append(f"Balance: {col}")
        for col in self.required_columns['cash_flow']:
            if col not in self.cash_flow_data_master.columns:
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
            prev_gross_margin = 0
        else:
            prev_gross_margin = self.prev_income_data['grossProfit'].iloc[0] / self.prev_income_data['revenue'].iloc[0]
        
        current_gross_margin = self.income_data['grossProfit'].iloc[0] / self.income_data['revenue'].iloc[0]
        
        return current_gross_margin - prev_gross_margin

    def calculate_acca(self):
        return ((self.income_data['netIncome'].iloc[0] - self.cash_flow_data['operatingCashFlow'].iloc[0]) /
                self.balance_data['totalAssets'].iloc[0])

    def calculate_all_factors(self):
        try:
            factors = []
            for _, income_row in self.income_data_master.iterrows():
                date = income_row['date']
                self.income_data = self.income_data_master[self.income_data_master['date'] == date]
                self.balance_data = self.balance_data_master[self.balance_data_master['date'] == date]
                self.cash_flow_data = self.cash_flow_data_master[self.cash_flow_data_master['date'] == date]
                self.prev_income_data = None
                if not self.income_data_master[self.income_data_master['date'] < date].empty:
                    self.prev_income_data = self.income_data_master[self.income_data_master['date'] < date].iloc[-1:]

                factors.append({
                    'date': date,
                    'net_profit_to_total_revenue': self.calculate_net_profit_to_revenue(),
                    'DECM': self.calculate_decm(),
                    'ROE': self.calculate_roe(),
                    'ROA': self.calculate_roa(),
                    'ACCA': self.calculate_acca(),
                    'GMI': self.calculate_gmi()
                })

            return pd.DataFrame(factors)
        
        except Exception as e:
            print(f"Error calculating quality factors: {e}")
            return {}
