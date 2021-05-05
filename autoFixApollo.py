'''
python3
'''

import re, sys

#a here is the 'restitched' extract
a = [x.replace('\n','') for x in open(sys.argv[1]).readlines()]

c = {}
temp = []
for x in a:
    temp.append(x)
    if x.startswith('FILE:'):
        cur_file = x.split('/')[-1]
    if x.startswith('INTERVAL:'):
        cur_int = x
    if x.startswith('TRANSCRIPTION:'):
        cur_tx = x.split(' ')[1:]
    if x == '':
        if cur_file not in c:
            c[cur_file] = {}
        c[cur_file][cur_int] = (cur_tx,temp)
        temp = []

def converter(x):
    return round((float(x.split(":")[0]) * 3600.0) + (float(x.split(":")[1]) * 60.0)+ float(x.split(":")[2]),3)

n_dict = {}

s = sorted(c.keys())

for filename in s:
    ss = sorted(c[filename].keys())
    current_speaker = "<speaker_1>"
    for interval in ss:
        base = c[filename][interval]
        tx = base[0]
        length = converter(interval.split(" ")[2]) - converter(interval.split(" ")[1])
        #get rid of extraneous spacing
        tx1 = [x for x in tx if x != ""] 
        speakers = [x for x in tx if x.startswith("<speaker_")] 
        unique_speakers = list(set(speakers))
        tag_only = [x for x in tx1 if x[0] == "[" or x[0] == "<" or x[0] == "~"]
        to_flag = 0
        if tag_only == tx1:
            to_flag = 1
        l_flag = 0
        sp_flag = 1
        tsp_flag = 0
        if len(speakers) > 1:
            tsp_flag = 1
        if length >= 15.0:
            l_flag = 1 
        if len(unique_speakers) == 0 and to_flag == 0:
            sp_flag = 0
        if len(unique_speakers) > 1:
            sp_flag = 2
        fsp_flag = 0
        try:
            if not tx1[0].startswith("<speaker_") and to_flag == 0:
                fsp_flag = 1
        except:
            pass
        if len(unique_speakers) == 1:
           current_speaker = unique_speakers[0]
        if sp_flag == 0:
            tx1.insert(0,current_speaker)
        if sp_flag == 2:
            tx1 = [x for x in tx1 if x not in unique_speakers[1:]]
        if fsp_flag == 1:
            tx1 = [current_speaker] + [x for x in tx1 if not x.startswith("<speaker_")] 
        if tsp_flag == 1:
            tx1 = [current_speaker] + [x for x in tx1 if not x.startswith("<speaker_")]
        if l_flag == 1:
            new_tx = []
            j = " ".join(tx1)
            pipe_split = j.split("|||")
            for x in pipe_split:
                n = x.split(" ")
                n1 = [y for y in n if y != "~" and y != "<continued>"]
                new_unique_speakers = list(set([y for y in n1 if y.startswith("<speaker_")]))
                if len(new_unique_speakers) == 0:
                    n1.insert(0,current_speaker)
                n1 = [y for y in n1 if y != ""]
                last = n1[-1]
                if last[-1] not in ["!",",",".","?",">"]:
                    n1.append(",")
                for y in n1:
                    new_tx.append(y)
                new_tx.append("|||")
            tx1 = new_tx[:-1]
        n_dict[(filename,interval)] = tx1

#ABOVE WORK WITH END OF FILE TO DETECT ~ or <continued>

nn_dict = {}

s = sorted(c.keys())

#Second pass just to make this easier on myself
for filename in s:
    ss = sorted(c[filename].keys())
    for interval in ss:
        new_tx = " ".join(n_dict[(filename,interval)])
        r1 = re.sub(r"([!,.?]) ,",r"\1",new_tx)
        r2 = re.sub(r"\|\|\| \|\|\|",r"\|\|\| <pause> \|\|\|",r1)
        r3 = re.sub(r"^<speaker_.> (<music>|<long_noise>|<short_noise>|<pause>)$",r"\1",r2)
        r4 = re.sub(r"^<speaker_.> (<loud>|<quiet>)$",r"<pause>",r3)
        r5 = re.sub(r"(<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>|<noise>|<music>)* <music> (<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>|<noise>|<music>)*",r"<music>",r4)
        r6 = re.sub(r"(<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>|<noise>)* <noise> (<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>|<noise>)*",r"<noise>",r5) 
        r7 = re.sub(r"(<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>)* (<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>) (<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>)*",r"\2",r6)
        r8 = re.sub(r"(<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>) (~|<continued>)* \|\|\| (~|<continued>)* (<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>) ([^\|])",r"\1 \2 \|\|\| \3 \5",r7)
        r9 = re.sub(r"(<music>) (~|<continued>)* \|\|\| (~|<continued>)* (<noise>|<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>) ([^\|])",r"\1 \2 \|\|\| \3 \5",r8)
        r10 = re.sub(r"(<noise>) (~|<continued>)* \|\|\| (~|<continued>)* (<noise>|<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>) ([^\|])",r"\1 \2 \|\|\| \3 \5",r9)
        r11 = re.sub(r"([^\|]) (<noise>|<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>) (~|<continued>)* \|\|\| (~|<continued>)* (<music>)",r"\1 \3 \|\|\| \4 \5",r10)
        r12 = re.sub(r"([^\|]) (<noise>|<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>) (~|<continued>)* \|\|\| (~|<continued>)* (<noise>)",r"\1 \3 \|\|\| \4 \5",r11)
        r13 = re.sub(r"(\S)(<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>|<noise>|<music>)",r"\1 \2",r12)
        r14 = re.sub(r"(<short_noise>|<long_noise>|<applause>|<lipsmack>|<laugh>|<cry>|<breath>|<click>|<cough>|<ring>|<shout>|<static>|<whisper>|<noise>|<music>)(\S)",r"\1 \2",r13)
        rr = [xx for xx in r14.split(" ") if xx != ""]
        if rr != []:
            if rr[-1][-1] in ["!",",",".","?","=","#","。","？","।","！","、","，","="]:
                r15 = r14
            else:
                if rr[-1] in ["<applause>","<long_noise>","<short_noise>","<breath>","<click>","<continued>","<cough>","<cry>","<dtmf>","<foreign_utx>","<hm>","<laugh>","<lipsmack>","<loud>","<music>","<no_speech>","<noise>","<pause>","<quiet>","<ring>","<static>","<unintelligible_interrupt>","<unintelligible_overlap>","<utx>","~","!",",",".","?","=","#","。","？","।","！","、","，","="]:
                    r15 = r14
                else:
                    r15 = r14 + "."
        else:
            r15 = r14
        nn_dict[(filename,interval)] = r15

s = sorted(c.keys())

for filename in s:
    ss = sorted(c[filename].keys())
    for interval in ss:
        utt = c[filename][interval][1]
        tx = nn_dict[(filename,interval)]
        for x in utt:
            if x.startswith("TRANSCRIPTION:"):
                print ("TRANSCRIPTION: " + tx)
            else:
                print (x)
