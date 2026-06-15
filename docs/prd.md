# FigStudio PRD

## Problem Statement

Researchers often write Python data-processing code comfortably but lose time when turning results into Matplotlib figures. The difficult part is not the data transformation; it is remembering and combining plotting, styling, layout, annotation, legend, tick, font, and export APIs until a figure is suitable for exploration or publication.

FigStudio should make graphical editing equivalent to writing reproducible Matplotlib code. Users keep their Python workflow, open a local editor from the current script or notebook, adjust the figure visually, and receive clean Matplotlib OO code that can be saved back into a controlled plotting block.

## Solution

FigStudio is a local web application launched from Python. It reads summaries of variables in the current namespace, lets users create or edit Matplotlib figures through a GUI, renders true Matplotlib previews, and generates plain Matplotlib OO code.

The product has two working modes:

- **Explore**: fast variable selection, chart type selection, rough styling, and immediate preview.
- **Publish**: publication-oriented figure sizing, fonts, labels, legends, ticks, annotations, vector export, and style presets.

## User Stories

1. As a scientific Python user, I want to open a graphical editor from `locals()`, so that I can use the data I already processed.
2. As a researcher, I want to choose DataFrame columns or ndarray variables in a GUI, so that I do not need to write initial plotting code by hand.
3. As a Matplotlib learner, I want every GUI edit to update visible code, so that I learn the corresponding Matplotlib API.
4. As a script user, I want FigStudio to update only a marked plotting block, so that my data-processing code remains untouched.
5. As a notebook user, I want a complete replacement cell, so that I can paste or replace code without unsafe notebook mutation.
6. As a paper author, I want publication-style controls for size, fonts, labels, legends, and vector export, so that figures are ready for manuscript workflows.
7. As an existing Matplotlib user, I want to pass a `Figure` into FigStudio, so that I can inspect and refine an already-created plot.
8. As a cautious user, I want unsupported existing artists marked read-only, so that the editor does not pretend it can safely rewrite arbitrary Matplotlib internals.

## V1 Functional Scope

FigStudio v1 prioritizes the complete loop:

1. Open local session from Python.
2. Inspect variables and optional existing figure.
3. Create/edit a figure in the browser.
4. Render a Matplotlib preview.
5. Generate plain OO Matplotlib code.
6. Save to a controlled script block or return a notebook cell.
7. Export PNG, SVG, or PDF.

V1 plot creation supports line, scatter, bar, horizontal bar, histogram, boxplot, violin, errorbar, heatmap, contour, step, and fill-between. V1 layout supports single axes, subplot grid basics, legends, colorbars, shared axes metadata, and common axis styling.

## Out Of Scope

- Cloud collaboration and accounts.
- BI dashboards or hosted interactive web publishing.
- A full Origin, Veusz, or LabPlot replacement.
- Full automatic rewriting of arbitrary user-written Matplotlib code.
- Automatic notebook file mutation.
- Complete support for 3D, polar, animation, and every Matplotlib artist.

## Success Criteria

- A user can open FigStudio from a script and create a figure from a DataFrame.
- Saving updates only the selected controlled block.
- A notebook user can copy a full replacement cell.
- Generated code can run without importing FigStudio.
- Exported SVG/PDF output comes from Matplotlib, not a front-end approximation.
