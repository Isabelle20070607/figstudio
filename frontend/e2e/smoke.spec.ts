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

test("notebook save populates replacement cell code and copy action", async ({ page }) => {
  await page.addInitScript(() => {
    Object.defineProperty(navigator, "clipboard", {
      configurable: true,
      value: {
        writeText: async (text: unknown) => {
          window.localStorage.setItem("figstudioCopiedCode", String(text));
        }
      }
    });
  });
  await page.goto("/");

  await expect(page.getByTestId("empty-preview")).toBeVisible();
  await expect(page.getByTestId("save-code-button")).toContainText("Prepare cell");
  await expect(page.getByTestId("code-panel-title")).toContainText("Generated code");
  await expect(page.getByTestId("copy-code-button")).toBeDisabled();

  await page.getByTestId("save-code-button").click();

  await expect(page.getByTestId("status-line")).toContainText("Notebook replacement cell ready");
  await expect(page.getByTestId("code-panel-title")).toContainText("Notebook replacement cell");
  await expect(page.getByTestId("save-message")).toContainText("Notebook replacement cell is shown below");
  await expect(page.getByTestId("copy-code-button")).toHaveAttribute("title", "Copy notebook replacement cell");
  await expect(page.getByTestId("copy-code-button")).toBeEnabled();
  await expect(page.getByTestId("code-panel")).toContainText("import matplotlib.pyplot as plt");
  await expect(page.getByTestId("code-panel")).toContainText("plt.subplots");

  await page.getByTestId("copy-code-button").click();

  await expect(page.getByTestId("save-message")).toContainText("Copied");
  await expect
    .poll(() => page.evaluate(() => window.localStorage.getItem("figstudioCopiedCode") ?? ""))
    .toContain("plt.subplots");

  const plotSelect = page.getByTestId("plot-kind-select");
  await expect(plotSelect.locator('optgroup[label="Cartesian layers"]')).toContainText("Line");
  await expect(plotSelect.locator('optgroup[label="Distribution/value layers"]')).toContainText("Histogram");
  await expect(plotSelect.locator('optgroup[label="2D field layers"]')).toContainText("Heatmap");
  await page.getByTestId("plot-kind-select").selectOption("line");
  await page.getByTestId("add-layer-button").click();

  await expect(page.getByTestId("code-panel-title")).toContainText("Generated code");
  await expect(page.getByTestId("copy-code-button")).toHaveAttribute("title", "Copy generated code");
  await expect(page.getByTestId("code-panel")).toContainText("axes_flat[0].plot");
});

