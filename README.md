# BilevelPy

[![CI](https://github.com/Institute-of-Transport-Logistics/bilevelpy/actions/workflows/ci.yml/badge.svg)](https://github.com/Institute-of-Transport-Logistics/bilevelpy/actions/workflows/ci.yml)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-brightgreen)](https://institute-of-transport-logistics.github.io/bilevelpy/)
[![Python](https://img.shields.io/badge/python-3.11--3.14-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21515530.svg)](https://doi.org/10.5281/zenodo.21515530)

<p align="center">
  <img
    src="https://raw.githubusercontent.com/Institute-of-Transport-Logistics/bilevelpy/main/docs/resources/bilevelpy_logo_text_background.png"
    alt="BilevelPy"
    height="180"
  >
</p>

<p align="center">
  An extensible Python framework for building, solving, and evaluating
  <strong>Gurobi-based optimization models</strong>,
  with built-in support for hub-location problems.
</p>

> **Project status:** BilevelPy is an alpha release. Its public API may change
> before version 1.0.0.

## Overview

BilevelPy provides reusable abstractions for implementing optimization models
with Gurobi. It separates data preparation, model construction, solver
execution, and solution extraction into focused components.

The current release includes:

- composable `Variable` and `Constraint` classes
- dependency-aware model construction through `BaseModel`
- structured datasets and preprocessing pipelines
- configurable Gurobi execution and structured solutions
- built-in hub-location components
- CAB25 and CAB100 benchmark datasets

## Installation

```bash
pip install bilevelpy
```

Requirements:

- Python 3.11–3.14
- Gurobi Optimizer 11.0 or newer
- a valid Gurobi licence

BilevelPy is licensed separately from Gurobi. Installing BilevelPy does not
provide a licence for Gurobi Optimizer.

See the
[installation guide](https://institute-of-transport-logistics.github.io/bilevelpy/installation/)
for development setup and further details.

## Typical workflow

```python
from bilevelpy import Dataset, ModelSolver
from bilevelpy.data.builder import DatasetBuilder
from bilevelpy.data.loaders import HLPLoader
from bilevelpy.data.processor import HLPNodeSelector

dataset = (
    DatasetBuilder()
    .pipe(HLPLoader(Dataset.CAB100))
    .pipe(HLPNodeSelector(n_nodes=10))
    .build()
)

# Define a BaseModel subclass with the required variables,
# constraints, and objective.
model = MyModel(data=dataset)
solution = ModelSolver(model).solve()

print(solution)
```

The
[quickstart tutorial](https://institute-of-transport-logistics.github.io/bilevelpy/tutorial/)
contains a complete single-allocation hub-location model.

## Documentation

- [Installation](https://institute-of-transport-logistics.github.io/bilevelpy/installation/)
- [Quickstart tutorial](https://institute-of-transport-logistics.github.io/bilevelpy/tutorial/)
- [Architecture](https://institute-of-transport-logistics.github.io/bilevelpy/architecture/)
- [Dataset guide](https://institute-of-transport-logistics.github.io/bilevelpy/guides/datasets/)
- [Model guide](https://institute-of-transport-logistics.github.io/bilevelpy/guides/models/)
- [Solver guide](https://institute-of-transport-logistics.github.io/bilevelpy/guides/solving/)
- [Full pipeline example](https://institute-of-transport-logistics.github.io/bilevelpy/guides/full_pipeline/)
- [API reference](https://institute-of-transport-logistics.github.io/bilevelpy/reference/)

## Research implementation

A complete research implementation built with BilevelPy is available in
[An Oracle-based Approach for Price-setting Problems in Logistics](https://institute-of-transport-logistics.github.io/oracle-price-settings-logistics/).

## Citation

Citation metadata is available in [`CITATION.cff`](CITATION.cff).

## Changelog

See [`CHANGELOG.md`](CHANGELOG.md) for the release history.

## Licence

BilevelPy is licensed under the [Apache License 2.0](LICENSE).

Gurobi Optimizer and `gurobipy` are proprietary software distributed and
licensed separately by Gurobi Optimization, LLC.
