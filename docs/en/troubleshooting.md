# Troubleshooting

FigStudio validates common problems before rendering, saving, or exporting. Start with the issue card in the preview when one is shown.

## Validation Issues

Click an issue card. When the API provides enough context, FigStudio selects the affected layer, recipe, axes, or field.

Common validation problems:

| Issue | Repair |
| --- | --- |
| Missing variable or column | Reopen with the expected variable in scope, or change the layer/recipe mapping. |
| Non-DataFrame recipe source | Switch to a pandas DataFrame variable or use a normal plot layer. |
| Missing target axes | Choose a valid target axes after layout changes. |
| Invalid layout geometry | Use a valid panel preset or fix duplicate axes ids, non-positive spans, out-of-bounds axes, or overlapping axes. |
| Dimension mismatch | Make X, Y, and optional Y error sources compatible. |
| Heatmap or contour lacks 2D values | Use a 2D ndarray or gridded value source. |
| Non-positive data on a log axis | Filter data, change limits, or switch back to linear scale. |
| Missing style profile | Select an available profile, restore `.figstudio/styles.json`, or accept fallback defaults. |

## Error Codes

| Code | Meaning |
| --- | --- |
| `validation_failed` | The spec references missing data, invalid layout, incompatible dimensions, invalid 2D data, or non-positive log-scale data. |
| `render_failed` | Generated Matplotlib code could not run after validation. |
| `export_failed` | Export rendering failed or an explicit output path could not be written. |
| `writeback_failed` | The controlled block was missing, duplicated, nested, had unmatched markers, or used a different `block_id`. |
| `writeback_io_failed` | Python could not read or write the target script path. |

## Render Or Export Fails

1. Fix validation issues first.
2. Check that the selected variables still exist in the live Python session.
3. For `heatmap` and `contour`, verify that the value source is 2D.
4. For export to an explicit path, verify that the directory exists and is writable.
5. Use the generated code panel to inspect the exact Matplotlib code path.

## Save Code Fails

Verify that:

- the marker pair exactly matches the session `block_id`;
- only one block uses that id;
- the markers are not nested;
- both start and end markers exist;
- the script path is readable and writable.

Generated code remains visible in the code panel so work can continue manually.
