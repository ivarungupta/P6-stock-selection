import pandas as pd
import numpy as np

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
        self.income_data = income_data
        self.balance_data = balance_data
        self.cash_flow_data = cash_flow_data
        self.enterprise_data = enterprise_data
        self.required_columns = {
            'income': {'netIncome', 'revenue', 'eps', 'EBIT'},
            'balance': {'totalLiabilities', 'totalAssets', 'netReceivables', 'inventory', 'totalStockholdersEquity'},
            'cash_flow': {'operatingCashFlow'},
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

    def calculate_financial_liability(self):
        return self.balance_data['totalLiabilities'].iloc[0]

    def calculate_cash_flow_to_price(self):
        return ((self.cash_flow_data['operatingCashFlow'].iloc[0] / self.enterprise_data['numberOfShares'].iloc[0]) /
                self.enterprise_data['stockPrice'].iloc[0])

    def calculate_net_profit(self):
        return self.income_data['netIncome'].iloc[0]

    def calculate_ebit(self):
        return self.income_data['EBIT'].iloc[0]

    def calculate_price_to_sales(self):
        return self.enterprise_data['stockPrice'].iloc[0] / (self.income_data['revenue'].iloc[0] /
                                                               self.enterprise_data['numberOfShares'].iloc[0])

    def calculate_price_to_earnings(self):
        return self.enterprise_data['stockPrice'].iloc[0] / self.income_data['eps'].iloc[0]

    def calculate_ltd_to_ta(self):
        return self.balance_data['totalLiabilities'].iloc[0] / self.balance_data['totalAssets'].iloc[0]

    def calculate_working_capital_ratio(self):
        return self.cash_flow_data['operatingCashFlow'].iloc[0] / self.balance_data['totalAssets'].iloc[0]

    def calculate_quick_ratio(self):
        return (self.balance_data['netReceivables'].iloc[0] + self.balance_data['inventory'].iloc[0]) / self.income_data['revenue'].iloc[0]

    def calculate_ev_to_ocl(self):
        return self.cash_flow_data['operatingCashFlow'].iloc[0] / self.balance_data['totalLiabilities'].iloc[0]

    def calculate_debt_to_equity(self):
        return self.balance_data['totalLiabilities'].iloc[0] / self.balance_data['totalStockholdersEquity'].iloc[0]

    def calculate_all_factors(self):
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
