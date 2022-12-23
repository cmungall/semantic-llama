"""
Evaluation Engines.

An evaluation engine incorporates different components to evaluate KE:

 1. ETL-ing the data from the source and mapping to a target schema
 2. Selecting test and training cases from a source database
 3. Executing the KE
 4. Calculating scores comparing test with training

"""

from dataclasses import dataclass
from typing import List, Optional, Set

from pydantic import BaseModel

from semantic_llama.engines.text_model_knowledge_engine import TextModelKnowledgeEngine


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
    false_positives: Optional[List[Optional[str]]]
    false_negatives: Optional[List[Optional[str]]]
    common: Optional[List[str]]

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

    extractor: TextModelKnowledgeEngine = None
    """Knowledge extractor to use"""

    num_tests: int = 10
    """Number of test cases to use for evaluation"""

    num_training: int = 5
    """Number of training/exemplar cases to use for evaluation in generalization task.
    Note this number will be low as we use few-shot learning."""
