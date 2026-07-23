"""Tests for ModelSolver."""

import pytest

from bilevelpy.solver import ModelSolver


class TestModelSolver:
    def test_rejects_non_base_model(self):
        with pytest.raises(TypeError):
            ModelSolver("not a model")