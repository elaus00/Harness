import { defineConfig } from '@playwright/test'
import { mkdtempSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join } from 'node:path'

const databasePath = process.env.HARNESS_E2E_DB || join(mkdtempSync(join(tmpdir(), 'harness-e2e-')), 'test.sqlite3')
process.env.HARNESS_E2E_DB = databasePath
export default defineConfig({
  testDir: './e2e', workers: 1, fullyParallel: false, timeout: 45000,
  use: { baseURL: 'http://127.0.0.1:4173', viewport: { width: 1440, height: 1000 }, trace: 'retain-on-failure' },
  webServer: [
    { command: 'uv run --project ../backend --directory ../backend uvicorn app.main:app --host 127.0.0.1 --port 18000', url: 'http://127.0.0.1:18000/api/v1/health', reuseExistingServer: false,
      env: { HARNESS_DATABASE_PATH: databasePath, HARNESS_ALLOWED_ORIGINS: '["http://127.0.0.1:4173"]', HARNESS_COOKIE_SECURE: 'false' } },
    { command: 'npm run dev -- --port 4173', url: 'http://127.0.0.1:4173', reuseExistingServer: false, env: { API_PROXY_TARGET: 'http://127.0.0.1:18000' } },
  ],
})
