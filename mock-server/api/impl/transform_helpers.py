"""Shared constants, types, and helpers for transform modules."""

from __future__ import annotations

from typing import Any

import polars as pl

from api.models.aggregations_inner_all_of_aggregations_inner import (
    AggregationsInnerAllOfAggregationsInner,
)
from api.models.characteristic import Characteristic
from api.models.competence import Competence
from api.models.competence_level import CompetenceLevel
from api.models.descriptive_statistics_descriptive_statistics import (
    DescriptiveStatisticsDescriptiveStatistics,
)
from api.models.domain import Domain
from api.models.exercise import Exercise
from api.models.item_parameters import ItemParameters
from api.models.item_statistics_inner import ItemStatisticsInner
from api.models.subject import Subject
from generator.booklets import Item

# Mapping from Item field names to aggregation type names.
# Used by _build_competences(), build_competence_groups(),
# and build_competence_aggregations().
COMPETENCE_FIELD_MAP: list[tuple[str, str]] = [
    ("competence_standard", "Kompetenz"),
    ("general_mathematical_competence", "Allgemeine Kompetenz"),
    ("core_idea", "Leitidee"),
    ("cognitive_demand_level", "Anforderungsbereich"),
    ("listening_or_reading_style", "Hör-/Lesestil"),
]

SUBJECT_NAMES: dict[str, str] = {
    "de": "Deutsch",
    "ma": "Mathematik",
    "en": "Englisch",
    "fr": "Französisch",
}


def _safe_round(value: Any, decimals: int = 4) -> float:
    """Round a numeric value, returning 0.0 for None.

    Accepts the broad numeric union types returned by Polars aggregation methods.
    """
    if value is None:
        return 0.0
    return round(float(value), decimals)


def build_domain(domain_name: str | None) -> Domain | None:
    """Create a Domain model, or None when domain_name is None."""
    if domain_name is None:
        return None
    return Domain(name=domain_name)


def build_subject(subject_code: str) -> Subject:
    """Create a Subject model from a subject code."""
    return Subject(name=SUBJECT_NAMES.get(subject_code, subject_code))


def _build_competences(item: Item) -> list[Competence] | None:
    """Build a list of Competence objects from an Item's competence fields."""
    competences: list[Competence] = []

    for field_name, type_name in COMPETENCE_FIELD_MAP:
        field_val = getattr(item, field_name)
        if field_val is None:
            continue
        if isinstance(field_val, list):
            for val in field_val:
                competences.append(Competence(type=type_name, name=val))
        else:
            competences.append(Competence(type=type_name, name=field_val))

    return competences if competences else None


def build_item_parameters(item: Item) -> ItemParameters:
    """Build an ItemParameters model from an Item dataclass."""
    return ItemParameters(
        logit=item.logit,
        bista_points=item.bista,
        solution_frequency_primary_school=item.solution_freq_primary_school,
        solution_frequency_gymnasium=item.solution_freq_gymnasium,
        solution_frequency_non_gymnasium=item.solution_freq_non_gymnasium,
        subject=item.subject,
        domain=item.domain,
        competence_level=CompetenceLevel(name_short=item.competence_level),
        competences=_build_competences(item),
    )


def build_student_covariates(
    row: dict[str, Any], covariate_columns: list[str]
) -> list[Characteristic]:
    """Build Characteristic instances from a student's covariate values."""
    return [Characteristic(type=col, value=str(row[col])) for col in covariate_columns]


def build_competence_groups(
    items: list[Item],
) -> dict[tuple[str, str], list[Item]]:
    """Group items by (competence_type, competence_value).

    Items with multiple values for a field appear in each group.
    """
    groups: dict[tuple[str, str], list[Item]] = {}
    for item in items:
        for field_name, type_name in COMPETENCE_FIELD_MAP:
            field_val = getattr(item, field_name)
            if field_val is None:
                continue
            if isinstance(field_val, list):
                for val in field_val:
                    groups.setdefault((type_name, val), []).append(item)
            else:
                groups.setdefault((type_name, field_val), []).append(item)
    return groups


