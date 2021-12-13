import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from tqdm import tqdm
from sklearn.cluster import DBSCAN
from statsmodels.tsa.stattools import grangercausalitytests, adfuller, kpss
from mongo_connection import Mongo_connection

import roi_config
import eye_metrics_utils
import data_utils
import utils

label = roi_config.label
roi_center = roi_config.roi_center

pdict = utils.get_pdict()

def calibration(df_fix, roi_center):
    diffx = []
    diffy = []
    idxmin= []
    for i in range(len(df_fix)):
        x = df_fix.iloc[i]
        m = np.argmin(x[-6:])
        idxmin.append(m)
        mx = list(roi_center.values())[m][0]
        my = list(roi_center.values())[m][1]

        if m == 0:
            w = 0.3
        else:
            w = 1
        diffx.append(w * (x.x - mx))
        diffy.append(w * (x.y - my))
    offsetx = np.mean(diffx)
    offsety = np.mean(diffy)
    print("offsetx", offsetx)
    print("offsety", offsety)
    
    return offsetx, offsety

def merge_consecutive_fixations_in_same_roi(df_fix):
    df_fix['value_grp'] = (df_fix.roi != df_fix.roi.shift()).cumsum()

    return pd.DataFrame({ 'start' : df_fix.groupby('value_grp').start.first(), 
                          'end' : df_fix.groupby('value_grp').end.last(),
                          'duration' : df_fix.groupby('value_grp').duration.sum(), 
                          'x' : df_fix.groupby('value_grp').x.mean(),
                          'y': df_fix.groupby('value_grp').y.mean(),
                          'roi': df_fix.groupby('value_grp').roi.first()
                         }).reset_index(drop=True)

def run_one_data(filename):
    print(filename)
    df_data = pd.read_csv(filename)

    df_data = data_utils.reset_time(df_data)
    null_percent = data_utils.check_percentage_null(df_data)
    if null_percent > 0.2:
        print("null percent: {}, exclude ID {}".format(null_percent, filename[14:17]))
        return 0

    df_fixation = eye_metrics_utils.detect_fixations(df_data)
    df_blink = eye_metrics_utils.detect_blinks(df_data)
    df_saccade = eye_metrics_utils.detect_saccades(df_data)

    X = df_fixation[["x", "y"]].values
    clustering = DBSCAN(eps=20, min_samples=5, metric = utils.distance).fit(X)
    df_fixation["roi"] = clustering.labels_
    df_fixation = merge_consecutive_fixations_in_same_roi(df_fixation)

    for k,v in roi_center.items():
        df_fixation["{}".format(k)] = df_fixation.apply(lambda x: utils.distance(x[["x","y"]], v), axis=1)
        
        
    X = df_fixation[["x", "y"]].values
    clustering = DBSCAN(eps=20, min_samples=5, metric = utils.distance).fit(X)

    color = clustering.labels_
    df_fixation["roi"] = clustering.labels_
        
#     img = plt.imread("flight.jpg")
#     h,w,c = img.shape
#     fig=plt.figure(figsize=(15,8))
#     ax=fig.add_axes([0,0,1,1])
#     # ax.imshow(img, extent=[0, 1600, 0, 900])
#     ax.imshow(img)
# #     ax.scatter(cluster_center[0], cluster_center[1], s=30, marker = "x", c = "red")
#     ax.scatter(X.T[0],X.T[1], c=color, cmap="jet", alpha = 0.5)

#     ax.set_xlabel('x')
#     ax.set_ylabel('y')
#     ax.set_title('center')

    offsetx, offsety = calibration(df_fixation, roi_center)
    df_fixation["x"] = df_fixation.x - offsetx
    df_fixation["y"] = df_fixation.y - offsety
    
    return df_fixation

def dist_func(point, v1, v2, type="c"): #between points and rectange/cirle
    """
    point: x, y
    v1,v2: topleft,bottomright if type = "r"
    v1,v2: center (x,y), diameter if type = "c"
    """    
    d = 0
    if type == "r":
        dx = max(v1[0] - point[0], 0, point[0] - v2[0])
        dy = max(v1[1] - point[1], 0, point[1] - v2[1])
        
        d = np.sqrt(dx*dx + dy*dy)
    elif type == "c":
        d = np.sqrt((point[0]-v1[0])**2 + (point[1]-v1[1])**2) - v2
        
    return d

def get_fixation_sequences(df_fixation, label = label, threshold = 20):
    roi = []
    count = 0
    pdict = utils.get_pdict()

    for i in range(len(df_fixation)):
        x = df_fixation.iloc[i]
        point = (x.x, x.y)
        d = [dist_func(point, v[0], v[1], v[2]) for k,v in label.items()]
        order = np.argsort(d)
        if 0.0 not in d: # point is outside ROI
            if d[order[0]] > threshold:
                key = "unknown"
            else:
                key = list(pdict.keys())[order[0]]
        else:# point falls inside a ROI
            count += 1
            key = list(pdict.keys())[order[0]]
    #     print(d, order, key)
        roi.append(key)
    return roi

# import glob
# csv_files = glob.glob("data/*.csv")
# csv_files_one = [v for v in csv_files if "One Gaze-Vergence" in v]
# csv_files_two = [v for v in csv_files if "Two Gaze-Vergence" in v]
# csv_files_three = [v for v in csv_files if "Three Go-Around Gaze-Vergence" in v]

# filename = csv_files_two[10]
# df_fixation = run_one_data(filename)
# roi = get_fixation_sequences(df_fixation)
# df_fixation["roi"] = roi
# df_fixation = merge_consecutive_fixations_in_same_roi(df_fixation)
# transitions = df_fixation["roi"]
# print(df_fixation.head())