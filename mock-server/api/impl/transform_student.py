"""Student-level transform functions (GroupData -> per-student API models)."""

from __future__ import annotations

import polars as pl

from api.impl.transform_helpers import (
    _safe_round,
    build_competence_groups,
    build_domain,
    build_item_parameters,
    build_student_covariates,
    build_subject,
)
from api.models.aggregations_inner import AggregationsInner
from api.models.aggregations_inner_all_of_aggregations_inner import (
    AggregationsInnerAllOfAggregationsInner,
)
from api.models.competence_level_descriptive_statistics_descriptive_statistics import (
    CompetenceLevelDescriptiveStatisticsDescriptiveStatistics,
)
from api.models.competence_level_statistics_inner import CompetenceLevelStatisticsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.descriptive_statistics_descriptive_statistics import (
    DescriptiveStatisticsDescriptiveStatistics,
)
from api.models.exercise import Exercise
from api.models.item_statistics_inner import ItemStatisticsInner
from api.models.items_inner import ItemsInner
from generator.config import EquivalenceTableEntry
from generator.core import GroupData


def build_student_competence_levels_response(
    group_data: GroupData,
    equiv_tables: list[EquivalenceTableEntry],
) -> list[CompetenceLevelsInner]:
    """Build per-student competence-level value groups.

    Each student becomes a value group. For each equivalence table entry,
    the student's raw score is mapped to a competence level with frequency=1
    for the matched level and 0 for all others.
    """
    cov_cols = group_data.covariate_columns
    student_rows = group_data.responses.select("id", "name", *cov_cols).to_dicts()

    results: list[CompetenceLevelsInner] = []

    for entry in equiv_tables:
        item_cols = group_data.booklet.column_names_for_domain(entry.domain)
        raw_scores = group_data.responses.select(item_cols).sum_horizontal().to_list()

        domain_model = build_domain(entry.domain)
        subject_model = build_subject(group_data.booklet.subject)

        for i, row in enumerate(student_rows):
            score_val = int(raw_scores[i])
            matched_level = entry.match_level(score_val)

            comp_levels = [
                CompetenceLevelStatisticsInner(
                    name_short=cl.name_short,
                    name=cl.name,
                    description=cl.description,
                    descriptive_statistics=CompetenceLevelDescriptiveStatisticsDescriptiveStatistics(
                        total=1,
                        mean=1.0 if cl.name_short == matched_level else 0.0,
                        frequency=1 if cl.name_short == matched_level else 0,
                    ),
                )
                for cl in entry.competence_levels
                if cl.name_short == matched_level
            ]

            vg = CompetenceLevelsInner(
                id=row["id"],
                name=row["name"],
                domain=domain_model,
                subject=subject_model,
                competence_levels=comp_levels,
            )
            vg.__dict__["covariates"] = build_student_covariates(row, cov_cols)
            results.append(vg)

    return results


def build_student_items_response(
    group_data: GroupData,
) -> list[ItemsInner]:
    """Build per-student item value groups.

    Each student gets one value group per domain, with per-item statistics
    (total=1, frequency=0/1, mean=0.0/1.0, std=0.0).
    """
    domain_items = group_data.booklet.items_by_domain()
    subject = group_data.booklet.subject

    cov_cols = group_data.covariate_columns
    student_rows = group_data.responses.select("id", "name", *cov_cols).to_dicts()

    results: list[ItemsInner] = []

    for domain_name, items in domain_items.items():
        sorted_items = sorted(items, key=lambda i: i.item_order_booklet)
        item_cols = [item.column_name for item in sorted_items]

        # Pre-build item parameters (same for all students)
        item_params = [build_item_parameters(item) for item in sorted_items]

        scores_rows = group_data.responses.select(item_cols).to_dicts()

        domain_model = build_domain(domain_name)
        subject_model = build_subject(subject)

        for student_row, scores_row in zip(student_rows, scores_rows, strict=True):
            items_stats = [
                ItemStatisticsInner(
                    name=item.item_nr_booklet,
                    iqb_id=item.iqbitem_id,
                    exercise=Exercise(name=item.name),
                    position=int(item.item_order_booklet),  # TODO: use counted position
                    parameters=params,
                    descriptive_statistics=DescriptiveStatisticsDescriptiveStatistics(
                        total=1,
                        frequency=int(scores_row[col]),
                        mean=float(scores_row[col]),
                        standard_deviation=0.0,
                    ),
                )
                for item, col, params in zip(
                    sorted_items, item_cols, item_params, strict=True
                )
            ]

            vg = ItemsInner(
                id=student_row["id"],
                name=student_row["name"],
                domain=domain_model,
                subject=subject_model,
                items=items_stats,
            )
            vg.__dict__["covariates"] = build_student_covariates(student_row, cov_cols)
            results.append(vg)

    return results


