'''
python3
'''

#THIS WORKS
import sys

original = [x.replace('\n','') for x in open(sys.argv[1]).readlines()]
resegmented = [x.replace('\n','') for x in open("tx.resegmented").readlines()]

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

#put endpoints matching to reseg_dict intervals in here as keys
n_dict = {}

s = sorted(c.keys())

for filename in s:
    ss = sorted(c[filename].keys())
    reseg_begs = reseg_dict[filename].keys()
    n_dict[filename] = {}
    current_run = []
    current_time = -1
    for interval in ss:
        base = c[filename][interval]
        beginning = interval[0]
        tx = base[1]
        mids = base[0]
        counter = 0
        for numx, x in enumerate(tx):
            if numx == 0:
                if beginning in reseg_begs and current_time != -1:
                    n_dict[filename][current_time] = current_run
                    current_run = []
                    current_run.append(x)
                    current_time = beginning
                elif beginning in reseg_begs and current_time == -1:
                    current_time = beginning
                    current_run.append(x)
                else:
                    current_run.append("|||")
                    current_run.append(x)
            else:
                if len(x) > 4:
                    if x[0] == "[" and x[1].isdigit():
                        n_dict[filename][current_time] = current_run
                        current_time = mids[counter]
                        counter += 1
                        current_run = []
                    else:
                        current_run.append(x)
                else:
                    current_run.append(x)
    n_dict[filename][current_time] = current_run

s = sorted(reseg_dict.keys())

for filename in s:
    ss = sorted(reseg_dict[filename].keys())
    for interval in ss:
        base = reseg_dict[filename][interval]
        utt = base[1]
        new_tx = n_dict[filename][interval]
        for x in utt:
            if x.startswith("TRANSCRIPTION:"):
                print ("TRANSCRIPTION: " + " ".join(new_tx))
            else:
                print (x)
