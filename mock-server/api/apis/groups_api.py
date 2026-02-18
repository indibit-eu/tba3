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
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2


router = APIRouter()

ns_pkg = api.impl
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/groups/{id}/competence-levels",
    responses={
        200: {"model": List[InlineObjectInner], "description": "Kompetenzstufenverteilung im Kontext"},
        404: {"description": "Lerngruppe oder Kompetenzstufenverteilung für die Lerngruppe nicht gefunden"},
    },
    tags=["groups"],
    response_model_by_alias=True,
)
async def groups_id_competence_levels_get(
    id: Annotated[StrictStr, Field(description="Id der Lerngruppe")] = Path(..., description="Id der Lerngruppe"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen", alias="type"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[InlineObjectInner]:
    """Kompetenzstufenverteilung in der Lerngruppe"""
    if not BaseGroupsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGroupsApi.subclasses[0]().groups_id_competence_levels_get(id, type, comparison)


@router.get(
    "/groups/{id}/items",
    responses={
        200: {"model": List[InlineObjectInner1], "description": "Lösungshäufigkeiten der Items im Kontext"},
        404: {"description": "Lerngruppe oder Lösungshäufigkeiten für die Lerngruppe nicht gefunden"},
    },
    tags=["groups"],
    response_model_by_alias=True,
)
async def groups_id_items_get(
    id: Annotated[StrictStr, Field(description="Id der Lerngruppe")] = Path(..., description="Id der Lerngruppe"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen", alias="type"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[InlineObjectInner1]:
    """Lösungshäufigkeiten je Item in der Lerngruppe"""
    if not BaseGroupsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGroupsApi.subclasses[0]().groups_id_items_get(id, type, comparison)


@router.get(
    "/groups/{id}/aggregations",
    responses={
        200: {"model": List[InlineObjectInner2], "description": "Lösungshäufigkeiten der Merkmale im Kontext"},
        400: {"description": "Lerngruppe oder Lösungshäufigkeiten für die Lerngruppe nicht gefunden"},
    },
    tags=["groups"],
    response_model_by_alias=True,
)
async def groups_id_aggregations_get(
    id: Annotated[StrictStr, Field(description="Id der Lerngruppe")] = Path(..., description="Id der Lerngruppe"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen", alias="type"),
    aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")] = Query(None, description="Aggregationsarten, die berechnet werden sollen", alias="aggregation"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[InlineObjectInner2]:
    """Aggregierte Lösungshäufigkeiten in der Lerngruppe"""
    if not BaseGroupsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseGroupsApi.subclasses[0]().groups_id_aggregations_get(id, type, aggregation, comparison)
