const hybrid = require("./src/ai/engine/hybrid_retrieval_engine");

const hit = hybrid.retrieve("میناب", {
  limit: 5,
  graphLimit: 3,
  graphDepth: 2,
  graphPerHit: 10
});

console.log("===== TOP =====");
console.log(JSON.stringify(hit.top, null, 2));

console.log("===== HITS =====");
console.log(JSON.stringify(hit.hits, null, 2));

console.log("===== GRAPH =====");
console.log(JSON.stringify(hit.graphRows, null, 2));

console.log("===== CONTEXT =====");
console.log(hit.context);
