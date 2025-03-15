import streamlit as st
import pandas as pd
import plotly.express as px
from components.utils import get_ic
def show_financial_trend(symbol):
    return 0
def show_income_trend(symbol, period_type="quarterly"):
    """
    1) 從 yfinance 抓取損益表 (年度或季度)
    2) 轉置後整理欄位
    3) 產生四張折線圖(2×2):
       (A) Total Revenue & Net Income
       (B) Gross Margin & Net Margin
       (C) EPS 成長圖 (Basic EPS & Diluted EPS 成長率)
       (D) Operating Income & Operating Expenses & EBITDA
    """

    # 1) 取得 DataFrame（columns=日期、index=科目）
    df = get_ic(symbol, type=period_type)
    
    if df.empty:
        st.warning(f"No {period_type} financial data for {symbol}.")
        return

    # 2) 轉置 -> 每列代表一個日期 (e.g. 2023-12-31)
    df_t = df.T  # df_t.index = 報表日期, df_t.columns = 科目名稱
    df_t = df_t.dropna(subset=["Total Revenue","Basic EPS"])
    # -- 我們會用到的欄位，若無則補0 --
    needed_cols = [
        "Total Revenue", "Net Income", "Gross Profit", 
        "Operating Income", "Operating Expense", "EBITDA",
        "Basic EPS", "Diluted EPS"
    ]
    for col in needed_cols:
        if col not in df_t.columns:
            df_t[col] = 0
    for col in needed_cols:
        df_t[col] = pd.to_numeric(df_t[col], errors="coerce").fillna(0)
    # 3) 計算毛利率 / 淨利率
    #    如果 "Total Revenue"=0，避免除零
    df_t["Gross Margin"] = (df_t["Gross Profit"] / df_t["Total Revenue"]).fillna(0)
    df_t["Net Margin"] = (df_t["Net Income"] / df_t["Total Revenue"]).fillna(0)

    # 4) 做成易繪圖格式: index -> 欄位 "ReportDate"
    df_t = df_t.reset_index().rename(columns={"index": "ReportDate"})
    # 排序一下日期
    df_t = df_t.sort_values("ReportDate")
    # -- EPS 成長率計算 (第3張圖) --
    # 若為年度 -> 與前1期相比 (YoY)
    # 若為季度 -> 與前4期相比 (approx. YoY)
    # shift_n = 1 if period_type == "annual" else 4

    # # pct_change(shift_n)*100 => %成長率
    # df_t["BasicEPS Growth (%)"] = df_t["Basic EPS"].pct_change(shift_n)*100
    # df_t["DilutedEPS Growth (%)"] = df_t["Diluted EPS"].pct_change(shift_n)*100

    # # 缺值用0填
    # df_t["BasicEPS Growth (%)"] = df_t["BasicEPS Growth (%)"].fillna(0)
    # df_t["DilutedEPS Growth (%)"] = df_t["DilutedEPS Growth (%)"].fillna(0)

    #
    # ---- (A) Total Revenue & Net Income ----
    #
    fig1 = px.line(
        df_t,
        x="ReportDate",
        y=["Total Revenue", "Net Income"],
        markers=True,
        title=f"{symbol.upper()} - {period_type.capitalize()} Total Revenue & Net Income"
    )
    fig1.update_layout(xaxis_title="Report Date", yaxis_title="Amount (USD)")

    #
    # ---- (B) Gross Margin & Net Margin ----
    #
    # 轉換成百分比顯示
    df_t["Gross Margin (%)"] = df_t["Gross Margin"] * 100
    df_t["Net Margin (%)"] = df_t["Net Margin"] * 100

    fig2 = px.line(
        df_t,
        x="ReportDate",
        y=["Gross Margin (%)", "Net Margin (%)"],
        markers=True,
        title=f"{symbol.upper()} - {period_type.capitalize()} Gross/Net Margin"
    )
    fig2.update_layout(xaxis_title="Report Date", yaxis_title="Margin (%)")

    #
    # ---- (C) EPS 成長圖 (Basic EPS & Diluted EPS Growth %) ----
    #
    fig3 = px.line(
        df_t,
        x="ReportDate",
        y=["Basic EPS", "Diluted EPS"],
        markers=True,
        title=f"{symbol.upper()} - {period_type.capitalize()} EPS"
    )
    fig3.update_layout(
        xaxis_title="Report Date",
        yaxis_title="EPS"
    )

    #
    # ---- (D) Operating Income & Operating Expenses & EBITDA ----
    #
    fig4 = px.line(
        df_t,
        x="ReportDate",
        y=["Operating Income", "Operating Expense", "EBITDA"],
        markers=True,
        title=f"{symbol.upper()} - {period_type.capitalize()} Operating & EBITDA"
    )
    fig4.update_layout(xaxis_title="Report Date", yaxis_title="Amount (USD)")

    # -- 2×2 方式排版 --
    col1, col2 = st.columns(2)
    col1.plotly_chart(fig1, use_container_width=True)
    col2.plotly_chart(fig2, use_container_width=True)

    col3, col4 = st.columns(2)
    col3.plotly_chart(fig3, use_container_width=True)
    col4.plotly_chart(fig4, use_container_width=True)