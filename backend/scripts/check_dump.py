import sqlite3
import re

DB = "data/hdp_v2.db"
DUMP = "/data/data/com.termux/files/home/hdp_dump.sql"

conn = sqlite3.connect(DB)
cur = conn.cursor()

new_count = 0
dup_count = 0

with open(DUMP, "r", encoding="utf-8", errors="ignore") as f:
    for line in f:
        if not line.startswith("INSERT INTO places"):
            continue

        m = re.search(r"VALUES\('([^']+)'", line)
        if not m:
            continue

        pid = m.group(1)

        cur.execute("SELECT 1 FROM places WHERE id=?", (pid,))
        if cur.fetchone():
            dup_count += 1
        else:
            new_count += 1

print(f"New Places : {new_count}")
print(f"Duplicate : {dup_count}")

conn.close()
