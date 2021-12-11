import numpy as np
import pandas as pd
from collections import defaultdict
from tqdm import tqdm

import roi_config
import utils

label = roi_config.label
roi_center = roi_config.roi_center
encode_table = roi_config.encode_table

def get_center(clustering, data):
    center = []
    for i in range(len(set(clustering.labels_)) - 1):
        xi = data[np.where(clustering.labels_ == i)]
        cx = sum(xi.T[0])/len(xi)
        cy = sum(xi.T[1])/len(xi)
        center.append((cx,cy))
    return center


def create_transition_matrix(transitions):
    m = pd.crosstab(pd.Series(list(transitions)[1:], name = "t+1"),
            pd.Series(list(transitions)[:-1], name = "t"),normalize=1)
        
    return m

def create_transition_count_matrix(transitions):
    m = pd.crosstab(pd.Series(list(transitions)[1:], name = "t+1"),
            pd.Series(list(transitions)[:-1], name = "t"))
        
    return m

def encode_transition(transitions, label_type = "random"):
    """
    assign a random letter for each roi
    """
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    L = list(set(transitions))
    print(L)
    enc_transitions = ""
    for roi in transitions:
        enc_transitions += letters[L.index(roi)]
        
    return enc_transitions, L

def decode_transitions(enc_transitions, list_labels):
    letters = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    dec_transitions = []
    for enc_t in enc_transitions:
        dec_transitions.append(list_labels[letters.index(enc_t)])
        
    return dec_transitions

def find_all(p, s):
    '''Yields all the positions of
    the pattern p in the string s.'''
    i = s.find(p)
    while i != -1:
        yield i
        i = s.find(p, i+1)
        
def find_index_of_most_subseq(enc_transitions, L):
    '''
    enc_transitions: encoded transitions
    '''
    length = 2
    subseqcount = defaultdict(int)

    for i in range(len(enc_transitions)-length + 1):
        substring = enc_transitions[i:i+length]
        subseqcount[substring] += 1
    max_subseq = max(subseqcount, key=subseqcount.get)
    max5 = {k:subseqcount.get(k) for k in sorted(subseqcount, key=subseqcount.get, reverse=True)[:5]}
    print("max 5 subseq:", max5)
    print("max_subseq:", max_subseq)
    print("max_subseq decode:", decode_transitions(max_subseq, L))
    list_idx_max_subseq = list(find_all(max_subseq, enc_transitions))
    
    return list_idx_max_subseq

def merge_2roi_to_1roi(df_fixation, list_idx):
    df_data = df_fixation.copy()
    for idx in list_idx:
        df_x = df_data.loc[idx:idx + 1]
        start = df_x.iloc[0]["start"]
        end = df_x.iloc[1]["end"]
        duration = end - start
        x = df_x.iloc[0]["x"]
        y = df_x.iloc[0]["y"]
        roi = "{}_{}".format(df_x.iloc[0]['roi'], df_x.iloc[1]['roi'])
        
        df_data.loc[idx] = start, end, duration, x, y, roi
        if idx + 1 not in list_idx:
            df_data = df_data.drop(idx + 1)
        
    return df_data.reset_index(drop=True)