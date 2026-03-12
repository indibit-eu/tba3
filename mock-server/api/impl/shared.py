"""Shared infrastructure for API endpoint implementations."""

import logging
import os
from pathlib import Path

from fastapi import HTTPException

from generator.booklet_registry import BookletRegistry
from generator.booklets import BookletKey
from generator.config import (
    CovariateConfig,
    DistrictConfig,
    EquivalenceTableEntry,
    GroupConfig,
    GroupsFileConfig,
    SchoolConfig,
    StateConfig,
    StatesFileConfig,
    load_equivalence_tables,
    load_groups_config,
    load_schools_config,
    load_states_config,
)
from generator.core import GroupData, generate_group
from generator.profiles import ClassProfile, CovariateDistribution

logger = logging.getLogger(__name__)

# --- Module-level initialization ---

_METADATA_DIR = Path(os.environ.get("TBA3_METADATA_DIR", "metadata"))
_CONFIG_DIR = Path(os.environ.get("TBA3_CONFIG_DIR", "config"))

# Load booklet metadata
registry = BookletRegistry()
if _METADATA_DIR.exists():
    registry.load_from_directory(_METADATA_DIR)
    logger.info("Loaded %d booklets from %s", registry.count, _METADATA_DIR)
else:
    logger.warning("Metadata directory not found: %s", _METADATA_DIR)

# Load YAML configs
groups_config: GroupsFileConfig | None = None
group_lookup: dict[str, GroupConfig] = {}
equiv_lookup: dict[tuple[BookletKey, str | None], EquivalenceTableEntry] = {}

_groups_path = _CONFIG_DIR / "groups.yml"
if _groups_path.exists():
    groups_config = load_groups_config(_groups_path)
    group_lookup = {g.id: g for g in groups_config.groups}
    logger.info("Loaded %d groups from %s", len(group_lookup), _groups_path)
else:
    logger.warning("Groups config not found: %s", _groups_path)

_equiv_path = _CONFIG_DIR / "equivalence_tables.yml"
if _equiv_path.exists():
    _equiv_config = load_equivalence_tables(_equiv_path, registry=registry)
    equiv_lookup = {
        (entry.booklet_key(), entry.domain): entry for entry in _equiv_config.tables
    }
    logger.info(
        "Loaded %d equivalence tables from %s",
        len(equiv_lookup),
        _equiv_path,
    )
else:
    logger.warning("Equivalence tables not found: %s", _equiv_path)

school_lookup: dict[str, SchoolConfig] = {}

_schools_path = _CONFIG_DIR / "schools.yml"
if _schools_path.exists():
    _schools_config = load_schools_config(_schools_path)
    school_lookup = {s.id: s for s in _schools_config.schools}
    logger.info("Loaded %d schools from %s", len(school_lookup), _schools_path)
else:
    logger.warning("Schools config not found: %s", _schools_path)

states_config: StatesFileConfig | None = None
state_lookup: dict[str, StateConfig] = {}

_states_path = _CONFIG_DIR / "states.yml"
if _states_path.exists():
    states_config = load_states_config(_states_path)
    state_lookup = {s.id: s for s in states_config.states}
    logger.info("Loaded %d states from %s", len(state_lookup), _states_path)
else:
    logger.warning("States config not found: %s", _states_path)


# --- Helper functions ---


VALID_AGGREGATION_TYPES = {"competence", "gender"}
STUDENT_VALID_AGGREGATION_TYPES = {"competence"}


def parse_aggregation_param(aggregation: str | None) -> set[str]:
    """Parse and validate the aggregation query parameter.

    Args:
        aggregation: Comma-separated aggregation types (e.g. "competence,gender").

    Returns:
        Set of validated aggregation type strings.

    Raises:
        HTTPException(400): If parameter is missing/empty or contains invalid values.
    """
    if not aggregation:
        raise HTTPException(
            status_code=400,
            detail="aggregation parameter is required",
        )
    requested = {t.strip().lower() for t in aggregation.split(",") if t.strip()}
    if not requested:
        raise HTTPException(
            status_code=400,
            detail="aggregation parameter is required",
        )
    invalid = requested - VALID_AGGREGATION_TYPES
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid aggregation type(s): {sorted(invalid)}. "
            f"Valid values: {sorted(VALID_AGGREGATION_TYPES)}",
        )
    return requested


