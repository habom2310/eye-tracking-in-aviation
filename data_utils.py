import pandas as pd
import numpy as np

def reset_time(df_data):
    df_x = df_data.copy()
    df_x["Start Time (secs)"] = df_x["Start Time (secs)"] - df_x["Start Time (secs)"][0]
    return df_x
    
def check_percentage_null(df_data):
    return len(df_data[df_data["Display"] == -1])/len(df_data)

def data_slicing(df_data, window_length = 1200, stride = 300, min_length = 600):
    L = len(df_data)
    for i in range(L//stride):
        df_slice = df_data.iloc[i*stride:i*stride+window_length].copy()
        if len(df_slice) < min_length:
            return
        else:
            yield df_slice.reset_index()