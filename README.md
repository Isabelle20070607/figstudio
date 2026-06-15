# FigStudio

FigStudio is a local graphical editor for Matplotlib figures aimed at researchers who already write Python data-processing code but do not want to memorize every Matplotlib plotting and styling API.

The intended workflow is:

```python
import figstudio

# Finish data processing first.
session = figstudio.open(locals(), script_path=__file__)
```

The browser UI can inspect available variables, build or edit a figure, preview Matplotlib output, and generate reproducible Matplotlib OO code.

## Development

```powershell
uv run pytest
```

Frontend:

```powershell
cd frontend
npm install
npm run build
```

## Controlled Code Block

For automatic script writeback, add a controlled block:

```python
# figstudio:start main
# figstudio:end main
```

FigStudio only replaces the contents between the matching markers.
