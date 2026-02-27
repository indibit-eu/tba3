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
from api.models.aggregations_inner import AggregationsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.items_inner import ItemsInner


class StatesApiImpl(BaseStatesApi):  # type: ignore[no-untyped-call]
    """Implementation of the States API endpoints."""

    async def get_state_competence_levels(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[CompetenceLevelsInner]:
        groups_with_equiv = resolve_state(id)

        if not any(eq for _, eq in groups_with_equiv):
            raise HTTPException(
                status_code=404,
                detail=f"No equivalence tables found for state: {id}",
            )

        return build_state_competence_levels_response(groups_with_equiv)

    async def get_state_items(
        self,
        id: StrictStr,
        comparison: StrictStr | None,
    ) -> list[ItemsInner]:
        groups_with_equiv = resolve_state(id)
        groups = [gd for gd, _ in groups_with_equiv]
        return build_state_items_response(groups)

    async def get_state_aggregations(
        self,
        id: StrictStr,
        type: StrictStr | None,
        aggregation: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[AggregationsInner]:
        groups_with_equiv = resolve_state(id)
        groups = [gd for gd, _ in groups_with_equiv]
        return build_state_aggregations_response(groups)
