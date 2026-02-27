# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from api.apis.groups_api_base import BaseGroupsApi
import api.impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from api.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from api.models.aggregations_inner import AggregationsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.items_inner import ItemsInner


router = APIRouter()

ns_pkg = api.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/groups/{id}/competence-levels",
    responses={
        200: {"model": List[CompetenceLevelsInner], "description": "Kompetenzstufenverteilung in der Lerngruppe"},
        400: {"description": "Ungültige Anfrage, z.B. ungültige Werte für die Parameter"},
        404: {"description": "Lerngruppe oder Kompetenzstufenverteilung für die Lerngruppe nicht gefunden"},
    },
    tags=["groups"],
    summary="Kompetenzstufenverteilung in der Lerngruppe",
    response_model_by_alias=True,
)
async def get_group_competence_levels(
    id: Annotated[StrictStr, Field(description="Id der Lerngruppe")] = Path(..., description="Id der Lerngruppe"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche ausgegeben werden sollen", alias="type"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[CompetenceLevelsInner]:
    if not BaseGroupsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGroupsApi.subclasses[0]().get_group_competence_levels(id, type, comparison)


@router.get(
    "/groups/{id}/items",
    responses={
        200: {"model": List[ItemsInner], "description": "Lösungshäufigkeiten je Item in der Lerngruppe"},
        400: {"description": "Ungültige Anfrage, z.B. ungültige Werte für die Parameter"},
        404: {"description": "Lerngruppe oder Lösungshäufigkeiten für die Lerngruppe nicht gefunden"},
    },
    tags=["groups"],
    summary="Lösungshäufigkeiten je Item in der Lerngruppe",
    response_model_by_alias=True,
)
async def get_group_items(
    id: Annotated[StrictStr, Field(description="Id der Lerngruppe")] = Path(..., description="Id der Lerngruppe"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche ausgegeben werden sollen", alias="type"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[ItemsInner]:
    if not BaseGroupsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGroupsApi.subclasses[0]().get_group_items(id, type, comparison)


@router.get(
    "/groups/{id}/aggregations",
    responses={
        200: {"model": List[AggregationsInner], "description": "Abhängig vom Typ berechnete Aggregation für die Lerngruppe"},
        400: {"description": "Ungültige Anfrage, z.B. ungültige Werte für die Parameter"},
        404: {"description": "Lerngruppe oder Werte für die Lerngruppe nicht gefunden"},
    },
    tags=["groups"],
    summary="Aggregierte Werte (z.B. Lösungshäufigkeiten) in der Lerngruppe",
    response_model_by_alias=True,
)
async def get_group_aggregations(
    id: Annotated[StrictStr, Field(description="Id der Lerngruppe")] = Path(..., description="Id der Lerngruppe"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche ausgegeben werden sollen", alias="type"),
    aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")] = Query(None, description="Aggregationsarten, die berechnet werden sollen", alias="aggregation"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[AggregationsInner]:
    if not BaseGroupsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGroupsApi.subclasses[0]().get_group_aggregations(id, type, aggregation, comparison)
