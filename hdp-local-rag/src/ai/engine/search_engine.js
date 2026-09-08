const db = require("../../core/database");

function escape(text) {
    return String(text).replace(/'/g, "''");
}

function search(text, limit = 10) {

    text = escape(text);

    const sql = `
        SELECT
            k.id,
            k.title,
            k.category,
            substr(k.content,1,180) AS snippet,
            k.topic,
            k.priority
        FROM knowledge_search
        JOIN knowledge AS k
            ON k.id = knowledge_search.rowid
        WHERE knowledge_search MATCH '${text}'
          AND k.is_deleted = 0
        ORDER BY
            bm25(knowledge_search),
            k.priority DESC
        LIMIT ${Number(limit)};
    `;

    return db.query(sql);
}

module.exports = {
    search
};