def validate_student_aggregation_types(aggregation_types: set[str]) -> None:
    """Raise 400 if aggregation types contain student-incompatible values."""
    invalid = aggregation_types - STUDENT_VALID_AGGREGATION_TYPES
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"Aggregation type(s) not supported at student level: "
            f"{sorted(invalid)}. "
            f"Valid values: {sorted(STUDENT_VALID_AGGREGATION_TYPES)}",
        )


def parse_comparison_param(primary_id: str, comparison: str | None) -> list[str]:
    """Parse comparison param and return deduplicated list including primary ID.

    Args:
        primary_id: The primary entity ID (always first in result).
        comparison: Comma-separated entity IDs, or None.

    Returns:
        Ordered list of unique IDs, primary first.
    """
    ids = [primary_id]
    if comparison:
        for cid_raw in comparison.split(","):
            cid = cid_raw.strip()
            if cid and cid not in ids:
                ids.append(cid)
    return ids


def resolve_requested_types(type_param: str | None) -> tuple[bool, bool]:
    """Parse type param and return (include_group, include_students).

    Default (no type param): include group only.
    type=students: include students only.
    type=group,students: include both.
    """
    if not type_param:
        requested: set[str] = set()
    else:
        requested = {t.strip().lower() for t in type_param.split(",") if t.strip()}
    include_group = "students" not in requested or "group" in requested
    include_students = "students" in requested
    return include_group, include_students


def resolve_state_requested_types(type_param: str | None) -> tuple[bool, bool]:
    """Parse type param and return (include_state, include_district).

    Default (no type param): include state only.
    type=district: include district only.
    type=state,district: include both.
    """
    if not type_param:
        requested: set[str] = set()
    else:
        requested = {t.strip().lower() for t in type_param.split(",") if t.strip()}
    include_state = "district" not in requested or "state" in requested
    include_district = "district" in requested
    return include_state, include_district


def _merge_covariates(
    default_covariates: dict[str, CovariateConfig] | None,
    entity_covariates: dict[str, CovariateConfig] | None,
) -> tuple[CovariateDistribution, ...]:
    """Build covariate distributions, merging entity-specific with defaults."""
    merged: dict[str, CovariateConfig] = {}
    if default_covariates:
        merged.update(default_covariates)
    if entity_covariates:
        merged.update(entity_covariates)

    return tuple(
        CovariateDistribution(
            type_name=type_name,
            categories=tuple(cov_cfg.categories),
            probabilities=tuple(cov_cfg.probabilities),
        )
        for type_name, cov_cfg in merged.items()
    )


def build_covariates(
    group_cfg: GroupConfig,
) -> tuple[CovariateDistribution, ...]:
    """Build covariate distributions, merging group-specific with defaults."""
    default_covariates = (
        groups_config.defaults.covariates
        if groups_config and groups_config.defaults
        else None
    )
    return _merge_covariates(default_covariates, group_cfg.covariates)


def build_state_covariates(
    state_cfg: StateConfig,
) -> tuple[CovariateDistribution, ...]:
    """Build covariate distributions, merging state-specific with defaults."""
    default_covariates = (
        states_config.defaults.covariates
        if states_config and states_config.defaults
        else None
    )
    return _merge_covariates(default_covariates, state_cfg.covariates)


def resolve_group(
    group_id: str,
) -> tuple[GroupData, list[EquivalenceTableEntry]]:
    """Look up group config by ID and generate data.

    Returns:
        Tuple of (GroupData, list of matching equivalence tables).

    Raises:
        HTTPException(404): If group ID or booklet is not found.
    """
    group_cfg = group_lookup.get(group_id)
    if group_cfg is None:
        raise HTTPException(
            status_code=404,
            detail=f"Group not found: {group_id}",
        )

    booklet_key = group_cfg.booklet_key()
    booklet = registry.get(booklet_key)
    if booklet is None:
        raise HTTPException(
            status_code=404,
            detail=f"Booklet not found: {booklet_key}",
        )

    covariates = build_covariates(group_cfg)
    profile = ClassProfile(
        name=group_cfg.display_name(),
        ability_mean=group_cfg.ability_mean,
        ability_std=group_cfg.ability_std,
    )

    group_data = generate_group(
        group_id=group_id,
        booklet=booklet,
        profile=profile,
        student_count=group_cfg.size,
        covariates=covariates,
        seed=group_cfg.seed,
    )

    # Collect all equivalence tables for this booklet
    equiv_tables = [
        entry for (bk, _domain), entry in equiv_lookup.items() if bk == booklet_key
    ]

    return group_data, equiv_tables


