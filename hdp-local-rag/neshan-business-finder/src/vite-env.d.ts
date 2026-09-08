/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_NESHAN_API_KEY: string
  readonly VITE_NESHAN_MAP_KEY: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
