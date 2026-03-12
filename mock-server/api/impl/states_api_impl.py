"""Implementation of States API endpoints."""

from fastapi import HTTPException
from pydantic import StrictStr

from api.apis.states_api_base import BaseStatesApi
from api.impl.shared import (
    parse_aggregation_param,
    parse_comparison_param,
    resolve_district,
    resolve_state,
    resolve_state_requested_types,
    state_lookup,
)
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
        type: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[CompetenceLevelsInner]:
        include_state, include_district = resolve_state_requested_types(type)
        ids = parse_comparison_param(id, comparison)
        result: list[CompetenceLevelsInner] = []

        for sid in ids:
            state_cfg = state_lookup.get(sid)
            if state_cfg is None:
                raise HTTPException(
                    status_code=404, detail=f"State not found: {sid}"
                )

            if include_state:
                groups_with_equiv = resolve_state(sid)
                if not any(eq for _, eq in groups_with_equiv):
                    raise HTTPException(
                        status_code=404,
                        detail=f"No equivalence tables found for state: {sid}",
                    )
                result.extend(
                    build_state_competence_levels_response(groups_with_equiv)
                )

            if include_district:
                for district in state_cfg.districts or []:
                    district_groups = resolve_district(state_cfg, district)
                    if any(eq for _, eq in district_groups):
                        result.extend(
                            build_state_competence_levels_response(
                                district_groups,
                                id=district.id,
                                name=district.display_name(),
                            )
                        )

        return result

    async def get_state_items(
        self,
        id: StrictStr,
        type: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[ItemsInner]:
        include_state, include_district = resolve_state_requested_types(type)
        ids = parse_comparison_param(id, comparison)
        result: list[ItemsInner] = []

        for sid in ids:
            state_cfg = state_lookup.get(sid)
            if state_cfg is None:
                raise HTTPException(
                    status_code=404, detail=f"State not found: {sid}"
                )

            if include_state:
                groups_with_equiv = resolve_state(sid)
                groups = [gd for gd, _ in groups_with_equiv]
                result.extend(build_state_items_response(groups))

            if include_district:
                for district in state_cfg.districts or []:
                    district_groups = resolve_district(state_cfg, district)
                    groups = [gd for gd, _ in district_groups]
                    result.extend(
                        build_state_items_response(
                            groups,
                            id=district.id,
                            name=district.display_name(),
                        )
                    )

        return result

    async def get_state_aggregations(
        self,
        id: StrictStr,
        type: StrictStr | None,
        aggregation: StrictStr | None,
        comparison: StrictStr | None,
    ) -> list[AggregationsInner]:
        aggregation_types = parse_aggregation_param(aggregation)
        include_state, include_district = resolve_state_requested_types(type)
        ids = parse_comparison_param(id, comparison)
        result: list[AggregationsInner] = []

        for sid in ids:
            state_cfg = state_lookup.get(sid)
            if state_cfg is None:
                raise HTTPException(
                    status_code=404, detail=f"State not found: {sid}"
                )

            if include_state:
                groups_with_equiv = resolve_state(sid)
                groups = [gd for gd, _ in groups_with_equiv]
                result.extend(
                    build_state_aggregations_response(groups, aggregation_types)
                )

            if include_district:
                for district in state_cfg.districts or []:
                    district_groups = resolve_district(state_cfg, district)
                    groups = [gd for gd, _ in district_groups]
                    result.extend(
                        build_state_aggregations_response(
                            groups,
                            aggregation_types,
                            id=district.id,
                            name=district.display_name(),
                        )
                    )

        return result
