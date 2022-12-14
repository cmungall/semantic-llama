# Semantic llama

Semantic Large LAnguage Model Annotation

A knowledge extraction tool that uses a large language model to extract semantic information from text.

## Usage

Given a short text `abstract.txt` with content such as:

> Marfan syndrome is a genetic disorder that affects connective tissue, which
> ...
> Defects or deletions (pathogenic variants) of the fibrillin-1 (FBN1)
> gene have been shown to cause Marfan

We can extract this into the MendelianDisease datamodel:

```bash
semllama extract -t mendelian_disease.MendelianDisease abstract.txt
```


## How it works

1. You provide an arbitrary data model, describing the structure you want to extract text into
    - this can be nested (but see limitations below)
2. provide your preferred annotations for grounding NamedEntity fields
3. semantic-llama will:
    - generate a prompt
    - feed the prompt to a language model (currently OpenAI)
    - parse the results into a dictionary structure
    - ground the results using a preferred annotator

## How to define your own extraction data model

### Step 1: Define a schema

See [src/semantic_llama/templates/](src/semantic_llama/templates/) for examples.

Define a schema (using a subset of LinkML) that describes the structure you want to extract from your text.

```yaml
classes:
  MendelianDisease:
    attributes:
      name:
        description: the name of the disease
        examples:
          - value: peroxisome biogenesis disorder
        identifier: true  ## needed for inlining
      description:
        description: a description of the disease
        examples:
          - value: >-
             Peroxisome biogenesis disorders, Zellweger syndrome spectrum (PBD-ZSS) is a group of autosomal recessive disorders affecting the formation of functional peroxisomes, characterized by sensorineural hearing loss, pigmentary retinal degeneration, multiple organ dysfunction and psychomotor impairment
      synonyms:
        multivalued: true
        examples:
          - value: Zellweger syndrome spectrum
          - value: PBD-ZSS
      subclass_of:
        multivalued: true
        range: MendelianDisease
        examples:
          - value: lysosomal disease
          - value: autosomal recessive disorder
      symptoms:
        range: Symptom
        multivalued: true
        examples:
          - value: sensorineural hearing loss
          - value: pigmentary retinal degeneration
      inheritance:
        range: Inheritance
        examples:
          - value: autosomal recessive
      genes:
        range: Gene
        multivalued: true
        examples:
          - value: PEX1
          - value: PEX2
          - value: PEX3

  Gene:
    is_a: NamedThing
    id_prefixes:
      - HGNC
    annotations:
      annotators: gilda:, bioportal:hgnc-nr

  Symptom:
    is_a: NamedThing
    id_prefixes:
      - HP
    annotations:
      annotators: sqlite:obo:hp

  Inheritance:
    is_a: NamedThing
    annotations:
      annotators: sqlite:obo:hp
```

- the schema is defined in LinkML
- prompt hints can be specified using the `prompt` annotation (otherwise description is used)
- multivalued fields are supported
- the default range is string - these are not grounded. E.g. disease name, synonyms
- define a class for each NamedEntity
- for any NamedEntity, you can specify a preferred annotator using the `annotators` annotation

We recommend following an established schema like biolink, but you can define your own.

### Step 2: Compile the schema

Run the `make` command at the top level. This will compile the schema to pedantic

### Step 3: Run the command line

## Limitations

### Two levels of nesting

Currently only two levels of nesting are supported

If a field has a range which is itself a class and not a primitive, it will attempt to nest

E.g. the gocam schema has an attribute:

```yaml
  attributes:
      ...
      gene_functions:
        description: semicolon-separated list of gene to molecular activity relationships
        multivalued: true
        range: GeneMolecularActivityRelationship
```

Because GeneMolecularActivityRelationship is *inlined* it will nest

The generated prompt is:

`gene_functions : <semicolon-separated list of gene to molecular activities relationships>`

llama will do its best to parse the return payload into *tuples* of gene and molecular activity, but
this can be hard to do reliably via string matching.

However, very soon llama will support N-pass annotation, where nested structures are fed back into the LLM!

## Coupled to OpenAI

You will need an openai account. In theory any LLM can be used but in practice the parser is tuned for OpenAI






# Acknowledgements

This [cookiecutter](https://cookiecutter.readthedocs.io/en/stable/README.html) project was developed from the [sphintoxetry-cookiecutter](https://github.com/hrshdhgd/sphintoxetry-cookiecutter) template and will be kept up-to-date using [cruft](https://cruft.github.io/cruft/).