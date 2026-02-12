# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2


class BaseStatesApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseStatesApi.subclasses = BaseStatesApi.subclasses + (cls,)
    async def states_id_competence_levels_get(
        self,
        id: Annotated[StrictStr, Field(description="Id des Bundeslandes")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[InlineObjectInner]:
        """Kompetenzstufenverteilung im Bundesland"""
        ...


    async def states_id_items_get(
        self,
        id: Annotated[StrictStr, Field(description="Id des Bundeslandes")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[InlineObjectInner1]:
        """Lösungshäufigkeiten je Item im Bundesland"""
        ...


    async def states_id_aggregations_get(
        self,
        id: Annotated[StrictStr, Field(description="Id des Bundeslandes")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")],
        aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[InlineObjectInner2]:
        """Aggregierte Lösungshäufigkeiten im Bundesland"""
        ...
