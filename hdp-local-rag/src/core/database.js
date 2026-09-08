const { execSync } = require("child_process");

const DB = "./backend/hdp_v2_dev.db";

function query(sql) {
    try {
        const cmd = `sqlite3 -json "${DB}" "${sql.replace(/"/g,'\\"')}"`;
        const out = execSync(cmd,{encoding:"utf8"});
        return out.trim() ? JSON.parse(out) : [];
    } catch(err){
        console.error(err.message);
        return [];
    }
}

module.exports = {
    DB,
    query
};
