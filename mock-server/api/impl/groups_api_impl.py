"""Implementation of Groups API endpoints."""

from fastapi import HTTPException
from pydantic import StrictStr

from api.apis.groups_api_base import BaseGroupsApi
from api.impl.shared import (
    parse_aggregation_param,
    parse_comparison_param,
    resolve_group,
    resolve_requested_types,
    validate_student_aggregation_types,
)
from api.impl.transform_group import (
    build_group_aggregations_response,
    build_group_competence_levels_response,
    build_group_items_response,
)
from api.impl.transform_student import (
    build_student_aggregations_response,
    build_student_competence_levels_response,
    build_student_items_response,
)
from api.models.aggregations_inner import AggregationsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.items_inner import ItemsInner


class GroupsApiImpl(BaseGroupsApi):  # type: ignore[no-untyped-call]
    """Implementation of the Groups API endpoints."""

    async def get_group_competence_levels(
        self,
        id: StrictStr,
        type: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[CompetenceLevelsInner]:
        include_group, include_students = resolve_requested_types(type)
        ids = parse_comparison_param(id, comparison)

        result: list[CompetenceLevelsInner] = []
        for gid in ids:
            group_data, equiv_tables = resolve_group(gid)
            if not equiv_tables:
                raise HTTPException(
                    status_code=404,
                    detail=f"No equivalence tables found for group: {gid}",
                )
            if include_group:
                result.extend(
                    build_group_competence_levels_response(group_data, equiv_tables)
                )
            if include_students:
                result.extend(
                    build_student_competence_levels_response(group_data, equiv_tables)
                )
        return result

    async def get_group_items(
        self,
        id: StrictStr,
        type: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[ItemsInner]:
        include_group, include_students = resolve_requested_types(type)
        ids = parse_comparison_param(id, comparison)

        result: list[ItemsInner] = []
        for gid in ids:
            group_data, _ = resolve_group(gid)
            if include_group:
                result.extend(build_group_items_response(group_data))
            if include_students:
                result.extend(build_student_items_response(group_data))
        return result

    async def get_group_aggregations(
        self,
        id: StrictStr,
        type: StrictStr | None,
        aggregation: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[AggregationsInner]:
        aggregation_types = parse_aggregation_param(aggregation)
        include_group, include_students = resolve_requested_types(type)
        if include_students:
            validate_student_aggregation_types(aggregation_types)
        ids = parse_comparison_param(id, comparison)

        result: list[AggregationsInner] = []
        for gid in ids:
            group_data, _ = resolve_group(gid)
            if include_group:
                result.extend(
                    build_group_aggregations_response(group_data, aggregation_types)
                )
            if include_students:
                result.extend(
                    build_student_aggregations_response(group_data, aggregation_types)
                )
        return result
