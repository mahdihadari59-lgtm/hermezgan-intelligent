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

function clampText(text, maxLen = 14000) {
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

function buildSectionTitle(hit, idx) {
    return [
        `### نتیجه ${idx + 1}`,
        `شناسه: ${hit.id}`,
        `عنوان: ${hit.title || ""}`,
        `دسته: ${hit.category || ""}`,
        `موضوع: ${hit.topic || ""}`,
        `اولویت: ${hit.priority ?? ""}`,
        `امتیاز نهایی: ${hit._score ?? ""}`,
        `خلاصه: ${hit.snippet || ""}`
    ].join("\n");
}

function buildGraphBlock(rows) {
    if (!rows.length) return "";

    const lines = [];
    for (const row of rows.slice(0, 10)) {
        lines.push(
            [
                `- [لایه ${row.layer || 1}] ${row.relation_type || ""} | ${row.direction || ""} | ${row.neighbor_title || ""}`,
                `  مبدأ: ${row.origin_title || ""} (${row.origin_id})`,
                `  گره: ${row.source_id} -> ${row.target_id}`,
                `  همسایه: ${row.neighbor_title || ""}`,
                `  نوع همسایه: ${row.neighbor_type || ""}`,
                `  وزن: ${row.weight ?? ""}`,
                `  اعتماد: ${row.confidence ?? ""}`,
                `  امتیاز: ${row._score ?? ""}`
            ].join("\n")
        );
    }

    return lines.join("\n\n");
}

function buildContext(pack) {
    const parts = [];

    parts.push("## پرسش");
    parts.push(pack.query);

    if (pack.hits.length) {
        parts.push("## نتایج اصلی");
        pack.hits.forEach((hit, idx) => {
            parts.push(buildSectionTitle(hit, idx));

            const localGraph = (hit._graphRows || []).slice(0, 6);
            if (localGraph.length) {
                parts.push("روابط وابسته:");
                parts.push(buildGraphBlock(localGraph));
            }
        });
    }

    if (pack.graphRows.length) {
        parts.push("## گراف فشرده");
        parts.push(buildGraphBlock(pack.graphRows));
    }

    if (pack.embeddings && pack.embeddings.length) {
        parts.push("## نتایج معنایی");
        for (const row of pack.embeddings.slice(0, 5)) {
            parts.push(
                [
                    `- ${row.title || ""}`,
                    `  دسته: ${row.category || ""}`,
                    `  امتیاز: ${row._score ?? ""}`,
                    `  خلاصه: ${row.snippet || ""}`
                ].join("\n")
            );
        }
    }

    return clampText(parts.join("\n\n"), 14000);
}

function retrieve(query, options = {}) {
    const q = String(query || "").trim();
    const searchLimit = Math.max(5, Number(options.limit ?? 5));
    const graphDepth = Math.max(1, Number(options.graphDepth ?? 2));
    const graphPerHit = Math.max(3, Number(options.graphPerHit ?? 10));
    const graphHitLimit = Math.max(1, Number(options.graphLimit ?? 3));
    const embeddingLimit = Math.max(0, Number(options.embeddingLimit ?? 0)); // hook for later

    if (!q) {
        return {
            query: q,
            hits: [],
            graphRows: [],
            embeddings: [],
            context: "",
            top: null
        };
    }

    const rawHits = search.search(q, Math.max(searchLimit * 4, 12)) || [];
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

    const hits = enrichedHits.slice(0, searchLimit);

    const graphRows = uniqueByKey(
        hits
            .slice(0, graphHitLimit)
            .flatMap(hit => hit._graphRows || [])
            .map(row => ({
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

    // hook for future embeddings search
    const embeddings = [];
    void embeddingLimit;

    return {
        query: q,
        hits,
        graphRows,
        embeddings,
        context: buildContext({ query: q, hits, graphRows, embeddings }),
        top: hits[0] || null
    };
}

module.exports = {
    retrieve,
    buildContext
};
