import streamlit as st # type: ignore
import pandas as pd
from utils.data_preprocess import load_pacing_data

st.set_page_config(page_title="Pacing Analysis", layout="wide")
st.title("Pacing")

st.info("info holder")

uploaded_file = st.file_uploader("Upload CSV", type='csv')

if uploaded_file:
    df = load_pacing_data(uploaded_file)
    
    with st.expander("Data Preview"):
        st.dataframe(df)

    # Holder for graph
    st.subheader("curve")
    st.line_chart(df.set_index('Date analysis')['Cumulative_Sales'])
else:
    st.warning("waiting for upload")