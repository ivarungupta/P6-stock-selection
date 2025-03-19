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
    def __init__(self, income_data, balance_data, cash_flow_data, enterprise_data, financial_ratio_data):
        self.income_data_master = income_data
        self.balance_data_master = balance_data
        self.cash_flow_data_master = cash_flow_data
        self.enterprise_data_master = enterprise_data
        self.financial_ratio_data_master = financial_ratio_data
        self.required_columns = {
            'income': {'netIncome', 'revenue', 'eps', 'costOfRevenue', 'operatingExpenses'},
            'balance': {'totalLiabilities', 'totalAssets', 'netReceivables', 'inventory', 'totalStockholdersEquity'},
            'cash_flow': {'operatingCashFlow'},
            'enterprise': {'numberOfShares', 'stockPrice'},
            'financial_ratio': {'priceCashFlowRatio', 'priceToSalesRatio', 'priceToBookRatio', 'priceEarningsRatio'}
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

    def calculate_financial_liability(self):
        return self.balance_data['totalLiabilities'].iloc[0]
    # ----------------
    def calculate_price_cashflow(self):
        return self.financial_ratio_data['priceCashFlowRatio'].iloc[0]
    
    def calculate_priceToBook(self):
        return self.financial_ratio_data['priceToBookRatio'].iloc[0]

    def calculate_price_to_sales(self):
        return self.financial_ratio_data['priceToSalesRatio'].iloc[0]

    def calculate_price_to_earnings(self):
        return self.financial_ratio_data['priceEarningsRatio'].iloc[0]
    # ----------------
    def calculate_ltd_to_ta(self):
        return self.balance_data['totalLiabilities'].iloc[0] / self.balance_data['totalAssets'].iloc[0]
    
    def calculate_net_profit(self):
        return self.income_data['netIncome'].iloc[0]

    def calculate_ebit(self):
        return self.income_data['revenue'].iloc[0] - self.income_data['costOfRevenue'].iloc[0] - self.income_data['operatingExpenses'].iloc[0]

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
            factors = []
            for i, income_row in self.income_data_master.iterrows():
                    date = income_row['date']
                    self.income_data = self.income_data_master[self.income_data_master['date'] == date]
                    self.balance_data = self.balance_data_master[self.balance_data_master['date'] == date]
                    self.cash_flow_data = self.cash_flow_data_master[self.cash_flow_data_master['date'] == date]
                    self.enterprise_data = self.enterprise_data_master[self.enterprise_data_master['date'] == date]
                    self.financial_ratio_data = self.financial_ratio_data_master[self.financial_ratio_data_master['date'] == date]
                    factors.append({
                        'date': date,
                        'financial_liability': self.calculate_financial_liability(),
                        'net_profit': self.calculate_net_profit(),
                        'EBIT': self.calculate_ebit(),
                        'LTD/TA': self.calculate_ltd_to_ta(),
                        'WCR': self.calculate_working_capital_ratio(),
                        'QR': self.calculate_quick_ratio(),
                        'EV/OCL': self.calculate_ev_to_ocl(),
                        'D/E': self.calculate_debt_to_equity(),
                        'P/E': self.calculate_price_to_earnings(),
                        'P/S': self.calculate_price_to_sales(),
                        'PriceToCashFlow': self.calculate_price_cashflow(),
                        'priceToBook': self.calculate_priceToBook()
                    })

            return pd.DataFrame(factors)
        except Exception as e:
            print(f"Error calculating value factors: {e}")
            return {}
