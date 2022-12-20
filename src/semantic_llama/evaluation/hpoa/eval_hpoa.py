"""
DrugMechDB evaluation.

Source Data Model: a direct transliteration of the DrugMechDB schema
Target Data Model: the semllama native representation of drugs and mechanism
"""
import gzip
from dataclasses import dataclass, field
from pathlib import Path
from random import shuffle
from typing import List, Tuple, Dict, Set, Optional, Union, TextIO

import pydantic
import yaml
from oaklib import get_implementation_from_shorthand
from oaklib.interfaces.obograph_interface import OboGraphInterface
from pydantic import BaseModel, Field

import semantic_llama.evaluation.drugmechdb.datamodel.drugmechdb as source_datamodel
from semantic_llama.evaluation.evaluation_engine import EvaluationEngine, Score
from semantic_llama.knowledge_extractor import KnowledgeExtractor
import semantic_llama.templates.drug as target_datamodel

THIS_DIR = Path(__file__).parent
DATABASE_DIR = Path(__file__).parent / "database"
TEST_CASES_DIR = THIS_DIR / "test_cases"
EXEMPLARS_DIR = THIS_DIR / "exemplars"
EXEMPLAR_CASES = EXEMPLARS_DIR / "drugmechdb-exemplars.yaml"


def _fix_source_mechanism(mechanism_dict: dict) -> dict:
    """Fix the id field in Graph objects.

    drugmechdb uses `_id` in the json but this is not
    compatible with pydantic, so we translate to `id`

    https://github.com/linkml/linkml/issues/1179
    """
    g = mechanism_dict["graph"]
    g["id"] = g["_id"]
    del g["_id"]
    # normalize alt_ids
    bad_fields = ["all_id", "alt_name", "alt-name", "comemt", "comemnt"]
    for n in mechanism_dict["nodes"]:
        if "alt_ids" in n and isinstance(n["alt_ids"], str):
            n["alt_ids"] = [n["alt_ids"]]
        for f in bad_fields:
            if f in n:
                del n[f]
                # don't bother trying to repair for now - too messy
    for f in bad_fields:
        if f in mechanism_dict:
            del mechanism_dict[f]
    #print(mechanism_dict)
    return mechanism_dict


def _fix_id(id: Optional[str]) -> str:
    return id.replace("UniProt:", "PR:").replace("DB:", "drugbank:") if id else None


class PredictionDrugMechDB(BaseModel):
    predicted_object: target_datamodel.DrugMechanism = None
    test_object: target_datamodel.DrugMechanism = None
    scores: Dict[str, Score] = None

    def calculate_scores(self):
        self.scores = {}
        def all_objects(dm: target_datamodel.DrugMechanism):
            return list(set(link.subject for link in dm.mechanism_links) | set(link.object for link in dm.mechanism_links))

        self.scores["similarity"] = Score.from_set(
                all_objects(self.test_object),
                all_objects(self.predicted_object),
            )


class EvaluationObjectSetDrugMechDB(BaseModel):
    """
    A result of predicting paths
    """
    test: List[target_datamodel.DrugMechanism] = None
    training: List[target_datamodel.DrugMechanism] = None
    predictions: List[PredictionDrugMechDB] = None


@dataclass
class EvalDrugMechDB(EvaluationEngine):
    #ontology: OboGraphInterface = None
    data: List[target_datamodel.DrugMechanism] = None
    default_labelers = ["sqlite:obo:mesh", "sqlite:obo:drugbank", "sqlite:obo:go", "sqlite:obo:uberon", "sqlite:obo:pr"]

    def __post_init__(self):
        self.extractor = KnowledgeExtractor("drug.DrugMechanism")
        self.extractor.labelers = [get_implementation_from_shorthand(l) for l in self.default_labelers]

    def load_mechanisms_from_path(self, file: Union[str, Path, TextIO]) -> List[source_datamodel.Mechanism]:
        if isinstance(file, Path):
            file = str(file)
        if isinstance(file, str):
            with open(file, "r") as f:
                return self.load_mechanisms_from_path(f)
        mechanisms = yaml.safe_load(file)
        print(f"Loading {len(mechanisms)} mechanism objects from yaml; translating...")
        return [source_datamodel.Mechanism(**_fix_source_mechanism(m)) for m in mechanisms]

    def load_exemplars(self) -> List[target_datamodel.DrugMechanism]:
        srcs = self.load_mechanisms_from_path(EXEMPLAR_CASES)
        return [self.translate_mechanism(m) for m in srcs]

    def load_source_database(self) -> List[target_datamodel.DrugMechanism]:
        """Load the entire DrugMechDB database."""
        with gzip.open(str(DATABASE_DIR / "indication_paths.yaml.gz"), "rb") as f:
            srcs = self.load_mechanisms_from_path(f)
            return [self.translate_mechanism(m) for m in srcs]

    def load_target_database(self) -> List[target_datamodel.DrugMechanism]:
        """Load the entire DrugMechDB database."""
        with gzip.open(str(DATABASE_DIR / "drugmechdb-normalized.yaml.gz"), "rb") as f:
            objs = yaml.safe_load(f)
            return [target_datamodel.DrugMechanism(**m) for m in objs]

    def translate_mechanism(self, mechanism: source_datamodel.Mechanism) -> target_datamodel.DrugMechanism:
        """Translate a mechanism from DrugMechDB to the target template."""
        triples = []
        for link in mechanism.links:
            triples.append(target_datamodel.MechanismLink(
                subject=_fix_id(link.source),
                object=_fix_id(link.target),
                predicate=link.key,
            ))
        return target_datamodel.DrugMechanism(
            disease=mechanism.graph.disease_mesh,
            drug=_fix_id(mechanism.graph.drugbank),
            mechanism_links=triples,
        )

    def create_test_and_training(self, num_test: int = 10, num_training: int = 5) -> EvaluationObjectSetDrugMechDB:
        """Create a test and training set from the DrugMechDB database."""
        if self.data is None:
            mechanisms = self.load_target_database()
        else:
            mechanisms = self.data
        shuffle(mechanisms)
        return EvaluationObjectSetDrugMechDB(
            test=mechanisms[:num_test],
            training=mechanisms[num_test:num_test + num_training],
        )

    def eval(self) -> EvaluationObjectSetDrugMechDB:
        ke = self.extractor
        eos = self.create_test_and_training(num_test=self.num_tests, num_training=self.num_training)
        eos.predictions = []
        print(yaml.dump(eos.dict()))
        for test_obj in eos.test:
            print(yaml.dump(test_obj.dict()))
            stub = {
                "disease": test_obj.disease,
                "drug": test_obj.drug,
            }
            results = ke.generalize(stub, eos.training)
            predicted_obj = results.results[0]
            pred = PredictionDrugMechDB(
                predicted_object=predicted_obj,
                test_object=test_obj)
            pred.calculate_scores()
            eos.predictions.append(pred)
        return eos






