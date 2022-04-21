from mongo_connection import Mongo_connection
import numpy as np
import pandas as pd
import pair_transition_analysis
import granger_causation_test
from matplotlib import pyplot as plt
from collections import defaultdict
import roi_config
import fixation
import hypothesis_testing


mongo = Mongo_connection()
mongo.connect()

def get_basic_metrics(df_fixation):
    d = {}
    d["fixation_mean_duration"] = df_fixation["duration"].mean()
    d["fixation_rate"] = len(df_fixation)/df_fixation["end"].values[-1]*1000/60
    d["saccade_amplitude"] = np.sqrt(np.diff(df_fixation["x"])**2 + np.diff(df_fixation["y"])**2).mean()
    d["saccade_mean_duration"] = np.mean(df_fixation["start"].values[1:] - df_fixation["end"].values[:-1])
    
    return d

def create_transition_matrix(transitions):
    m = pd.crosstab(pd.Series(list(transitions)[1:], name = "t+1"),
            pd.Series(list(transitions)[:-1], name = "t"),normalize=1)
        
    return m

def calculate_entropy(transitions):
    if len(transitions) == 0:
        return 0, 0
#     transitions = replace_repeated_character(transitions)

    trans_matrix = create_transition_matrix(transitions)
    m = {}
    for c in trans_matrix.columns:
        m[c] = trans_matrix[c].tolist()

    Hs = 0
    Ht = 0
    pA = {c:len(np.where(np.array(list(transitions))==c)[0])/len(transitions) for c in list(set(transitions))}

    for k,v in pA.items():
        Hs += -1 * np.nan_to_num(v*np.log2(v))
        Ht += -sum(pA[k]*(np.nan_to_num(m[k]*np.log2(m[k]))))
        
    return Hs, Ht

def get_advanced_metrics(df_fixation):
    d = {}
    transitions, L = pair_transition_analysis.encode_transition(df_fixation["roi"])
    Hs, Ht = calculate_entropy(transitions)
    d["Hs"] = Hs
    d["Ht"] = Ht
    
    return d


def get_dwell_stat(df_data):
    agg_sum = df_data.groupby(["roi"]).agg({'duration': 'sum'})
    agg_sum_percent = agg_sum/sum(agg_sum['duration'])
    agg_mean = df_data.groupby(["roi"]).agg({'duration': 'mean'})
    agg_var = df_data.groupby(["roi"]).agg({'duration': 'var'})
    agg_fixrate = df_data.groupby(["roi"]).agg({'duration': 'count'})/df_data.iloc[-1]["end"]*1000/60
    
    list_roi = list(set(df_data["roi"]))
    d = {}
    for roi in list_roi:
        d["duration_{}".format(roi)] = agg_sum.loc[roi][0]
        d["duration_percentage_{}".format(roi)] = agg_sum_percent.loc[roi][0]
        d["duration_average_{}".format(roi)] = agg_mean.loc[roi][0]
        d["duration_var_{}".format(roi)] = agg_var.loc[roi][0]
        d["fix_rate_{}".format(roi)] = agg_fixrate.loc[roi][0]
        
#     df_data = fixation.merge_consecutive_fixations_in_same_roi(df_data)
    
#     df_runway = df_data[df_data["roi"]=="runway"]
#     duration_in_between_runway = df_runway["start"].values[1:] - df_runway["end"].values[:-1]
#     n_transition_in_between_runway = np.diff(df_runway.index) - 1
#     d["between_runway_mean_duration_all"] = np.mean(duration_in_between_runway/n_transition_in_between_runway)
    
#     n_trans = list(set(n_transition_in_between_runway))
#     for n in range(1,4):
#         d["between_runway_n_trans_{}".format(n)] = sum(n_transition_in_between_runway==n)
#         d["between_runway_mean_duration_{}".format(n)] = np.mean(duration_in_between_runway[np.where(n_transition_in_between_runway == n)])

    return d

