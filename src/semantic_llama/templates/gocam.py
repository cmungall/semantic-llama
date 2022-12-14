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


class GoCamAnnotations(ConfiguredBaseModel):

    genes: Optional[List[str]] = Field(
        default_factory=list, description="""semicolon-separated list of genes"""
    )
    organisms: Optional[List[str]] = Field(
        default_factory=list, description="""semicolon-separated list of organism taxons"""
    )
    gene_organisms: Optional[List[GeneOrganismRelationship]] = Field(default_factory=list)
    activities: Optional[List[str]] = Field(
        default_factory=list, description="""semicolon-separated list of molecular activities"""
    )
    gene_functions: Optional[List[GeneMolecularActivityRelationship]] = Field(
        default_factory=list,
        description="""semicolon-separated list of gene to molecular activity relationships""",
    )
    cellular_processes: Optional[List[str]] = Field(
        default_factory=list, description="""semicolon-separated list of cellular processes"""
    )
    pathways: Optional[List[str]] = Field(
        default_factory=list, description="""semicolon-separated list of pathways"""
    )
    gene_gene_interactions: Optional[List[GeneGeneInteraction]] = Field(
        default_factory=list,
        description="""semicolon-separated list of gene to gene interactions""",
    )
    gene_localizations: Optional[List[GeneSubcellularLocalizationRelationship]] = Field(
        default_factory=list,
        description="""semicolon-separated list of gene to subcellular localization relationships""",
    )


class NamedThing(ConfiguredBaseModel):

    id: Optional[str] = Field(None)


class Gene(NamedThing):

    id: Optional[str] = Field(None)


class Pathway(NamedThing):

    id: Optional[str] = Field(None)


class CellularProcess(NamedThing):

    id: Optional[str] = Field(None)


class MolecularActivity(NamedThing):

    id: Optional[str] = Field(None)


class CellularComponent(NamedThing):

    id: Optional[str] = Field(None)


class Organism(NamedThing):

    id: Optional[str] = Field(None)


class Relationship(ConfiguredBaseModel):

    None


class GeneOrganismRelationship(Relationship):

    gene: Optional[str] = Field(None)
    organism: Optional[str] = Field(None)


class GeneMolecularActivityRelationship(Relationship):

    gene: Optional[str] = Field(None)
    molecular_activity: Optional[str] = Field(None)


class GeneSubcellularLocalizationRelationship(Relationship):

    gene: Optional[str] = Field(None)
    location: Optional[str] = Field(None)


class GeneGeneInteraction(Relationship):

    gene1: Optional[str] = Field(None)
    gene2: Optional[str] = Field(None)


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
GoCamAnnotations.update_forward_refs()
NamedThing.update_forward_refs()
Gene.update_forward_refs()
Pathway.update_forward_refs()
CellularProcess.update_forward_refs()
MolecularActivity.update_forward_refs()
CellularComponent.update_forward_refs()
Organism.update_forward_refs()
Relationship.update_forward_refs()
GeneOrganismRelationship.update_forward_refs()
GeneMolecularActivityRelationship.update_forward_refs()
GeneSubcellularLocalizationRelationship.update_forward_refs()
GeneGeneInteraction.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()