test("covers the public beta editor workflow", async ({ page }, testInfo) => {
  await page.setViewportSize({ width: 1280, height: 800 });
  await page.goto("/");

  await expect(page.getByTestId("app-shell")).toBeVisible();
  await expect(page.getByTestId("variable-panel")).toContainText("df");
  await expect(page.getByTestId("variable-panel")).toContainText("signal_map");
  await expect(page.getByTestId("variable-panel")).toContainText("signal_sequence");
  await expect(page.getByTestId("inspector-panel")).toContainText("Polish");
  await expect(page.getByTestId("empty-preview")).toBeVisible();
  await expect(page.getByTestId("empty-preview-steps")).toContainText("Choose a variable");

  await page.locator('[data-testid="variable-row"][data-variable-name="signal_map"]').click();
  await expect(page.getByTestId("repeated-panel-kind-note")).toContainText("mapping keys");
  await page.locator('[data-testid="variable-row"][data-variable-name="signal_sequence"]').click();
  await expect(page.getByTestId("repeated-panel-kind-note")).toContainText("sequence items");
  await page.locator('[data-testid="variable-row"][data-variable-name="df"]').click();

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

  await page.getByTestId("y-column-select").selectOption("rate");
  await page.getByTestId("add-layer-button").click();
  await page.getByTestId("layer-y-axis-field-select").selectOption("right");
  await expect(page.getByTestId("code-panel")).toContainText("twinx()");
  await expect(page.getByTestId("code-panel")).toContainText("secondary_axes[0].plot");

  await page.getByTestId("builder-mode-select").selectOption("recipe");
  const recipeSelect = page.getByTestId("recipe-kind-select");
  await expect(recipeSelect.locator('optgroup[label="Time-course comparison"]')).toContainText("Mean +/- SEM line");
  await expect(recipeSelect.locator('optgroup[label="Group/condition comparison"]')).toContainText("Grouped points");
  await expect(recipeSelect.locator('optgroup[label="Group/condition comparison"]')).toContainText("Category boxplots");
  await expect(recipeSelect.locator('optgroup[label="Group/condition comparison"]')).toContainText("Category violins");
  await expect(recipeSelect.locator('optgroup[label="Distribution inspection"]')).toContainText("ECDF");
  await expect(recipeSelect.locator('optgroup[label="Categorical counts/composition"]')).toContainText("Stacked count bars");
  await expect(recipeSelect.locator('optgroup[label="Paired observations"]')).toContainText("Paired before/after");
  await expect(page.getByTestId("recipe-question-note")).toContainText("Time-course comparison");
  await page.getByTestId("recipe-kind-select").selectOption("mean_sem_line");
  await page.getByTestId("add-recipe-button").click();
  await expect(page.locator('[data-testid="layer-row"]').filter({ hasText: "recipe · mean_sem_line" })).toBeVisible();
  await expect(page.getByTestId("recipe-kind-field-note")).toContainText("Time-course comparison");
  await expect(page.getByTestId("recipe-kind-field-select").locator('optgroup[label="Time-course comparison"]')).toContainText(
    "Mean +/- SEM line"
  );
  await expect(page.getByTestId("status-line")).toContainText("Preview synced");
  await page.getByTestId("recipe-kind-select").selectOption("count_bar");
  await expect(page.getByTestId("recipe-question-note")).toContainText("Categorical counts/composition");
  await expect(page.getByTestId("recipe-y-column-select")).toHaveCount(0);
  await expect(page.getByTestId("recipe-error-select")).toHaveCount(0);
  await page.getByTestId("add-recipe-button").click();
  await expect(page.locator('[data-testid="layer-row"]').filter({ hasText: "recipe · count_bar" })).toBeVisible();
  await expect(page.getByTestId("code-panel")).toContainText(".size().reindex");
  await page.getByTestId("recipe-kind-select").selectOption("stacked_bar");
  await expect(page.getByTestId("recipe-question-note")).toContainText("Categorical counts/composition");
  await expect(page.getByTestId("recipe-y-column-select")).toHaveCount(0);
  await expect(page.getByTestId("recipe-error-select")).toHaveCount(0);
  await expect(page.getByTestId("recipe-group-column-select")).not.toHaveValue("");
  await page.getByTestId("add-recipe-button").click();
  await expect(page.locator('[data-testid="layer-row"]').filter({ hasText: "recipe · stacked_bar" })).toBeVisible();
  await expect(page.getByTestId("code-panel")).toContainText("bottom=");
  await page.getByTestId("recipe-kind-select").selectOption("boxplot_by_category");
  await expect(page.getByTestId("recipe-question-note")).toContainText("Group/condition comparison");
  await expect(page.getByTestId("recipe-y-column-select")).toHaveCount(1);
  await expect(page.getByTestId("recipe-error-select")).toHaveCount(0);
  await page.getByTestId("add-recipe-button").click();
  await expect(page.locator('[data-testid="layer-row"]').filter({ hasText: "recipe · boxplot_by_category" })).toBeVisible();
  await expect(page.getByTestId("code-panel")).toContainText(".boxplot(");
  await page.getByTestId("recipe-kind-select").selectOption("violin_by_category");
  await expect(page.getByTestId("recipe-question-note")).toContainText("Group/condition comparison");
  await page.getByTestId("recipe-x-column-select").selectOption("condition");
  await expect(page.getByTestId("recipe-y-column-select")).toHaveCount(1);
  await expect(page.getByTestId("recipe-error-select")).toHaveCount(0);
  await page.getByTestId("add-recipe-button").click();
  await expect(page.locator('[data-testid="layer-row"]').filter({ hasText: "recipe · violin_by_category" })).toBeVisible();
  await expect(page.getByTestId("code-panel")).toContainText(".violinplot(");
  await page.getByTestId("recipe-kind-select").selectOption("ecdf");
  await expect(page.getByTestId("recipe-question-note")).toContainText("Distribution inspection");
  await page.getByTestId("recipe-x-column-select").selectOption("signal");
  await expect(page.getByTestId("recipe-y-column-select")).toHaveCount(0);
  await expect(page.getByTestId("recipe-error-select")).toHaveCount(0);
  await page.getByTestId("recipe-group-column-select").selectOption("condition");
  await page.getByTestId("add-recipe-button").click();
  await expect(page.locator('[data-testid="layer-row"]').filter({ hasText: "recipe · ecdf" })).toBeVisible();
  await expect(page.getByTestId("code-panel")).toContainText(".step(");
  await page.getByTestId("facet-column-select").selectOption("condition");
  await page.getByTestId("facet-share-y-field-input").check();
  await page.getByTestId("create-facet-panels-button").click();
  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(2);
  await expect(page.getByTestId("rows-field-input")).toHaveValue("1");
  await expect(page.getByTestId("cols-field-input")).toHaveValue("2");
  await expect(page.getByTestId("status-line")).toContainText("1x2 layout");
  await expect(page.getByTestId("code-panel")).toContainText("sharex=True, sharey=True");

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
  await page.getByTestId("axis-secondary-ylabel-field-input").fill("Rate");
  await expect(page.getByTestId("code-panel")).toContainText("set_ylabel('Rate')");
  await expect(page.getByTestId("code-panel")).toContainText("add_gridspec");
  await expectDesktopWorkspaceFitsViewport(page);

  await page.getByTestId("add-arrow-annotation-button").click();
  await expect(page.getByTestId("annotation-card")).toHaveCount(1);
  await page.getByTestId("annotation-text-field-input").fill("Peak");
  await expect(page.getByTestId("annotation-text-field-input")).toHaveValue("Peak");
  await page.getByTestId("add-horizontal-reference-line-button").click();
  await expect(page.getByTestId("reference-line-card")).toHaveCount(1);
  await page.getByTestId("reference-line-label-field-input").fill("Baseline");
  await expect(page.getByTestId("reference-line-label-field-input")).toHaveValue("Baseline");

  const specDownloadPromise = page.waitForEvent("download");
  await page.getByTestId("export-spec-button").click();
  const specDownload = await specDownloadPromise;
  expect(specDownload.suggestedFilename()).toBe("figure.figstudio.json");
  const exportedSpecPath = testInfo.outputPath("figure.figstudio.json");
  await specDownload.saveAs(exportedSpecPath);
  const exportedSpec = JSON.parse(readFileSync(exportedSpecPath, "utf-8"));
  expect(exportedSpec.style.profile_id).toBe("manuscript");
  expect(exportedSpec.style.profile_overrides).toContain("width");
  expect(exportedSpec.reference_lines).toHaveLength(1);
  expect(exportedSpec.reference_lines[0].style.label).toBe("Baseline");
  expect(exportedSpec.layers.some((layer: any) => layer.y_axis === "right")).toBe(true);
  expect(exportedSpec.axes[0].secondary_y.ylabel).toBe("Rate");
  expect(exportedSpec.recipes.some((recipe: any) => recipe.dataset.filters?.[0]?.column === "condition")).toBe(true);
  const countRecipe = exportedSpec.recipes.find((recipe: any) => recipe.kind === "count_bar");
  expect(countRecipe).toBeTruthy();
  expect(countRecipe.dataset.y).toBeNull();
  expect(countRecipe.error).toBe("none");
  const stackedRecipe = exportedSpec.recipes.find((recipe: any) => recipe.kind === "stacked_bar");
  expect(stackedRecipe).toBeTruthy();
  expect(stackedRecipe.dataset.y).toBeNull();
  expect(stackedRecipe.dataset.group).toBeTruthy();
  expect(stackedRecipe.error).toBe("none");
  const violinRecipe = exportedSpec.recipes.find((recipe: any) => recipe.kind === "violin_by_category");
  expect(violinRecipe).toBeTruthy();
  expect(violinRecipe.dataset.y).toBeTruthy();
  expect(violinRecipe.error).toBe("none");
  const ecdfRecipe = exportedSpec.recipes.find((recipe: any) => recipe.kind === "ecdf");
  expect(ecdfRecipe).toBeTruthy();
  expect(ecdfRecipe.dataset.x).toBe("signal");
  expect(ecdfRecipe.dataset.y).toBeNull();
  expect(ecdfRecipe.dataset.group).toBe("condition");
  expect(ecdfRecipe.error).toBe("none");
  await page.getByTestId("import-spec-input").setInputFiles(exportedSpecPath);
  await expect(page.getByTestId("style-profile-field-select")).toHaveValue("manuscript");
  await expect(page.getByTestId("layout-preset-field-select")).toHaveValue("large_left");
  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(3);
  await expect(page.getByTestId("reference-line-card")).toHaveCount(1);

  const figureDownloadPromise = page.waitForEvent("download");
  await page.getByTestId("export-svg-button").click();
  const figureDownload = await figureDownloadPromise;
  expect(figureDownload.suggestedFilename()).toBe("figstudio-export.svg");
  await expect(page.getByTestId("status-line")).toContainText("SVG export ready");

  await page.getByTestId("save-code-button").click();
  await expect(page.getByTestId("status-line")).toContainText("Notebook replacement cell ready");
  await expect(page.getByTestId("code-panel-title")).toContainText("Notebook replacement cell");
  await expect(page.getByTestId("save-message")).toContainText("Notebook replacement cell is shown below");
  await expect(page.getByTestId("copy-code-button")).toBeEnabled();
});

