"""Core tests."""
import unittest

import yaml

from semantic_llama.evaluation.drugmechdb.datamodel.drugmechdb import Mechanism, Graph
from semantic_llama.evaluation.drugmechdb.eval_drugmechdb import EvalDrugMechDB
from tests import CASES_DIR, OUTPUT_DIR

NORMALIZED_OUT = OUTPUT_DIR / "drugmechdb-normalized.yaml"
PREDICTIONS_OUT = OUTPUT_DIR / "eval-drugmechdb-predictions.yaml"

class TestDrugMechDB(unittest.TestCase):
    """Test GO evaluation."""

    def setUp(self) -> None:
        """Set up all extractors in advance."""
        self.engine = EvalDrugMechDB()

    def test_data_model(self):
        g = Graph(id="x")
        m = Mechanism(
            directed=True,
            graph={
                "id": "DB11888_MESH_D007251_1",
            }
        )

    def test_load_exemplars(self):
        mechanisms = self.engine.load_exemplars()
        objs = [m.dict() for m in mechanisms]
        print(yaml.dump(objs[0:5]))
        self.assertGreater(len(mechanisms), 0)

    def test_load_source_database(self):
        mechanisms = self.engine.load_source_database()
        print(f"Loaded {len(mechanisms)} mechanisms")
        objs = [m.dict() for m in mechanisms]
        with open(NORMALIZED_OUT, "w") as f:
            yaml.dump(objs, f)
        print(yaml.dump(objs[0:5]))
        self.assertGreater(len(mechanisms), 0)

    def test_load_target_database(self):
        mechanisms = self.engine.load_target_database()
        print(f"Loaded {len(mechanisms)} mechanisms")
        objs = [m.dict() for m in mechanisms[0:5]]
        print(yaml.dump(objs))
        self.assertGreater(len(mechanisms), 0)

    def test_eval_small(self):
        evaluator = self.engine
        evaluator.num_tests = 3
        evaluator.num_training = 3
        mechanisms = self.engine.load_exemplars()
        evaluator.data = mechanisms
        eos = evaluator.eval()
        with open(PREDICTIONS_OUT, "w") as f:
            yaml.dump(eos.dict(), f)


