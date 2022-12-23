from typing import Optional, Type, Union

from class_resolver import ClassResolver

from semantic_llama.engines.code_model_knowledge_engine import CodeModelKnowledgeEngine
from semantic_llama.engines.engine import KnowledgeEngine
from semantic_llama.engines.text_model_knowledge_engine import TextModelKnowledgeEngine

resolver = ClassResolver([TextModelKnowledgeEngine, CodeModelKnowledgeEngine], base=KnowledgeEngine)


def create_engine(
    template: str, model: Optional[Union[str, Type]] = None, **kwargs
) -> KnowledgeEngine:
    """Create a knowledge engine."""
    if model is None:
        model = TextModelKnowledgeEngine
    if isinstance(model, str):
        model = resolver.get_class(model)(**kwargs)
    return model(template, **kwargs)
