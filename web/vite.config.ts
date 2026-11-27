import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    // Only unit tests: end-to-end tests will live in tests/e2e and run with Playwright
    dir: "tests/unit",
    include: ["**/test_*.{ts,tsx}"],
    coverage: {
      include: ["src/**/*.{ts,tsx}"],
      thresholds: { lines: 90, functions: 90, branches: 90, statements: 90 },
    },
  },
});
