"""
Evaluation Engines.

An evaluation engine incorporates different components to evaluate KE:

 1. ETL-ing the data from the source and mapping to a target schema
 2. Selecting test and training cases from a source database
 3. Executing the KE
 4. Calculating scores comparing test with training

"""

from dataclasses import dataclass
from typing import Optional, List, Set

from pydantic import BaseModel

from semantic_llama.knowledge_extractor import KnowledgeExtractor


def jaccard_index(a: Set, b: Set):
    """Compute the Jaccard index between two sets."""
    if not a and not b:
        return None
    return len(a & b) / len(a | b)


class Score(BaseModel):
    """
    Scores for an individual prediction.

    The scores are computed as the Jaccard index between the predicted and true sets.
    """
    jaccard: Optional[float]
    false_positives: List[str]
    false_negatives: List[str]
    common: List[str]

    @staticmethod
    def from_set(test_set: List, prediction_set: List):
        test_set = set(test_set)
        prediction_set = set(prediction_set)
        return Score(
            jaccard=jaccard_index(test_set, prediction_set),
            false_positives=list(prediction_set - test_set),
            false_negatives=list(test_set - prediction_set),
            common=list(test_set & prediction_set),
        )

@dataclass
class EvaluationEngine:
    """Base class for all evaluation engines"""

    extractor: KnowledgeExtractor = None
    """Knowledge extractor to use"""

    num_tests: int = 10
    """Number of test cases to use for evaluation"""

    num_training: int = 5
    """Number of training/exemplar cases to use for evaluation in generalization task.
    Note this number will be low as we use few-shot learning."""