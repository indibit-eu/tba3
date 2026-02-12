# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from api.apis.states_api_base import BaseStatesApi
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
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2


router = APIRouter()

ns_pkg = api.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/states/{id}/competence-levels",
    responses={
        200: {"model": List[InlineObjectInner], "description": "Kompetenzstufenverteilung im Kontext"},
        404: {"description": "Bundesland oder Kompetensstufenverteilung für das Bundesland nicht gefunden"},
    },
    tags=["states"],
    response_model_by_alias=True,
)
async def states_id_competence_levels_get(
    id: Annotated[StrictStr, Field(description="Id des Bundeslandes")] = Path(..., description="Id des Bundeslandes"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[InlineObjectInner]:
    """Kompetenzstufenverteilung im Bundesland"""
    if not BaseStatesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseStatesApi.subclasses[0]().states_id_competence_levels_get(id, comparison)


@router.get(
    "/states/{id}/items",
    responses={
        200: {"model": List[InlineObjectInner1], "description": "Lösungshäufigkeiten der Items im Kontext"},
        404: {"description": "Bundesland oder Lösungshäufigkeit je Item für das Bundesland nicht gefunden"},
    },
    tags=["states"],
    response_model_by_alias=True,
)
async def states_id_items_get(
    id: Annotated[StrictStr, Field(description="Id des Bundeslandes")] = Path(..., description="Id des Bundeslandes"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[InlineObjectInner1]:
    """Lösungshäufigkeiten je Item im Bundesland"""
    if not BaseStatesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseStatesApi.subclasses[0]().states_id_items_get(id, comparison)


@router.get(
    "/states/{id}/aggregations",
    responses={
        200: {"model": List[InlineObjectInner2], "description": "Lösungshäufigkeiten der Merkmale im Kontext"},
        404: {"description": "Bundesland oder Lösungshäufigkeit je Merkmal für das Bundesland nicht gefunden"},
    },
    tags=["states"],
    response_model_by_alias=True,
)
async def states_id_aggregations_get(
    id: Annotated[StrictStr, Field(description="Id des Bundeslandes")] = Path(..., description="Id des Bundeslandes"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen", alias="type"),
    aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")] = Query(None, description="Aggregationsarten, die berechnet werden sollen", alias="aggregation"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[InlineObjectInner2]:
    """Aggregierte Lösungshäufigkeiten im Bundesland"""
    if not BaseStatesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseStatesApi.subclasses[0]().states_id_aggregations_get(id, type, aggregation, comparison)
