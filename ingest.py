"""
Data Ingestion and Vector Store Creation for Therapeutic Companion.

This module handles:
1. Loading CSVs and JSONs from ./dataa/
2. Cleaning and processing therapeutic content
3. Chunking text using RecursiveCharacterTextSplitter
4. Initializing ChromaDB vector store with sentence-transformers

Usage:
    python ingest.py
"""

import os
import json
import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter


# ============================================================================
# CONFIGURATION
# ============================================================================

# Directories
DATA_DIR = Path("./dataa")
VECTOR_DB_DIR = Path("./vector_db")
LOG_DIR = Path("./logs")

# Create necessary directories
DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "ingest.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Embedding model (used by both ingest and retrieval)
EMBEDDING_FUNCTION = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")

# Text splitting configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# ============================================================================
# TEXT SPLITTER
# ============================================================================

def get_text_splitter() -> RecursiveCharacterTextSplitter:
    """
    Initialize and return a RecursiveCharacterTextSplitter.

    Returns:
        RecursiveCharacterTextSplitter configured for therapeutic content.
    """
    return RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""]
    )


# ============================================================================
# DATA LOADING
# ============================================================================

def load_csv_files() -> List[Dict[str, Any]]:
    """
    Load all CSV files from ./dataa/ directory.

    Returns:
        List of dictionaries containing processed CSV data.
    """
    documents = []

    if not DATA_DIR.exists():
        logger.warning(f"Data directory {DATA_DIR} does not exist.")
        return documents

    csv_files = list(DATA_DIR.glob("*.csv"))
    logger.info(f"Found {len(csv_files)} CSV files in {DATA_DIR}")

    for csv_file in csv_files:
        try:
            logger.info(f"Loading CSV: {csv_file.name}")
            df = pd.read_csv(csv_file)

            for idx, row in df.iterrows():
                doc = {
                    "source": csv_file.name,
                    "type": "csv",
                    "content": _combine_therapeutic_fields(row),
                    "metadata": {
                        "filename": csv_file.name,
                        "row_index": idx,
                        "columns": list(df.columns)
                    }
                }
                documents.append(doc)

            logger.info(f"Successfully loaded {len(df)} rows from {csv_file.name}")

        except Exception as e:
            logger.error(f"Error loading CSV {csv_file.name}: {e}")

    return documents


def load_json_files() -> List[Dict[str, Any]]:
    """
    Load all JSON files from ./dataa/ directory.

    Returns:
        List of dictionaries containing processed JSON data.
    """
    documents = []

    if not DATA_DIR.exists():
        logger.warning(f"Data directory {DATA_DIR} does not exist.")
        return documents

    json_files = list(DATA_DIR.glob("*.json"))
    logger.info(f"Found {len(json_files)} JSON files in {DATA_DIR}")

    for json_file in json_files:
        try:
            logger.info(f"Loading JSON: {json_file.name}")

            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Handle both list and dict formats
            if isinstance(data, list):
                for idx, item in enumerate(data):
                    doc = {
                        "source": json_file.name,
                        "type": "json",
                        "content": _combine_therapeutic_fields(item),
                        "metadata": {
                            "filename": json_file.name,
                            "index": idx,
                            "keys": list(item.keys()) if isinstance(item, dict) else []
                        }
                    }
                    documents.append(doc)
            elif isinstance(data, dict):
                doc = {
                    "source": json_file.name,
                    "type": "json",
                    "content": _combine_therapeutic_fields(data),
                    "metadata": {
                        "filename": json_file.name,
                        "keys": list(data.keys())
                    }
                }
                documents.append(doc)

            logger.info(f"Successfully loaded data from {json_file.name}")

        except Exception as e:
            logger.error(f"Error loading JSON {json_file.name}: {e}")

    return documents


def _combine_therapeutic_fields(row: Dict[str, Any]) -> str:
    """
    Combine therapeutic instruction/context and response fields.

    Args:
        row: Dictionary with therapeutic content.

    Returns:
        Combined and cleaned text.
    """
    content_parts = []

    # Look for common field names
    instruction_fields = ['instruction', 'context', 'prompt', 'question', 'input']
    response_fields = ['response', 'answer', 'output', 'reply']

    # Extract instruction/context
    for field in instruction_fields:
        if field in row and row[field] is not None:
            value = str(row[field]).strip()
            if value:
                content_parts.append(f"Context: {value}")
                break

    # Extract response
    for field in response_fields:
        if field in row and row[field] is not None:
            value = str(row[field]).strip()
            if value:
                content_parts.append(f"Response: {value}")
                break

    # If no structured fields found, combine all values
    if not content_parts:
        for key, value in row.items():
            if pd.notna(value):
                content_parts.append(f"{key}: {str(value).strip()}")

    combined = "\n".join(content_parts)
    return combined if combined else "No content"


# ============================================================================
# TEXT PROCESSING
# ============================================================================

