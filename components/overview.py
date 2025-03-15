import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from components.config import FINNCLIENT, STARTDATE
import datetime
import pandas as pd
from plotly.subplots import make_subplots
import textwrap
from components.utils import format_number
def get_candle_data(symbol, start_date, end_date):
    """
    使用 Finnhub Client 取得指定區間的日 K 線資料，並轉換成適合 mplfinance 的 DataFrame。
    """
    end_dt_inclusive = end_date + datetime.timedelta(days=1)

    candle_df = yf.download(
        symbol,
        start=start_date,
        end=end_dt_inclusive,
        interval='1d'
    )
    
    if candle_df.empty:
        return pd.DataFrame()
    candle_df.columns = candle_df.columns.get_level_values(0)
    
    # 只留我們要用的欄位
    candle_df = candle_df[['Open', 'High', 'Low', 'Close', 'Volume']].astype(float)
  
    # 讓 index 名稱是 "Date"
    candle_df.index.name = "Date"

    #plot
    st.subheader("Daily Candlestick Chart")
    if candle_df.empty:
        st.write("No candlestick data for this symbol and date range.")
        return

    fig = make_subplots(
        rows=1, cols=1, 
        shared_xaxes=True, 
        specs=[[{"secondary_y": True}]]  # 開啟次 Y 軸
    )

    # K 線圖
    fig.add_trace(go.Candlestick(
        x=candle_df.index,
        open=candle_df['Open'],
        high=candle_df['High'],
        low=candle_df['Low'],
        close=candle_df['Close'],
        increasing_line_color='green',  # 上漲顏色
        decreasing_line_color='red',    # 下跌顏色
        name='Candlestick'
    ), secondary_y=True)

    # 成交量顏色（用紅綠做區分）
    volume_colors = [
        'green' if close >= open_ else 'red'
        for open_, close in zip(candle_df['Open'], candle_df['Close'])
    ]

    # 成交量 (Bar)
    fig.add_trace(go.Bar(
        x=candle_df.index,
        y=candle_df['Volume'],
        marker_color=volume_colors,
        opacity=0.5,
        name="Volume"
    ), secondary_y=False)

    # 調整 Layout
    fig.update_layout(
        title="Stock Price & Volume Chart",
        xaxis_title="Date",
        yaxis_title="Volume",   # 左側 Y 軸
        yaxis2_title="Price",   # 右側 Y 軸
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        barmode='overlay',
        bargap=0.2,
        bargroupgap=0.2
    )

    # 在 Streamlit 中顯示
    st.plotly_chart(fig, use_container_width=True)


def show_overview(symbol):
    # 下載股票數據
    stock_data = yf.Ticker(symbol)
    profile = FINNCLIENT.company_profile2(symbol=symbol)
    weburl = profile.get("weburl", "N/A")
    logo_url = profile.get("logo", "")
    # 創建左右兩欄布局
    col1, col2 = st.columns([1, 2])  # 左邊 1，右邊 2（右側較大）

    with col1:  # **左邊顯示基本資訊**

        info = stock_data.info
        if logo_url:
                st.markdown(
                    f"""
                    <div style="display: flex; align-items: center;">
                        <img src="{logo_url}" width="50" style="margin-right: 10px;">
                        <h3 style="margin: 0;">Basic Info</h3>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        else:
            st.subheader("📌 Basic info")
        st.write(f"**Company Name:** {info.get('longName', 'N/A')}")
        st.write(f"**Symbol:** {info.get('symbol', 'N/A')}")
        st.write(f"**MarketCap:** {format_number(info.get('marketCap', 'N/A'))} USD")
        st.write(f"**Price:** {info.get('currentPrice', 'N/A')} USD")
        st.write(f"**PE Ratio:** {info.get('trailingPE', 'N/A')}")
        st.write(f"**EPS:** {info.get('trailingEps', 'N/A')}")
        st.write(f"**Industry:** {info.get("industry")}")
        st.write(f"**Sector:** { info.get("sector", "Unknown Sector")}")
        with st.expander("📖 Click to view Business Summary"):
            st.write(f"**Business Summary:** {info.get("longBusinessSummary", "Unknown summary")}")
        if weburl != "N/A":
            st.markdown(f"[🌐 Company Website]({weburl})", unsafe_allow_html=True)
    
    with col2:  # k chart
        st.subheader("📈 K chart")
        # 顯示 K 線
        get_candle_data(symbol, datetime.datetime.strptime(STARTDATE, "%Y-%m-%d"), datetime.datetime.today())
    
    

def show_news(symbol):
    news = FINNCLIENT.company_news(symbol,_from=(datetime.datetime.today()-datetime.timedelta(days=7)).strftime('%Y-%m-%d'), to=datetime.datetime.today().strftime('%Y-%m-%d'))
    show_all = st.button("Show more")
    
    if show_all:
        news_to_display = news  # 顯示全部
    else:
        news_to_display = news[:5]  # 顯示前5則

    st.write(f"**{symbol} 的最新新聞**")
    
    # 3) 逐篇展示
    for i, article in enumerate(news_to_display):
        headline = article.get("headline", "No Title")
        image_url = article.get("image")
        summary = article.get("summary", "")
        news_url = article.get("url", "#")
        source = article.get("source", "")
        dt = article.get("datetime", "")  # 可能是時間戳記，可再處理格式

        # 顯示標題
        st.subheader(f"{i+1}. {headline}")
        
        # 若有圖片就顯示
        if image_url:
            st.image(image_url, width=300)

        # 若想摘要只顯示部分，可以裁剪 summary
        short_summary = textwrap.shorten(summary, width=300, placeholder="...")
        st.write(short_summary)
        
        # 顯示來源 & 時間
        st.write(f"**Source**: {source}")
        st.write(f"**DateTime**: {datetime.datetime.fromtimestamp(dt,datetime.UTC)}")
        # 若要轉成人類可讀時間，可以用 datetime.fromtimestamp(dt)
        # st.write(f"**DateTime**: {datetime.fromtimestamp(dt).strftime('%Y-%m-%d %H:%M:%S')}")

        # 新聞連結
        st.markdown(f"[Read more]({news_url})")
        
        st.write("---")  # 分隔線
