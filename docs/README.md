# Rossum API SDK Documentation

This directory contains the Sphinx documentation for the Rossum API SDK.

## Building the Documentation

### Install Dependencies

First, install the documentation dependencies:

```bash
pip install -e ".[docs]"
```

### Build HTML Documentation

```bash
cd docs
make html
```

The generated HTML documentation will be available in `_build/html/`. Open `_build/html/index.html` in your browser to view it.

### Clean Build Artifacts

To clean up build artifacts:

```bash
make clean
```

### Other Build Formats

Sphinx supports various output formats:

```bash
make latexpdf  # Build PDF documentation (requires LaTeX)
make epub      # Build ePub documentation
make help      # Show all available build targets
```

## Documentation Structure

- `conf.py` - Sphinx configuration file
- `index.rst` - Main documentation index with introduction
- `clients.rst` - API clients documentation (async and sync)
- `models.rst` - Data models documentation
- `_static/` - Static files (CSS, images, etc.)
- `_build/` - Generated documentation (gitignored)

## Contributing to Documentation

The documentation uses:

- **reStructuredText (rST)** for documentation files
- **Sphinx autodoc** to automatically extract docstrings from code
- **Napoleon extension** for NumPy-style docstrings
- **Read the Docs theme** for styling

When adding new models or client methods, ensure they have proper docstrings
following the NumPy documentation style. The documentation will be automatically
generated from these docstrings.
