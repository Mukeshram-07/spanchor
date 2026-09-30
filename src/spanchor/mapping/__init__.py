"""Chunk-to-span mapping layer.

Provides functionality to map retrieval results in chunk-text form back to
canonical document spans, with support for exact and whitespace-normalized matching.
"""

from spanchor.mapping.mapper import ChunkMapper, MappingResult

__all__ = ["ChunkMapper", "MappingResult"]
