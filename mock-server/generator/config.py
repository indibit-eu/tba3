"""YAML configuration models for groups and equivalence tables."""

import math
from pathlib import Path
from typing import TYPE_CHECKING, Self

import yaml
from pydantic import BaseModel, Field, ValidationInfo, model_validator

from generator.booklets import BookletKey

if TYPE_CHECKING:
    from generator.booklet_registry import BookletRegistry


def _find_duplicates(values: list[str]) -> set[str]:
    """Return the set of values that appear more than once."""
    seen: set[str] = set()
    duplicates: set[str] = set()
    for v in values:
        if v in seen:
            duplicates.add(v)
        seen.add(v)
    return duplicates


class CovariateConfig(BaseModel):
    """Configuration for a single covariate distribution."""

    categories: list[str]
    probabilities: list[float]

    @model_validator(mode="after")
    def validate_distribution(self) -> Self:
        """Validate that categories and probabilities are consistent."""
        if len(self.categories) != len(self.probabilities):
            raise ValueError("categories and probabilities must have same length")
        if any(p < 0 for p in self.probabilities):
            raise ValueError("probabilities must be non-negative")
        if not math.isclose(math.fsum(self.probabilities), 1.0):
            raise ValueError("probabilities must sum to 1.0")
        return self


class GroupConfig(BaseModel):
    """Configuration for a single group."""

    id: str
    name: str | None = None
    booklet: str
    ability_mean: float
    ability_std: float = Field(gt=0)
    size: int = Field(ge=1)
    seed: str
    covariates: dict[str, CovariateConfig] | None = None

    def booklet_key(self) -> BookletKey:
        """Parse the booklet string into a BookletKey."""
        return BookletKey.from_str(self.booklet)

    def display_name(self) -> str:
        """Return the display name, falling back to the ID."""
        return self.name or f"Lerngruppe {self.id}"


class DefaultsConfig(BaseModel):
    """Default values applied to all groups unless overridden."""

    covariates: dict[str, CovariateConfig] | None = None


class GroupsFileConfig(BaseModel):
    """Root model for config/groups.yml."""

    defaults: DefaultsConfig | None = None
    groups: list[GroupConfig]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        """Ensure all group IDs are unique."""
        duplicates = _find_duplicates([g.id for g in self.groups])
        if duplicates:
            raise ValueError(f"Duplicate group IDs: {duplicates}")
        return self


class CompetenceLevelRange(BaseModel):
    """A competence level with its score range (inclusive)."""

    name_short: str
    name: str | None = None
    description: str | None = None
    min_score: int = Field(ge=0)
    max_score: int


class EquivalenceTableEntry(BaseModel):
    """Equivalence table for one booklet (optionally domain-specific)."""

    booklet: str
    domain: str | None = None
    competence_levels: list[CompetenceLevelRange]

    def booklet_key(self) -> BookletKey:
        """Parse the booklet string into a BookletKey."""
        return BookletKey.from_str(self.booklet)

    def match_level(self, raw_score: int) -> str | None:
        """Return the competence level name_short for a raw score, or None."""
        for cl in self.competence_levels:
            if cl.min_score <= raw_score <= cl.max_score:
                return cl.name_short
        return None

    @model_validator(mode="after")
    def validate_ranges(self) -> Self:
        """Validate that score ranges are ascending and contiguous."""
        levels = self.competence_levels
        if not levels:
            raise ValueError("competence_levels must not be empty")
        for i, level in enumerate(levels):
            if level.min_score > level.max_score:
                raise ValueError(
                    f"Level '{level.name_short}': "
                    f"min_score ({level.min_score}) > max_score ({level.max_score})"
                )
            if i > 0:
                prev = levels[i - 1]
                if level.min_score != prev.max_score + 1:
                    raise ValueError(
                        f"Gap or overlap between '{prev.name_short}' "
                        f"(max={prev.max_score}) and '{level.name_short}' "
                        f"(min={level.min_score})"
                    )
        return self


