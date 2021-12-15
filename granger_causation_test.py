import numpy as np
import pandas as pd
import itertools
from statsmodels.tsa.stattools import grangercausalitytests, adfuller, kpss

def construct_signal(start, end, signal_end, sr = 1000, signal_type = "rect"):
    signal = np.zeros(int(signal_end*sr), dtype=int)

    if signal_type == "rect":
        for i, s in enumerate(start):
            s = int(start[i]*sr)
            e = int(end[i]*sr)
            signal[s:e] = 1
    elif signal_type == "spike":
        for i, s in enumerate(start):
            s = int(start[i]*sr)
            signal[s] = 1
        
    return signal


def create_signal_from_transitions(df_transition, sr = 10, signal_type = "rect"):
    list_signals = {}
    signal_end = list(df_transition["end"])[-1]
    for roi in list(set(df_transition["roi"])):
        df_x = df_transition[df_transition["roi"] == roi]
        start = df_x['start'].values
        end = df_x['end'].values
        signal = construct_signal(start, end, signal_end, sr, signal_type)
        list_signals[roi] = signal
        
    return list_signals


def adf_test(time_series):
    """
    tests the null hypothesis that a unit root is present in a time series sample."""
    result = adfuller(time_series)
    print('ADF Statistics: %f' % result[0])
    print('p-value: %f' % result[1])
    print('Critical values:')
    for key, value in result[4].items():
        print('\t%s: %.3f' % (key, value))
    return result

def kpss_test(time_series):
    '''
    testing a null hypothesis that an observable time series is stationary 
    around a deterministic trend (i.e. trend-stationary) against the alternative of a unit root.'''
    result = kpss(time_series)
    statistic, p_value, n_lags, critical_values = result
    
    print(f'KPSS Statistic: {statistic}')
    print(f'p-value: {p_value}')
    print(f'num lags: {n_lags}')
    print('Critial Values:')
    for key, value in critical_values.items():
        print(f'   {key} : {value}')
    return result


def granger_causality_test(signals_from_transitions):
    rois = list(signals_from_transitions.keys())
    list_perm = list(itertools.permutations(rois, 2))

    df_granger = pd.DataFrame(columns = ["roi1", "roi2", "lag", "pval"])

    for perm in list_perm:
        data = pd.DataFrame(signals_from_transitions)[list(perm)]
        maxlag = 4
        x = grangercausalitytests(data, maxlag=maxlag, verbose=False)
        lroi1 = [perm[0]] * maxlag
        lroi2 = [perm[1]] * maxlag
        llag = np.arange(maxlag)
        lpval = []
        for i in range(1, maxlag + 1):
            p_val = x[i][0]["ssr_ftest"][1]
            lpval.append(round(p_val, 3))
            
        df_x = pd.DataFrame({"roi1": lroi1,
                            "roi2": lroi2,
                            "lag": llag,
                            "pval": lpval})
        df_granger = pd.concat([df_granger, df_x], ignore_index=True)

    return df_granger

# from mongo_connection import Mongo_connection

# mongo = Mongo_connection()
# mongo.connect()
# document = mongo.find_one({"pID": "001", "trial": 2})

# d_data = document["data"]
# df_data = pd.DataFrame(d_data)

# signal = create_signal_from_transitions(df_data)

# df_granger = granger_causality_test(signal)

# print(df_granger[df_granger["pval"] < 0.05])