def chunk_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Chunk long documents using RecursiveCharacterTextSplitter.

    Args:
        documents: List of documents to chunk.

    Returns:
        List of chunked documents with metadata.
    """
    splitter = get_text_splitter()
    chunked_docs = []

    logger.info(f"Chunking {len(documents)} documents...")

    for doc in documents:
        content = doc["content"]
        metadata = doc["metadata"]
        source = doc["source"]
        doc_type = doc["type"]

        # Split the content into chunks
        chunks = splitter.split_text(content)

        for chunk_idx, chunk in enumerate(chunks):
            chunked_doc = {
                "content": chunk,
                "metadata": {
                    **metadata,
                    "chunk_index": chunk_idx,
                    "source_type": doc_type,
                    "source_file": source
                }
            }
            chunked_docs.append(chunked_doc)

    logger.info(f"Successfully chunked into {len(chunked_docs)} chunks")
    return chunked_docs


# ============================================================================
# VECTOR STORE INITIALIZATION
# ============================================================================

def initialize_chromadb(documents: List[Dict[str, Any]]) -> chromadb.Collection:
    """
    Initialize ChromaDB with sentence-transformers embeddings.

    Args:
        documents: List of documents to add to the vector store.

    Returns:
        ChromaDB collection instance.
    """
    logger.info("Initializing ChromaDB with sentence-transformers...")

    try:
        # PersistentClient auto-persists to disk (chromadb >=0.4)
        client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))

        # Get or create collection with explicit embedding function
        collection = client.get_or_create_collection(
            name="therapeutic_companion",
            metadata={"hnsw:space": "cosine"},
            embedding_function=EMBEDDING_FUNCTION
        )

        logger.info("Collection 'therapeutic_companion' initialized/retrieved")

        if documents:
            ids = []
            documents_text = []
            metadatas = []

            for idx, doc in enumerate(documents):
                doc_id = f"doc_{idx}_{hash(doc['content']) % 1000000}"
                ids.append(doc_id)
                documents_text.append(doc["content"])
                metadatas.append(doc["metadata"])

            collection.add(
                ids=ids,
                documents=documents_text,
                metadatas=metadatas
            )

            logger.info(f"Added {len(documents)} documents to ChromaDB collection")
            logger.info(f"ChromaDB persisted to {VECTOR_DB_DIR}")

        return collection

    except Exception as e:
        logger.error(f"Error initializing ChromaDB: {e}")
        raise


# ============================================================================
# MAIN INGESTION PIPELINE
# ============================================================================

def ingest_all_data() -> Optional[chromadb.Collection]:
    """
    Run the complete data ingestion pipeline.

    Returns:
        ChromaDB collection instance or None if ingestion fails.
    """
    try:
        logger.info("=" * 80)
        logger.info("STARTING DATA INGESTION PIPELINE")
        logger.info("=" * 80)

        # Load data
        csv_docs = load_csv_files()
        json_docs = load_json_files()

        all_docs = csv_docs + json_docs
        logger.info(f"Total documents loaded: {len(all_docs)}")

        if not all_docs:
            logger.warning("No documents found in ./dataa/ directory!")
            logger.warning("Creating an empty collection for initialization...")
            return initialize_chromadb([])

        # Chunk documents
        chunked_docs = chunk_documents(all_docs)

        # Initialize vector store
        collection = initialize_chromadb(chunked_docs)

        logger.info("=" * 80)
        logger.info("DATA INGESTION COMPLETE")
        logger.info(f"Vector store location: {VECTOR_DB_DIR}")
        logger.info(f"Total chunks in vector store: {len(chunked_docs)}")
        logger.info("=" * 80)

        return collection

    except Exception as e:
        logger.error(f"Fatal error during ingestion: {e}")
        raise


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_collection_stats() -> Dict[str, Any]:
    """
    Get statistics about the ChromaDB collection.

    Returns:
        Dictionary with collection statistics.
    """
    try:
        client = chromadb.PersistentClient(path=str(VECTOR_DB_DIR))
        collection = client.get_collection(
            name="therapeutic_companion",
            embedding_function=EMBEDDING_FUNCTION
        )

        return {
            "collection_name": "therapeutic_companion",
            "total_documents": collection.count(),
            "vector_store_path": str(VECTOR_DB_DIR),
            "embedding_model": EMBEDDING_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP
        }
    except Exception as e:
        logger.error(f"Error retrieving collection stats: {e}")
        return {"error": str(e)}


def clear_and_reingest(force: bool = False) -> Optional[chromadb.Collection]:
    """
    Clear the existing vector store and re-ingest all data.

    Args:
        force: If True, force re-ingestion without confirmation.

    Returns:
        New ChromaDB collection instance.
    """
    try:
        if not force:
            response = input("This will delete the current vector store. Continue? (yes/no): ")
            if response.lower() != "yes":
                logger.info("Re-ingestion cancelled.")
                return None

        # Delete existing vector store
        if VECTOR_DB_DIR.exists():
            import shutil
            shutil.rmtree(VECTOR_DB_DIR)
            logger.info(f"Deleted existing vector store at {VECTOR_DB_DIR}")

        # Re-ingest
        return ingest_all_data()

    except Exception as e:
        logger.error(f"Error during re-ingestion: {e}")
        raise


# ============================================================================
# CLI ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--reingest":
        collection = clear_and_reingest()
    else:
        collection = ingest_all_data()

    if collection:
        stats = get_collection_stats()
        print("\n" + "=" * 80)
        print("INGESTION SUMMARY")
        print("=" * 80)
        for key, value in stats.items():
            print(f"{key}: {value}")
        print("=" * 80)
    else:
        print("Ingestion failed or produced no collection.")
        sys.exit(1)
