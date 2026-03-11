import streamlit as st # type: ignore
import plotly.graph_objects as go # type: ignore
import os
import glob
from utils.data_preprocess import load_pacing_data # type: ignore

st.set_page_config(page_title="Pacing Analysis", layout="wide")
st.title("Pacing & Velocity")

# --- (1) Historical Data ---
@st.cache_data
def get_historical_data():
    historical_dict = {}
    path = os.path.join("data", "historical_date_analysis", "*.csv")
    
    for file_path in glob.glob(path):
        show_name = os.path.basename(file_path).replace("_date_analysis.csv", "").title()
        historical_dict[show_name] = load_pacing_data(file_path)
        
    return historical_dict

historical_data = get_historical_data()

# --- (2) UI: upload current CSV ---
st.markdown("Current Show Tracing")
uploaded_file = st.file_uploader("Upload current date_analysis.csv", type='csv')


# --- (3) Historical Curves ---
if uploaded_file is not None or len(historical_data) > 0:
    
    fig_pacing = go.Figure()
    fig_velocity = go.Figure()

    # ---- A. Historical curves ----
    for show_name, df_hist in historical_data.items():
        # Figure 1：Pacing cumulative
        if 'Cumulative_Sales' in df_hist.columns:
            fig_pacing.add_trace(go.Scatter(
                x=df_hist['Date analysis'], 
                y=df_hist['Cumulative_Sales'],
                mode='lines', 
                opacity=0.5, 
                line=dict(width=2), 
                name=show_name, 
                hovertemplate="<b>" + show_name + "</b><br>Day Until Show: %{x} <br>Cumulative Sales: %{y} <extra></extra>" 
            ))
        
        # Figure 2：Velocity
        if 'Days_Since_On_Sale' in df_hist.columns:
            fig_velocity.add_trace(go.Scatter(
                x=df_hist['Days_Since_On_Sale'], 
                y=df_hist['Booked - Quantity'],
                mode='lines', 
                opacity=0.5,
                line=dict(width=1.5),
                name=show_name, 
                hovertemplate="<b>" + show_name + "</b><br>Day On Sale %{x} <br>Today's Sale: %{y} <extra></extra>"
            ))

    # ---- B. Current Show ----
    if uploaded_file is not None:
        df_current = load_pacing_data(uploaded_file)
        current_show_name = "Current Show" 
        
        # Figure 1
        if 'Cumulative_Sales' in df_current.columns:
            fig_pacing.add_trace(go.Scatter(
                x=df_current['Date analysis'], 
                y=df_current['Cumulative_Sales'],
                mode='lines', 
                line=dict(color='#d62728', width=5), 
                opacity=1.0, 
                name=current_show_name,
                hovertemplate="<b>" + current_show_name + "</b><br>Day Until Show: %{x} <br>Cumulative Sales: %{y} <extra></extra>" 
            ))
        
        # Figure 2
        if 'Days_Since_On_Sale' in df_current.columns:
            fig_velocity.add_trace(go.Bar(
                x=df_current['Days_Since_On_Sale'], 
                y=df_current['Booked - Quantity'],
                marker_color='#ff7f0e', 
                name=current_show_name,
                hovertemplate="<b>" + current_show_name + "</b><br>Day On Sale %{x} <br>Today's Sale: %{y} <extra></extra>"
            ))

    # ---- C. UI ----
    fig_pacing.update_layout(
        title="1. Cumulative Pacing",
        xaxis_title="Days to Premiere",
        yaxis_title="Total Tickets Sold",
        hovermode="closest", 
        showlegend=True, 
        legend=dict(title="Click to show/hide; Double click to focus"), 
        plot_bgcolor="white",
        height=600 
    )
    fig_pacing.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0', zeroline=True, zerolinecolor='black')
    fig_pacing.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

    fig_velocity.update_layout(
        title="2. Sales Velocity Spikes",
        xaxis_title="Days Since On Sale",
        yaxis_title="Daily Tickets Sold",
        hovermode="closest", 
        showlegend=True, 
        legend=dict(title="Show List"),
        plot_bgcolor="white",
        height=500
    )
    fig_velocity.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')
    fig_velocity.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

    st.plotly_chart(fig_pacing, use_container_width=True)
    st.plotly_chart(fig_velocity, use_container_width=True)