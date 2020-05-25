import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt


def transition_matrix(transitions):
    if len(transitions) == 0:
        return 0
    n = 1+ max(transitions) #number of states

    M = [[0]*n for _ in range(n)]

    for (i,j) in zip(transitions,transitions[1:]):
        M[i][j] += 1

    #now convert to probabilities:
    for row in M:
        s = sum(row)
        if s > 0:
            row[:] = [f/s for f in row]

    return M

def distance(x,y):
    return ((x[0]-y[0])**2 + (x[1]-y[1])**2)**0.5

def get_center(clustering, data):
    center = []
    for i in range(len(set(clustering.labels_)) - 1):
        xi = data[np.where(clustering.labels_ == i)]
        cx = sum(xi.T[0])/len(xi)
        cy = sum(xi.T[1])/len(xi)
        center.append((cx,cy))

    return center

def dbscan_predict(cluster_center, X_new, min_dist = 50, metric=distance):
    # Result is noise by default
    y_new = np.ones(shape=len(X_new), dtype=int)*-1 

    # Iterate all input samples for a label
    for j, x_new in enumerate(X_new):
        # Find a core sample closer than EPS
        for i, x_core in enumerate(cluster_center): 
            if metric(x_new, x_core) < min_dist:
                # Assign label of x_core to x_new
                y_new[j] = i
                break

    return y_new

def dbscan_predict2(cluster_center, X_new, min_dist = 50, metric=distance):
    # Result is noise by default
    y_new = np.ones(shape=len(X_new), dtype=int)*-1 

    # Iterate all input samples for a label
    for j, x_new in enumerate(X_new):
        # Find a core sample closer than EPS
        dist = [metric(x_new, v) for v in cluster_center]
        # print("dist", dist)
        # print("argmin", np.argmin(dist))
        if len(dist) == 0:
            continue
        y_new[j] = np.argmin(dist)

    return y_new

def entropy(X, max_dist=20, min_samples=3, cluster_method="DBSCAN"):
    # clustering
    clustering = DBSCAN(eps=max_dist, min_samples=min_samples, metric=distance).fit(X)
    # print("X", X)
    cluster_center = get_center(clustering,X)
    # print("cluster_center", cluster_center)
    pred = dbscan_predict2(cluster_center, X)
    # print("pred", pred)

    transitions = pred[np.where(pred!=-1)]
    # print("trans", transitions)

    # transition matrix and GTE, SGE
    trans_matrix = transition_matrix(transitions)
    Hs = 0
    Ht = 0
    if trans_matrix != 0:
        pA = [len(np.where(np.array(transitions)==i)[0])/len(transitions) for i in range(len(set(transitions)))]
        for i in range(len(pA)):
            Hs += -1 * np.nan_to_num(pA[i]*np.log2(pA[i]))
            t = np.nan_to_num(trans_matrix[i]*np.log2(trans_matrix[i]))
            Ht += -sum(pA[i]*(t))

    cluster_center =[[v[0] for v in cluster_center], [v[1] for v in cluster_center]]

    # color = clustering.labels_
    # # print("color", color)
    # img = plt.imread("flight.jpg")
    # fig=plt.figure(figsize=(15,8))
    # ax=fig.add_axes([0,0,1,1])
    # # ax.imshow(img, extent=[0, 1600, 0, 900])
    # ax.imshow(img)
    # ax.scatter(cluster_center[0], cluster_center[1], s=100, c = "red")
    # ax.scatter(X.T[0],X.T[1], c=color, cmap="jet", s=5, alpha = 0.7)

    # ax.set_xlabel('x')
    # ax.set_ylabel('y')
    # ax.set_title('center')
    # plt.show()

    return Hs, Ht


import eye_metrics_utils
import data_utils
import warnings
# warnings.filterwarnings(action='once')
warnings.filterwarnings('ignore')
if __name__ == "__main__":
    csv_file = "data/PISSS_ID_003_Approach Two Gaze-Vergence.csv"
    df_data = pd.read_csv(csv_file)

    for v in data_utils.data_slicing(df_data.copy()):
        Efix = eye_metrics_utils.detect_fixations(v)
        print(Efix)
        X = np.array(Efix).T[3:].T
        Hs, Ht = entropy(X)
        print(Hs, Ht)
