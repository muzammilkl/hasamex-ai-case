import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")


client = genai.Client(
    api_key=api_key
)


def generate_answer(question: str, evidence: str):
    """
    Generate a grounded answer using only the supplied transcript evidence.

    The model is asked to return:
    - a concise answer
    - the supporting call
    - timestamp
    - exact quote
    """

    prompt = f"""
You are analyzing expert interview transcripts.

Answer the user's question using ONLY the transcript evidence provided below.

Rules:
- Do not use outside knowledge.
- Do not invent facts.
- Do not invent quotes.
- Do not change the wording of a quote.
- Use the transcript evidence as the source of truth.
- Select the evidence that directly supports the answer.
- Keep the answer concise.

Return your response in exactly this format:

ANSWER:
<1-3 sentence answer>

EVIDENCE:
CALL: <call id>
TIMESTAMP: <timestamp>
SPEAKER: <speaker>
QUOTE: "<exact quote copied from the evidence>"

USER QUESTION:
{question}

TRANSCRIPT EVIDENCE:
{evidence}
"""

    interaction = client.interactions.create(
        model="gemini-3.6-flash",
        input=prompt
    )

    return interaction.output_text