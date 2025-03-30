import pandas as pd
import numpy as np

class Value:
    """
    A class to calculate value-related financial factors.
    """
    def __init__(self, income_data, balance_data, cash_flow_data, market_data, financial_ratio_data):
        self.income_data_master = income_data
        self.balance_data_master = balance_data
        self.cash_flow_data_master = cash_flow_data
        self.market_data_master = market_data
        self.financial_ratio_data_master = financial_ratio_data
        self.required_columns = {
            'income': {'netIncome', 'revenue', 'eps', 'costOfRevenue', 'operatingExpenses', 'weightedAverageShsOut'},
            'balance': {'totalLiabilities', 'totalAssets', 'netReceivables', 'inventory', 'totalStockholdersEquity'},
            'cash_flow': {'operatingCashFlow'},
            'market': {'close'},
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

    def safe_get_value(self, df, column):
        if df.empty or column not in df.columns:
            return np.nan
        try:
            return df[column].iloc[0]
        except Exception:
            return np.nan

    def calculate_financial_liability(self):
        return self.safe_get_value(self.balance_data, 'totalLiabilities')

    # to be changed
    def calculate_price_cashflow(self):
        return self.safe_get_value(self.financial_ratio_data, 'priceCashFlowRatio')
    
    # to be changed
    def calculate_priceToBook(self):
        return self.safe_get_value(self.financial_ratio_data, 'priceToBookRatio')

    # to be changed
    def calculate_price_to_sales(self):
        return self.safe_get_value(self.financial_ratio_data, 'priceToSalesRatio')

    # to be changed
    def calculate_price_to_earnings(self):
        return self.safe_get_value(self.financial_ratio_data, 'priceEarningsRatio')

    def calculate_ltd_to_ta(self):
        total_assets = self.safe_get_value(self.balance_data, 'totalAssets')
        if pd.isna(total_assets) or total_assets == 0:
            return np.nan
        total_liabilities = self.safe_get_value(self.balance_data, 'totalLiabilities')
        return total_liabilities / total_assets
    
    # to be changed (ttm)
    def calculate_net_profit(self):
        return self.safe_get_value(self.income_data, 'netIncome')

    # to be changed (wrong formula)
    def calculate_ebit(self):
        revenue = self.safe_get_value(self.income_data, 'revenue')
        cost = self.safe_get_value(self.income_data, 'costOfRevenue')
        op_exp = self.safe_get_value(self.income_data, 'operatingExpenses')
        if pd.isna(revenue) or pd.isna(cost) or pd.isna(op_exp):
            return np.nan
        return revenue - cost - op_exp

    # to be changed (wrong formula)
    def calculate_working_capital_ratio(self):
        total_assets = self.safe_get_value(self.balance_data, 'totalAssets')
        if pd.isna(total_assets) or total_assets == 0:
            return np.nan
        op_cf = self.safe_get_value(self.cash_flow_data, 'operatingCashFlow')
        return op_cf / total_assets

    # to be changed (wrong formula)
    def calculate_quick_ratio(self):
        revenue = self.safe_get_value(self.income_data, 'revenue')
        if pd.isna(revenue) or revenue == 0:
            return np.nan
        net_receivables = self.safe_get_value(self.balance_data, 'netReceivables')
        inventory = self.safe_get_value(self.balance_data, 'inventory')
        return (net_receivables + inventory) / revenue

    # change nomenclature & formula is wrong as-well & to be removed
    def calculate_ev_to_ocl(self):
        total_liabilities = self.safe_get_value(self.balance_data, 'totalLiabilities')
        if pd.isna(total_liabilities) or total_liabilities == 0:
            return np.nan
        op_cf = self.safe_get_value(self.cash_flow_data, 'operatingCashFlow')
        return op_cf / total_liabilities

    # operating cashflow to total asset
    # ev to operating cashflow (ttm)
    # operating cashflow to net profit
    # debt to ebitda
    
    def calculate_debt_to_equity(self):
        total_equity = self.safe_get_value(self.balance_data, 'totalStockholdersEquity')
        if pd.isna(total_equity) or total_equity == 0:
            return np.nan
        total_liabilities = self.safe_get_value(self.balance_data, 'totalLiabilities')
        return total_liabilities / total_equity

    def calculate_all_factors(self):
        factors = []
        for i, income_row in self.income_data_master.iterrows():
            date = income_row['date']
            self.income_data = self.income_data_master[self.income_data_master['date'] == date]
            self.balance_data = self.balance_data_master[self.balance_data_master['date'] == date]
            self.cash_flow_data = self.cash_flow_data_master[self.cash_flow_data_master['date'] == date]
            self.market_data = self.market_data_master[self.market_data_master['date'] == date]
            self.financial_ratio_data = self.financial_ratio_data_master[self.financial_ratio_data_master['date'] == date]
            # If any required data is missing, skip this date
            if self.income_data.empty or self.balance_data.empty or self.cash_flow_data.empty or self.financial_ratio_data.empty:
                print(f"Warning: Skipping value factors for date {date} due to missing data")
                continue
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
        try:
            return pd.DataFrame(factors)
        except Exception as e:
            print(f"Error calculating value factors: {e}")
            return pd.DataFrame()
