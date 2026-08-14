"""
Reads every .md/.txt file in docs/, splits it into small chunks,
embeds each chunk with OpenAI, and upserts it into Pinecone.

Run this once (and again whenever you add/update docs):

    python ingest.py
"""

import os
import glob
import time

from dotenv import load_dotenv
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

print("Starting ingestion...")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

EMBED_MODEL = "text-embedding-3-small"
EMBED_DIM = 1536

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

INDEX_NAME = os.environ.get(
    "PINECONE_INDEX_NAME",
    "bootcamp-debug-agent"
)


# ---------------------------------------------------------
# API clients
# ---------------------------------------------------------

openai_client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"]
)

pc = Pinecone(
    api_key=os.environ["PINECONE_API_KEY"]
)


# ---------------------------------------------------------
# Chunk text
# ---------------------------------------------------------

def chunk_text(text: str) -> list[str]:
    """Very simple fixed-size character chunker with overlap."""

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end - CHUNK_OVERLAP

    return chunks


# ---------------------------------------------------------
# Create embedding
# ---------------------------------------------------------

def embed(text: str) -> list[float]:
    """Create an OpenAI embedding for a piece of text."""

    response = openai_client.embeddings.create(
        model=EMBED_MODEL,
        input=text
    )

    return response.data[0].embedding


# ---------------------------------------------------------
# Ensure Pinecone index exists
# ---------------------------------------------------------

def ensure_index():
    print("\nChecking Pinecone indexes...")

    indexes = pc.list_indexes()

    # Convert Pinecone index objects to names
    existing = [index["name"] for index in indexes]

    print("Existing Pinecone indexes:", existing)
    print("Index we need:", INDEX_NAME)

    # Index already exists
    if INDEX_NAME in existing:
        print(f"Index '{INDEX_NAME}' already exists.")
        return

    # Index doesn't exist
    print(f"Creating index '{INDEX_NAME}'...")

    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBED_DIM,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        ),
    )

    print("Index creation request completed.")

    # Wait until Pinecone reports that the index is ready
    print("Waiting for index to become ready...")

    while True:
        description = pc.describe_index(INDEX_NAME)

        status = description["status"]

        print("Index status:", status)

        if status.get("ready") is True:
            break

        time.sleep(2)

    print(f"Index '{INDEX_NAME}' is ready.")


# ---------------------------------------------------------
# Main ingestion process
# ---------------------------------------------------------

def main():

    print("\n==============================")
    print("BOOTCAMP DEBUG AGENT INGEST")
    print("==============================")

    # Check/create Pinecone index
    ensure_index()

    print("\nConnecting to Pinecone index...")

    index = pc.Index(INDEX_NAME)

    print("Connected successfully.")

    # -----------------------------------------------------
    # Find documentation files
    # -----------------------------------------------------

    files = (
        glob.glob("docs/**/*.md", recursive=True)
        + glob.glob("docs/**/*.txt", recursive=True)
    )

    print(f"\nFound {len(files)} documentation file(s).")

    if not files:
        print(
            "No files found in docs/. "
            "Add some .md or .txt files first."
        )
        return

    # -----------------------------------------------------
    # Process files
    # -----------------------------------------------------

    vectors = []

    for filepath in files:

        print(f"\nProcessing: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = chunk_text(text)

        print(f"  Created {len(chunks)} chunk(s).")

        for i, chunk in enumerate(chunks):

            print(
                f"  Creating embedding "
                f"{i + 1}/{len(chunks)}..."
            )

            vector_id = f"{filepath}-{i}"

            vector = {
                "id": vector_id,
                "values": embed(chunk),
                "metadata": {
                    "source": filepath,
                    "text": chunk
                }
            }

            vectors.append(vector)

    # -----------------------------------------------------
    # Upload vectors to Pinecone
    # -----------------------------------------------------

    print(f"\nTotal vectors to upload: {len(vectors)}")

    batch_size = 50

    for i in range(0, len(vectors), batch_size):

        batch = vectors[i:i + batch_size]

        print(
            f"Uploading vectors "
            f"{i + 1}-{i + len(batch)} "
            f"of {len(vectors)}..."
        )

        index.upsert(
            vectors=batch
        )

    # -----------------------------------------------------
    # Finished
    # -----------------------------------------------------

    print("\n==============================")
    print("INGESTION COMPLETE")
    print("==============================")

    print(
        f"Ingested {len(vectors)} chunks "
        f"from {len(files)} file(s) "
        f"into '{INDEX_NAME}'."
    )


# ---------------------------------------------------------
# Run program
# ---------------------------------------------------------

if __name__ == "__main__":
    main()