def run_dwell_stats(cmd):
    documents = mongo.find(cmd)
    d = defaultdict(list)
    for document in documents:
        print("trial: {}, group: {}, pID: {}".format(document["trial"], document["group"], document["pID"]))
        if document["trial"] == 4:
            continue
            
        d['pID'].append(document["pID"])
        d['group'].append(document["group"])
        d['trial'].append(document["trial"])
        d['rating'].append(document["rating"])
        
        
        d["null_percent"].append(document["null_percent"])
    #     d["calibration"].append(document["calibration"])
        d_data = document["data"]
        df_data = pd.DataFrame(d_data)
        
        d_dwell = get_dwell_stat(df_data)
        for k in roi_config.encode_table.keys():
            d["duration_{}".format(k)].append(d_dwell.get("duration_{}".format(k), 0))
            d["duration_percentage_{}".format(k)].append(d_dwell.get("duration_percentage_{}".format(k), 0))
            d["duration_average_{}".format(k)].append(d_dwell.get("duration_average_{}".format(k), 0))
            d["fix_rate_{}".format(k)].append(d_dwell.get("fix_rate_{}".format(k), 0))
            
    #     for k in d_dwell.keys():
    #         if "between_runway" in str(k):
    #             d[k].append(d_dwell.get(k, 0))
    df_dwell = pd.DataFrame(d).sort_values(["pID","trial", "group","rating"]).dropna().reset_index().drop(columns=["index"])
    return df_dwell

def run_basic_metrics(cmd):
    documents = mongo.find(cmd)
    d = defaultdict(list)
    for document in documents:
        print("trial: {}, group: {}, pID: {}".format(document["trial"], document["group"], document["pID"]))
        if document["trial"] == 4:
            continue

        d['pID'].append(document["pID"])
        d['group'].append(document["group"])
        d['trial'].append(document["trial"])
            
        d["null_percent"].append(document["null_percent"])
    #     d["calibration"].append(document["calibration"])
        d_data = document["data"]
        df_data = pd.DataFrame(d_data)
        transitions, L = pair_transition_analysis.encode_transition(df_data["roi"])
        
        basic_metrics = get_basic_metrics(df_data)
        advance_metrics = get_advanced_metrics(df_data)
        
        d["fixation_mean_duration"].append(basic_metrics["fixation_mean_duration"])
        d["fixation_rate"].append(basic_metrics["fixation_rate"])
        d["saccade_amplitude"].append(basic_metrics["saccade_amplitude"])
        d["saccade_mean_duration"].append(basic_metrics["saccade_mean_duration"])
        
        # d["Hs"].append(advance_metrics["Hs"])
        # d["Ht"].append(advance_metrics["Ht"])

    #     for ngram_length in range(3,7):
    #         subseqcount = defaultdict(dict)

    #         for i in range(len(transitions)-ngram_length + 1):
    #             substring = transitions[i:i+ngram_length]
    #             if subseqcount[substring].get("count"):
    #                 subseqcount[substring]["count"] += 1
    #                 subseqcount[substring]["duration"] += df_data.iloc[i:i+ngram_length]["duration"].sum()
    #             else:
    #                 subseqcount[substring]["count"] = 1
    #                 subseqcount[substring]["duration"] = df_data.iloc[i:i+ngram_length]["duration"].sum()

    #         sorted_subseqcount = {k: v for k, v in sorted(subseqcount.items(), key=lambda item: item[1]["count"], reverse=True)}
    #         more_than_2_time_seq = {k: v for k, v in subseqcount.items() if v["count"] >= 2}
    #         count_of_most_seq = 0
    #         N_unique_seq = 0
    #         print(sorted_subseqcount)
    #         if len(subseqcount.values())>0:
    #             count_of_most_seq = max(subseqcount.values())/sum(subseqcount.values())
    #             N_unique_seq = len(subseqcount.keys())
                
    #         N_unique_seq_more_than_2_times = 0
    #         if len(more_than_2_time_seq.values())>0:
    #             N_unique_seq_more_than_2_times = len(more_than_2_time_seq.keys())
                
    #         d["N_unique_seq_{}".format(ngram_length)].append(N_unique_seq)
    #         d["count_of_most_seq_{}".format(ngram_length)].append(count_of_most_seq)
    #         d["N_unique_seq_more_than_2_times_{}".format(ngram_length)].append(N_unique_seq_more_than_2_times)
    #         d["mean_repetition_{}".format(ngram_length)].append(np.mean(list(more_than_2_time_seq.values())))


    df_res = pd.DataFrame(d).sort_values(["pID","trial", "group","rating"]).dropna().reset_index().drop(columns=["index"])
    return df_res
    
