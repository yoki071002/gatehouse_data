import pandas as pd
import numpy as np

def get_filled_cumulative_sales(df, min_day, max_day):
    if df.empty or 'Date analysis' not in df.columns:
        return pd.Series(dtype=float)
    
    s = df.set_index('Date analysis')['Cumulative_Sales']
    full_index = np.arange(min_day, max_day + 1)
    s = s.reindex(full_index)
    s = s.ffill().fillna(0)
    
    return s

def find_similar_shows(df_current, historical_dict, top_k=3):
    current_day = df_current['Date analysis'].max() 
    start_day = df_current['Date analysis'].min()   

    current_series = get_filled_cumulative_sales(df_current, start_day, current_day)

    distances = {}
    final_sales_dict = {}

    for show_name, df_hist in historical_dict.items():
        if df_hist.empty or 'Date analysis' not in df_hist.columns:
            continue

        final_sale = df_hist['Cumulative_Sales'].max()
        final_sales_dict[show_name] = final_sale

        hist_series = get_filled_cumulative_sales(df_hist, start_day, current_day)

        diff = current_series - hist_series
        distance = np.sqrt(np.sum(diff**2))
        distances[show_name] = distance

    sorted_shows = sorted(distances.items(), key=lambda item: item[1])
    top_matches = sorted_shows[:top_k]

    top_final_sales = [final_sales_dict[show[0]] for show in top_matches]
    matched_names = [show[0] for show in top_matches]

    return {
        'matches': matched_names,
        'distances': [show[1] for show in top_matches],
        'final_sales': top_final_sales,
        'max_pred': max(top_final_sales) if top_final_sales else 0,
        'min_pred': min(top_final_sales) if top_final_sales else 0,
        'avg_pred': np.mean(top_final_sales) if top_final_sales else 0,
        'current_day': current_day
    }