import streamlit as st
import datetime
from dateutil.relativedelta import relativedelta
from components.overview import show_overview,show_news
from components.financialdata import sankey_plot
from components.financialTrend import show_income_trend
from components.insider import show_holdings_pies,show_insider_transactions
def main():
    st.set_page_config(page_title="Stock Dashboard", layout="wide")

# 頂部選單
    menu = st.sidebar.radio("Choose the page", ["Overview", "Financial Data","Financial Trend", "Insider & Whale"])
    # 1) User input: Stock symbol
    symbol = st.sidebar.text_input("Enter a stock symbol (e.g., AAPL, TSLA):", "AAPL")


    if menu == "Overview":
        st.title("Stock Dashboard")
        st.write("Welcome to the Stock Dashboard!")
        show_overview(symbol)
        show_news(symbol)
    elif menu == "Financial Data":
        st.title("Financial Data")
        st.write("Breakdown financial report for certain period.")
        period_choice = st.selectbox("Select Period Type", ["quarterly", "annual"])
        sankey_plot(symbol,period_choice)
    elif menu == "Insider & Whale":
        st.title("Big Whale and Insider.")
        st.write("Show the shareholding distribution.")
        show_holdings_pies(symbol)
        show_insider_transactions(symbol)
    elif menu == 'Financial Trend':
        st.title("Income Statement Line Charts")
        st.write("Show the trend of financial data.")
        period_choice = st.selectbox("Select Period Type", ["quarterly", "annual"])
        show_income_trend(symbol, period_choice)
        


   

if __name__ == "__main__":
    main()