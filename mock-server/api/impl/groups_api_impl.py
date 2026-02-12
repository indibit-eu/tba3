"""Implementation of Groups API endpoints."""

from fastapi import HTTPException
from pydantic import StrictStr

from api.apis.groups_api_base import BaseGroupsApi
from api.impl.shared import resolve_group, resolve_requested_types
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
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2


class GroupsApiImpl(BaseGroupsApi):  # type: ignore[no-untyped-call]
    """Implementation of the Groups API endpoints."""

    async def groups_id_competence_levels_get(
        self,
        id: StrictStr,
        type: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner]:
        group_data, equiv_tables = resolve_group(id)
        if not equiv_tables:
            raise HTTPException(
                status_code=404,
                detail=f"No equivalence tables found for group: {id}",
            )

        include_group, include_students = resolve_requested_types(type)

        result: list[InlineObjectInner] = []
        if include_group:
            result.extend(
                build_group_competence_levels_response(group_data, equiv_tables)
            )
        if include_students:
            result.extend(
                build_student_competence_levels_response(
                    group_data, equiv_tables
                )
            )
        return result

    async def groups_id_items_get(
        self,
        id: StrictStr,
        type: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner1]:
        group_data, _ = resolve_group(id)

        include_group, include_students = resolve_requested_types(type)

        result: list[InlineObjectInner1] = []
        if include_group:
            result.extend(build_group_items_response(group_data))
        if include_students:
            result.extend(build_student_items_response(group_data))
        return result

    async def groups_id_aggregations_get(
        self,
        id: StrictStr,
        type: StrictStr | None,
        aggregation: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner2]:
        group_data, _ = resolve_group(id)

        include_group, include_students = resolve_requested_types(type)

        result: list[InlineObjectInner2] = []
        if include_group:
            result.extend(build_group_aggregations_response(group_data))
        if include_students:
            result.extend(build_student_aggregations_response(group_data))
        return result