def build_competence_aggregations(
    items: list[Item],
    responses: pl.DataFrame,
) -> list[AggregationsInnerAllOfAggregationsInner]:
    """Build competence aggregations for a set of items and their responses.

    Creates one aggregation entry per individual competence value across all
    competence types present in the items. Items with multiple competence
    values count toward each value.

    Args:
        items: Items to aggregate (typically filtered to a single domain).
        responses: DataFrame containing item response columns (0/1 scores).

    Returns:
        List of aggregation entries, one per (competence_type, competence_value).
    """
    comp_groups = build_competence_groups(items)
    results: list[AggregationsInnerAllOfAggregationsInner] = []

    for (type_name, value), group_items in sorted(comp_groups.items()):
        item_cols = [item.column_name for item in group_items]
        iqb_ids = sorted({item.iqbitem_id for item in group_items})

        domain_df = responses.select(item_cols)
        student_means = domain_df.mean_horizontal()
        frequency = int(domain_df.sum_horizontal().sum())

        results.append(
            AggregationsInnerAllOfAggregationsInner(
                type=type_name,
                value=value,
                descriptive_statistics=DescriptiveStatisticsDescriptiveStatistics(
                    total=len(responses),
                    mean=_safe_round(student_means.mean()),
                    frequency=frequency,
                    standard_deviation=_safe_round(student_means.std()),
                ),
                included_iqb_ids=iqb_ids,
            )
        )

    return results


def build_gender_aggregations(
    items: list[Item],
    responses: pl.DataFrame,
) -> list[AggregationsInnerAllOfAggregationsInner]:
    """Build gender aggregations for a set of items and their responses.

    Groups students by gender, then computes descriptive statistics per group.

    Args:
        items: Items in this domain.
        responses: Full DataFrame with gender column and item response columns.

    Returns:
        List of aggregation entries, one per gender category found.
    """
    if "gender" not in responses.columns:
        return []

    item_cols = [item.column_name for item in items]
    iqb_ids = sorted(item.iqbitem_id for item in items)

    results: list[AggregationsInnerAllOfAggregationsInner] = []

    for gender_val, group_df in responses.group_by("gender", maintain_order=False):
        val = gender_val[0] if isinstance(gender_val, tuple) else gender_val
        gender_str = str(val)
        domain_df = group_df.select(item_cols)
        student_means = domain_df.mean_horizontal()
        frequency = int(domain_df.sum_horizontal().sum())

        results.append(
            AggregationsInnerAllOfAggregationsInner(
                type="gender",
                value=gender_str,
                descriptive_statistics=DescriptiveStatisticsDescriptiveStatistics(
                    total=len(group_df),
                    mean=_safe_round(student_means.mean()),
                    frequency=frequency,
                    standard_deviation=_safe_round(student_means.std()),
                ),
                included_iqb_ids=iqb_ids,
            )
        )

    return sorted(results, key=lambda a: a.value)


def build_single_item_stats(item: Item, responses: pl.DataFrame) -> ItemStatisticsInner:
    """Build statistics for a single item from the responses DataFrame."""
    col = item.column_name

    stats = responses.select(
        pl.col(col).len().alias("total"),
        pl.col(col).sum().alias("frequency"),
        pl.col(col).mean().alias("mean"),
        pl.col(col).std().alias("std"),
    ).row(0, named=True)

    return ItemStatisticsInner(
        name=item.item_nr_booklet,
        iqb_id=item.iqbitem_id,
        exercise=Exercise(name=item.name),
        position=int(item.item_order_booklet),  # TODO: use counted position
        parameters=build_item_parameters(item),
        descriptive_statistics=DescriptiveStatisticsDescriptiveStatistics(
            total=int(stats["total"]),
            mean=_safe_round(stats["mean"]),
            frequency=int(stats["frequency"]),
            standard_deviation=_safe_round(stats["std"]),
        ),
    )
