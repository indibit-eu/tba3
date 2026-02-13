"""Implementation of States API endpoints."""

from fastapi import HTTPException
from pydantic import StrictStr

from api.apis.states_api_base import BaseStatesApi
from api.impl.shared import resolve_state
from api.impl.transform_state import (
    build_state_aggregations_response,
    build_state_competence_levels_response,
    build_state_items_response,
)
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2


class StatesApiImpl(BaseStatesApi):  # type: ignore[no-untyped-call]
    """Implementation of the States API endpoints."""

    async def states_id_competence_levels_get(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner]:
        groups_with_equiv = resolve_state(id)

        if not any(eq for _, eq in groups_with_equiv):
            raise HTTPException(
                status_code=404,
                detail=f"No equivalence tables found for state: {id}",
            )

        return build_state_competence_levels_response(groups_with_equiv)

    async def states_id_items_get(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner1]:
        groups_with_equiv = resolve_state(id)
        groups = [gd for gd, _ in groups_with_equiv]
        return build_state_items_response(groups)

    async def states_id_aggregations_get(
        self,
        id: StrictStr,
        type: StrictStr | None,
        aggregation: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[InlineObjectInner2]:
        groups_with_equiv = resolve_state(id)
        groups = [gd for gd, _ in groups_with_equiv]
        return build_state_aggregations_response(groups)
