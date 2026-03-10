import pandas as pd

def load_pacing_data(file):
    df = pd.read_csv(file)

    df.columns = [c.strip() for c in df.columns]
    df['Date analysis'] = pd.to_numeric(df['Date analysis'], errors='coerce')
    df = df.dropna(subset=['Date analysis'])
    
    df = df.sort_values(by='Date analysis', ascending=True)

    if 'Booked - Quantity' in df.columns:
        df['Cumulative_Sales'] = df['Booked - Quantity'].cumsum()
    
    return df