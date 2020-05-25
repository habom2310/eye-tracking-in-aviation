import pandas as pd
import numpy as np

def check_percentage_null(df_data):
    df_x = df_data.copy()
    df_x.fillna(0, inplace=True)
    return len(df_x[df_x["X Pos"] != 0])/len(df_x)

def data_slicing(df_data, window_length = 1200, stride = 300):
    L = len(df_data)
    for i in range(L//stride):
        df_slice = df_data.iloc[i*stride:i*stride+window_length].copy()
        if len(df_slice) < 600:
            return
        else:
            yield df_slice.reset_index()