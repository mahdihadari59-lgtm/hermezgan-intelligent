const db=require("./src/core/database");

console.log("Database:",db.DB);

const tables=db.query("SELECT name FROM sqlite_master WHERE type='table' LIMIT 10;");

console.log(tables);
