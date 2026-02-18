# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any, List, Optional
from typing_extensions import Annotated
from api.models.inline_object_inner import InlineObjectInner
from api.models.inline_object_inner1 import InlineObjectInner1
from api.models.inline_object_inner2 import InlineObjectInner2


class BaseGroupsApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseGroupsApi.subclasses = BaseGroupsApi.subclasses + (cls,)
    async def groups_id_competence_levels_get(
        self,
        id: Annotated[StrictStr, Field(description="Id der Lerngruppe")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[InlineObjectInner]:
        """Kompetenzstufenverteilung in der Lerngruppe"""
        ...


    async def groups_id_items_get(
        self,
        id: Annotated[StrictStr, Field(description="Id der Lerngruppe")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[InlineObjectInner1]:
        """Lösungshäufigkeiten je Item in der Lerngruppe"""
        ...


    async def groups_id_aggregations_get(
        self,
        id: Annotated[StrictStr, Field(description="Id der Lerngruppe")],
        type: Annotated[Optional[StrictStr], Field(description="Wertegruppen, welche zusätzlich zur Standardgruppe ausgegeben werden sollen")],
        aggregation: Annotated[Optional[StrictStr], Field(description="Aggregationsarten, die berechnet werden sollen")],
        comparison: Annotated[Optional[StrictStr], Field(description="Filter für bestimmte Vergleichsgruppen, die ausgegeben werden sollen")],
    ) -> List[InlineObjectInner2]:
        """Aggregierte Lösungshäufigkeiten in der Lerngruppe"""
        ...
