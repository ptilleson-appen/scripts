'''
python3
'''

#THIS WORKS AS WELL!

import itertools, sys

original = [x.replace('\n','') for x in open(sys.argv[1]).readlines()]
resegmented = [x.replace('\n','') for x in open(sys.argv[2]).readlines()]

def converter(x):
    return round((float(x.split(":")[0]) * 3600.0) + (float(x.split(":")[1]) * 60.0)+ float(x.split(":")[2]),3)

#c = original_dict
c = {}
temp = []
for x in original:
    temp.append(x)
    if x.startswith('FILE:'):
        cur_file = x.split('/')[-1]
    if x.startswith('INTERVAL:'):
        beginning = converter(x.split(" ")[1])
        cur_int = (beginning,converter(x.split(" ")[2]))
    if x.startswith('TRANSCRIPTION:'):
        cur_tx = [y for y in x.split(' ')[1:] if y != '']
        mid_points = []
        for y in cur_tx:
            if len(y) > 4:
                if y[0] == "[" and y[1].isdigit():
                    mid_point = beginning + float(y[1:-1])
                    mid_points.append(round(mid_point,3))
    if x == '':
        if cur_file not in c:
            c[cur_file] = {}
        c[cur_file][cur_int] = (mid_points,cur_tx,temp)
        temp = []

reseg_dict = {}
temp = []
for x in resegmented:
    temp.append(x)
    if x.startswith('FILE:'):
        cur_file = x.split('/')[-1]
    if x.startswith('INTERVAL:'):
        cur_int = converter(x.split(" ")[1])
    if x.startswith('TRANSCRIPTION:'):
        cur_tx = [y for y in x.split(' ')[1:] if y != '']
    if x == '':
        if cur_file not in reseg_dict:
            reseg_dict[cur_file] = {}
        reseg_dict[cur_file][cur_int] = (cur_tx,temp)
        temp = []

n_dict = {}

s = sorted(c.keys())

for filename in s:
    ss = sorted(c[filename].keys())
    reseg_begs = reseg_dict[filename].keys()
    n_dict[filename] = {}
    holdover = []
    for interval in ss:
        base = c[filename][interval]
        beginning = interval[0]
        mids = base[0]
        counter = 0
        times = [beginning] + mids
        tx = base[1]
        timestamps = []
        for x in tx:
            if len(x) > 4:
                if x[0] == "[" and x[1].isdigit():
                    timestamps.append(x)
        new_tx = [] 
        for time in times:
            if time in reseg_begs:
                reseg_tx = reseg_dict[filename][time][0]
                if "|||" in reseg_tx:
                    initial = " ".join(reseg_tx).split("|||")[0].split(" ")[:-1]
                    holdover = " ".join(reseg_tx)[len(" ".join(initial)):].split(" ")[2:]
                    new_tx.append(initial)
                else:
                    new_tx.append(reseg_tx)
                    if counter < len(timestamps):
                        new_tx.append([timestamps[counter]])
                    counter += 1
                    holdover = []
            else:
                if "|||" in holdover:
                    initial = " ".join(holdover).split("|||")[0].split(" ")[:-1]
                    holdover = " ".join(holdover)[len(" ".join(initial)):].split(" ")[2:]
                    new_tx.append(initial)
                else:
                    new_tx.append(holdover)
                    if counter < len(timestamps):
                        new_tx.append([timestamps[counter]])
                    counter += 1
                    holdover = []
        n_dict[filename][interval] = list(itertools.chain(*new_tx))

s = sorted(c.keys())

for filename in s:
    ss = sorted(c[filename].keys())
    for interval in ss:
        utt = c[filename][interval][2]
        new_tx = n_dict[filename][interval]
        for x in utt:
            if x.startswith("TRANSCRIPTION:"):
                print ("TRANSCRIPTION: " + " ".join(new_tx))
            else:
                print (x)
            
