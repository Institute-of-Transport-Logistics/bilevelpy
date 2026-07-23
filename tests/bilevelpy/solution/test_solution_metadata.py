"""Tests for SolutionMetadata (pure-Python parts only)."""

import pytest

from bilevelpy.solution.core import SolutionMetadata, SolutionLabels


class TestSolutionMetadata:

    class TestTranslate:
        def test_known_key_returns_label(self):
            meta = SolutionMetadata(1.0, 100.0, True, 0.05, 42)
            assert meta._translate("solving_time") == "Solving Time (s)"
            assert meta._translate("objective_value") == "Objective Value"
            assert meta._translate("is_optimal") == "Is Optimal"

        def test_unknown_key_returns_itself(self):
            meta = SolutionMetadata(1.0, 100.0, True, 0.05, 42)
            assert meta._translate("unknown_key") == "unknown_key"

    class TestToDict:
        def test_raw_keys(self):
            meta = SolutionMetadata(1.0, 100.0, True, 0.05, 42)
            d = meta.to_dict(with_label=False)
            assert d == {
                "solving_time": 1.0,
                "objective_value": 100.0,
                "is_optimal": True,
                "mip_gap": 0.05,
                "node_count": 42,
            }

        def test_with_labels(self):
            meta = SolutionMetadata(2.5, 200.0, False, 0.01, 10)
            d = meta.to_dict(with_label=True)
            assert d["Solving Time (s)"] == 2.5
            assert d["Objective Value"] == 200.0
            assert d["Is Optimal"] is False
            assert d["MIP Gap (%)"] == 0.01
            assert d["Nodes Explored"] == 10

        def test_extra_fields(self):
            meta = SolutionMetadata(1.0, 100.0, True, 0.0, 5,
                                    extra={"custom_metric": 42})
            d = meta.to_dict(with_label=False)
            assert d["custom_metric"] == 42

        def test_extra_field_collision_raises(self):
            meta = SolutionMetadata(1.0, 100.0, True, 0.0, 5,
                                    extra={"solving_time": 999})
            with pytest.raises(ValueError, match="Key collision"):
                meta.to_dict()


class TestSolutionLabels:
    def test_values_are_strings(self):
        for label in SolutionLabels:
            assert isinstance(label.value, str)