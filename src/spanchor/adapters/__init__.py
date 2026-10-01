"""Retriever protocol adapters.

Defines protocols for integrating custom retrievers with spanchor.
Framework-agnostic and dependency-free.

Generic converters for transforming common retrieval formats:
    - dicts_to_retrieval_results(): Convert list of dicts to RetrievalResults
    - dict_to_retrieval_result(): Convert single dict to RetrievalResult

Framework-specific adapters (optional):
    - langchain: Convert LangChain Documents (requires langchain optional dependency)
    - llamaindex: Convert LlamaIndex Nodes (requires llama-index optional dependency)
"""

from spanchor.adapters.base import RetrieverProtocol
from spanchor.adapters.generic import dict_to_retrieval_result, dicts_to_retrieval_results

__all__: list[str] = [
    "RetrieverProtocol",
    "dict_to_retrieval_result",
    "dicts_to_retrieval_results",
]
