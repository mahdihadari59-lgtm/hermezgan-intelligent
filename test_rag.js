const rag = require("./src/ai/engine/rag_engine");

const hit = rag.retrieve("میناب", { limit: 5, graphLimit: 3 });

console.log("===== HITS =====");
console.log(JSON.stringify(hit.hits, null, 2));

console.log("===== GRAPH =====");
console.log(JSON.stringify(hit.graphRows, null, 2));

console.log("===== CONTEXT =====");
console.log(hit.context);
