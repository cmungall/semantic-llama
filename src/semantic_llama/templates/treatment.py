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


class DiseaseTreatmentSummary(ConfiguredBaseModel):
    
    disease: Optional[str] = Field(None, description="""the name of the disease that is treated""")
    drugs: Optional[List[str]] = Field(default_factory=list, description="""semicolon-separated list of drugs""")
    treatments: Optional[List[str]] = Field(default_factory=list, description="""semicolon-separated list of treatments""")
    treatment_mechanisms: Optional[List[TreatmentMechanism]] = Field(default_factory=list, description="""semicolon-separated list of treatment to asterisk-separated mechanism associations""")
    


class NamedEntity(ConfiguredBaseModel):
    
    id: Optional[str] = Field(None)
    


class Gene(NamedEntity):
    
    id: Optional[str] = Field(None)
    


class Symptom(NamedEntity):
    
    id: Optional[str] = Field(None)
    


class Disease(NamedEntity):
    
    id: Optional[str] = Field(None)
    


class Treatment(NamedEntity):
    
    id: Optional[str] = Field(None)
    


class Drug(NamedEntity):
    
    id: Optional[str] = Field(None)
    


class Relationship(ConfiguredBaseModel):
    
    None
    


class TreatmentMechanism(Relationship):
    
    treatment: Optional[str] = Field(None)
    mechanism: Optional[str] = Field(None)
    


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
DiseaseTreatmentSummary.update_forward_refs()
NamedEntity.update_forward_refs()
Gene.update_forward_refs()
Symptom.update_forward_refs()
Disease.update_forward_refs()
Treatment.update_forward_refs()
Drug.update_forward_refs()
Relationship.update_forward_refs()
TreatmentMechanism.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()

