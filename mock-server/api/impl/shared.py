"""Shared infrastructure for API endpoint implementations."""

import logging
import os
from pathlib import Path

from fastapi import HTTPException

from generator.booklet_registry import BookletRegistry
from generator.booklets import BookletKey
from generator.config import (
    CovariateConfig,
    EquivalenceTableEntry,
    GroupConfig,
    GroupsFileConfig,
    SchoolConfig,
    load_equivalence_tables,
    load_groups_config,
    load_schools_config,
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
        (entry.booklet_key(), entry.domain): entry
        for entry in _equiv_config.tables
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


# --- Helper functions ---


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


def build_covariates(
    group_cfg: GroupConfig,
) -> tuple[CovariateDistribution, ...]:
    """Build covariate distributions, merging group-specific with defaults."""
    defaults: dict[str, CovariateConfig] = {}
    if (
        groups_config
        and groups_config.defaults
        and groups_config.defaults.covariates
    ):
        defaults = dict(groups_config.defaults.covariates)

    merged = dict(defaults)
    if group_cfg.covariates:
        merged.update(group_cfg.covariates)

    return tuple(
        CovariateDistribution(
            type_name=type_name,
            categories=tuple(cov_cfg.categories),
            probabilities=tuple(cov_cfg.probabilities),
        )
        for type_name, cov_cfg in merged.items()
    )


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
        entry
        for (bk, _domain), entry in equiv_lookup.items()
        if bk == booklet_key
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
