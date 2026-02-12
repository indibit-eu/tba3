"""Student-level transform functions (GroupData -> per-student API models)."""

from __future__ import annotations

import polars as pl

from api.impl.transform_helpers import (
    _DomainAggInfo,
    _safe_round,
    make_domain,
)
from api.models.competence_level import CompetenceLevel
from api.models.descriptive_statistics import DescriptiveStatistics
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2
from api.models.inline_object_inner2_all_of_aggregations_inner import (
    InlineObjectInner2AllOfAggregationsInner,
)
from api.models.inline_object_inner_all_of_competence_levels_inner import (
    InlineObjectInnerAllOfCompetenceLevelsInner,
)
from api.models.item_parameters import ItemParameters
from api.models.item_statistics_inner import ItemStatisticsInner
from generator.config import EquivalenceTableEntry
from generator.core import GroupData


def build_student_competence_levels_response(
    group_data: GroupData,
    equiv_tables: list[EquivalenceTableEntry],
) -> list[InlineObjectInner]:
    """Build per-student competence-level value groups.

    Each student becomes a value group. For each equivalence table entry,
    the student's raw score is mapped to a competence level with frequency=1
    for the matched level and 0 for all others.
    """
    student_ids = group_data.student_ids
    student_names = group_data.student_names

    results: list[InlineObjectInner] = []

    for entry in equiv_tables:
        item_cols = group_data.booklet.column_names_for_domain(entry.domain)
        raw_scores = group_data.responses.select(item_cols).sum_horizontal().to_list()

        domain_model = make_domain(entry.domain, group_data.booklet.subject)

        for i, (sid, sname) in enumerate(zip(student_ids, student_names, strict=True)):
            score_val = int(raw_scores[i])
            matched_level = entry.match_level(score_val)

            comp_levels = [
                InlineObjectInnerAllOfCompetenceLevelsInner(
                    name_short=cl.name_short,
                    name=cl.name,
                    description=cl.description,
                    frequency=1 if cl.name_short == matched_level else 0,
                )
                for cl in entry.competence_levels
            ]

            results.append(
                InlineObjectInner(
                    id=sid,
                    name=sname,
                    domain=domain_model,
                    competence_levels=comp_levels,
                )
            )

    return results


def build_student_items_response(
    group_data: GroupData,
) -> list[InlineObjectInner1]:
    """Build per-student item value groups.

    Each student gets one value group per domain, with per-item statistics
    (total=1, frequency=0/1, mean=0.0/1.0, std=0.0).
    """
    domain_items = group_data.booklet.items_by_domain()
    subject = group_data.booklet.subject

    student_ids = group_data.student_ids
    student_names = group_data.student_names

    results: list[InlineObjectInner1] = []

    for domain_name, items in domain_items.items():
        sorted_items = sorted(items, key=lambda i: i.item_order_booklet)
        item_cols = [item.column_name for item in sorted_items]

        # Pre-build item parameters (same for all students)
        item_params = [
            ItemParameters(
                logit=item.logit,
                bista_points=item.bista,
                # TBA3 spec's ItemParameters.subject maps to our domain concept
                subject=item.domain,
                domain=item.domain,
                competence_level=CompetenceLevel(name_short=item.competence_level),
            )
            for item in sorted_items
        ]

        scores_rows = group_data.responses.select(item_cols).to_dicts()

        domain_model = make_domain(domain_name, subject)

        for sid, sname, row in zip(
            student_ids, student_names, scores_rows, strict=True
        ):
            items_stats = [
                ItemStatisticsInner(
                    name=item.item_nr_booklet,
                    iqb_id=item.iqbitem_id,
                    parameters=params,
                    descriptive_statistics=DescriptiveStatistics(
                        total=1,
                        frequency=int(row[col]),
                        mean=float(row[col]),
                        standard_deviation=0.0,
                    ),
                )
                for item, col, params in zip(
                    sorted_items, item_cols, item_params, strict=True
                )
            ]

            results.append(
                InlineObjectInner1(
                    id=sid,
                    name=sname,
                    domain=domain_model,
                    items=items_stats,
                )
            )

    return results


def build_student_aggregations_response(
    group_data: GroupData,
) -> list[InlineObjectInner2]:
    """Build per-student aggregation value groups.

    Each student gets one value group per domain, with a single aggregation
    (total=n_items, frequency=sum_correct, mean=freq/total, std=0.0).
    """
    domain_items = group_data.booklet.items_by_domain()
    subject = group_data.booklet.subject

    # Pre-compute domain info and per-student domain sums
    domain_info: list[_DomainAggInfo] = []
    sum_exprs: list[pl.Expr] = []

    for domain_name, items in domain_items.items():
        cols = [item.column_name for item in items]
        iqb_ids = [item.iqbitem_id for item in items]
        sum_col = f"_sum_{domain_name or '_all'}"
        domain_info.append(_DomainAggInfo(domain_name, len(cols), iqb_ids, sum_col))
        sum_exprs.append(pl.sum_horizontal(cols).alias(sum_col))

    # Compute all domain sums in one Polars operation
    domain_sums_df = group_data.responses.select(
        pl.col("id"), pl.col("name"), *sum_exprs
    )
    rows = domain_sums_df.to_dicts()

    results: list[InlineObjectInner2] = []

    for domain_name, total, iqb_ids, sum_col in domain_info:
        domain_model = make_domain(domain_name, subject)

        for row in rows:
            frequency = int(row[sum_col])
            mean = frequency / total if total > 0 else 0.0

            aggregation = InlineObjectInner2AllOfAggregationsInner(
                type="custom",
                value=domain_name or subject,
                descriptive_statistics=DescriptiveStatistics(
                    total=total,
                    frequency=frequency,
                    mean=_safe_round(mean),
                    standard_deviation=0.0,
                ),
                included_iqb_ids=iqb_ids,
            )

            results.append(
                InlineObjectInner2(
                    id=row["id"],
                    name=row["name"],
                    domain=domain_model,
                    aggregations=[aggregation],
                )
            )

    return results
