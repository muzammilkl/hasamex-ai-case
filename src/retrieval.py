from sentence_transformers import SentenceTransformer
import numpy as np

from src.models import TranscriptSegment


# Load the local embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


def prepare_documents(segments: list[TranscriptSegment]):
    """
    Convert transcript segments into retrieval documents.

    Interviewer questions are excluded because they should not
    be treated as evidence for answering user questions.
    """

    documents = []

    for segment in segments:

        # Do not use interviewer questions as evidence
        if segment.speaker.lower() == "interviewer":
            continue

        documents.append(
            {
                "text": segment.text,
                "metadata": {
                    "call_id": segment.call_id,
                    "timestamp": segment.timestamp,
                    "speaker": segment.speaker,
                },
            }
        )

    return documents


def cosine_similarity(vector_a, vector_b):
    """
    Calculate cosine similarity between two vectors.
    """

    vector_a = np.array(vector_a)
    vector_b = np.array(vector_b)

    denominator = (
        np.linalg.norm(vector_a)
        * np.linalg.norm(vector_b)
    )

    if denominator == 0:
        return 0.0

    return float(
        np.dot(vector_a, vector_b) / denominator
    )


def create_embeddings(documents):
    """
    Create embeddings for all transcript documents.
    """

    texts = [
        document["text"]
        for document in documents
    ]

    embeddings = model.encode(
        texts,
        normalize_embeddings=True
    )

    return embeddings


def search(
    question: str,
    documents,
    embeddings,
    top_k: int = 10
):
    """
    Find the most relevant transcript segments
    for a user question.

    We retrieve the top 10 candidates so that the LLM
    has enough relevant evidence to work with.
    """

    # Convert the question into an embedding
    question_embedding = model.encode(
        question,
        normalize_embeddings=True
    )

    # Calculate similarity between the question
    # and every transcript segment
    scores = np.dot(
        embeddings,
        question_embedding
    )

    # Get the highest-scoring documents
    top_indices = np.argsort(scores)[::-1][:top_k]

    results = []

    for index in top_indices:

        result = {
            "text": documents[index]["text"],
            "metadata": documents[index]["metadata"],
            "score": float(scores[index])
        }

        results.append(result)

    return results