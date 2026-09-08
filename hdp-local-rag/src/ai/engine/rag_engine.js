const search = require("./search_engine");
const graph = require("./graph_engine");
const ranking = require("./ranking_engine");

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

function clampText(text, maxLen = 12000) {
    const t = String(text || "");
    return t.length > maxLen ? `${t.slice(0, maxLen)}\n...` : t;
}

function dedupeHitsKeepBest(hits) {
    const map = new Map();

    for (const hit of hits || []) {
        const key = ranking.normalizeFa(hit?.title || "");
        const prev = map.get(key);

        if (!prev) {
            map.set(key, hit);
            continue;
        }

        const prevPriority = Number(prev?.priority ?? 0);
        const curPriority = Number(hit?.priority ?? 0);
        const prevConfidence = Number(prev?.confidence ?? 0);
        const curConfidence = Number(hit?.confidence ?? 0);

        if (
            curPriority > prevPriority ||
            (curPriority === prevPriority && curConfidence > prevConfidence) ||
            (curPriority === prevPriority && curConfidence === prevConfidence && Number(hit?.id) < Number(prev?.id))
        ) {
            map.set(key, hit);
        }
    }

    return [...map.values()];
}

function buildContextFromHits(hits, graphRows) {
    const parts = [];

    if (hits.length) {
        parts.push("## نتایج رتبه‌بندی‌شده");

        hits.forEach((hit, idx) => {
            parts.push(
                [
                    `### نتیجه ${idx + 1}`,
                    `شناسه: ${hit.id}`,
                    `عنوان: ${hit.title || ""}`,
                    `دسته: ${hit.category || ""}`,
                    `موضوع: ${hit.topic || ""}`,
                    `اولویت: ${hit.priority ?? ""}`,
                    `امتیاز: ${hit._score ?? ""}`,
                    `خلاصه: ${hit.snippet || ""}`
                ].join("\n")
            );

            const localGraph = (hit._graphRows || []).slice(0, 6);
            if (localGraph.length) {
                parts.push("روابط کلیدی:");
                for (const row of localGraph) {
                    parts.push(
                        [
                            `- [لایه ${row.layer || 1}] ${row.relation_type || ""} | ${row.direction || ""} | ${row.neighbor_title || ""}`,
                            `  گره مبدأ گراف: ${row.source_id}`,
                            `  گره مقصد گراف: ${row.target_id}`,
                            `  همسایه: ${row.neighbor_title || ""}`,
                            `  نوع همسایه: ${row.neighbor_type || ""}`,
                            `  امتیاز: ${row._score ?? ""}`
                        ].join("\n")
                    );
                }
            }
        });
    }

    if (graphRows.length) {
        parts.push("## روابط گراف کلیدی");
        graphRows.slice(0, 12).forEach((row, idx) => {
            parts.push(
                [
                    `### رابطه ${idx + 1}`,
                    `گره مبدأ: ${row.origin_id}`,
                    `عنوان مبدأ: ${row.origin_title || ""}`,
                    `گره گراف: ${row.source_id} -> ${row.target_id}`,
                    `نوع رابطه: ${row.relation_type || ""}`,
                    `جهت: ${row.direction || ""}`,
                    `همسایه: ${row.neighbor_title || ""}`,
                    `نوع همسایه: ${row.neighbor_type || ""}`,
                    `وزن: ${row.weight ?? ""}`,
                    `اعتماد: ${row.confidence ?? ""}`,
                    `امتیاز: ${row._score ?? ""}`
                ].join("\n")
            );
        });
    }

    return clampText(parts.join("\n\n"), 12000);
}

function retrieve(query, options = {}) {
    const q = String(query || "").trim();
    const limit = Number.isFinite(options.limit) ? Number(options.limit) : 5;
    const graphLimit = Number.isFinite(options.graphLimit) ? Number(options.graphLimit) : 3;
    const graphPerHit = Number.isFinite(options.graphPerHit) ? Number(options.graphPerHit) : 10;
    const graphDepth = Number.isFinite(options.graphDepth) ? Number(options.graphDepth) : 2;

    if (!q) {
        return {
            query: q,
            hits: [],
            graphRows: [],
            context: "",
            top: null
        };
    }

    const rawHits = search.search(q, Math.max(limit * 4, 12)) || [];
    const dedupedHits = dedupeHitsKeepBest(rawHits);

    const enrichedHits = dedupedHits.map(hit => {
        const expanded = graph.expand(hit.id, hit.title, graphDepth, graphPerHit) || { rows: [] };
        const scoredRows = (expanded.rows || []).map(row => ({
            ...row,
            _score: ranking.scoreGraphRow(q, row)
        })).sort((a, b) =>
            (Number(b._score ?? 0) - Number(a._score ?? 0)) ||
            (Number(b.weight ?? 0) - Number(a.weight ?? 0)) ||
            (Number(b.confidence ?? 0) - Number(a.confidence ?? 0)) ||
            (Number(b.source_id ?? 0) - Number(a.source_id ?? 0))
        );

        return {
            ...hit,
            _graphRows: scoredRows,
            _score: ranking.scoreHit(q, hit, scoredRows.length)
        };
    });

    enrichedHits.sort((a, b) =>
        (Number(b._score ?? 0) - Number(a._score ?? 0)) ||
        (Number(b.priority ?? 0) - Number(a.priority ?? 0)) ||
        (Number(b.confidence ?? 0) - Number(a.confidence ?? 0)) ||
        (Number(a.id ?? 0) - Number(b.id ?? 0))
    );

    const hits = enrichedHits.slice(0, limit);

    const graphRows = uniqueByKey(
        hits.flatMap(hit => hit._graphRows || []).map(row => ({
            origin_id: row.origin_id,
            origin_title: row.origin_title,
            source_id: row.source_id,
            target_id: row.target_id,
            relation_type: row.relation_type,
            direction: row.direction,
            neighbor_id: row.neighbor_id,
            neighbor_title: row.neighbor_title,
            neighbor_type: row.neighbor_type,
            weight: row.weight,
            confidence: row.confidence,
            layer: row.layer,
            _score: row._score
        })),
        row => `${row.origin_id}|${row.source_id}|${row.target_id}|${row.relation_type}|${row.direction}|${row.neighbor_id}`
    ).sort((a, b) =>
        (Number(b._score ?? 0) - Number(a._score ?? 0)) ||
        (Number(b.weight ?? 0) - Number(a.weight ?? 0)) ||
        (Number(b.confidence ?? 0) - Number(a.confidence ?? 0))
    );

    return {
        query: q,
        hits,
        graphRows,
        context: buildContextFromHits(hits, graphRows),
        top: hits[0] || null
    };
}

module.exports = {
    retrieve,
    buildContextFromHits
};
