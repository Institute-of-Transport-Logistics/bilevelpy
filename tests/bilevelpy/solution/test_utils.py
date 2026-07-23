"""Tests for extract_gurobi_name."""

import pytest

from bilevelpy.solution.utils import extract_gurobi_name


class TestExtractGurobiName:

    class TestBracketNotation:
        def test_two_indices(self):
            assert extract_gurobi_name("x[3,7]") == ("x", (3, 7))

        def test_single_index(self):
            assert extract_gurobi_name("z[5]") == ("z", (5,))

        def test_multi_char_name(self):
            assert extract_gurobi_name("alloc[1,2]") == ("alloc", (1, 2))

    class TestParenNotation:
        def test_three_indices(self):
            assert extract_gurobi_name("y(2,3,5)") == ("y", (2, 3, 5))

        def test_single_index(self):
            assert extract_gurobi_name("v(0)") == ("v", (0,))

    class TestUnderscoreNotation:
        def test_two_indices(self):
            assert extract_gurobi_name("p_0_1") == ("p", (0, 1))

        def test_no_trailing_underscore_in_name(self):
            assert extract_gurobi_name("p_0") == ("p", (0,))

    class TestEdgeCases:
        def test_plain_name_no_indices(self):
            assert extract_gurobi_name("objective") == ("objective", ())

