import yfinance as yf

def format_number(value):
    """Format large numbers into B (Billion) or M (Million)."""
    if value >= 1_000_000_000:
        return f"{value / 1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"
    else:
        return f"{value:,}"  # Keep smaller numbers with commas
    
def get_ic(symbol,type="quarterly"):
    ticker = yf.Ticker(symbol)

    if type =="quarterly":
        df_quarterly = ticker.quarterly_financials 
        return df_quarterly
    elif type =="annual":
        df_annual = ticker.financials
        return df_annual


def get_bs(symbol,type="quarterly"):
    ticker = yf.Ticker(symbol)
    if type =="quarterly":
        df_quarterly = ticker.quarterly_balance_sheet
        return df_quarterly
    elif type =="annual":
        df_annual = ticker.balance_sheet
        return df_annual

def get_cf(symbol,type="quarterly"):
    ticker = yf.Ticker(symbol)
    if type =="quarterly":
        df_quarterly = ticker.quarterly_cashflow
        return df_quarterly
    elif type =="annual":
        df_annual = ticker.cashflow
        return df_annual

def get_institutional_holders(symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.institutional_holders
    return df

def get_major_holders(symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.major_holders
    return df