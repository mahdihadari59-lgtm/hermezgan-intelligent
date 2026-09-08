const db = require("../../core/database");

function escapeSql(value) {
    return String(value ?? "").replace(/'/g, "''");
}

function normalizeFa(text) {
    if (!text) return "";

    let t = String(text)
        .replace(/\u064A/g, "\u06CC")
        .replace(/\u0643/g, "\u06A9")
        .replace(/\u0629/g, "\u0647")
        .replace(/\u0649/g, "\u06CC")
        .replace(/[\u064B-\u065F\u0670\u06D6-\u06ED]/g, "")
        .replace(/[\u200c\u200f\u200e]/g, " ")
        .trim()
        .toLowerCase();

    const faDigits = "۰۱۲۳۴۵۶۷۸۹";
    const arDigits = "٠١٢٣٤٥٦٧٨٩";

    for (let i = 0; i < 10; i++) {
        t = t.split(faDigits[i]).join(String(i));
        t = t.split(arDigits[i]).join(String(i));
    }

    t = t.replace(/\s+/g, " ").trim();
    return t;
}

function uniqueByKey(list, keyFn) {
    const seen = new Set();
    const out = [];

    for (const item of list || []) {
        const key = keyFn(item);
        if (seen.has(key)) continue;
        seen.add(key);
        out.push(item);
    }

    return out;
}

function degree(nodeId) {
    const rows = db.query(`
        SELECT COUNT(*) AS c
        FROM graph_edges
        WHERE source_id = ${Number(nodeId)}
           OR target_id = ${Number(nodeId)}
    `);

    return Number(rows?.[0]?.c || 0);
}

function chooseBestCandidate(candidates) {
    const scored = (candidates || []).map(row => ({
        ...row,
        _degree: degree(row.id),
        _baseScore: Number(row.score ?? 0)
    }));

    scored.sort((a, b) =>
        (b._degree - a._degree) ||
        (b._baseScore - a._baseScore) ||
        (Number(b.level ?? 0) - Number(a.level ?? 0)) ||
        (Number(b.depth ?? 0) - Number(a.depth ?? 0)) ||
        (Number(a.id) - Number(b.id))
    );

    return scored[0] || null;
}

function resolveNode(nodeId, title = "") {
    const id = Number(nodeId);

    let candidates = db.query(`
        SELECT
            id,
            knowledge_id,
            title,
            node_type,
            score,
            level,
            depth,
            path,
            title_normalized
        FROM graph_nodes
        WHERE id = ${id}
           OR knowledge_id = ${id}
        LIMIT 20
    `) || [];

    if ((!candidates.length || !chooseBestCandidate(candidates)) && title) {
        const t = escapeSql(title);
        const norm = escapeSql(normalizeFa(title));

        const fallback = db.query(`
            SELECT
                id,
                knowledge_id,
                title,
                node_type,
                score,
                level,
                depth,
                path,
                title_normalized
            FROM graph_nodes
            WHERE title = '${t}'
               OR title_normalized = '${norm}'
            LIMIT 20
        `) || [];

        candidates = uniqueByKey([...candidates, ...fallback], row => String(row.id));
    }

    if (!candidates.length) return null;
    return chooseBestCandidate(candidates);
}

function neighbors(nodeId, title = "", limit = 50) {
    const node = resolveNode(nodeId, title);
    if (!node) return [];

    const id = Number(node.id);
    const maxRows = Math.max(1, Math.min(100, Number(limit) || 50));

    const sql = `
        SELECT
            e.id AS edge_id,
            e.source_id,
            e.target_id,
            e.relation_type,
            CASE
                WHEN e.source_id = ${id} THEN 'out'
                ELSE 'in'
            END AS direction,
            n.id AS neighbor_id,
            n.title AS neighbor_title,
            n.node_type AS neighbor_type,
            e.weight,
            e.confidence
        FROM graph_edges e
        LEFT JOIN graph_nodes n
            ON n.id = CASE
                WHEN e.source_id = ${id} THEN e.target_id
                ELSE e.source_id
            END
        WHERE e.source_id = ${id}
           OR e.target_id = ${id}
        ORDER BY e.weight DESC, e.confidence DESC, e.id DESC
        LIMIT ${maxRows}
    `;

    return db.query(sql) || [];
}

function expand(nodeId, title = "", depth = 2, limitPerNode = 20) {
    const root = resolveNode(nodeId, title);
    if (!root) {
        return { root: null, layers: [], rows: [] };
    }

    const maxDepth = Math.max(1, Math.min(4, Number(depth) || 2));
    const maxPerNode = Math.max(1, Math.min(50, Number(limitPerNode) || 20));

    const visited = new Set([Number(root.id)]);
    let frontier = [{ id: Number(root.id), title: root.title || title || "", depth: 0 }];

    const layers = [];
    const allRows = [];

    for (let d = 1; d <= maxDepth; d++) {
        const nextFrontier = [];
        const layerRows = [];

        for (const node of frontier) {
            const rows = neighbors(node.id, node.title, maxPerNode);

            for (const row of rows) {
                const neighborId = Number(
                    row.neighbor_id ||
                    (row.direction === "out" ? row.target_id : row.source_id)
                );

                const scored = {
                    ...row,
                    origin_id: node.id,
                    origin_title: node.title,
                    layer: d
                };

                layerRows.push(scored);

                if (neighborId && !visited.has(neighborId)) {
                    visited.add(neighborId);
                    nextFrontier.push({
                        id: neighborId,
                        title: row.neighbor_title || "",
                        depth: d
                    });
                }
            }
        }

        const uniqLayer = uniqueByKey(
            layerRows,
            row => `${row.origin_id}|${row.source_id}|${row.target_id}|${row.relation_type}|${row.direction}|${row.neighbor_id}`
        );

        layers.push({
            depth: d,
            rows: uniqLayer
        });

        allRows.push(...uniqLayer);
        frontier = nextFrontier.slice(0, 50);

        if (!frontier.length) break;
    }

    const rows = uniqueByKey(
        allRows,
        row => `${row.origin_id}|${row.source_id}|${row.target_id}|${row.relation_type}|${row.direction}|${row.neighbor_id}`
    );

    return {
        root,
        layers,
        rows
    };
}

module.exports = {
    resolveNode,
    neighbors,
    expand
};
