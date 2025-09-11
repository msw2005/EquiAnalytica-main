import akshare as ak
from typing import Dict

def fetch_stock_financial_indicators(symbol: str, start_year: str) -> Dict:
    """
    Fetch historical financial indicators for a given stock symbol starting from start_year using AkShare.

    Args:
        symbol (str): Stock code (e.g., "600004").
        start_year (str): Year to start retrieval (e.g., "2020").

    Returns:
        Dict: A nested dictionary where each key is a report date ("日期") and its value is another dictionary
              containing financial indicators for that date. All values are strings.

        Example structure:
        {
            "2020-03-31": {
                "摊薄每股收益(元)": "0.23",
                "加权每股收益(元)": "0.20",
                ...
            },
            "2020-06-30": {
                "摊薄每股收益(元)": "0.25",
                ...
            },
            ...
        }

    Example:
        >>> result = fetch_stock_financial_indicators("600004", "2020")
        >>> # result is a dict keyed by dates
        >>> indicators_20200331 = result.get("2020-03-31")
    """
    try:
        # Retrieve DataFrame from AkShare
        df = ak.stock_financial_analysis_indicator(symbol=symbol, start_year=start_year)
        
        if df is None or df.empty:
            return {}

        # Convert all columns to string type
        df = df.astype(str)

        # Build nested dict: key = date, value = dict of other columns
        nested: Dict[str, Dict[str, str]] = {}
        for record in df.to_dict(orient='records'):
            date_key = record.get("日期")
            # Exclude the '日期' key from inner dict
            inner = {k: v for k, v in record.items() if k != "日期"}
            nested[date_key] = inner

        return nested

    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    

