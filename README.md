# Hasamex Expert Call Intelligence

An AI-powered expert interview analysis application that analyzes three expert-call transcripts and provides grounded answers, supporting evidence, timestamps, cross-call themes, differences, and transcript-based Q&A.

## Overview

This application was built as part of the Hasamex technical case study.

The application analyzes expert interviews from:

* France
* Germany
* UK

Users can:

* Answer the provided interview guide questions for each expert
* Ask questions across all three transcripts
* Identify common themes across experts
* Identify differences and disagreements
* View supporting transcript evidence
* Trace evidence back to the original expert call and timestamp

The application is designed to reduce hallucination by retrieving transcript evidence before generating an answer and instructing the language model to use only the supplied evidence.

## Architecture

```text
Expert Transcripts
        |
        v
Transcript Parser
        |
        v
Structured Segments
(Call ID + Speaker + Timestamp + Text)
        |
        v
Local Embeddings
(sentence-transformers)
        |
        v
Semantic Retrieval
        |
        v
Relevant Transcript Evidence
        |
        v
Gemini
        |
        v
Grounded Answer
        |
        v
Streamlit UI
```

## Technology Stack

* Python
* Streamlit
* Google Gemini
* Google GenAI SDK
* Sentence Transformers
* NumPy
* Pydantic
* python-dotenv

## Project Structure

```text
hasamex-ai-case/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
├── data/
│   ├── france.txt
│   ├── germany.txt
│   └── uk.txt
│
└── src/
    ├── __init__.py
    ├── models.py
    ├── parser.py
    ├── retrieval.py
    └── llm.py
```

## How It Works

### 1. Transcript Parsing

Each transcript is parsed into structured segments containing:

* Call ID
* Timestamp
* Speaker
* Transcript text

This metadata is preserved throughout the application so that generated answers can be traced back to the original source.

### 2. Retrieval

The transcript segments are converted into vector embeddings using the local `all-MiniLM-L6-v2` sentence-transformer model.

When a user asks a question:

1. The question is converted into an embedding.
2. Semantic similarity is calculated against transcript segments.
3. The most relevant segments are retrieved.
4. These segments are provided to Gemini as evidence.

### 3. Grounded Generation

Gemini receives the user's question together with the retrieved transcript evidence.

The model is instructed to:

* Use only the supplied transcript evidence
* Not use outside knowledge
* Not invent facts
* Not invent quotes
* Keep answers concise

This creates an evidence-first RAG workflow.

### 4. Source Traceability

Retrieved evidence is displayed in the UI with:

* Expert/call
* Timestamp
* Speaker
* Original transcript text
* Similarity score

This allows the user to verify where the answer came from.

## Features

### Interview Guide

The application provides the six required interview guide questions for each expert:

1. What is the current adoption of robotic surgery?
2. What are the main barriers to adoption?
3. How important are hospital budgets and ROI?
4. How important are surgeon training and clinical outcomes?
5. What is the expected adoption trend over the next 3–5 years?
6. What is the typical hospital decision-making timeline?

### Cross-Call Analysis

The application compares all three expert interviews to identify:

* Common themes
* Differences and disagreements
* Overall areas of agreement and variation

The analysis is based only on the supplied transcript evidence.

### Ask Questions

Users can ask questions across all three transcripts using natural language.

Example:

```text
What are the main barriers to robotic surgery adoption?
```

The application retrieves relevant evidence and generates a grounded answer.

### Sources

The Sources section provides access to the parsed transcript segments from all three expert calls.

## Hallucination Reduction

The application uses several mechanisms to reduce unsupported answers:

1. **Evidence-first retrieval**
   Relevant transcript segments are retrieved before generation.

2. **Restricted generation**
   Gemini is explicitly instructed to use only the supplied evidence.

3. **No outside knowledge**
   The model is instructed not to introduce external information.

4. **Source visibility**
   Supporting transcript text, call ID, speaker, and timestamp are shown to the user.

5. **Prefer insufficient evidence over invention**
   The system is designed around the principle that unsupported information should not be generated.

## Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>
cd hasamex-ai-case
```

### 2. Create a virtual environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure the Gemini API key

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Do not commit the `.env` file to GitHub.

### 5. Run the application

```powershell
streamlit run app.py --server.fileWatcherType none
```

The application will open in the browser at:

```text
http://localhost:8501
```

## Usage

### Interview Guide

1. Open **Interview Guide**.
2. Select an expert.
3. Select an interview question.
4. Click **Analyze**.
5. Review the generated answer and retrieved evidence.

### Cross-Call Analysis

1. Open **Cross-Call Analysis**.
2. Click **Analyze All Experts**.
3. Review common themes and differences.
4. Expand the source evidence to verify the transcript segments.

### Ask Questions

1. Open **Ask Questions**.
2. Enter a question.
3. Click **Ask**.
4. Review the answer and supporting evidence.

## Scaling to 30+ Expert Calls

The current implementation is intentionally simple for the three-transcript case study.

For a larger production system, the same RAG architecture could be extended with:

* Asynchronous transcript ingestion
* Batch embedding generation
* A scalable vector database
* Metadata filtering by expert, country, interview, or topic
* Hybrid keyword + semantic retrieval
* Reranking of retrieved results
* Embedding and response caching
* Evaluation datasets and automated retrieval/answer evaluation
* Logging and observability
* Background processing for large transcript collections

The core workflow remains:

```text
Ingestion → Chunking → Embeddings → Retrieval → LLM → Evidence
```

## Design Principles

The application follows three main principles:

**Traceability**
Important answers should be traceable to the original transcript.

**Evidence-first generation**
The language model should generate from retrieved evidence rather than independently creating an answer.

**Simplicity**
The MVP uses a lightweight local retrieval setup and Streamlit UI so the complete workflow can be demonstrated clearly.

## Limitations

This is an MVP developed for the three-transcript technical case study.

Current limitations include:

* Retrieval is based on semantic similarity and may return partially relevant segments.
* The application uses a local embedding model rather than a production vector database.
* The current transcript format assumes timestamped speaker sections.
* Production-scale ingestion, evaluation, monitoring, and authentication are not implemented.

## Author

**Muzammil Kalghatgi**

AI Engineer | Generative AI | LLM Applications | RAG
