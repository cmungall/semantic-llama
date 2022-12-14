from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel as BaseModel
from pydantic import Field

metamodel_version = "None"
version = "None"


class WeakRefShimBaseModel(BaseModel):
    __slots__ = "__weakref__"


class ConfiguredBaseModel(
    WeakRefShimBaseModel,
    validate_assignment=True,
    validate_all=True,
    underscore_attrs_are_private=True,
    extra="forbid",
    arbitrary_types_allowed=True,
):
    pass


class MendelianDisease(ConfiguredBaseModel):

    name: Optional[str] = Field(None, description="""the name of the disease""")
    description: Optional[str] = Field(None, description="""a description of the disease""")
    synonyms: Optional[List[str]] = Field(default_factory=list)
    subclass_of: Optional[List[str]] = Field(default_factory=list)
    symptoms: Optional[List[str]] = Field(default_factory=list)
    inheritance: Optional[str] = Field(None)
    genes: Optional[List[str]] = Field(default_factory=list)


class NamedThing(ConfiguredBaseModel):

    id: Optional[str] = Field(None)


class Gene(NamedThing):

    id: Optional[str] = Field(None)


class Symptom(NamedThing):

    id: Optional[str] = Field(None)


class Inheritance(NamedThing):

    id: Optional[str] = Field(None)


class Publication(ConfiguredBaseModel):

    id: Optional[str] = Field(None, description="""The publication identifier""")
    title: Optional[str] = Field(None, description="""The title of the publication""")
    abstract: Optional[str] = Field(None, description="""The abstract of the publication""")
    full_text: Optional[str] = Field(None, description="""The full text of the publication""")


class AnnotatorResult(ConfiguredBaseModel):

    subject_text: Optional[str] = Field(None)
    object_id: Optional[str] = Field(None)
    object_text: Optional[str] = Field(None)


# Update forward refs
# see https://pydantic-docs.helpmanual.io/usage/postponed_annotations/
MendelianDisease.update_forward_refs()
NamedThing.update_forward_refs()
Gene.update_forward_refs()
Symptom.update_forward_refs()
Inheritance.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()
