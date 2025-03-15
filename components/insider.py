import streamlit as st
import plotly.express as px
import pandas as pd
from components.utils import get_institutional_holders, get_major_holders
from components.config import FINNCLIENT, STARTDATE
import datetime
def show_holdings_pies(symbol):
    """
    Generates two pie charts:
    1. Overall shareholding distribution: Insiders vs. Institutions vs. Others
    2. Top 10 institutions' shareholding distribution within total institutional holdings
    """
    major_hold = get_major_holders(symbol)
    institution_hold = get_institutional_holders(symbol)

    insiders_pct = major_hold.at["insidersPercentHeld", "Value"]
    institutions_pct = major_hold.at["institutionsPercentHeld","Value"]
    #
    others_pct = 1 - insiders_pct - institutions_pct
    if others_pct < 0:  # 數據有時可能略超過1
        others_pct = 0

    
    st.write(f'latest update:{institution_hold["Date Reported"].unique()[0]}')

    df_pie1 = pd.DataFrame({
        "Category": ["Insiders", "Institutions", "Others"],
        "Percent": [insiders_pct, institutions_pct, others_pct]
    })
    fig1 = px.pie(
        df_pie1,
        values="Percent",
        names="Category",
        title="(Insiders vs Institutions vs Others)",
        hover_data={"Percent": ":.2%"}  # 顯示為百分比格式
    )
    # 在圖中顯示百分比+類別
    fig1.update_traces(
        textposition="inside",
        textinfo="percent+label"
    )
    

    # -------------------------------------------------------------------
   

    # institution_hold 應該是一個 DataFrame
    #   Holder, pctHeld, Value, pctChange, ...
    df_insti = institution_hold.copy()

    # 機構持股佔全部公司股份 = institutions_pct
    # 若 want：前10 機構相對機構總量 => df_insti["pctOfInstitution"] = (pctHeld / institutions_pct) * 100
    df_insti["pctOfInstitution"] = (df_insti["pctHeld"] / institutions_pct).fillna(0) * 100

    # 我們用 px.pie 顯示這個 "pctOfInstitution"
    fig2 = px.pie(
        df_insti,
        values="pctOfInstitution",
        names="Holder",
        title="Top 10 Institutions vs. Institutional Holdings (Percentage)",
        hover_data=["Value", "pctChange", "pctHeld"]
    )
    
# Display text inside the pie slices
    fig2.update_traces(
        textposition='inside',
        textinfo='percent+label'
    )

    # Customize hover template
    fig2.update_traces(
        hovertemplate=(
            "<b>%{label}</b><br>"
            "Institutional Holding Percentage: %{value:.2f}%<br>"
            "Relative to Total Company Shares: %{customdata[2]:.2%}<br>"
            "Value: %{customdata[0]:$,.0f}<br>"
            "Percentage Change: %{customdata[1]:.2%}<extra></extra>"
        )
    )
    colA, colB = st.columns(2)
    with colA:
        st.subheader("1) Insiders vs Institutions vs Others")
        st.plotly_chart(fig1, use_container_width=True)
    with colB:
        st.subheader("2) TOP 10 Institutions' Shareholding Distribution")
        st.plotly_chart(fig2, use_container_width=True)
   


def show_insider_transactions(symbol):
    
    order = ["transactionDate","change","Transaction value","transactionPrice","share","isDerivative","name","transactionCode"]
    transactions = FINNCLIENT.stock_insider_transactions(symbol,STARTDATE,datetime.datetime.today())     
    transactions = pd.DataFrame(transactions["data"])
    transactions.drop(columns=["id","currency","filingDate","source","symbol"], inplace=True)
    transactions["Transaction value"] = transactions["share"] * transactions["transactionPrice"]
    transactions = transactions[order]
    transactions.set_index("transactionDate", inplace=True)
    
    ## Plot streamlit
    st.subheader("3) Insider Transactions")
    if transactions.empty:
        st.write("No insider transaction data available for the selected period.")
        
    if "transactionDate" in transactions.columns:
        transactions["transactionDate"] = pd.to_datetime(transactions["transactionDate"])
        transactions.sort_values("transactionDate", ascending=True, inplace=True)
    with st.expander("Click to view Insider Transaction Codes & Explanations"):
        st.write("""
            ### Insider Transaction Codes & Explanations

            - **P**: **Purchase** – The insider bought shares in the open market.
            - **S**: **Sale** – The insider sold shares in the open market.
            - **A**: **Grant, Award, or Other Acquisition** – The insider received shares through a grant, stock award, or another type of acquisition (often part of compensation).
            - **D**: **Disposition (Non-Sale-Related)** – The insider transferred shares without a sale (e.g., gifts or moving shares to a trust).
            - **G**: **Gift** – The insider gifted shares to another person or entity.
            - **M**: **Exercise of Stock Options** – The insider exercised stock options, meaning they converted stock options into actual shares.
            - **C**: **Conversion of Derivative Securities** – The insider converted derivative securities (e.g., convertible bonds, warrants) into common stock.
            - **F**: **Payment of Exercise Price or Tax Liability by Selling Shares** – The insider sold shares to cover option exercise costs or taxes.
            - **X**: **Exercise of Stock Options (Tax-Related)** – Similar to "M" but specifically when exercised for tax purposes.
            - **V**: **Voluntary Report of Transaction** – The insider voluntarily reported a transaction that was not required by law.
            - **I**: **Indirect Ownership** – The shares are owned indirectly (e.g., through a trust, family member, or company).
            - **J**: **Other Acquisition or Disposition (Not Otherwise Listed)** – Any transaction that doesn’t fall into other categories.
            - **K**: **Equity Swap or Similar** – The insider participated in an equity swap transaction.
            """)

    st.dataframe(transactions)
    
   
    if "change" in transactions.columns:
    # Reset index to make 'transactionDate' a regular column
        transactions = transactions.reset_index()
        
        # Ensure 'transactionDate' is a datetime type
        transactions["transactionDate"] = pd.to_datetime(transactions["transactionDate"])
        
        # Group by date and sum the 'change' values
        insider_bar_data = transactions.groupby(transactions["transactionDate"].dt.date)["change"].sum().reset_index()

        # Add a color column: green for positive, red for negative
        insider_bar_data["color"] = insider_bar_data["change"].apply(lambda x: "green" if x > 0 else "red")

        # Create a bar chart with custom colors
        fig = px.bar(
            insider_bar_data,
            x="transactionDate",
            y="change",
            title="Insider Transactions Change by Date",
            labels={"transactionDate": "Date", "change": "Change"},
            color="color",  # Use color column
            color_discrete_map={"green": "green", "red": "red"}  # Define color mapping
        )

        
        st.plotly_chart(fig, use_container_width=True)