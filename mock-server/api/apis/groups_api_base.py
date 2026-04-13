# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from api.models.aggregations_inner import AggregationsInner
from api.models.competence_levels_inner import CompetenceLevelsInner
from api.models.items_inner import ItemsInner


class BaseGroupsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseGroupsApi.subclasses = BaseGroupsApi.subclasses + (cls,)
    async def get_group_competence_levels(
        self,
        id: Annotated[StrictStr, Field(description="Id der Lerngruppe")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen.")],
    ) -> List[CompetenceLevelsInner]:
        ...


    async def get_group_items(
        self,
        id: Annotated[StrictStr, Field(description="Id der Lerngruppe")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen.")],
    ) -> List[ItemsInner]:
        ...


    async def get_group_aggregations(
        self,
        id: Annotated[StrictStr, Field(description="Id der Lerngruppe")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche ausgegeben werden sollen")],
        aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen.")],
    ) -> List[AggregationsInner]:
        ...
