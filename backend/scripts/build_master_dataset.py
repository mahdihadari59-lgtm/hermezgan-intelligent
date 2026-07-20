#!/usr/bin/env python3

import os
import re
import json
import sqlite3
import hashlib
from collections import Counter,defaultdict

INPUT_FILE="/data/data/com.termux/files/home/hormozgan-driver-pro121/hdp_flask_app/data/hormozgan_knowledge.json"

OUT_DIR="data/master"

DB_FILE=f"{OUT_DIR}/master_dataset.db"

os.makedirs(OUT_DIR,exist_ok=True)

PLACEHOLDER_PATTERNS=[
r'جاذبه گردشگری شماره \d+',
r'مرکز درمانی شماره \d+',
r'اطلاعات ترافیکی نقطه \d+',
r'هتل شماره \d+',
r'غذای محلی شماره \d+',
r'اصطلاح بندری شماره \d+',
r'اطلاعات متفرقه شماره \d+',
r'ماده قانونی شماره \d+',
r'مرکز خرید شماره \d+'
]

STOPWORDS={
"و","در","از","به","برای","با","این",
"آن","یک","را","که","تا","یا","اما",
"اگر","می","شود","شد","است"
}

CATEGORY_RULES={
"traffic":[
"ترافیک","راهور","رانندگی","تصادف",
"جریمه","دوربین","سرعت","مسیر"
],

"tourism":[
"هتل","گردشگری","جزیره","ساحل",
"رستوران","کیش","قشم","هرمز"
],

"medical":[
"بیمارستان","درمانگاه","داروخانه",
"پزشک","دکتر","اورژانس"
],

"food":[
"غذا","قلیه","ماهی","میگو",
"هواری","مهیاوه"
],

"culture":[
"گویش","بندری","اصطلاح",
"فرهنگ","محلی"
],

"legal":[
"قانون","حقوق","وکیل",
"ماده","دادگاه"
],

"shopping":[
"بازار","خرید","فروشگاه",
"قیمت","مرکز خرید"
]
}

def normalize(text):

    text=str(text)

    text=text.replace("ي","ی")
    text=text.replace("ك","ک")
    text=text.replace("\u200c"," ")

    text=re.sub(r"\s+"," ",text)

    return text.strip()

def get_prefix(key):

    key=normalize(key)

    key=key.replace("_"," ")

    key=re.sub(r"\d+$","",key)

    key=re.sub(r"\s+"," ",key)

    return key.strip()

def is_placeholder(content):

    content=normalize(content)

    for p in PLACEHOLDER_PATTERNS:
        if re.search(p,content):
            return True

    return False

def detect_category(text):

    scores=defaultdict(int)

    for cat,words in CATEGORY_RULES.items():

        for w in words:

            if w in text:
                scores[cat]+=1

    if not scores:
        return "general"

    return max(scores,key=scores.get)

def content_hash(text):

    txt=normalize(text)

    return hashlib.md5(
        txt.encode("utf8")
    ).hexdigest()

with open(INPUT_FILE,"r",encoding="utf8") as f:
    data=json.load(f)

prefix_counter=Counter()

duplicates=[]

archive={}

master={}

seen_hash={}

keyword_counter=Counter()

for key,val in data.items():

    text=normalize(val)

    prefix=get_prefix(key)

    prefix_counter[prefix]+=1

    if is_placeholder(text):

        archive[key]=val
        continue

    h=content_hash(text)

    if h in seen_hash:

        duplicates.append({
            "original":seen_hash[h],
            "duplicate":key
        })

        continue

    seen_hash[h]=key

    master[key]=val

    words=re.findall(
        r'[\u0600-\u06FF]{3,}',
        text
    )

    for w in words:

        if w not in STOPWORDS:

            keyword_counter[w]+=1

print("TOTAL:",len(data))
print("MASTER:",len(master))
print("PLACEHOLDERS:",len(archive))
print("DUPLICATES:",len(duplicates))

with open(
f"{OUT_DIR}/master_dataset.json",
"w",
encoding="utf8"
) as f:

    json.dump(
        master,
        f,
        ensure_ascii=False,
        indent=2
    )

with open(
f"{OUT_DIR}/placeholder_archive.json",
"w",
encoding="utf8"
) as f:

    json.dump(
        archive,
        f,
        ensure_ascii=False,
        indent=2
    )

with open(
f"{OUT_DIR}/duplicates.json",
"w",
encoding="utf8"
) as f:

    json.dump(
        duplicates,
        f,
        ensure_ascii=False,
        indent=2
    )

with open(
f"{OUT_DIR}/prefix_map.json",
"w",
encoding="utf8"
) as f:

    json.dump(
        dict(prefix_counter),
        f,
        ensure_ascii=False,
        indent=2
    )

with open(
f"{OUT_DIR}/keyword_index.json",
"w",
encoding="utf8"
) as f:

    json.dump(
        dict(keyword_counter.most_common(3000)),
        f,
        ensure_ascii=False,
        indent=2
    )

if os.path.exists(DB_FILE):
    os.remove(DB_FILE)

conn=sqlite3.connect(DB_FILE)

cur=conn.cursor()

cur.execute("""
CREATE TABLE knowledge(
id INTEGER PRIMARY KEY,
title TEXT,
content TEXT,
category TEXT
)
""")

cur.execute("""
CREATE VIRTUAL TABLE knowledge_fts
USING fts5(
title,
content,
category
)
""")

for title,content in master.items():

    category=detect_category(
        normalize(content)
    )

    cur.execute("""
    INSERT INTO knowledge(
    title,
    content,
    category
    )
    VALUES(?,?,?)
    """,
    (
    title,
    str(content),
    category
    ))

    rowid=cur.lastrowid

    cur.execute("""
    INSERT INTO knowledge_fts(
    rowid,
    title,
    content,
    category
    )
    VALUES(?,?,?,?)
    """,
    (
    rowid,
    title,
    str(content),
    category
    ))

conn.commit()
conn.close()

report={
"total_records":len(data),
"master_records":len(master),
"placeholders":len(archive),
"duplicates":len(duplicates),
"top_prefixes":
dict(prefix_counter.most_common(100)),
"top_keywords":
dict(keyword_counter.most_common(100))
}

with open(
f"{OUT_DIR}/report.json",
"w",
encoding="utf8"
) as f:

    json.dump(
        report,
        f,
        ensure_ascii=False,
        indent=2
    )

print("\nDONE")
print(DB_FILE)
