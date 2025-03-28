import pandas as pd
import numpy as np

class Growth:
    """
    A class to calculate growth-related financial factors.
    """
    def __init__(self, income_data, balance_data, cash_flow_data):
        self.income_data_master = income_data
        self.balance_data_master = balance_data
        self.cash_flow_data_master = cash_flow_data
        self.required_columns = {
            'income': {'eps', 'netIncome', 'revenue'},
            'balance': {'totalStockholdersEquity'},
            'cash_flow': {'operatingCashFlow'}
        }
        self._validate_columns()

    def _validate_columns(self):
        missing_cols = []
        for df_name, columns in self.required_columns.items():
            current_df = getattr(self, f"{df_name}_data_master")
            for col in columns:
                if col not in current_df.columns:
                    missing_cols.append(f"Current {df_name}: {col}")
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

    def safe_get_value(self, df, column):
        if df.empty or column not in df.columns:
            return np.nan
        try:
            return df[column].iloc[0]
        except Exception:
            return np.nan

    def calculate_peg(self):
        prev_eps = self.safe_get_value(self.prev_income_data, 'eps') if self.prev_income_data is not None else np.nan
        if pd.isna(prev_eps) or prev_eps == 0:
            return np.nan
        return self.safe_get_value(self.income_data, 'eps') / prev_eps

    def calculate_net_profit_growth(self):
        prev_net = self.safe_get_value(self.prev_income_data, 'netIncome') if self.prev_income_data is not None else np.nan
        if pd.isna(prev_net) or prev_net == 0:
            return np.nan
        return self.safe_get_value(self.income_data, 'netIncome') / prev_net

    def calculate_revenue_growth(self):
        prev_rev = self.safe_get_value(self.prev_income_data, 'revenue') if self.prev_income_data is not None else np.nan
        if pd.isna(prev_rev) or prev_rev == 0:
            return np.nan
        return self.safe_get_value(self.income_data, 'revenue') / prev_rev

    def calculate_net_asset_growth(self):
        prev_equity = self.safe_get_value(self.prev_balance_data, 'totalStockholdersEquity') if self.prev_balance_data is not None else np.nan
        if pd.isna(prev_equity) or prev_equity == 0:
            return np.nan
        return self.safe_get_value(self.balance_data, 'totalStockholdersEquity') / prev_equity

    def calculate_operating_cashflow_growth(self):
        prev_ocf = self.safe_get_value(self.prev_cash_flow_data, 'operatingCashFlow') if self.prev_cash_flow_data is not None else np.nan
        if pd.isna(prev_ocf) or prev_ocf == 0:
            return np.nan
        return (self.safe_get_value(self.cash_flow_data, 'operatingCashFlow') / prev_ocf) - 1

    def calculate_all_factors(self):
        factors = []
        for _, income_row in self.income_data_master.iterrows():
            date = income_row['date']
            self.income_data = self.income_data_master[self.income_data_master['date'] == date]
            self.balance_data = self.balance_data_master[self.balance_data_master['date'] == date]
            self.cash_flow_data = self.cash_flow_data_master[self.cash_flow_data_master['date'] == date]
            self.prev_income_data = None
            if not self.income_data_master[self.income_data_master['date'] < date].empty:
                self.prev_income_data = self.income_data_master[self.income_data_master['date'] < date].iloc[-1:]
            self.prev_balance_data = None
            if not self.balance_data_master[self.balance_data_master['date'] < date].empty:
                self.prev_balance_data = self.balance_data_master[self.balance_data_master['date'] < date].iloc[-1:]
            self.prev_cash_flow_data = None
            if not self.cash_flow_data_master[self.cash_flow_data_master['date'] < date].empty:
                self.prev_cash_flow_data = self.cash_flow_data_master[self.cash_flow_data_master['date'] < date].iloc[-1:]
            factors.append({
                'date': date,
                'PEG': self.calculate_peg(),
                'net_profit_growth_rate': self.calculate_net_profit_growth(),
                'total_revenue_growth_rate': self.calculate_revenue_growth(),
                'net_asset_growth_rate': self.calculate_net_asset_growth(),
                'net_operate_cashflow_growth_rate': self.calculate_operating_cashflow_growth()
            })
        try:
            return pd.DataFrame(factors)
        except Exception as e:
            print(f"Error calculating growth factors: {e}")
            return pd.DataFrame()
