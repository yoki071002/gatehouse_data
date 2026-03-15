import streamlit as st # type: ignore
import plotly.graph_objects as go # type: ignore
import os
import glob
from utils.data_preprocess import load_pacing_data # type: ignore
from utils.model_engine import find_similar_shows # type: ignore

st.set_page_config(page_title="Forecasting", layout="wide")
st.title("KNN Curve Matching Forecast")
st.markdown("""
**How it works:** This model doesn't rely on subjective guesswork. The algorithm takes the current show's sales trajectory and performs **Dynamic Time Alignment** against the historical database. It identifies the 3 historical shows with the most similar sales patterns at this exact same stage in their lifecycle, and uses their final results to project a realistic fan-out forecast range.
""")

# --- (1) Historical data ---
@st.cache_data
def get_historical_data():
    historical_dict = {}
    path = os.path.join("data", "historical_date_analysis", "*.csv")
    for file_path in glob.glob(path):
        show_name = os.path.basename(file_path).replace("_date_analysis.csv", "").title()
        historical_dict[show_name] = load_pacing_data(file_path)
    return historical_dict

historical_data = get_historical_data()

# --- (2) Current Show ---
with st.sidebar:
    st.header("Data Input")
    uploaded_file = st.file_uploader("Upload current show's date_analysis.csv", type='csv')

if uploaded_file is not None and len(historical_data) > 0:
    df_current = load_pacing_data(uploaded_file)
    
    result = find_similar_shows(df_current, historical_data, top_k=3)
    
    st.divider()
    
    # --- (3) Forecasting Metric ---
    days_out = abs(result['current_day'])
    st.subheader(f"Forecast based on T-{days_out} Days Out")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Min Forecast", f"{int(result['min_pred'])} tickets", delta="Worst-case", delta_color="off")
    with col2:
        st.metric("Baseline Forecast", f"{int(result['avg_pred'])} tickets", delta="Most likely expected", delta_color="normal")
    with col3:
        st.metric("Max Forecast", f"{int(result['max_pred'])} tickets", delta="Best-case potential", delta_color="normal")
        
    st.info(f"Model Insight: The algorithm identified the 3 most historically similar shows: {', '.join(result['matches'])}. The projections above are directly derived from the final total sales of these nearest neighbors.")

    # --- (4) Trajectory Fan-out Prediction Chart ---
    st.subheader("Trajectory Fan-out View")
    fig = go.Figure()

    colors = ['rgba(44, 160, 44, 0.6)', 'rgba(255, 127, 14, 0.6)', 'rgba(148, 103, 189, 0.6)']
    
    for i, show_name in enumerate(result['matches']):
        df_hist = historical_data[show_name]
        fig.add_trace(go.Scatter(
            x=df_hist['Date analysis'], 
            y=df_hist['Cumulative_Sales'],
            mode='lines', 
            line=dict(color=colors[i], width=2, dash='dot'),
            name=f"Ref: {show_name} (Final: {int(result['final_sales'][i])})"
        ))

    fig.add_trace(go.Scatter(
        x=df_current['Date analysis'], 
        y=df_current['Cumulative_Sales'],
        mode='lines', 
        line=dict(color='#d62728', width=4), 
        name="Current Show"
    ))
    
    fig.add_vline(x=result['current_day'], line_width=2, line_dash="dash", line_color="black")
    fig.add_annotation(
        x=result['current_day'], 
        y=df_current['Cumulative_Sales'].max(),
        text="Today's Progress", 
        showarrow=True, 
        arrowhead=1,
        ay=-40
    )

    fig.update_layout(
        xaxis_title="Days to Premiere (T-Minus)",
        yaxis_title="Cumulative Tickets Sold",
        hovermode="x unified",
        plot_bgcolor="white",
        height=600,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0', zeroline=True, zerolinecolor='black')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#f0f0f0')

    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Please upload the current show's CSV data from the left sidebar to activate the forecasting engine.")