"""Class profiles and covariate distributions for student generation."""

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class ClassProfile:
    """Configuration for a class ability distribution.

    Attributes:
        name: Human-readable name for the profile
        ability_mean: Mean ability on logit scale (0.0 = average difficulty)
        ability_std: Standard deviation of ability distribution
    """

    name: str
    ability_mean: float
    ability_std: float


@dataclass(frozen=True)
class CovariateDistribution:
    """Distribution configuration for a single covariate.

    Attributes:
        type_name: The covariate type (e.g., "geschlecht", "SES")
        categories: Possible values for this covariate
        probabilities: Probability for each category (must sum to 1.0)
    """

    type_name: str
    categories: tuple[str, ...]
    probabilities: tuple[float, ...]

    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if len(self.categories) != len(self.probabilities):
            raise ValueError("categories and probabilities must have same length")
        if not math.isclose(math.fsum(self.probabilities), 1.0):
            raise ValueError("probabilities must sum to 1.0")
        if any(p < 0 for p in self.probabilities):
            raise ValueError("probabilities must be non-negative")
