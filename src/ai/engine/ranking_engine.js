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

function tokenize(text) {
    return normalizeFa(text)
        .match(/[\w\u0600-\u06FF]+/g) || [];
}

function overlapScore(a, b) {
    const A = new Set(tokenize(a));
    const B = tokenize(b);

    if (!A.size || !B.length) return 0;

    let common = 0;
    for (const token of B) {
        if (A.has(token)) common++;
    }

    return common / Math.max(A.size, B.length);
}

function scoreHit(query, hit, graphCount = 0) {
    const qn = normalizeFa(query);
    const title = normalizeFa(hit?.title);
    const category = normalizeFa(hit?.category);
    const topic = normalizeFa(hit?.topic);
    const snippet = normalizeFa(hit?.snippet);
    const priority = Number(hit?.priority ?? 0);
    const confidence = Number(hit?.confidence ?? 0);

    let score = 0;

    score += priority * 2.5;
    score += confidence * 2.0;

    if (qn && title && title === qn) score += 8;
    if (qn && title && (title.includes(qn) || qn.includes(title))) score += 5;
    if (qn && category && category.includes(qn)) score += 1.5;
    if (qn && topic && topic.includes(qn)) score += 1.5;

    score += overlapScore(query, `${hit?.title || ""} ${hit?.category || ""} ${hit?.topic || ""} ${hit?.snippet || ""}`) * 4;
    score += Math.min(Number(graphCount) || 0, 10) * 0.35;

    if (snippet.length > 0) score += 0.15;

    return Number(score.toFixed(4));
}

function scoreGraphRow(query, row) {
    const qn = normalizeFa(query);
    const neighbor = normalizeFa(row?.neighbor_title);
    const relation = normalizeFa(row?.relation_type);

    let score = 0;

    score += Number(row?.weight ?? 1) * 1.2;
    score += Number(row?.confidence ?? 1) * 1.5;

    if (qn && neighbor && (neighbor.includes(qn) || qn.includes(neighbor))) score += 4;
    if (relation.includes("contain")) score += 2;
    if (relation.includes("location")) score += 1.5;
    if (relation.includes("parent")) score += 1.3;
    if (String(row?.direction || "") === "out") score += 0.5;

    return Number(score.toFixed(4));
}

module.exports = {
    normalizeFa,
    tokenize,
    overlapScore,
    scoreHit,
    scoreGraphRow
};
