"""Gold-set bootstrapping generation module.

Provides utilities for extracting candidate sentences from documents and
preparing them for review and manual annotation.
"""

from spanchor.generation.extract import extract_sentences
from spanchor.generation.promote import promote_candidate_to_gold

__all__: list[str] = ["extract_sentences", "promote_candidate_to_gold"]
