

class SolutionRegistry:
    """Map model classes to their solution classes.

    When [ModelSolver][bilevelpy.solver.ModelSolver] finishes solving, it uses
    the registry to find the correct solution class for the model. Models
    are registered via the :meth:`register_for` decorator.

    Example:
        ```python
        @SolutionRegistry.register_for(MySolution)
        class MyModel(BaseModel):
            ...
        ```
    """

    _registry: dict[type, type] = {}

    @classmethod
    def register_for(cls, solution_class: type):
        """Decorator that registers a solution class for a model class.

        Args:
            solution_class: The [BaseModelSolution][bilevelpy.solution.BaseModelSolution]
                subclass to use for the decorated model.

        Returns:
            A decorator that adds the model→solution mapping.
        """
        def decorator(model_class: type):
            cls._registry[model_class] = solution_class
            return model_class
        return decorator

    @classmethod
    def get_solution_class(cls, model_instance_or_class) -> type:
        """Look up the registered solution class for a model.

        Walks up the MRO so that subclasses inherit their parent's
        solution if none is registered directly.

        Args:
            model_instance_or_class: A model instance or class.

        Returns:
            The registered [BaseModelSolution][bilevelpy.solution.BaseModelSolution]
            subclass.

        Raises:
            NotImplementedError: If no solution is registered for the
                model or any of its base classes.
        """

        model_type = model_instance_or_class if isinstance(model_instance_or_class, type) else type(
            model_instance_or_class)


        for base in model_type.__mro__:
            if base in cls._registry:
                return cls._registry[base]
        raise NotImplementedError(f"No solution registered for {model_type.__name__} or its bases.")
