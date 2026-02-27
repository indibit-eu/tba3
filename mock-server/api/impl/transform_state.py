"""State-level transform functions (multi-booklet data -> API response models).

Each state generates one group per booklet. Results are output as one
ValueGroup per booklet/domain, identified by booklet key.
"""

from __future__ import annotations

from api.impl.transform_group import (
    build_group_aggregations_response,
    build_group_competence_levels_response,
    build_group_items_response,
)
from api.models.aggregations_inner import AggregationsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.items_inner import ItemsInner
from generator.config import EquivalenceTableEntry
from generator.core import GroupData


def build_state_competence_levels_response(
    groups_with_equiv: list[tuple[GroupData, list[EquivalenceTableEntry]]],
) -> list[CompetenceLevelsInner]:
    """Build state-level competence-levels response.

    One ValueGroup per booklet per domain, identified by booklet key.
    """
    results: list[CompetenceLevelsInner] = []
    for group_data, equiv_tables in groups_with_equiv:
        booklet_id = str(group_data.booklet.key)
        for vg in build_group_competence_levels_response(group_data, equiv_tables):
            results.append(
                CompetenceLevelsInner(
                    id=booklet_id,
                    name=booklet_id,
                    domain=vg.domain,
                    subject=vg.subject,
                    competence_levels=vg.competence_levels,
                )
            )
    return results


def build_state_items_response(
    groups: list[GroupData],
) -> list[ItemsInner]:
    """Build state-level items response.

    One ValueGroup per booklet per domain, identified by booklet key.
    """
    results: list[ItemsInner] = []
    for group_data in groups:
        booklet_id = str(group_data.booklet.key)
        for vg in build_group_items_response(group_data):
            results.append(
                ItemsInner(
                    id=booklet_id,
                    name=booklet_id,
                    domain=vg.domain,
                    subject=vg.subject,
                    items=vg.items,
                )
            )
    return results


def build_state_aggregations_response(
    groups: list[GroupData],
) -> list[AggregationsInner]:
    """Build state-level aggregations response.

    One ValueGroup per booklet per domain, identified by booklet key.
    """
    results: list[AggregationsInner] = []
    for group_data in groups:
        booklet_id = str(group_data.booklet.key)
        for vg in build_group_aggregations_response(group_data):
            results.append(
                AggregationsInner(
                    id=booklet_id,
                    name=booklet_id,
                    domain=vg.domain,
                    subject=vg.subject,
                    aggregations=vg.aggregations,
                )
            )
    return results
