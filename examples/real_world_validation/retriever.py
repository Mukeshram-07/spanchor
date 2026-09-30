#!/usr/bin/env python3
"""
Lightweight lexical retriever for CloudSync documentation demo.

Uses simple BM25-style scoring without external dependencies.
"""

import json
import math
from dataclasses import dataclass
from pathlib import Path


@dataclass
class RetrievalDocument:
    """A document chunk for retrieval."""
    doc_id: str
    text: str
    start: int  # Character offset in original document
    end: int


class LexicalRetriever:
    """Simple BM25-style lexical retriever."""
    
    def __init__(self, chunk_size: int = 250, chunk_overlap: int = 0):
        """Initialize retriever.
        
        Args:
            chunk_size: Size of chunks in characters
            chunk_overlap: Overlap between consecutive chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.documents: list[RetrievalDocument] = []
        self.word_doc_freq: dict[str, int] = {}  # IDF calculation
        self.doc_count = 0
        
    def index_corpus(self, corpus_dir: Path) -> None:
        """Index all documents in corpus directory."""
        corpus_files = sorted(corpus_dir.glob("*.txt"))
        
        for file_path in corpus_files:
            doc_id = file_path.stem
            text = file_path.read_text(encoding="utf-8")
            self._add_document(doc_id, text)
        
        # Calculate IDF values
        self.doc_count = len(set(doc.doc_id for doc in self.documents))
        for words_set in self.word_doc_freq.values():
            # This is hacky but works for our use case
            pass
    
    def _add_document(self, doc_id: str, text: str) -> None:
        """Chunk and index a document."""
        # Create chunks with overlap
        offset = 0
        while offset < len(text):
            end = min(offset + self.chunk_size, len(text))
            chunk_text = text[offset:end]
            
            # Add as retrieval document
            doc = RetrievalDocument(
                doc_id=doc_id,
                text=chunk_text,
                start=offset,
                end=end
            )
            self.documents.append(doc)
            
            # Track word frequencies for IDF
            words = self._tokenize(chunk_text)
            for word in set(words):
                if word not in self.word_doc_freq:
                    self.word_doc_freq[word] = 0
                self.word_doc_freq[word] += 1
            
            # Move to next chunk
            if offset + self.chunk_size >= len(text):
                break
            offset += self.chunk_size - self.chunk_overlap
    
    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization: lowercase and split on non-alphanumeric."""
        text = text.lower()
        words = []
        current = []
        
        for char in text:
            if char.isalnum():
                current.append(char)
            else:
                if current:
                    words.append(''.join(current))
                    current = []
        
        if current:
            words.append(''.join(current))
        
        return words
    
    def _bm25_score(self, query_words: list[str], doc: RetrievalDocument) -> float:
        """Calculate BM25 score for a document.
        
        Simplified BM25: k1=1.5, b=0.75, IDF based on word frequency
        """
        k1 = 1.5
        b = 0.75
        
        doc_words = self._tokenize(doc.text)
        doc_length = len(doc_words) if doc_words else 1
        
        score = 0.0
        for query_word in query_words:
            if not query_word:
                continue
            
            # Term frequency
            tf = sum(1 for w in doc_words if w == query_word)
            
            # Inverse document frequency
            doc_freq = self.word_doc_freq.get(query_word, 1)
            idf = math.log((self.doc_count - doc_freq + 0.5) / (doc_freq + 0.5) + 1.0)
            
            # BM25 formula
            numerator = tf * (k1 + 1)
            denominator = tf + k1 * (1 - b + b * (doc_length / 250.0))  # avg doc length ~250
            
            score += idf * (numerator / denominator)
        
        return score
    
    def retrieve(self, query: str, k: int = 5) -> list[dict]:
        """Retrieve top-k documents for a query.
        
        Returns list of dicts with:
        - rank: rank starting from 1
        - score: retrieval score
        - document_id: document ID
        - text: chunk text
        - start: start offset
        - end: end offset
        """
        query_words = self._tokenize(query)
        
        # Score all documents
        scored_docs = []
        for i, doc in enumerate(self.documents):
            score = self._bm25_score(query_words, doc)
            scored_docs.append((score, i, doc))
        
        # Sort by score (descending)
        scored_docs.sort(key=lambda x: (-x[0], x[1]))
        
        # Return top-k
        results = []
        for rank, (score, _, doc) in enumerate(scored_docs[:k], 1):
            results.append({
                "rank": rank,
                "score": float(score),
                "document_id": doc.doc_id,
                "text": doc.text,
                "start": doc.start,
                "end": doc.end
            })
        
        return results


def run_retrieval(corpus_dir: Path, gold_path: Path, output_path: Path,
                  chunk_size: int = 250, chunk_overlap: int = 0) -> None:
    """Run retrieval on all gold questions and save results."""
    
    # Initialize retriever
    retriever = LexicalRetriever(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    retriever.index_corpus(corpus_dir)
    
    # Load gold questions
    questions = []
    with open(gold_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                questions.append(json.loads(line))
    
    # Run retrieval for each question
    results = []
    for q in questions:
        query_id = q["query_id"]
        question = q["question"]
        
        # Retrieve
        retrieved = retriever.retrieve(question, k=5)
        
        # Store result
        result_entry = {
            "query_id": query_id,
            "question": question,
            "retrieved": retrieved
        }
        results.append(result_entry)
    
    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        for result in results:
            f.write(json.dumps(result) + '\n')
    
    print(f"Retrieved for {len(results)} queries, saved to {output_path}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python retriever.py <corpus_dir> <gold_path> <output_path> [chunk_size] [chunk_overlap]")
        sys.exit(1)
    
    corpus = Path(sys.argv[1])
    gold = Path(sys.argv[2])
    output = Path(sys.argv[3])
    chunk_sz = int(sys.argv[4]) if len(sys.argv) > 4 else 250
    chunk_ov = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    
    run_retrieval(corpus, gold, output, chunk_size=chunk_sz, chunk_overlap=chunk_ov)
