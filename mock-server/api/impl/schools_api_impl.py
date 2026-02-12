"""Implementation of Schools API endpoints."""

from fastapi import HTTPException
from pydantic import StrictStr

from api.apis.schools_api_base import BaseSchoolsApi
from api.impl.shared import resolve_school, school_lookup
from api.impl.transform_group import (
    build_group_aggregations_response,
    build_group_competence_levels_response,
    build_group_items_response,
)
from api.impl.transform_school import (
    build_school_aggregations_response,
    build_school_competence_levels_response,
    build_school_items_response,
)
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2


class SchoolsApiImpl(BaseSchoolsApi):  # type: ignore[no-untyped-call]
    """Implementation of the Schools API endpoints."""

    async def schools_id_competence_levels_get(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner]:
        groups_with_equiv = resolve_school(id)

        # Check that at least one group has equivalence tables
        if not any(eq for _, eq in groups_with_equiv):
            raise HTTPException(
                status_code=404,
                detail=f"No equivalence tables found for school: {id}",
            )

        school_cfg = school_lookup[id]
        result: list[InlineObjectInner] = []

        # School-level aggregated
        result.extend(
            build_school_competence_levels_response(
                id, school_cfg.display_name(), groups_with_equiv
            )
        )

        # Per-group
        for group_data, equiv_tables in groups_with_equiv:
            result.extend(
                build_group_competence_levels_response(group_data, equiv_tables)
            )

        return result

    async def schools_id_items_get(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner1]:
        groups_with_equiv = resolve_school(id)
        school_cfg = school_lookup[id]
        groups = [gd for gd, _ in groups_with_equiv]
        result: list[InlineObjectInner1] = []

        # School-level aggregated (per booklet)
        result.extend(
            build_school_items_response(id, school_cfg.display_name(), groups)
        )

        # Per-group
        for group_data in groups:
            result.extend(build_group_items_response(group_data))

        return result

    async def schools_id_aggregations_get(
        self,
        id: StrictStr,
        type: StrictStr | None,
        aggregation: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner2]:
        groups_with_equiv = resolve_school(id)
        school_cfg = school_lookup[id]
        groups = [gd for gd, _ in groups_with_equiv]
        result: list[InlineObjectInner2] = []

        # School-level aggregated
        result.extend(
            build_school_aggregations_response(
                id, school_cfg.display_name(), groups
            )
        )

        # Per-group
        for group_data in groups:
            result.extend(build_group_aggregations_response(group_data))

        return result
