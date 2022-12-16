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


class Study(ConfiguredBaseModel):
    
    environments: Optional[List[str]] = Field(default_factory=list)
    causal_relationships: Optional[List[CausalRelationship]] = Field(default_factory=list)
    variables: Optional[List[str]] = Field(default_factory=list)
    treatments: Optional[List[str]] = Field(default_factory=list)
    measurements: Optional[List[Measurement]] = Field(default_factory=list)
    location: Optional[List[str]] = Field(default_factory=list, description="""the sites at which the study was conducted""")
    environmental_material: Optional[List[str]] = Field(default_factory=list, description="""the environmental material that was sampled""")
    sequencing_technologies: Optional[str] = Field(None)
    organisms: Optional[List[str]] = Field(default_factory=list, description="""semicolon-separated list of all studied organism taxons""")
    


class ExtractionResult(ConfiguredBaseModel):
    """
    A result of extracting knowledge on text
    """
    input_id: Optional[str] = Field(None)
    input_title: Optional[str] = Field(None)
    input_text: Optional[str] = Field(None)
    results: Optional[Any] = Field(None)
    named_entities: Optional[List[Any]] = Field(default_factory=list)
    


class NamedEntity(ConfiguredBaseModel):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Location(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class EnvironmentalMaterial(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Environment(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Variable(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Unit(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class SequencingTechnology(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Treatment(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Organism(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Relationship(ConfiguredBaseModel):
    
    None
    


class Measurement(Relationship):
    
    value: Optional[str] = Field(None, description="""the value of the measurement""")
    unit: Optional[str] = Field(None, description="""the unit of the measurement""")
    


class CausalRelationship(Relationship):
    
    cause: Optional[str] = Field(None, description="""the variable that is the cause of the effect""")
    effect: Optional[str] = Field(None, description="""the things that is affected""")
    


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
Study.update_forward_refs()
ExtractionResult.update_forward_refs()
NamedEntity.update_forward_refs()
Location.update_forward_refs()
EnvironmentalMaterial.update_forward_refs()
Environment.update_forward_refs()
Variable.update_forward_refs()
Unit.update_forward_refs()
SequencingTechnology.update_forward_refs()
Treatment.update_forward_refs()
Organism.update_forward_refs()
Relationship.update_forward_refs()
Measurement.update_forward_refs()
CausalRelationship.update_forward_refs()
CompoundExpression.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()