def resolve_school(
    school_id: str,
) -> list[tuple[GroupData, list[EquivalenceTableEntry]]]:
    """Look up school config by ID and generate data for all its groups.

    Returns:
        List of (GroupData, equiv_tables) tuples, one per group in the school.

    Raises:
        HTTPException(404): If school ID or any referenced group is not found.
    """
    school_cfg = school_lookup.get(school_id)
    if school_cfg is None:
        raise HTTPException(
            status_code=404,
            detail=f"School not found: {school_id}",
        )

    return [resolve_group(gid) for gid in school_cfg.groups]


def resolve_state(
    state_id: str,
) -> list[tuple[GroupData, list[EquivalenceTableEntry]]]:
    """Generate one group per booklet for a state.

    Returns:
        List of (GroupData, equiv_tables) tuples, one per booklet.

    Raises:
        HTTPException(404): If state ID or any booklet is not found.
    """
    state_cfg = state_lookup.get(state_id)
    if state_cfg is None:
        raise HTTPException(
            status_code=404,
            detail=f"State not found: {state_id}",
        )

    covariates = build_state_covariates(state_cfg)
    profile = ClassProfile(
        name=state_cfg.display_name(),
        ability_mean=state_cfg.ability_mean,
        ability_std=state_cfg.ability_std,
    )

    results: list[tuple[GroupData, list[EquivalenceTableEntry]]] = []
    for booklet_str in state_cfg.booklets:
        booklet_key = BookletKey.from_str(booklet_str)
        booklet = registry.get(booklet_key)
        if booklet is None:
            raise HTTPException(
                status_code=404,
                detail=f"Booklet not found: {booklet_key}",
            )

        group_data = generate_group(
            group_id=f"{state_id}:{booklet_str}",
            booklet=booklet,
            profile=profile,
            student_count=state_cfg.size,
            covariates=covariates,
            seed=f"{state_cfg.seed}-{booklet_str}",
        )

        equiv_tables = [
            entry for (bk, _domain), entry in equiv_lookup.items() if bk == booklet_key
        ]
        results.append((group_data, equiv_tables))

    return results


def resolve_district(
    state_cfg: StateConfig,
    district_cfg: DistrictConfig,
) -> list[tuple[GroupData, list[EquivalenceTableEntry]]]:
    """Generate one group per booklet for a district within a state.

    Uses the district's ability distribution and size, but the state's booklets.

    Returns:
        List of (GroupData, equiv_tables) tuples, one per booklet.

    Raises:
        HTTPException(404): If any booklet is not found.
    """
    default_covariates = (
        states_config.defaults.covariates
        if states_config and states_config.defaults
        else None
    )
    state_covariates = state_cfg.covariates
    # Merge: defaults -> state -> district
    merged_state: dict[str, CovariateConfig] = {}
    if default_covariates:
        merged_state.update(default_covariates)
    if state_covariates:
        merged_state.update(state_covariates)
    covariates = _merge_covariates(merged_state, district_cfg.covariates)

    profile = ClassProfile(
        name=district_cfg.display_name(),
        ability_mean=district_cfg.ability_mean,
        ability_std=district_cfg.ability_std,
    )

    results: list[tuple[GroupData, list[EquivalenceTableEntry]]] = []
    for booklet_str in state_cfg.booklets:
        booklet_key = BookletKey.from_str(booklet_str)
        booklet = registry.get(booklet_key)
        if booklet is None:
            raise HTTPException(
                status_code=404,
                detail=f"Booklet not found: {booklet_key}",
            )

        group_data = generate_group(
            group_id=f"{state_cfg.id}:{district_cfg.id}:{booklet_str}",
            booklet=booklet,
            profile=profile,
            student_count=district_cfg.size,
            covariates=covariates,
            seed=f"{district_cfg.seed}-{booklet_str}",
        )

        equiv_tables = [
            entry
            for (bk, _domain), entry in equiv_lookup.items()
            if bk == booklet_key
        ]
        results.append((group_data, equiv_tables))

    return results
