# Build Instructions

This project has been converted from the old `setup.py` style to the modern `pyproject.toml` configuration.

## Building the Package

### Using pip (recommended)
```bash
pip install build
python -m build
```

### Using setuptools directly
```bash
python setup.py sdist bdist_wheel
```

### Installing in development mode
```bash
pip install -e .
```

## RPM Package Building

The `.spec` file has been updated to work with the new build system:

```bash
rpmbuild -ba recodex-monitor.spec
```

## Changes Made

1. **Created `pyproject.toml`** - Modern Python packaging configuration
2. **Updated `setup.py`** - Now defers to `pyproject.toml` for backward compatibility
3. **Created `setup.cfg`** - Additional configuration file (optional)
4. **Updated `recodex-monitor.spec`** - Modified to work with wheel-based builds
5. **Updated `requirements.txt`** - Cleaned up dependencies

## Migration Notes

- Version is now dynamically read from `monitor.__version__`
- All package metadata is centralized in `pyproject.toml`
- The build process now creates modern wheel packages
- RPM packaging uses wheel installation instead of direct setup.py
