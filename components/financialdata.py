import streamlit  as st
import plotly.graph_objects as go
from components.config import FINNCLIENT,STARTDATE
from components.utils import get_ic,format_number
import datetime
import pandas as pd


def sankey_plot(symbol,period_choice = "quarterly"):
    df = get_ic(symbol,type=period_choice)
    df_q = df.T
    
    available_periods = df_q.index.tolist()  # e.g. [Timestamp('2022-09-30 00:00:00'), ...]
    if period_choice == "quarterly":
        selected_periods = st.selectbox("Select a Quarter End Date", available_periods)
    elif period_choice == "annual":
        selected_periods = st.selectbox("Select a Year End Date", available_periods)
 

    # 篩選出該季度數據
    row = df_q.loc[selected_periods]

  
    # 1) 各節點的標籤
    labels = [
        "Total Revenue",                 # 0
        "Cost Of Revenue",               # 1
        "Gross Profit",                  # 2
        "Operating Expense",             # 3
        "EBITDA",                        # 4
        "Depreciation & Amortization",   # 5
        "Operating Income",              # 6
        "Pretax Income",                  # 7
        "Tax Provision",                  # 8
        "Net Income"                      # 9
    ]
    # 2) 流向 (來源 → 目標) 索引
    #   - 來源與目標都對應 labels 的索引位置
    sources = [0, 0, 2, 2, 4, 5, 6, 7, 7]
    targets = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # 3) 各流向對應的數值
    #    取不到值時預設給 0，避免 KeyError
    values = [
    row.get("Cost Of Revenue", 0),             # 0->1
    row.get("Gross Profit", 0),                # 0->2
    row.get("Operating Expense", 0),           # 2->3
    row.get("EBITDA", 0),                      # 2->4
    row.get("EBITDA", 0) - row.get("Operating Income", 0),
    row.get("Operating Income", 0),            # 4->6 (這裡其實是 5->6，請見下文)
    row.get("Pretax Income", 0),                # 6->7
    row.get("Tax Provision", 0),                # 7->8
    row.get("Net Income", 0)                    # 7->9
    ]


    link_colors = [
        # 0->1 (Cost)
        "rgba(255,0,0,0.4)",  
        # 0->2 (Leftover)
        "rgba(0,255,0,0.4)",  
        # 2->3 (Cost)
        "rgba(255,0,0,0.4)",
        # 2->4 (Leftover)
        "rgba(0,255,0,0.4)",
        # 4->5 (Cost)
        "rgba(255,0,0,0.4)",
        # 5->6 (Leftover)
        "rgba(0,255,0,0.4)",
        # 6->7 (Cost)
        "rgba(255,0,0,0.4)",
        # 7->8 (Cost)
        "rgba(255,0,0,0.4)",
        # 7->9 (Leftover)
        "rgba(0,255,0,0.4)"
    ]
    
    formatted_values = [format_number(v) for v in values]
    # -- 建立 Sankey 圖 --
    fig = go.Figure(go.Sankey(
       
        node=dict(
            pad=30,
            thickness=15,
            line=dict(color="black", width=0.5),
            label=labels,
            
        ),
        link=dict(
            source=sources,
            target=targets,
            value=values,
            color=link_colors,
            # hovertemplate=[
            # f"{labels[s]} → {labels[t]}<br>Value: {formatted_values[i]}" 
            # for i, (s, t) in enumerate(zip(sources, targets))
        
        )
    ))

    title_str = f"Sankey for {symbol} / {selected_periods.date()}"
    fig.update_layout(title_text=title_str, font_size=12, width=1000, height=800)

    st.plotly_chart(fig)
