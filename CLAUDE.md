# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

HackNation_2025_SkillSense is a Python project built for HackNation 2025. The project uses data science libraries (pandas, numpy, matplotlib) suggesting data analysis, visualization, or machine learning capabilities.

## Development Environment

- **Python Version**: 3.13 (specified in `.python-version`)
- **Package Manager**: `uv` (modern Python package manager)
- **Virtual Environment**: `.venv` directory

## Common Commands

### Environment Setup
```bash
# Install dependencies (uv reads from pyproject.toml)
uv sync

# Activate virtual environment
# Windows
.venv\Scripts\activate
# Unix/MacOS
source .venv/bin/activate
```

### Running the Application
```bash
# Run the main application
python main.py

# Or with uv
uv run main.py
```

### Package Management
```bash
# Add a new dependency
uv add <package-name>

# Remove a dependency
uv remove <package-name>

# Update dependencies
uv lock --upgrade
```

## Project Structure

Currently minimal structure with:
- `main.py` - Entry point with basic hello world implementation
- `pyproject.toml` - Project metadata and dependencies
- `uv.lock` - Locked dependency versions

## Dependencies

Core data science stack:
- **pandas** (>=2.3.3) - Data manipulation and analysis
- **numpy** (>=2.3.4) - Numerical computing
- **matplotlib** (>=3.10.7) - Data visualization

## Notes for Development

This project uses `uv` instead of `pip` for faster dependency resolution and management. Always use `uv` commands for package management to maintain consistency with the lock file.
