import react from "@vitejs/plugin-react";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    // Tests live outside the component, as required by AGENTS.md
    dir: "../tests/unit/web",
    include: ["**/test_*.{ts,tsx}"],
    coverage: {
      include: ["src/**/*.{ts,tsx}"],
      thresholds: { lines: 90, functions: 90, branches: 90, statements: 90 },
    },
  },
});