def build_student_aggregations_response(
    group_data: GroupData,
    aggregation_types: set[str],
) -> list[AggregationsInner]:
    """Build per-student aggregation value groups.

    Each student gets one value group per domain, containing competence
    aggregations. Gender aggregation is not supported at student level
    and must be rejected by the caller before invoking this function.
    """
    domain_items = group_data.booklet.items_by_domain()
    subject = group_data.booklet.subject
    cov_cols = group_data.covariate_columns

    # Pre-compute competence groups per domain
    domain_comp_groups: list[
        tuple[
            str | None,
            list[tuple[tuple[str, str], list[str], list[str]]],
        ]
    ] = []
    sum_exprs: list[pl.Expr] = []
    sum_col_map: dict[str, tuple[str, str, int, list[str]]] = {}

    for domain_name, items in domain_items.items():
        comp_groups = build_competence_groups(items)
        group_info: list[tuple[tuple[str, str], list[str], list[str]]] = []

        for key, group_items in sorted(comp_groups.items()):
            item_cols = [item.column_name for item in group_items]
            iqb_ids = sorted({item.iqbitem_id for item in group_items})
            group_info.append((key, item_cols, iqb_ids))

            # Create a sum expression for efficient per-student computation
            sum_col = f"_sum_{domain_name or '_all'}_{key[0]}_{key[1]}"
            sum_exprs.append(pl.sum_horizontal(item_cols).alias(sum_col))
            sum_col_map[sum_col] = (key[0], key[1], len(item_cols), iqb_ids)

        domain_comp_groups.append((domain_name, group_info))

    if not sum_exprs:
        return []

    # Compute all sums in one Polars operation
    computed_df = group_data.responses.select(
        pl.col("id"), pl.col("name"), *[pl.col(c) for c in cov_cols], *sum_exprs
    )
    rows = computed_df.to_dicts()

    results: list[AggregationsInner] = []

    for domain_name, group_info in domain_comp_groups:
        if not group_info:
            continue

        domain_model = build_domain(domain_name)
        subject_model = build_subject(subject)

        for row in rows:
            aggregations: list[AggregationsInnerAllOfAggregationsInner] = []

            for key, _item_cols, iqb_ids in group_info:
                sum_col = f"_sum_{domain_name or '_all'}_{key[0]}_{key[1]}"
                total = sum_col_map[sum_col][2]
                frequency = int(row[sum_col])
                mean = frequency / total if total > 0 else 0.0

                aggregations.append(
                    AggregationsInnerAllOfAggregationsInner(
                        type=key[0],
                        value=key[1],
                        descriptive_statistics=DescriptiveStatisticsDescriptiveStatistics(
                            total=total,
                            frequency=frequency,
                            mean=_safe_round(mean),
                            standard_deviation=0.0,
                        ),
                        included_iqb_ids=iqb_ids,
                    )
                )

            if aggregations:
                vg = AggregationsInner(
                    id=row["id"],
                    name=row["name"],
                    domain=domain_model,
                    subject=subject_model,
                    aggregations=aggregations,
                )
                vg.__dict__["covariates"] = build_student_covariates(row, cov_cols)
                results.append(vg)

    return results
