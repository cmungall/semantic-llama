RUN = poetry run
PACKAGE = semantic_llama
TEMPLATE_DIR = src/$(PACKAGE)/templates
TEMPLATES = core gocam mendelian_disease biological_process treatment environmental_sample

all: $(patsubst %, $(TEMPLATE_DIR)/%.py, $(TEMPLATES))

test:
	$(RUN) pytest

$(TEMPLATE_DIR)/%.py: src/$(PACKAGE)/templates/%.yaml
	$(RUN) gen-pydantic $< > $@
