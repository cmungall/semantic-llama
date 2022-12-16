from __future__ import annotations
from datetime import datetime, date
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel as BaseModel, Field

metamodel_version = "None"
version = "None"

class WeakRefShimBaseModel(BaseModel):
   __slots__ = '__weakref__'
    
class ConfiguredBaseModel(WeakRefShimBaseModel,
                validate_assignment = True, 
                validate_all = True, 
                underscore_attrs_are_private = True, 
                extra = 'forbid', 
                arbitrary_types_allowed = True):
    pass                    


class GeneToReaction(ConfiguredBaseModel):
    
    gene: Optional[str] = Field(None, description="""name of the gene that catalyzes the reaction""")
    reactions: Optional[List[Reaction]] = Field(default_factory=list, description="""semicolon separated list of reaction equations (e.g. A+B = C+D) catalyzed by the gene""")
    organism: Optional[str] = Field(None)
    


class MultiGeneToReaction(ConfiguredBaseModel):
    
    genes: Optional[List[str]] = Field(default_factory=list, description="""semicolon separated list of genes that catalyzes the mentioned reactions""")
    reactions: Optional[List[Reaction]] = Field(default_factory=list, description="""semicolon separated list of reaction equations (e.g. A+B = C+D) catalyzed by the gene""")
    gene_reaction_pairings: Optional[List[GeneReactionPairing]] = Field(default_factory=list, description="""semicolon separated list of gene to reaction pairings""")
    organism: Optional[str] = Field(None)
    


class NamedEntity(ConfiguredBaseModel):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Reaction(NamedEntity):
    
    label: Optional[str] = Field(None, description="""the name of the reaction""")
    description: Optional[str] = Field(None, description="""a textual description of the reaction""")
    synonyms: Optional[List[str]] = Field(default_factory=list, description="""alternative names of the reaction""")
    subclass_of: Optional[str] = Field(None, description="""the category to which this biological process belongs""")
    left_side: Optional[List[str]] = Field(default_factory=list, description="""semicolon separated list of chemical entities on the left side""")
    right_side: Optional[List[str]] = Field(default_factory=list, description="""semicolon separated list of chemical entities on the right side""")
    id: Optional[str] = Field(None)
    


class ReactionGrouping(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class ChemicalEntity(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Gene(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Organism(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Relationship(ConfiguredBaseModel):
    
    None
    


class GeneReactionPairing(Relationship):
    
    gene: Optional[str] = Field(None, description="""name of the gene that catalyzes the reaction""")
    reaction: Optional[str] = Field(None, description="""equation describing the reaction (e.g. A+B = C+D) catalyzed by the gene""")
    


class CompoundExpression(ConfiguredBaseModel):
    
    None
    


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
GeneToReaction.update_forward_refs()
MultiGeneToReaction.update_forward_refs()
NamedEntity.update_forward_refs()
Reaction.update_forward_refs()
ReactionGrouping.update_forward_refs()
ChemicalEntity.update_forward_refs()
Gene.update_forward_refs()
Organism.update_forward_refs()
Relationship.update_forward_refs()
GeneReactionPairing.update_forward_refs()
CompoundExpression.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()