test("creates mapping-key repeated panels from the layer builder", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("variable-panel")).toBeVisible();

  await page.locator('[data-testid="variable-row"][data-variable-name="signal_map"]').click();
  await expect(page.getByTestId("repeated-panel-kind-note")).toContainText("mapping keys");
  await page.getByTestId("create-facet-panels-button").click();

  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(2);
  await expect(page.getByTestId("code-panel")).toContainText("signal_map['baseline']");
});

test("suggests compact repeated-panel layout for sequence sources", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("variable-panel")).toBeVisible();

  await page.getByTestId("figure-width-field-input").fill("8");
  await page.getByTestId("figure-height-field-input").fill("6");
  await page.locator('[data-testid="variable-row"][data-variable-name="signal_sequence"]').click();
  await expect(page.getByTestId("repeated-panel-kind-note")).toContainText("sequence items");
  await page.getByTestId("create-facet-panels-button").click();

  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(8);
  await expect(page.getByTestId("rows-field-input")).toHaveValue("2");
  await expect(page.getByTestId("cols-field-input")).toHaveValue("4");
  await expect(page.getByTestId("status-line")).toContainText("2x4 layout");
  await expect(page.getByTestId("code-panel")).toContainText("signal_sequence[0]");
});

test("uses figure aspect when suggesting repeated-panel layout", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByTestId("variable-panel")).toBeVisible();

  await page.getByTestId("figure-width-field-input").fill("4");
  await page.getByTestId("figure-height-field-input").fill("8");
  await page.locator('[data-testid="variable-row"][data-variable-name="signal_sequence"]').click();
  await expect(page.getByTestId("repeated-panel-kind-note")).toContainText("sequence items");
  await page.getByTestId("create-facet-panels-button").click();

  await expect(page.getByTestId("active-axes-select").locator("option")).toHaveCount(8);
  await expect(page.getByTestId("rows-field-input")).toHaveValue("4");
  await expect(page.getByTestId("cols-field-input")).toHaveValue("2");
  await expect(page.getByTestId("status-line")).toContainText("4x2 layout");
  await expect(page.getByTestId("code-panel")).toContainText("signal_sequence[0]");
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
            secondary_y: {
              ylabel: "",
              yscale: "linear",
              ylim: null
            },
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
            y_axis: "left",
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
