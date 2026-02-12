"""Shared constants, types, and helpers for transform modules."""

from __future__ import annotations

from typing import Any, NamedTuple

import polars as pl

from api.models.competence_level import CompetenceLevel
from api.models.descriptive_statistics import DescriptiveStatistics
from api.models.domain import Domain
from api.models.domain_subject import DomainSubject
from api.models.item_parameters import ItemParameters
from api.models.item_statistics_inner import ItemStatisticsInner
from generator.booklets import Item

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


class _DomainAggInfo(NamedTuple):
    """Pre-computed domain aggregation info for efficient batch processing."""

    name: str | None
    total: int
    iqb_ids: list[str]
    sum_col: str


def make_domain(
    domain_name: str | None, subject_code: str
) -> Domain | None:
    """Create a Domain model, or None if domain_name is None."""
    if domain_name is None:
        return None
    subject_display = SUBJECT_NAMES.get(subject_code, subject_code)
    return Domain(
        name=domain_name,
        subject=DomainSubject(name=subject_display),
    )


def build_single_item_stats(
    item: Item, responses: pl.DataFrame
) -> ItemStatisticsInner:
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
        parameters=ItemParameters(
            logit=item.logit,
            bista_points=item.bista,
            solution_frequency_primary_school=item.solution_freq_primary_school,
            solution_frequency_gymnasium=item.solution_freq_gymnasium,
            solution_frequency_non_gymnasium=item.solution_freq_non_gymnasium,
            # TBA3 spec's ItemParameters.subject maps to our domain concept
            subject=item.domain,
            domain=item.domain,
            competence_level=CompetenceLevel(name_short=item.competence_level),
        ),
        descriptive_statistics=DescriptiveStatistics(
            total=int(stats["total"]),
            mean=_safe_round(stats["mean"]),
            frequency=int(stats["frequency"]),
            standard_deviation=_safe_round(stats["std"]),
        ),
    )
