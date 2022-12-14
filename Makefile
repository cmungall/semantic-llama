RUN = poetry run
PACKAGE = semantic_llama
TEMPLATE_DIR = src/$(PACKAGE)/templates
EVAL_DIR = src/$(PACKAGE)/evaluation
TEMPLATES = core gocam mendelian_disease biological_process treatment environmental_sample metagenome_study reaction recipe ontology_class metabolic_process drug

all: $(patsubst %, $(TEMPLATE_DIR)/%.py, $(TEMPLATES))

test:
	$(RUN) pytest

$(TEMPLATE_DIR)/%.py: src/$(PACKAGE)/templates/%.yaml
	$(RUN) gen-pydantic $< > $@.tmp && mv $@.tmp $@

%.py: %.yaml
	$(RUN) gen-pydantic $< > $@
