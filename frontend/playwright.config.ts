import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const configDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(configDir, "..");
const smokePort = Number(process.env.FIGSTUDIO_SMOKE_PORT ?? "8767");
const smokeBaseURL = `http://127.0.0.1:${smokePort}`;

export default defineConfig({
  testDir: "./e2e",
  timeout: 45_000,
  expect: {
    timeout: 10_000
  },
  use: {
    baseURL: smokeBaseURL,
    trace: "retain-on-failure"
  },
  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] }
    }
  ],
  webServer: {
    command: "uv run python examples/smoke_server.py",
    cwd: repoRoot,
    url: `${smokeBaseURL}/api/session`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000
  }
});
