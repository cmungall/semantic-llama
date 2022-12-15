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


class BiologicalProcess(ConfiguredBaseModel):

    name: Optional[str] = Field(None, description="""the name of the biological process""")
    description: Optional[str] = Field(
        None, description="""a textual description of the biological process"""
    )
    synonyms: Optional[List[str]] = Field(
        default_factory=list, description="""alternative names of the biological process"""
    )
    subclass_of: Optional[BiologicalProcess] = Field(
        None, description="""the category to which this biological process belongs"""
    )
    inputs: Optional[List[str]] = Field(
        default_factory=list, description="""the inputs of the biological process"""
    )
    outputs: Optional[List[str]] = Field(
        default_factory=list, description="""the outputs of the biological process"""
    )
    steps: Optional[List[str]] = Field(
        default_factory=list, description="""the steps involved in this biological process"""
    )
    genes: Optional[List[str]] = Field(default_factory=list)
    gene_activities: Optional[List[GeneMolecularActivityRelationship]] = Field(
        default_factory=list,
        description="""semicolon-separated list of gene to molecular activity relationships""",
    )


class GeneMolecularActivityRelationship(ConfiguredBaseModel):

    gene: Optional[str] = Field(None)
    molecular_activity: Optional[str] = Field(None)


class NamedEntity(ConfiguredBaseModel):

    id: Optional[str] = Field(None)


class Gene(NamedEntity):

    id: Optional[str] = Field(None)


class MolecularActivity(NamedEntity):

    id: Optional[str] = Field(None)


class ChemicalEntity(NamedEntity):

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
BiologicalProcess.update_forward_refs()
GeneMolecularActivityRelationship.update_forward_refs()
NamedEntity.update_forward_refs()
Gene.update_forward_refs()
MolecularActivity.update_forward_refs()
ChemicalEntity.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()
