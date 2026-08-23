import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    environment: "node",
    include: ["tests/**/*.test.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "lcov"],
      // Pure modules that the layered architecture exists to keep testable.
      include: [
        "src/changelog.ts",
        "src/model/**/*.ts",
        "src/ink/pressure.ts",
        "src/ink/presets.ts",
        "src/ink/stroke-builder.ts",
        "src/ink/freehand.ts",
        "src/canvas/viewport.ts",
        "src/canvas/hit-test.ts",
        "src/canvas/spatial-index.ts",
        "src/canvas/zoom.ts",
        "src/canvas/ink-color.ts",
        "src/input/palm-rejection.ts",
        "src/input/diagnostics.ts",
        "src/input/input-normalizer.ts",
        "src/recognition/text-layer.ts",
        "src/recognition/registry.ts",
        "src/recognition/manual.ts",
        "src/recognition/llm-request.ts",
        "src/recognition/openrouter-auth.ts",
        "src/recognition/lines.ts",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        statements: 80,
        branches: 70,
      },
    },
  },
});
