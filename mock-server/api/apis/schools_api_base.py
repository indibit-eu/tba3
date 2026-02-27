# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from api.models.aggregations_inner import AggregationsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.items_inner import ItemsInner


class BaseSchoolsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseSchoolsApi.subclasses = BaseSchoolsApi.subclasses + (cls,)
    async def get_school_competence_levels(
        self,
        id: Annotated[StrictStr, Field(description="Id der Schule")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[CompetenceLevelsInner]:
        ...


    async def get_school_items(
        self,
        id: Annotated[StrictStr, Field(description="Id der Schule")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[ItemsInner]:
        ...


    async def get_school_aggregations(
        self,
        id: Annotated[StrictStr, Field(description="Id der Schule")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")],
        aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[AggregationsInner]:
        ...
