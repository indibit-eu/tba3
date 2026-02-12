"""Group-level transform functions (GroupData -> API response models)."""

from __future__ import annotations

from api.impl.transform_helpers import (
    _safe_round,
    build_single_item_stats,
    make_domain,
)
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
from generator.config import EquivalenceTableEntry
from generator.core import GroupData


def build_group_items_response(group_data: GroupData) -> list[InlineObjectInner1]:
    """Build items endpoint response.

    Returns one value group per domain, each containing per-item
    statistics for that domain's items.
    """
    domain_items = group_data.booklet.items_by_domain()
    subject = group_data.booklet.subject

    results: list[InlineObjectInner1] = []
    for domain_name, items in domain_items.items():
        sorted_items = sorted(items, key=lambda i: i.item_order_booklet)

        items_stats = [
            build_single_item_stats(item, group_data.responses)
            for item in sorted_items
        ]

        results.append(
            InlineObjectInner1(
                id=group_data.group_id,
                name=f"Lerngruppe {group_data.group_id}",
                domain=make_domain(domain_name, subject),
                items=items_stats,
            )
        )

    return results


def build_group_aggregations_response(
    group_data: GroupData,
) -> list[InlineObjectInner2]:
    """Build aggregations endpoint response.

    Returns one value group per domain, each containing a single
    aggregation with statistics for that domain's items.
    """
    domain_items = group_data.booklet.items_by_domain()
    subject = group_data.booklet.subject

    results: list[InlineObjectInner2] = []

    for domain_name, items in domain_items.items():
        item_cols = [item.column_name for item in items]
        iqb_ids = [item.iqbitem_id for item in items]

        # Per-student mean score across domain items, then aggregate
        domain_df = group_data.responses.select(item_cols)
        student_means = domain_df.mean_horizontal()
        frequency = int(domain_df.sum_horizontal().sum())

        aggregation = InlineObjectInner2AllOfAggregationsInner(
            type="custom",
            value=domain_name or subject,
            descriptive_statistics=DescriptiveStatistics(
                total=len(item_cols),
                mean=_safe_round(student_means.mean()),
                frequency=frequency,
                standard_deviation=_safe_round(student_means.std()),
            ),
            included_iqb_ids=iqb_ids,
        )

        results.append(
            InlineObjectInner2(
                id=group_data.group_id,
                name=f"Lerngruppe {group_data.group_id}",
                domain=make_domain(domain_name, subject),
                aggregations=[aggregation],
            )
        )

    return results


def build_group_competence_levels_response(
    group_data: GroupData,
    equiv_tables: list[EquivalenceTableEntry],
) -> list[InlineObjectInner]:
    """Build competence-levels endpoint response.

    For each equivalence table entry (one per domain, or one for the
    whole booklet), compute the raw score per student and assign each
    student to a competence level. Returns one InlineObjectInner per entry.

    Args:
        group_data: Generated group data with responses.
        equiv_tables: Equivalence tables for this booklet (one per domain
            or one without domain for the whole booklet).

    Returns:
        List of InlineObjectInner, one per equivalence table entry.
    """
    results: list[InlineObjectInner] = []

    for entry in equiv_tables:
        item_cols = group_data.booklet.column_names_for_domain(entry.domain)

        # Compute raw score per student (sum of binary responses)
        raw_scores = group_data.responses.select(item_cols).sum_horizontal().to_list()

        # Count students per competence level
        level_counts: dict[str, int] = {
            cl.name_short: 0 for cl in entry.competence_levels
        }
        for score in raw_scores:
            matched = entry.match_level(int(score))
            if matched is not None:
                level_counts[matched] += 1

        # Build response
        comp_levels = [
            InlineObjectInnerAllOfCompetenceLevelsInner(
                name_short=cl.name_short,
                name=cl.name,
                description=cl.description,
                frequency=level_counts[cl.name_short],
            )
            for cl in entry.competence_levels
        ]

        results.append(
            InlineObjectInner(
                id=group_data.group_id,
                name=group_data.profile.name,
                domain=make_domain(entry.domain, group_data.booklet.subject),
                competence_levels=comp_levels,
            )
        )

    return results
