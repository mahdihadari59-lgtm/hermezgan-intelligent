const fs = require('fs');
const path = require('path');

class PluginManager {
  constructor(deps = {}) {
    this.deps = deps;
    this.registry = new Map();
    this.sources = new Map();
  }

  register(intentType, instance, meta = {}) {
    if (!intentType || !instance) return;
    this.registry.set(intentType, instance);
    this.sources.set(intentType, meta);
  }

  get(intentType) { return this.registry.get(intentType) || null; }

  autoLoad({ pluginsDir = null, expertsDir = null, manifestMap = {} } = {}) {
    if (pluginsDir && fs.existsSync(pluginsDir)) {
      const subdirs = fs.readdirSync(pluginsDir, { withFileTypes: true }).filter(d => d.isDirectory());
      for (const dirent of subdirs) {
        const pluginDir = path.join(pluginsDir, dirent.name);
        const manifestPath = path.join(pluginDir, 'manifest.json');
        if (!fs.existsSync(manifestPath)) continue;

        try {
          const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
          if (manifest.enabled === false) continue;
          const entry = path.resolve(pluginDir, manifest.entry);
          const mod = require(entry);
          const PluginClass = mod?.default || mod;
          const instance = new PluginClass(this.deps, manifest.configPath || undefined);
          const intents = Array.isArray(manifest.intents) ? manifest.intents : [manifest.intent || dirent.name.toLowerCase()];
          for (const intentType of intents) {
            this.register(intentType, instance, { plugin: manifest.name || dirent.name, entry: manifest.entry, dir: pluginDir });
          }
        } catch (err) {
          this.deps.logger?.error({ event: 'plugin_load_failed', dir: pluginDir, error: err.message });
        }
      }
    }

    if (expertsDir && fs.existsSync(expertsDir)) {
      const files = fs.readdirSync(expertsDir).filter(f => f.endsWith('Expert.js') && f !== 'BaseExpert.js');
      for (const file of files) {
        const fullPath = path.join(expertsDir, file);
        try {
          const mod = require(fullPath);
          const ExpertClass = mod?.default || mod;
          const intentType = manifestMap[file] || file.replace('Expert.js', '').toLowerCase();
          if (this.registry.has(intentType)) continue;
          const instance = new ExpertClass(this.deps);
          this.register(intentType, instance, { source: 'experts', file });
        } catch (err) {
          this.deps.logger?.error({ event: 'expert_load_failed', file, error: err.message });
        }
      }
    }

    return this.list();
  }

  list() { return [...this.registry.keys()]; }

  async route(intent, query, context, deps) {
    const expert = this.get(intent.type);
    if (!expert) {
      const result = await deps.searchPipeline?.search(query, deps.searchOptions || {});
      return result || deps.defaultResponses?.unknown || null;
    }
    return expert.handle(intent, query, context, deps);
  }

  async routeMulti(intents, query, context, deps) {
    const out = [];
    for (const intent of intents.slice(0, 2)) {
      const res = await this.route(intent, query, context, deps);
      if (res) out.push(res);
    }
    return out.join('\n\n───\n\n');
  }
}

module.exports = PluginManager;
