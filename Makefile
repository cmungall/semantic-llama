RUN = poetry run
TEMPLATE_DIR = src/oak_ai/templates
TEMPLATES = gocam mendelian_disease biological_process treatment environmental_sample

all: $(patsubst %, $(TEMPLATE_DIR)/%.py, $(TEMPLATES))

test:
	$(RUN) pytest

$(TEMPLATE_DIR)/%.py: src/oak_ai/templates/%.yaml
	$(RUN) gen-pydantic $< > $@
