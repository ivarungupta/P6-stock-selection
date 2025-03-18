import requests
import pandas as pd
import numpy as np
class FMPWrapper:
    def __init__(self, api_key):
        """
        Initialize the FMPWrapper class with the API key and base URL.
        """
        self.api_key = api_key
        self.base_url = "https://financialmodelingprep.com/api/v3"

    def _make_request(self, endpoint, params=None):
        """
        Internal method to make API requests.
        """
        if params is None:
            params = {}
        params['apikey'] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_historical_price(self, ticker, start_date, end_date):
        """
        Fetch historical price data for a given ticker and date range.
        """
        endpoint = f"historical-price-full/{ticker}"
        params = {
            "from": start_date,
            "to": end_date
        }
        data = self._make_request(endpoint, params)
        if "historical" in data:
            return pd.DataFrame(data["historical"])
        else:
            return pd.DataFrame()

    def get_financial_ratios(self, symbol):
        """
        Fetch financial ratios for a given symbol.
        """
        endpoint = f"ratios/{symbol}"
        return self._make_request(endpoint)

    def get_income_statement(self, symbol, period="annual"):
        """
        Fetch the income statement for a given symbol.
        """
        endpoint = f"income-statement/{symbol}"
        params = {"period": period}
        return self._make_request(endpoint, params)

    def get_balance_sheet(self, symbol, period="annual"):
        """
        Fetch the balance sheet for a given symbol.
        """
        endpoint = f"balance-sheet-statement/{symbol}"
        params = {"period": period}
        return self._make_request(endpoint, params)

    def get_cash_flow_statement(self, symbol, period="annual"):
        """
        Fetch the cash flow statement for a given symbol.
        """
        endpoint = f"cash-flow-statement/{symbol}"
        params = {"period": period}
        return self._make_request(endpoint, params)

    def get_stock_news(self, symbol, limit=50):
        """
        Fetch the latest stock news for a given symbol.
        """
        endpoint = f"stock_news"
        params = {"tickers": symbol, "limit": limit}
        return self._make_request(endpoint, params)

    def get_company_peers(self, symbol):
        """
        Fetch the peers of a given company.
        """
        endpoint = f"peers/{symbol}"
        return self._make_request(endpoint)

    def get_earnings_calendar(self, symbol):
        """
        Fetch the earnings calendar for a given symbol.
        """
        endpoint = f"earning_calendar/{symbol}"
        return self._make_request(endpoint)
