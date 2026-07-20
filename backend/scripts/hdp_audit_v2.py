#!/usr/bin/env python3

import json
import re
import os
import hashlib
from collections import Counter,defaultdict

JSON_PATH="/data/data/com.termux/files/home/hormozgan-driver-pro121/hdp_flask_app/data/hormozgan_knowledge.json"

REPORT="data/logs/hdp_audit_report.json"

STOP_WORDS=set([
"و","در","از","به","با","برای","که","این","آن",
"یک","را","می","های","های","است","شود","شد",
"بر","تا","یا","اما","اگر","هم","هر","نیز"
])

def normalize(txt):
    txt=str(txt)
    txt=re.sub(r"\s+"," ",txt)
    return txt.strip()

def get_prefix(key):
    k=key.replace("_"," ")
    k=re.sub(r"\d+$","",k)
    k=re.sub(r"\s+"," ",k)
    return k.strip()

with open(JSON_PATH,"r",encoding="utf8") as f:
    data=json.load(f)

print("="*80)
print("HDP DATASET AUDIT V2")
print("="*80)

total=len(data)

prefix_counter=Counter()
keyword_counter=Counter()
hash_map=defaultdict(list)

high=[]
medium=[]
low=[]

for key,val in data.items():

    text=str(val)
    length=len(text)

    prefix=get_prefix(key)
    prefix_counter[prefix]+=1

    norm=normalize(text)
    md5=hashlib.md5(norm.encode()).hexdigest()
    hash_map[md5].append(key)

    words=re.findall(r'[\u0600-\u06FF]{3,}',text)

    for w in words:
        if w not in STOP_WORDS:
            keyword_counter[w]+=1

    score=0

    if length>300:
        score+=3

    elif length>120:
        score+=2

    elif length>50:
        score+=1

    hormozgan_words=[
    "بندرعباس","قشم","هرمز","کیش","میناب",
    "جاسک","بندرلنگه","بشاگرد","رودان",
    "جزیره","ساحل","خلیج","اسکله",
    "ترافیک","رانندگی","هتل","بیمارستان",
    "قلیه","گویش","بندری"
    ]

    for w in hormozgan_words:
        if w in text:
            score+=1

    if score>=5:
        high.append(key)

    elif score>=2:
        medium.append(key)

    else:
        low.append(key)

duplicates=[]

for h,items in hash_map.items():
    if len(items)>1:
        duplicates.append(items)

print(f"\nTOTAL RECORDS : {total:,}")
print(f"HIGH QUALITY  : {len(high):,}")
print(f"MEDIUM QUALITY: {len(medium):,}")
print(f"LOW QUALITY   : {len(low):,}")
print(f"DUP GROUPS    : {len(duplicates):,}")

print("\nTOP PREFIXES")
print("-"*80)

for name,count in prefix_counter.most_common(50):
    print(f"{count:5d} | {name}")

print("\nTOP KEYWORDS")
print("-"*80)

for word,count in keyword_counter.most_common(50):
    print(f"{count:5d} | {word}")

report={
"total":total,
"high_quality":len(high),
"medium_quality":len(medium),
"low_quality":len(low),
"duplicate_groups":len(duplicates),
"top_prefixes":dict(prefix_counter.most_common(200)),
"top_keywords":dict(keyword_counter.most_common(200)),
"sample_high":high[:100],
"sample_medium":medium[:100],
"sample_low":low[:100]
}

os.makedirs("data/logs",exist_ok=True)

with open(REPORT,"w",encoding="utf8") as f:
    json.dump(report,f,ensure_ascii=False,indent=2)

print("\nREPORT SAVED:")
print(REPORT)

print("\nDONE")
