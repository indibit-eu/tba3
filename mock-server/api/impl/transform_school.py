"""School-level transform functions (multi-group data -> API response models)."""

from __future__ import annotations

import polars as pl

from api.impl.transform_group import build_group_competence_levels_response
from api.impl.transform_helpers import (
    _safe_round,
    build_domain,
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
from api.models.descriptive_statistics_descriptive_statistics import (
    DescriptiveStatisticsDescriptiveStatistics,
)
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
                domain=build_domain(entries[0].domain),
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
) -> list[AggregationsInner]:
    """Build school-level aggregations response.

    For each domain across all groups, per-student means are computed
    and aggregated. Returns one value group per domain.
    """
    student_means: dict[DomainKey, list[float]] = {}
    frequencies: dict[DomainKey, int] = {}
    iqb_ids: dict[DomainKey, set[str]] = {}

    for gd in groups:
        items_by_domain = gd.booklet.items_by_domain()

        for domain_name, items in items_by_domain.items():
            key = DomainKey(subject=gd.booklet.subject, domain=domain_name)
            item_cols = [item.column_name for item in items]

            domain_df = gd.responses.select(item_cols)
            means = domain_df.mean_horizontal().to_list()

            student_means.setdefault(key, []).extend(means)

            total_correct_row = domain_df.select(pl.all().sum()).row(0)
            frequencies[key] = frequencies.get(key, 0) + sum(total_correct_row)

            iqb_ids.setdefault(key, set()).update(item.iqbitem_id for item in items)

    # Build school-level value groups (one per subject+domain)
    results: list[AggregationsInner] = []
    for key, means in student_means.items():
        means_series = pl.Series("m", means)
        mean_val = means_series.mean()
        std_val = means_series.std()

        aggregation = AggregationsInnerAllOfAggregationsInner(
            type="custom",
            value=key.domain or key.subject,
            descriptive_statistics=DescriptiveStatisticsDescriptiveStatistics(
                total=len(iqb_ids.get(key, set())),
                frequency=int(frequencies.get(key, 0)),
                mean=_safe_round(mean_val),
                standard_deviation=_safe_round(std_val),
            ),
            included_iqb_ids=sorted(iqb_ids.get(key, set())),
        )

        results.append(
            AggregationsInner(
                id=school_id,
                name=school_name,
                domain=build_domain(key.domain),
                subject=build_subject(key.subject),
                aggregations=[aggregation],
            )
        )

    return results
