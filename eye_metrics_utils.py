import pandas as pd
import numpy as np

def cal_dist(df_data, x_col = "X Pos", y_col = "Y Pos"):
    df_data[['xnext', 'ynext']] = df_data.loc[1:].reset_index()[[x_col, y_col]]

    def lambda_dist(x, y, xnext, ynext):
        return np.sqrt((xnext - x)**2 + (ynext - y)**2)

    dist = df_data.apply(lambda x: lambda_dist(x[x_col], x[y_col], x['xnext'], x['ynext']), axis=1)[:-1]
    df_data['dist'] = np.insert(dist.values, 0, None)

    return df_data

def consecutive(data, stepsize=1):
    return np.split(data, np.where(np.diff(data) != stepsize)[0]+1)

def cleanup(df_data, x_col = "X Pos", y_col = "Y Pos"):
    df_x = df_data.copy()
    dif = np.abs(df_x["Display"].diff())
    for arr in consecutive(np.where(dif!=0)[0]):
        if len(arr) == 1:
            continue
        else:
            df_x.drop(df_x[(df_x.index >= arr[0]) & (df_x.index <=arr[-1]) & (df_x["Display"] == -1)].index, inplace=True)
    
    return df_x.reset_index()

def detect_fixations(df_data, max_dist = 5, min_dur = 5, x_col = "X Pos", y_col = "Y Pos", time_col = "Start Time (secs)", is_cleanup = True):
    df_x = df_data.copy()
    if is_cleanup == True:
        df_x = cleanup(df_x)
    df_x = cal_dist(df_x)
    time = df_x[time_col].values
    x = df_x[x_col].values
    y = df_x[y_col].values
    condition = np.array(df_x.iloc[:-1]['dist'].values < max_dist, dtype = int)
    diff = np.diff(condition)
    starts = np.where(diff==1)[0]
    ends = np.where(diff==-1)[0] 
    if len(ends) == 0 or len(starts) == 0: # no fixation
        return []

    if starts[0] > ends[0]: #data starts with fixation
        starts = np.insert(starts,0,0)
    if starts[-1] > ends[-1]: #data ends with fixation
        ends = np.append(ends, len(x) - 1)

    Efix = []
    # compile blink starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1
        # append only if the duration in samples is equal to or greater than
        # the minimal duration
        if e-s >= min_dur:
            meanx = np.mean(x[s:e])

            meany = np.mean(y[s:e])

            # add ending time
            Efix.append([time[s], time[e], time[e]-time[s], meanx, meany])
    
    return pd.DataFrame(Efix, columns=["start", "end", "duration", "x", "y"])

def detect_blinks(df_data, missing = 0.0, min_dur = 3, x_col = "X Pos", y_col = "Y Pos", time_col = "Start Time (secs)"):
    df_x = df_data.copy()
    df_x = cleanup(df_x)
    time = df_x[time_col].values
    df_x.fillna(0.0, inplace=True)
    condition = np.array(df_x.iloc[:-1][x_col].values == missing, dtype = int)
    diff = np.diff(condition)
    starts = np.where(diff==1)[0] + 1
    ends = np.where(diff==-1)[0] 
    if len(ends) == 0 or len(starts) == 0: # no blink
        return []

    if starts[0] > ends[0]: #data starts with blink
        starts = np.insert(starts,0,0)
    if starts[-1] > ends[-1]: #data ends with blink
        ends = np.append(ends, len(time) - 1)

    Eblk = []
    # compile starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1
        # append only if the duration in samples is equal to or greater than
        # the minimal duration
        if e-s >= min_dur:
            # add ending time
            Eblk.append([time[s], time[e], time[e]-time[s]])
    
    return pd.DataFrame(Eblk, columns=["start", "end", "duration"])

def detect_saccades(df_data, min_dist = 10, min_dur = 3, x_col = "X Pos", y_col = "Y Pos", time_col = "Start Time (secs)"):
    df_x = df_data.copy()
    df_x = cal_dist(df_x)
    time = df_x[time_col].values
    x = df_x[x_col].values
    y = df_x[y_col].values
    condition = np.array(df_x.iloc[:-1]['dist'].values > min_dist, dtype = int)
    diff = np.diff(condition)
    starts = np.where(diff==1)[0]
    ends = np.where(diff==-1)[0] 
    if len(ends) == 0 or len(starts) == 0: # no saccade
        return []

    if starts[0] > ends[0]: #data starts with saccade
        starts = np.insert(starts,0,0)
    if starts[-1] > ends[-1]: #data ends with saccade
        ends = np.append(ends, len(x) - 1)
    
    Esac = []
    # compile starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1
        # append only if the duration in samples is equal to or greater than
        # the minimal duration
        if e-s >= min_dur:
            intdist = (np.diff(x[s:e])**2 + np.diff(y[s:e])**2)**0.5
            inttime = np.diff(time[s:e])
            vel = intdist / inttime
            acc = np.diff(vel)

            # add ending time
            Esac.append([time[s], time[e], time[e]-time[s], max(vel), max(acc)])
    
    return pd.DataFrame(Esac, columns=["start", "end", "duration", "velocity", "acceleration"])


def detect_microsaccades(df_data, min_dist = 5, max_dist = 10, min_dur = 1, x_col = "X Pos", y_col = "Y Pos", time_col = "Start Time (secs)"):
    df_x = df_data.copy()
    df_x = cleanup(df_x)
    df_x = cal_dist(df_x)
    time = df_x[time_col].values
    x = df_x[x_col].values
    y = df_x[y_col].values

    a = df_x.iloc[:-1]['dist'].values
    cond1 = a > min_dist
    cond2 = a < max_dist
    condition = np.array(np.logical_and(cond1, cond2), dtype = int)

    diff = np.diff(condition)
    starts = np.where(diff==1)[0]
    ends = np.where(diff==-1)[0] 
    if len(ends) == 0 or len(starts) == 0: # no microsaccade
        return []

    if starts[0] > ends[0]: #data starts with microsaccade
        starts = np.insert(starts,0,0)
    if starts[-1] > ends[-1]: #data ends with microsaccade
        ends = np.append(ends, len(x) - 1)
    
    Emsac = []
    # compile starts and ends
    for i in range(len(starts)):
        # get starting index
        s = starts[i]
        # get ending index
        if i < len(ends):
            e = ends[i]
        elif len(ends) > 0:
            e = ends[-1]
        else:
            e = -1
        # append only if the duration in samples is equal to or greater than
        # the minimal duration
        if e-s >= min_dur:
            # intdist = (np.diff(x[s:e])**2 + np.diff(y[s:e])**2)**0.5
            # inttime = np.diff(time[s:e])
            # vel = intdist / inttime
            # acc = np.diff(vel)
            
            # add ending time
            Emsac.append([time[s], time[e], time[e]-time[s]])
    
    return Emsac

# if __name__ == "__main__":
#     csv_file = "data/PISSS_ID_003_Approach Two Gaze-Vergence.csv"
#     df_data = pd.read_csv(csv_file)
#     Emsac = detect_microsaccades(df_data)
#     print(Emsac)