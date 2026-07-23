class VariableMetaData:
    """Metadata descriptor for a decision variable.

    Used as a class-level attribute on [Variable][bilevelpy.models.vars.core.Variable]
    subclasses. Enables variables to be used as dictionary keys, DataFrame
    column labels, and cross-referenced by [Constraint][bilevelpy.models.constraints.core.Constraint]
    declarations.

    Attributes:
        value: Short code used as the Gurobi variable name (e.g. ``"x"``, ``"y"``).
        display_name: Human-readable label for UIs and reports.
        identifiers: List of [DataCol][bilevelpy.core.columns.DataCol]
            entries describing the tuple dimensions.
        description: Optional longer description.
    """

    value: str
    display_name: str
    identifiers: list
    description: str

    def __init__(
        self,
        value: str,
        display_name: str,
        identifiers: list,
        description: str = "",
    ) -> None:
        """Create a new variable metadata instance.

        Args:
            value: Short code (e.g. ``"x"``).
            display_name: Human-readable name (e.g. ``"Allocations"``).
            identifiers: List of [DataCol][bilevelpy.core.columns.DataCol]
                entries defining the variable's dimensions.
            description: Optional longer description.
        """
        self.value = value
        self.display_name = display_name
        self.identifiers = identifiers
        self.description = description

    @property
    def number_of_identifiers(self) -> int:
        """Return the number of dimensions this variable spans."""
        return len(self.identifiers)

    def __str__(self) -> str:
        """Return the short value string (e.g. ``"x"``)."""
        return self.value

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: '{self.value}'>"

    def __hash__(self) -> int:
        """Hash by value, so instances can be dict keys and DataFrame columns."""
        return hash(self.value)

    def __eq__(self, other) -> bool:
        """Compare by value against other metadata, strings, or Variables.

        ``VariableMetaData("x") == "x"`` → ``True``
        ``VariableMetaData("x") == VariableMetaData("x")`` → ``True``
        ``VariableMetaData("x") == AllocationVariable`` → ``True``
            (if ``AllocationVariable.var_metadata.value == "x"``)
        """
        if isinstance(other, VariableMetaData):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        if hasattr(other, "var_metadata"):
            return self.value == other.var_metadata.value
        return False


class ModelMetaData:
    """Metadata descriptor for a model identity.

    Used in benchmark configurations, the [SolutionRegistry][bilevelpy.solution.solution_registry.SolutionRegistry], and
    UI model selectors to identify models without importing them.

    Attributes:
        value: Short code (e.g. ``"PS_HLP"``).
        display_name: Human-readable name (e.g. ``"Big M Model"``).
    """

    value: str
    display_name: str

    def __init__(self, value: str, display_name: str) -> None:
        """Create a new model metadata instance.

        Args:
            value: Short identifier code.
            display_name: Human-readable label for reports and UIs.
        """
        self.value = value
        self.display_name = display_name

    def __str__(self) -> str:
        """Return the display name when printed."""
        return self.display_name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}: '{self.value}'>"

    def __hash__(self) -> int:
        """Hash by value for use as registry/dictionary keys."""
        return hash(self.value)

    def __eq__(self, other) -> bool:
        """Compare by value against other metadata or strings."""
        if isinstance(other, ModelMetaData):
            return self.value == other.value
        if isinstance(other, str):
            return self.value == other
        return False