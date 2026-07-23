# Installation

## Prerequisites

- **Gurobi** installed and licensed ([gurobi.com](https://www.gurobi.com/downloads/))
- **Python 3.11+**
- **Poetry** ([install guide](https://python-poetry.org/docs/#installation))


## Install via Poetry

```bash
poetry add git+https://github.com/Institute-of-Transport-Logistics/bilevelpy.git
```

## Verify

```bash
python -c "from bilevelpy import BaseModel, Variable, Constraint; print('OK')"
```

