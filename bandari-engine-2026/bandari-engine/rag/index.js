const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const PY_BRIDGE = String.raw`
import json, re, sqlite3, sys

DB_PATH = sys.argv[1]
QUERY = (sys.argv[2] or "").strip()

def normalize_fa(text):
    if not text:
        return ""
    t = text.replace("\u064A", "\u06CC").replace("\u0643", "\u06A9").replace("\u0629", "\u0647").replace("\u0649", "\u06CC")
    t = re.sub(r"[\u064B-\u065F\u0670\u06D6-\u06ED]", "", t)
    t = t.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    t = t.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    t = re.sub(r"[\u200c\u200f\u200e]", " ", t)
    t = re.sub(r"\s+", " ", t).strip().lower()
    return t

def tokenize(text):
    t = normalize_fa(text)
    return [w for w in re.findall(r"[\w\u0600-\u06FF]+", t) if len(w) > 1]

def build_match_expr(query):
    tokens = tokenize(query)
    if not tokens:
        tokens = tokenize(query[:32])
    if not tokens:
        return ""
    return " OR ".join(f'"{t.replace(chr(34), "")}"' for t in tokens)

def has_fts_table(conn):
    try:
        result = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_fts'"
        ).fetchone()
        return result is not None
    except:
        return False

q_norm = normalize_fa(QUERY)
match_expr = build_match_expr(QUERY)

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

def row_to_result(row):
    rid = row["rowid"] if "rowid" in row.keys() else row["id"]
    # Use rowid to fetch the document (safer than using id directly)
    doc = conn.execute(
        "SELECT rowid, id, title, category, content FROM knowledge WHERE rowid = ? LIMIT 1",
        (rid,)
    ).fetchone()
    if not doc:
        return None
    content = doc["content"] or ""
    snippet = re.sub(r"\s+", " ", content)[:220]
    return {
        "id": doc["id"] if doc["id"] is not None else doc["rowid"],
        "title": doc["title"],
        "category": doc["category"],
        "snippet": snippet,
    }

results = []
has_fts = has_fts_table(conn)

# Try FTS first if available
if has_fts and match_expr:
    try:
        rows = conn.execute(
            "SELECT rowid, bm25(knowledge_fts) AS rank FROM knowledge_fts WHERE knowledge_fts MATCH ? ORDER BY rank LIMIT 5",
            (match_expr,)
        ).fetchall()
        for r in rows:
            item = row_to_result(r)
            if item:
                item["score"] = float(r["rank"])
                item["source"] = "fts"
                results.append(item)
    except Exception:
        pass

# If no FTS results or no FTS table, use LIKE
if not results:
    try:
        like = f"%{QUERY}%"
        rows = conn.execute(
            "SELECT rowid, id, title, category, content FROM knowledge WHERE title LIKE ? OR content LIKE ? LIMIT 5",
            (like, like)
        ).fetchall()
        for r in rows:
            item = {
                "id": r["id"] if r["id"] is not None else r["rowid"],
                "title": r["title"],
                "category": r["category"],
                "snippet": re.sub(r"\s+", " ", (r["content"] or ""))[:220],
                "score": 0.0,
                "source": "like",
            }
            results.append(item)
    except Exception:
        pass

if results:
    top = results[0]
    print(json.dumps({
        "found": True,
        "response": f"{top['title']}\n\n{top['snippet']}",
        "confidence": 0.86 if top["source"] == "fts" else 0.62,
        "top": top,
        "results": results[:3]
    }, ensure_ascii=False))
else:
    print(json.dumps({
        "found": False,
        "response": None,
        "confidence": 0.0,
        "results": []
    }, ensure_ascii=False))
`;

