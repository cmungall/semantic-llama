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


class Recipe(ConfiguredBaseModel):
    
    label: Optional[str] = Field(None, description="""the name of the recipe""")
    description: Optional[str] = Field(None, description="""a brief textual description of the recipe""")
    category: Optional[List[str]] = Field(default_factory=list, description="""a semicolon separated list of the categories to which this recipe belongs""")
    ingredients: Optional[List[Ingredient]] = Field(default_factory=list, description="""a semicolon separated list of the ingredients plus quantities of the recipe""")
    steps: Optional[List[Step]] = Field(default_factory=list, description="""a semicolon separated list of the individual steps involved in this recipe""")
    


class NamedEntity(ConfiguredBaseModel):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class FoodItem(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class RecipeCategory(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Action(NamedEntity):
    
    id: Optional[str] = Field(None)
    label: Optional[str] = Field(None, description="""The label of the named thing""")
    


class Relationship(ConfiguredBaseModel):
    
    None
    


class Ingredient(Relationship):
    
    food_item: Optional[str] = Field(None, description="""the food item""")
    quantity: Optional[str] = Field(None, description="""the quantity of the ingredient""")
    


class Step(Relationship):
    
    action: Optional[str] = Field(None, description="""the action taken in this step (e.g. mix, add)""")
    inputs: Optional[List[str]] = Field(default_factory=list, description="""a semicolon separated list of the inputs of this step""")
    outputs: Optional[List[str]] = Field(default_factory=list, description="""a semicolon separated list of the outputs of this step""")
    


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
Recipe.update_forward_refs()
NamedEntity.update_forward_refs()
FoodItem.update_forward_refs()
RecipeCategory.update_forward_refs()
Action.update_forward_refs()
Relationship.update_forward_refs()
Ingredient.update_forward_refs()
Step.update_forward_refs()
CompoundExpression.update_forward_refs()
Publication.update_forward_refs()
AnnotatorResult.update_forward_refs()

