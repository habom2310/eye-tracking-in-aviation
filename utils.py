import roi_config
import cv2
from collections import defaultdict
import numpy as np
from datetime import datetime
from airtable import config, airtable

table = airtable.AirTableClient(
    config.config['airtable']['api_key'],
    config.config['airtable']['base_id'],
    config.config['airtable']['table']
)

encode_table = roi_config.encode_table
label = roi_config.label

def distance(x, y):
    return ((x[0]-y[0])**2 + (x[1] - y[1])**2)**0.5

def encode(lst_transition):
    str_transition = ""
    for v in lst_transition:
        str_transition = str_transition + encode_table[v]
    return str_transition

def decode(str_transition):
    lst_transition = []
    for v in str_transition:
        key_index = list(encode_table.values()).index(v)
        lst_transition.append(list(encode_table.keys())[key_index])
    return lst_transition

def get_pdict(label = label):
    img = cv2.imread("flight.jpg")
    h,w,c = img.shape

    pdict = defaultdict()
    for key in label:
        if label[key][-1] == "c":
            mask = np.zeros((h,w), np.uint8)
            cv2.circle(mask,label[key][0], label[key][1],255,-1)
            points = np.where(mask==255)
            pdict[key] = points
        elif label[key][-1] == "r":
            mask = np.zeros((h,w), np.uint8)
            cv2.rectangle(mask,label[key][0], label[key][1],255,-1)
            points = np.where(mask==255)
            pdict[key] = points

    return pdict

def log_to_airtable(res):
    now = datetime.now()
    
    result = res
    result['Time'] = now.strftime('%H:%M:%S %d-%m-%Y')

    table.add_row(result)
    
    print(result)