class SchoolConfig(BaseModel):
    """Configuration for a single school (composed of groups)."""

    id: str
    name: str | None = None
    groups: list[str] = Field(min_length=1)

    def display_name(self) -> str:
        """Return the display name, falling back to the ID."""
        return self.name or f"Schule {self.id}"


class SchoolsFileConfig(BaseModel):
    """Root model for config/schools.yml."""

    schools: list[SchoolConfig]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        """Ensure all school IDs are unique."""
        duplicates = _find_duplicates([s.id for s in self.schools])
        if duplicates:
            raise ValueError(f"Duplicate school IDs: {duplicates}")
        return self


class StateConfig(BaseModel):
    """Configuration for a single state (generates one group per booklet)."""

    id: str
    name: str | None = None
    booklets: list[str] = Field(min_length=1)
    ability_mean: float
    ability_std: float = Field(gt=0)
    size: int = Field(ge=1)
    seed: str
    covariates: dict[str, CovariateConfig] | None = None

    def display_name(self) -> str:
        """Return the display name, falling back to the ID."""
        return self.name or f"Bundesland {self.id}"

    def booklet_keys(self) -> list[BookletKey]:
        """Parse all booklet strings into BookletKey objects."""
        return [BookletKey.from_str(b) for b in self.booklets]


class StatesFileConfig(BaseModel):
    """Root model for config/states.yml."""

    defaults: DefaultsConfig | None = None
    states: list[StateConfig]

    @model_validator(mode="after")
    def validate_unique_ids(self) -> Self:
        """Ensure all state IDs are unique."""
        duplicates = _find_duplicates([s.id for s in self.states])
        if duplicates:
            raise ValueError(f"Duplicate state IDs: {duplicates}")
        return self


class EquivalenceTablesFileConfig(BaseModel):
    """Root model for config/equivalence_tables.yml."""

    tables: list[EquivalenceTableEntry]

    @model_validator(mode="after")
    def validate_item_counts(self, info: ValidationInfo) -> Self:
        """Validate that each table's last max_score matches the item count.

        Requires a BookletRegistry passed via validation context.
        """
        registry: BookletRegistry | None = (
            info.context.get("registry") if info.context else None
        )
        if registry is None:
            return self

        for entry in self.tables:
            booklet = registry.get(entry.booklet_key())
            if booklet is None:
                raise ValueError(f"Unknown booklet: {entry.booklet}")

            # Count only items matching the domain, if specified
            if entry.domain is not None:
                num_items = sum(
                    1 for item in booklet.items if item.domain == entry.domain
                )
            else:
                num_items = booklet.item_count

            last = entry.competence_levels[-1]
            if last.max_score != num_items:
                domain_info = f" domain={entry.domain}" if entry.domain else ""
                raise ValueError(
                    f"Equivalence table {entry.booklet}{domain_info}: "
                    f"last level '{last.name_short}' has "
                    f"max_score={last.max_score}, "
                    f"but booklet has {num_items} items"
                )
        return self


def load_groups_config(path: Path) -> GroupsFileConfig:
    """Load and validate groups configuration from a YAML file."""
    raw = yaml.safe_load(path.read_text())
    return GroupsFileConfig.model_validate(raw)


def load_equivalence_tables(
    path: Path, registry: BookletRegistry | None = None
) -> EquivalenceTablesFileConfig:
    """Load and validate equivalence tables from a YAML file.

    Args:
        path: Path to the YAML file.
        registry: Optional booklet registry for validating max_score
            against actual item counts.
    """
    raw = yaml.safe_load(path.read_text())
    context = {"registry": registry} if registry is not None else None
    return EquivalenceTablesFileConfig.model_validate(raw, context=context)


def load_schools_config(path: Path) -> SchoolsFileConfig:
    """Load and validate schools configuration from a YAML file."""
    raw = yaml.safe_load(path.read_text())
    return SchoolsFileConfig.model_validate(raw)


def load_states_config(path: Path) -> StatesFileConfig:
    """Load and validate states configuration from a YAML file."""
    raw = yaml.safe_load(path.read_text())
    return StatesFileConfig.model_validate(raw)
