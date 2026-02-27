"""Shared constants, types, and helpers for transform modules."""

from __future__ import annotations

from typing import Any

import polars as pl

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

    if item.competence_standard:
        for cs in item.competence_standard:
            competences.append(Competence(type="Kompetenz", name=cs))

    if item.general_mathematical_competence:
        for gmc in item.general_mathematical_competence:
            competences.append(Competence(type="Allgemeine Kompetenz", name=gmc))

    if item.core_idea:
        for ci in item.core_idea:
            competences.append(Competence(type="Leitidee", name=ci))

    if item.cognitive_demand_level:
        competences.append(
            Competence(type="Anforderungsbereich", name=item.cognitive_demand_level)
        )

    if item.listening_or_reading_style:
        competences.append(
            Competence(type="Hör-/Lesestil", name=item.listening_or_reading_style)
        )

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
) -> list[dict[str, str]]:
    """Build covariate dicts from a student's covariate values.

    Returns plain dicts (not Characteristic models) because the generated
    Characteristic oneOf wrapper is not serializable by Pydantic v2.
    The dicts are assigned via __dict__ to bypass model validation.
    """
    return [{"type": col, "value": str(row[col])} for col in covariate_columns]


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
