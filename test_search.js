const search = require("./src/ai/engine/search_engine");

const result = search.search("میناب",5);

console.log(JSON.stringify(result,null,2));
