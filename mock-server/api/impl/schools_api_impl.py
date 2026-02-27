"""Implementation of Schools API endpoints."""

from fastapi import HTTPException
from pydantic import StrictStr

from api.apis.schools_api_base import BaseSchoolsApi
from api.impl.shared import resolve_requested_types, resolve_school, school_lookup
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
from api.impl.transform_student import build_student_aggregations_response
from api.models.aggregations_inner import AggregationsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.items_inner import ItemsInner


class SchoolsApiImpl(BaseSchoolsApi):  # type: ignore[no-untyped-call]
    """Implementation of the Schools API endpoints."""

    async def get_school_competence_levels(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[CompetenceLevelsInner]:
        groups_with_equiv = resolve_school(id)

        # Check that at least one group has equivalence tables
        if not any(eq for _, eq in groups_with_equiv):
            raise HTTPException(
                status_code=404,
                detail=f"No equivalence tables found for school: {id}",
            )

        school_cfg = school_lookup[id]
        result: list[CompetenceLevelsInner] = []

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

    async def get_school_items(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[ItemsInner]:
        groups_with_equiv = resolve_school(id)
        school_cfg = school_lookup[id]
        groups = [gd for gd, _ in groups_with_equiv]
        result: list[ItemsInner] = []

        # School-level aggregated (per booklet)
        result.extend(
            build_school_items_response(id, school_cfg.display_name(), groups)
        )

        # Per-group
        for group_data in groups:
            result.extend(build_group_items_response(group_data))

        return result

    async def get_school_aggregations(
        self,
        id: StrictStr,
        type: StrictStr | None,
        aggregation: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[AggregationsInner]:
        groups_with_equiv = resolve_school(id)
        school_cfg = school_lookup[id]
        groups = [gd for gd, _ in groups_with_equiv]
        include_group, include_students = resolve_requested_types(type)
        result: list[AggregationsInner] = []

        if include_group:
            # School-level aggregated
            result.extend(
                build_school_aggregations_response(
                    id, school_cfg.display_name(), groups
                )
            )

            # Per-group
            for group_data in groups:
                result.extend(build_group_aggregations_response(group_data))

        if include_students:
            for group_data in groups:
                student_vgs = build_student_aggregations_response(group_data)
                group_cov = {"type": "group", "value": group_data.profile.name}
                for vg in student_vgs:
                    vg.__dict__["covariates"].append(group_cov)
                result.extend(student_vgs)

        return result
