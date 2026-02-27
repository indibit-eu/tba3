# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from api.apis.schools_api_base import BaseSchoolsApi
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
    "/schools/{id}/competence-levels",
    responses={
        200: {"model": List[CompetenceLevelsInner], "description": "Kompetenzstufenverteilung an der Schule"},
        400: {"description": "Ungültige Anfrage, z.B. ungültige Werte für die Parameter"},
        404: {"description": "Schule oder Kompetensstufenverteilung für die Schule nicht gefunden"},
    },
    tags=["schools"],
    summary="Kompetenzstufenverteilung an der Schule",
    response_model_by_alias=True,
)
async def get_school_competence_levels(
    id: Annotated[StrictStr, Field(description="Id der Schule")] = Path(..., description="Id der Schule"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[CompetenceLevelsInner]:
    if not BaseSchoolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSchoolsApi.subclasses[0]().get_school_competence_levels(id, comparison)


@router.get(
    "/schools/{id}/items",
    responses={
        200: {"model": List[ItemsInner], "description": "Lösungshäufigkeiten je Item an der Schule"},
        400: {"description": "Ungültige Anfrage, z.B. ungültige Werte für die Parameter"},
        404: {"description": "Schule oder Lösungshäufigkeit je Item für die Schule nicht gefunden"},
    },
    tags=["schools"],
    summary="Lösungshäufigkeiten je Item an der Schule",
    response_model_by_alias=True,
)
async def get_school_items(
    id: Annotated[StrictStr, Field(description="Id der Schule")] = Path(..., description="Id der Schule"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[ItemsInner]:
    if not BaseSchoolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSchoolsApi.subclasses[0]().get_school_items(id, comparison)


@router.get(
    "/schools/{id}/aggregations",
    responses={
        200: {"model": List[AggregationsInner], "description": "Abhängig vom Typ berechnete Aggregation für die Schule"},
        400: {"description": "Ungültige Anfrage, z.B. ungültige Werte für die Parameter"},
        404: {"description": "Schule oder Werte für die Schule nicht gefunden"},
    },
    tags=["schools"],
    summary="Aggregierte Werte (z.B. Lösungshäufigkeiten) an der Schule",
    response_model_by_alias=True,
)
async def get_school_aggregations(
    id: Annotated[StrictStr, Field(description="Id der Schule")] = Path(..., description="Id der Schule"),
    type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")] = Query(None, description="Wertegruppen, welche ausgegeben werden sollen", alias="type"),
    aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")] = Query(None, description="Aggregationsarten, die berechnet werden sollen", alias="aggregation"),
    comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")] = Query(None, description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen", alias="comparison"),
) -> List[AggregationsInner]:
    if not BaseSchoolsApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseSchoolsApi.subclasses[0]().get_school_aggregations(id, type, aggregation, comparison)
