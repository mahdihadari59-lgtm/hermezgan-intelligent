const graph = require("./src/ai/engine/graph_engine");

console.log(
  JSON.stringify(
    graph.neighbors(14),
    null,
    2
  )
);
