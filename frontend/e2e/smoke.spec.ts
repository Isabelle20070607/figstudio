import { expect, test } from "@playwright/test";
import { writeFileSync } from "node:fs";

test("covers the public beta editor workflow", async ({ page }, testInfo) => {
  await page.goto("/");

  await expect(page.getByTestId("app-shell")).toBeVisible();
  await expect(page.getByTestId("variable-panel")).toContainText("df");
  await expect(page.getByTestId("empty-preview")).toBeVisible();

  await page.getByTestId("plot-kind-select").selectOption("line");
  await page.getByTestId("add-layer-button").click();
  await expect(page.getByTestId("figure-preview")).toBeVisible();
  await expect(page.getByTestId("status-line")).toContainText("Preview synced");

  await page.getByTestId("style-preset-field-select").selectOption("journal_single");
  await expect(page.getByTestId("figure-width-field-input")).toHaveValue("3.35");

  await page.getByTestId("rows-field-input").fill("2");
  await page.getByTestId("cols-field-input").fill("2");
  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(4);

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
  await page.getByTestId("import-spec-input").setInputFiles(exportedSpecPath);
  await expect(page.getByTestId("status-line")).toContainText("FigureSpec imported");

  const figureDownloadPromise = page.waitForEvent("download");
  await page.getByTestId("export-svg-button").click();
  const figureDownload = await figureDownloadPromise;
  expect(figureDownload.suggestedFilename()).toBe("figstudio-export.svg");
  await expect(page.getByTestId("status-line")).toContainText("SVG export ready");

  await page.getByTestId("save-code-button").click();
  await expect(page.getByTestId("status-line")).toContainText("Notebook cell ready");
  await expect(page.getByTestId("save-message")).toContainText("No script_path was provided");
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
  await page.getByTestId("validation-issue").click();

  await expect(page.locator('[data-testid="layer-row"][data-layer-id="bad-layer"]')).toHaveClass(/selected/);
  await expect(page.locator('[data-testid="layer-row"][data-layer-id="bad-layer"]')).toBeFocused();
  await expect(page.getByTestId("active-axes-select")).toHaveValue("ax0");
});
