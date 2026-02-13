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
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2
from generator.config import EquivalenceTableEntry
from generator.core import GroupData


def build_state_competence_levels_response(
    groups_with_equiv: list[tuple[GroupData, list[EquivalenceTableEntry]]],
) -> list[InlineObjectInner]:
    """Build state-level competence-levels response.

    One ValueGroup per booklet per domain, identified by booklet key.
    """
    results: list[InlineObjectInner] = []
    for group_data, equiv_tables in groups_with_equiv:
        booklet_id = str(group_data.booklet.key)
        for vg in build_group_competence_levels_response(group_data, equiv_tables):
            results.append(
                InlineObjectInner(
                    id=booklet_id,
                    name=booklet_id,
                    domain=vg.domain,
                    competence_levels=vg.competence_levels,
                )
            )
    return results


def build_state_items_response(
    groups: list[GroupData],
) -> list[InlineObjectInner1]:
    """Build state-level items response.

    One ValueGroup per booklet per domain, identified by booklet key.
    """
    results: list[InlineObjectInner1] = []
    for group_data in groups:
        booklet_id = str(group_data.booklet.key)
        for vg in build_group_items_response(group_data):
            results.append(
                InlineObjectInner1(
                    id=booklet_id,
                    name=booklet_id,
                    domain=vg.domain,
                    items=vg.items,
                )
            )
    return results


def build_state_aggregations_response(
    groups: list[GroupData],
) -> list[InlineObjectInner2]:
    """Build state-level aggregations response.

    One ValueGroup per booklet per domain, identified by booklet key.
    """
    results: list[InlineObjectInner2] = []
    for group_data in groups:
        booklet_id = str(group_data.booklet.key)
        for vg in build_group_aggregations_response(group_data):
            results.append(
                InlineObjectInner2(
                    id=booklet_id,
                    name=booklet_id,
                    domain=vg.domain,
                    aggregations=vg.aggregations,
                )
            )
    return results
