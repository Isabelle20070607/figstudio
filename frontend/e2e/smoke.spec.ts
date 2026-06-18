import { expect, test } from "@playwright/test";
import { readFileSync, writeFileSync } from "node:fs";

async function expectDesktopWorkspaceFitsViewport(page: import("@playwright/test").Page) {
  const metrics = await page.evaluate(() => {
    const codePanel = document.querySelector('[data-testid="code-panel"]');
    const codeRect = codePanel?.getBoundingClientRect();
    return {
      clientHeight: document.documentElement.clientHeight,
      scrollHeight: document.documentElement.scrollHeight,
      bodyScrollHeight: document.body.scrollHeight,
      codePanelBottom: codeRect?.bottom ?? 0
    };
  });

  expect(metrics.scrollHeight).toBeLessThanOrEqual(metrics.clientHeight + 1);
  expect(metrics.bodyScrollHeight).toBeLessThanOrEqual(metrics.clientHeight + 1);
  expect(metrics.codePanelBottom).toBeLessThanOrEqual(metrics.clientHeight + 1);
}

test("covers the public beta editor workflow", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/");

  await expect(page.getByTestId("app-shell")).toBeVisible();
  await expect(page.getByTestId("variable-panel")).toContainText("df");
  await expect(page.getByTestId("inspector-panel")).toContainText("Polish");
  await expect(page.getByTestId("empty-preview")).toBeVisible();
  await expect(page.getByTestId("empty-preview-steps")).toContainText("Choose a variable");

  const previewBox = await page.locator("#preview-panel").boundingBox();
  const inspectorBox = await page.getByTestId("inspector-panel").boundingBox();
  expect(previewBox).not.toBeNull();
  expect(inspectorBox).not.toBeNull();
  expect(inspectorBox!.x).toBeGreaterThan(previewBox!.x + previewBox!.width - 2);
  await expectDesktopWorkspaceFitsViewport(page);

  await page.getByTestId("plot-kind-select").selectOption("line");
  await page.getByTestId("add-layer-button").click();
  await expect(page.getByTestId("figure-preview")).toBeVisible();
  await expect(page.getByTestId("status-line")).toContainText("Preview synced");
  await expectDesktopWorkspaceFitsViewport(page);

  await page.getByTestId("builder-mode-select").selectOption("recipe");
  await page.getByTestId("recipe-kind-select").selectOption("mean_sem_line");
  await page.getByTestId("add-recipe-button").click();
  await expect(page.locator('[data-testid="layer-row"]').filter({ hasText: "recipe · mean_sem_line" })).toBeVisible();
  await expect(page.getByTestId("status-line")).toContainText("Preview synced");

  await page.getByTestId("style-preset-field-select").selectOption("journal_single");
  await expect(page.getByTestId("figure-width-field-input")).toHaveValue("3.35");
  await page.getByTestId("style-profile-field-select").selectOption("manuscript");
  await expect(page.getByTestId("style-profile-note")).toContainText("Using project profile defaults");
  await expect(page.getByTestId("figure-width-field-input")).toHaveValue("3.35");
  await page.getByTestId("figure-width-field-input").fill("4");
  await expect(page.getByTestId("style-profile-note")).toContainText("width");

  await page.getByTestId("rows-field-input").fill("2");
  await page.getByTestId("cols-field-input").fill("2");
  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(4);
  await page.getByTestId("layout-preset-field-select").selectOption("large_left");
  await expect(page.getByTestId("layout-preset-field-select")).toHaveValue("large_left");
  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(3);
  await expect(page.getByTestId("active-axes-select").locator("option").first()).toContainText("2x1");
  await expect(page.getByTestId("code-panel")).toContainText("add_gridspec");
  await expectDesktopWorkspaceFitsViewport(page);

  await page.getByTestId("add-arrow-annotation-button").click();
  await expect(page.getByTestId("annotation-card")).toHaveCount(1);
  await page.getByTestId("annotation-text-field-input").fill("Peak");
  await expect(page.getByTestId("annotation-text-field-input")).toHaveValue("Peak");

  const specDownloadPromise = page.waitForEvent("download");
  await page.getByTestId("export-spec-button").click();
  const specDownload = await specDownloadPromise;
  expect(specDownload.suggestedFilename()).toBe("figure.figstudio.json");
  const exportedSpecPath = testInfo.outputPath("figure.figstudio.json");
  await specDownload.saveAs(exportedSpecPath);
  const exportedSpec = JSON.parse(readFileSync(exportedSpecPath, "utf-8"));
  expect(exportedSpec.style.profile_id).toBe("manuscript");
  expect(exportedSpec.style.profile_overrides).toContain("width");
  await page.getByTestId("import-spec-input").setInputFiles(exportedSpecPath);
  await expect(page.getByTestId("style-profile-field-select")).toHaveValue("manuscript");
  await expect(page.getByTestId("layout-preset-field-select")).toHaveValue("large_left");
  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(3);

  const figureDownloadPromise = page.waitForEvent("download");
  await page.getByTestId("export-svg-button").click();
  const figureDownload = await figureDownloadPromise;
  expect(figureDownload.suggestedFilename()).toBe("figstudio-export.svg");
  await expect(page.getByTestId("status-line")).toContainText("SVG export ready");

  await page.getByTestId("save-code-button").click();
  await expect(page.getByTestId("status-line")).toContainText("Notebook replacement code ready");
  await expect(page.getByTestId("save-message")).toContainText("No script_path was provided");
  await expect(page.getByTestId("save-message")).toContainText("Copy the replacement cell code");
});

test("validation issues select the affected editor context", async ({ page }, testInfo) => {
  await page.goto("/");
  await expect(page.getByTestId("variable-panel")).toBeVisible();

  const invalidSpecPath = testInfo.outputPath("invalid.figstudio.json");
  writeFileSync(
    invalidSpecPath,
    JSON.stringify(
      {
        version: 1,
        mode: "explore",
        width: 6.4,
        height: 4.8,
        dpi: 120,
        rows: 1,
        cols: 1,
        axes: [
          {
            id: "ax0",
            row: 0,
            col: 0,
            title: "",
            xlabel: "",
            ylabel: "",
            xscale: "linear",
            yscale: "linear",
            xlim: null,
            ylim: null,
            grid: false,
            legend: true,
            colorbar: false
          }
        ],
        layers: [
          {
            id: "bad-layer",
            kind: "line",
            axes_id: "ax0",
            dataset: { variable: "missing_values" },
            style: { label: "Missing" },
            readonly: false,
            source: "generated"
          }
        ],
        recipes: [],
        annotations: [],
        style: {
          preset: "custom",
          title: "",
          font_size: 10,
          constrained_layout: true
        },
        show: false
      },
      null,
      2
    ),
    "utf-8"
  );

  await page.getByTestId("import-spec-input").setInputFiles(invalidSpecPath);
  await expect(page.getByTestId("validation-list")).toBeVisible();
  await expect(page.getByTestId("validation-issue")).toContainText("missing_variable");
  await expect(page.getByTestId("validation-issue")).toContainText(
    "Suggested fix: Set dataset.variable to 'df'"
  );
  await page.getByTestId("validation-issue").click();

  await expect(page.getByTestId("status-line")).toContainText("Repair missing_variable");
  await expect(page.locator('[data-testid="layer-row"][data-layer-id="bad-layer"]')).toHaveClass(/selected/);
  await expect(page.locator('[data-testid="layer-row"][data-layer-id="bad-layer"]')).toBeFocused();
  await expect(page.getByTestId("active-axes-select")).toHaveValue("ax0");
});
