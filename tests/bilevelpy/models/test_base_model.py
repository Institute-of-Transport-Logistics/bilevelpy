"""Tests for BaseModel.model_name property fallback."""

import pytest

from bilevelpy.data.core import MultiEntityDataset
from bilevelpy.models.core import BaseModel
from bilevelpy.models.meta import ModelMetaData


class TestModelNameFallback:

    def test_falls_back_to_model_metadata(self):
        """When a subclass defines model_metadata but not model_name,
        the property should return model_metadata."""

        class MyModel(BaseModel):
            model_metadata = ModelMetaData("TEST", "Test Model")

        model = MyModel(MultiEntityDataset())
        assert model.model_name == ModelMetaData("TEST", "Test Model")
        assert model.model_name.display_name == "Test Model"

    def test_falls_back_to_class_name(self):
        """When a subclass defines neither model_metadata nor model_name,
        the property should fall back to the class name."""

        class EmptyModel(BaseModel):
            pass

        result = EmptyModel(MultiEntityDataset()).model_name
        assert result.value == "EmptyModel"
        assert result.display_name == "EmptyModel"

    def test_override_still_works(self):
        """A subclass that explicitly overrides model_name should still work."""

        class CustomModel(BaseModel):
            @property
            def model_name(self):
                return ModelMetaData("CUSTOM", "Custom Name")

        model = CustomModel(MultiEntityDataset())
        assert model.model_name == ModelMetaData("CUSTOM", "Custom Name")
        assert model.model_name.display_name == "Custom Name"