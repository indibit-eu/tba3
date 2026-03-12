"""School-level transform functions (multi-group data -> API response models)."""

from __future__ import annotations

import polars as pl

from api.impl.transform_group import build_group_competence_levels_response
from api.impl.transform_helpers import (
    _safe_round,
    build_competence_aggregations,
    build_domain,
    build_gender_aggregations,
    build_single_item_stats,
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
from api.models.items_inner import ItemsInner
from generator.booklets import BookletKey, DomainKey
from generator.config import EquivalenceTableEntry
from generator.core import GroupData


def build_school_competence_levels_response(
    school_id: str,
    school_name: str,
    groups_with_equiv: list[tuple[GroupData, list[EquivalenceTableEntry]]],
) -> list[CompetenceLevelsInner]:
    """Build school-level competence-levels response.

    Calls per-group competence level computation, then merges results
    by domain: frequencies per level are summed across all groups.
    """
    # Collect per-group results and map group_id -> subject
    all_results: list[CompetenceLevelsInner] = []
    group_subject = {gd.group_id: gd.booklet.subject for gd, _ in groups_with_equiv}
    for group_data, equiv_tables in groups_with_equiv:
        all_results.extend(
            build_group_competence_levels_response(group_data, equiv_tables)
        )

    # Group by (subject, domain) to keep domains from different subjects separate
    by_key: dict[DomainKey, list[CompetenceLevelsInner]] = {}
    for result in all_results:
        assert result.id is not None
        subject = group_subject[result.id]
        dk = DomainKey(
            subject=subject,
            domain=result.domain.name if result.domain else None,
        )
        by_key.setdefault(dk, []).append(result)

    # Merge each (subject, domain) group
    merged: list[CompetenceLevelsInner] = []
    for key, entries in by_key.items():
        # Sum frequencies per level, preserve order from first entry
        level_freq: dict[str, int] = {}
        level_meta: dict[str, tuple[str | None, str | None]] = {}
        for entry in entries:
            for cl in entry.competence_levels:
                level_freq[cl.name_short] = (
                    level_freq.get(cl.name_short, 0)
                    + cl.descriptive_statistics.frequency
                )
                if cl.name_short not in level_meta:
                    level_meta[cl.name_short] = (cl.name, cl.description)

        total_students = sum(level_freq.values())

        comp_levels = [
            CompetenceLevelStatisticsInner(
                name_short=cl.name_short,
                name=level_meta.get(cl.name_short, (None, None))[0],
                description=level_meta.get(cl.name_short, (None, None))[1],
                descriptive_statistics=CompetenceLevelDescriptiveStatisticsDescriptiveStatistics(
                    total=total_students,
                    mean=(
                        _safe_round(level_freq.get(cl.name_short, 0) / total_students)
                        if total_students > 0
                        else 0.0
                    ),
                    frequency=level_freq.get(cl.name_short, 0),
                ),
            )
            for cl in entries[0].competence_levels
        ]

        merged.append(
            CompetenceLevelsInner(
                id=school_id,
                name=school_name,
                domain=entries[0].domain,
                subject=build_subject(key.subject),
                competence_levels=comp_levels,
            )
        )

    return merged


def build_school_items_response(
    school_id: str,
    school_name: str,
    groups: list[GroupData],
) -> list[ItemsInner]:
    """Build school-level items response.

    Groups are grouped by booklet, then by domain. For each
    booklet+domain combination, response DataFrames are concatenated
    and item statistics computed across all students. Returns one
    value group per booklet per domain.
    """
    by_booklet: dict[BookletKey, list[GroupData]] = {}
    for gd in groups:
        by_booklet.setdefault(gd.booklet.key, []).append(gd)

    results: list[ItemsInner] = []
    for _booklet_key, booklet_groups in by_booklet.items():
        booklet = booklet_groups[0].booklet
        subject = booklet.subject

        # Merge all group responses for this booklet
        all_item_cols = [item.column_name for item in booklet.items]
        merged_responses = pl.concat(
            [gd.responses.select(all_item_cols) for gd in booklet_groups]
        )

        domain_items = booklet.items_by_domain()

        for domain_name, items in domain_items.items():
            sorted_items = sorted(items, key=lambda i: i.item_order_booklet)

            items_stats = [
                build_single_item_stats(item, merged_responses) for item in sorted_items
            ]

            results.append(
                ItemsInner(
                    id=school_id,
                    name=school_name,
                    domain=build_domain(domain_name),
                    subject=build_subject(subject),
                    items=items_stats,
                )
            )

    return results


def build_school_aggregations_response(
    school_id: str,
    school_name: str,
    groups: list[GroupData],
    aggregation_types: set[str],
) -> list[AggregationsInner]:
    """Build school-level aggregations response.

    Groups are grouped by booklet, responses merged across groups,
    then competence/gender aggregations computed per domain.
    """
    by_booklet: dict[BookletKey, list[GroupData]] = {}
    for gd in groups:
        by_booklet.setdefault(gd.booklet.key, []).append(gd)

    results: list[AggregationsInner] = []

    for _booklet_key, booklet_groups in by_booklet.items():
        booklet = booklet_groups[0].booklet
        subject = booklet.subject

        # Merge responses from all groups for this booklet
        all_item_cols = [item.column_name for item in booklet.items]
        select_cols = all_item_cols.copy()
        has_gender = "gender" in booklet_groups[0].responses.columns
        if "gender" in aggregation_types and has_gender:
            select_cols = ["gender"] + select_cols
        merged_responses = pl.concat(
            [gd.responses.select(select_cols) for gd in booklet_groups]
        )

        domain_items = booklet.items_by_domain()

        for domain_name, items in domain_items.items():
            aggregations: list[AggregationsInnerAllOfAggregationsInner] = []

            if "competence" in aggregation_types:
                aggregations.extend(
                    build_competence_aggregations(items, merged_responses)
                )
            if "gender" in aggregation_types:
                aggregations.extend(build_gender_aggregations(items, merged_responses))

            if aggregations:
                results.append(
                    AggregationsInner(
                        id=school_id,
                        name=school_name,
                        domain=build_domain(domain_name),
                        subject=build_subject(subject),
                        aggregations=aggregations,
                    )
                )

    return results