class RAGEngine {
  constructor(options = {}) {
    this.fallback = new Map([
      ['دلم گرفته', 'ناراحت نباش. همه چی درست میشه.'],
      ['خسته‌ام', 'خسته نباشی. یه استراحت کن.'],
      ['واویلا', 'واویلا یعنی وای خدای من! (تعجب)'],
      ['اَبی چِش', 'اَبی چِش یعنی حالت چطوره؟'],
      ['دِلِمی', 'دِلِمی یعنی عزیز دلم.'],
      ['چِطوری مِردُم', 'چِطوری مِردُم یعنی چطوری مردم؟'],
      ['سَلام خَری', 'سَلام خَری یعنی سلام رفیق.'],
      ['خُبَه رَه', 'خُبَه رَه یعنی خوبی رفیق؟'],
    ]);

    // Primary database path - HDP v2
    const primaryDb = path.join(process.env.HOME || '', 'hermezgan-intelligent/backend/hdp_v2.db');

    // More comprehensive database candidates with all project paths
    this.dbCandidates = [
      process.env.HDP_KNOWLEDGE_DB,
      options.dbPath,

      // Primary HDP database
      primaryDb,

      // HDP X1 paths
      path.join(process.env.HOME || '', 'hermezgan-intelligent/backend/data/hdp_v2.db'),
      path.join(process.env.HOME || '', 'hermezgan-intelligent/backend/hdp_v2_embedding_ok.db'),
      path.join(process.env.HOME || '', 'hermezgan-intelligent/backend/hdp.db'),
      path.join(process.env.HOME || '', 'hermezgan-intelligent/backend/data/hormozgan.db'),

      // Alternative project paths
      path.join(process.env.HOME || '', 'ai-system/hdp_x1/backend/hdp_v2_embedding_ok.db'),
      path.join(process.env.HOME || '', 'ai-system/hdp_x1/backend/hdp_v2.db'),
      path.join(process.env.HOME || '', 'ai-system/hdp_x1/backend/data/hdp_v2.db'),

      // Local paths
      path.join(process.cwd(), 'hdp_v2.db'),
      path.join(process.cwd(), 'data/hdp_v2.db'),
      path.join(process.cwd(), 'backend/hdp_v2.db'),

      // Docker/container paths
      '/app/data/hdp_v2.db',
      '/app/hdp_v2.db',
    ].filter(Boolean);

    // Force primary database as first priority if it exists
    if (fs.existsSync(primaryDb)) {
      // Move primary to front of array
      this.dbCandidates = [
        primaryDb,
        ...this.dbCandidates.filter(p => p !== primaryDb)
      ];
    }
  }

  getDbPath() {
    // Filter existing files and sort by size (largest first)
    const candidates = this.dbCandidates
      .filter(p => p && fs.existsSync(p))
      .map(p => {
        try {
          const stats = fs.statSync(p);
          return {
            path: p,
            size: stats.size,
            mtime: stats.mtime
          };
        } catch {
          return null;
        }
      })
      .filter(c => c !== null)
      .sort((a, b) => b.size - a.size);

    if (candidates.length === 0) {
      return null;
    }

    // Log the chosen database
    const chosen = candidates[0];
    console.log(`📚 RAG: Using database ${chosen.path} (${(chosen.size / 1024 / 1024).toFixed(2)} MB)`);
    return chosen.path;
  }

  searchKnowledgeDb(query) {
    const dbPath = this.getDbPath();
    if (!dbPath) {
      console.log('📚 RAG: No database found');
      return null;
    }

    try {
      const out = spawnSync('python3', ['-c', PY_BRIDGE, dbPath, query], {
        encoding: 'utf8',
        timeout: 7000,
        maxBuffer: 1024 * 1024,
      });

      if (out.status !== 0 || !out.stdout) {
        if (out.stderr) {
          console.log('📚 RAG: Python error:', out.stderr.toString().trim());
        }
        return null;
      }

      const data = JSON.parse(out.stdout.trim());
      return data && data.found ? data : null;
    } catch (err) {
      console.log('📚 RAG: Error:', err.message);
      return null;
    }
  }

  search(query) {
    const q = (query || '').trim();
    if (!q) return { found: false, response: null, confidence: 0 };

    // Try database search first
    const dbHit = this.searchKnowledgeDb(q);
    if (dbHit) {
      dbHit.source = 'database';
      return dbHit;
    }

    // Check fallback exact matches
    if (this.fallback.has(q)) {
      return {
        found: true,
        response: this.fallback.get(q),
        confidence: 0.95,
        source: 'fallback-exact'
      };
    }

    // Check fallback partial matches
    for (const [key, value] of this.fallback.entries()) {
      if (q.includes(key) || key.includes(q)) {
        return {
          found: true,
          response: value,
          confidence: 0.7,
          source: 'fallback-partial'
        };
      }
    }

    return { found: false, response: null, confidence: 0 };
  }

  addSample(query, response) {
    this.fallback.set(query, response);
    return { added: true, total: this.fallback.size };
  }

  getStats() {
    const dbPath = this.getDbPath();
    let dbSize = 0;
    let dbSizeMB = 0;

    if (dbPath) {
      try {
        const stats = fs.statSync(dbPath);
        dbSize = stats.size;
        dbSizeMB = stats.size / 1024 / 1024;
      } catch {
        // Ignore
      }
    }

    return {
      totalSamples: this.fallback.size,
      dbPath: dbPath,
      connected: Boolean(dbPath),
      dbSize: dbSize,
      dbSizeMB: dbSizeMB.toFixed(2),
      dbCandidates: this.dbCandidates.length,
      activeCandidates: this.dbCandidates.filter(p => p && fs.existsSync(p)).length,
    };
  }

  getAllDbCandidates() {
    return this.dbCandidates.filter(p => p && fs.existsSync(p));
  }
}

module.exports = RAGEngine;
