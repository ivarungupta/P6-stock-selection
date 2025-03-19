# models/factors.py

import pandas as pd
from data_sources.fmp import FMPWrapper
from .quality import Quality
from .value import Value
from .stock import Stock
from .growth import Growth
from .emotional import Emotional
from .style import Style
from .risk import Risk
from .momentum import Momentum
from .technical import Technical

class FactorsWrapper:
    """
    A wrapper class to aggregate all factor calculations for a given ticker using data from FMP.

    It fetches financial statements and market data via the FMPWrapper, converts the responses to DataFrames,
    and passes them to the individual factor calculation classes.
    """
    def __init__(self, ticker, fmp: FMPWrapper, start_date, end_date, period="quarterly"):
        self.ticker = ticker
        self.fmp = fmp
        self.period = period

        # Fetch current financial statements and convert to DataFrames.
        self.income_data = self._get_df(self.fmp.get_income_statement(self.ticker, period=self.period))
        self.balance_data = self._get_df(self.fmp.get_balance_sheet(self.ticker, period=self.period))
        self.cash_flow_data = self._get_df(self.fmp.get_cash_flow_statement(self.ticker, period=self.period))
        self.enterprise_data = self._get_df(self.fmp.get_enterprise_values(self.ticker, period=self.period))

        # For growth factors, fetch the previous period data.
        self.prev_income_data = self._get_df(self.fmp.get_income_statement(self.ticker, period=self.period), index=1)
        self.prev_balance_data = self._get_df(self.fmp.get_balance_sheet(self.ticker, period=self.period), index=1)
        self.prev_cash_flow_data = self._get_df(self.fmp.get_cash_flow_statement(self.ticker, period=self.period), index=1)
        
        # Fetch historical market data for market-related factors.
        # Adjust the date range as needed.
        self.market_data = self.fmp.get_historical_price(self.ticker, start_date, end_date)
        
    def _get_df(self, data, index=0):
        """
        Convert the JSON response (a list of dicts) from FMPWrapper to a pandas DataFrame.
        If the list contains more than one period, use the element at the provided index.
        """
        if isinstance(data, list) and len(data) > index:
            return pd.DataFrame([data[index]])
        elif isinstance(data, list) and len(data) > 0:
            return pd.DataFrame([data[0]])
        else:
            return pd.DataFrame()

    def calculate_all_factors(self):
        results = {}

        # Quality factors
        try:
            quality_obj = Quality(
                income_data=self.income_data,
                balance_data=self.balance_data,
                cash_flow_data=self.cash_flow_data,
                prev_income_data=self.prev_income_data
            )
            results['quality'] = quality_obj.calculate_all_factors()
        except Exception as e:
            results['quality'] = f"Error: {e}"

        # Value factors
        try:
            value_obj = Value(
                income_data=self.income_data,
                balance_data=self.balance_data,
                cash_flow_data=self.cash_flow_data,
                enterprise_data=self.enterprise_data
            )
            results['value'] = value_obj.calculate_all_factors()
        except Exception as e:
            results['value'] = f"Error: {e}"

        # Stock factors
        try:
            stock_obj = Stock(
                income_data=self.income_data,
                balance_data=self.balance_data,
                cash_flow_data=self.cash_flow_data,
                enterprise_data=self.enterprise_data
            )
            results['stock'] = stock_obj.calculate_all_factors()
        except Exception as e:
            results['stock'] = f"Error: {e}"

        # Growth factors
        try:
            growth_obj = Growth(
                income_data=self.income_data,
                balance_data=self.balance_data,
                cash_flow_data=self.cash_flow_data,
                prev_income_data=self.prev_income_data,
                prev_balance_data=self.prev_balance_data,
                prev_cash_flow_data=self.prev_cash_flow_data
            )
            results['growth'] = growth_obj.calculate_all_factors()
        except Exception as e:
            results['growth'] = f"Error: {e}"

        # Emotional factors using market data
        try:
            emotional_obj = Emotional(self.market_data)
            results['emotional'] = emotional_obj.calculate_all_factors()
        except Exception as e:
            results['emotional'] = f"Error: {e}"

        # Style factors (stub - adjust if style factor calculations are implemented)
        try:
            combined_data = self.market_data.copy()
            sp500_returns = pd.DataFrame({'returns': [0.01, 0.02, -0.01, 0.005]})
            tickers = [self.ticker]
            style_obj = Style(combined_data, sp500_returns, tickers)
            results['style'] = {}  # Placeholder since no calculate_all_factors method is defined.
        except Exception as e:
            results['style'] = f"Error: {e}"

        # Risk factors
        try:
            risk_obj = Risk(
                df=self.market_data,
                risk_free_rate_20=0.02,
                risk_free_rate_60=0.02
            )
            results['risk'] = risk_obj.calculate_all_factors()
        except Exception as e:
            results['risk'] = f"Error: {e}"

        # Momentum factors
        try:
            momentum_obj = Momentum(self.market_data)
            results['momentum'] = momentum_obj.calculate_all_factors()
        except Exception as e:
            results['momentum'] = f"Error: {e}"

        # Technical factors
        try:
            technical_obj = Technical(self.market_data)
            results['technical'] = technical_obj.calculate_all_factors()
        except Exception as e:
            results['technical'] = f"Error: {e}"

        return results

if __name__ == "__main__":
    # For testing this module individually.
    api_key = "bEiVRux9rewQy16TXMPxDqBAQGIW8UBd"
    fmp = FMPWrapper(api_key)
    ticker = "AAPL"
    wrapper = FactorsWrapper(ticker, fmp)
    all_factors = wrapper.calculate_all_factors()
    print(all_factors)
