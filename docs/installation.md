# Installation

BilevelPy is distributed through [PyPI](https://pypi.org/project/bilevelpy/) and
can be installed with any standard Python package manager.

## Requirements

- Python 3.11–3.14
- Gurobi Optimizer 11.0 or newer
- a valid Gurobi licence

BilevelPy is licensed separately from Gurobi. Installing BilevelPy or
`gurobipy` does not provide a production or academic Gurobi licence.

## Install from PyPI

### Using pip

```bash
pip install bilevelpy
```

### Using Poetry

```bash
poetry add bilevelpy
```

Both commands install the same BilevelPy release from PyPI. Use `pip` in a
regular virtual environment and `poetry add` when BilevelPy should become a
managed dependency of a Poetry project.

## Verify the installation

```bash
python -c "import bilevelpy; print(bilevelpy.__file__)"
```

You can also verify that Gurobi is available:

```bash
python -c "import gurobipy; print(gurobipy.gurobi.version())"
```

## Install a specific version

For reproducible experiments, pin the exact version used by your project.

### pip

```bash
python -m pip install "bilevelpy==0.1.0"
```

### Poetry

```bash
poetry add "bilevelpy==0.1.0"
```

## Install the development version

The latest unreleased version can be installed directly from GitHub.

### pip

```bash
python -m pip install   "bilevelpy @ git+https://github.com/Institute-of-Transport-Logistics/bilevelpy.git"
```

### Poetry

```bash
poetry add git+https://github.com/Institute-of-Transport-Logistics/bilevelpy.git
```

The development version may contain changes that are not yet part of a stable
release.

## Contributing from source

Clone the repository and install the development dependencies:

```bash
git clone https://github.com/Institute-of-Transport-Logistics/bilevelpy.git
cd bilevelpy
poetry install --with dev,docs
```

Run the tests:

```bash
poetry run pytest
```

Serve the documentation locally:

```bash
poetry run mkdocs serve
```

## Gurobi licensing

BilevelPy depends on the proprietary `gurobipy` package. The Apache License 2.0
applies to BilevelPy itself and does not grant rights to Gurobi Optimizer.

Users are responsible for obtaining and configuring a suitable Gurobi licence.
For installation and licence options, consult the official Gurobi
documentation.
