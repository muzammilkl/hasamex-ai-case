import streamlit as st

from src.parser import load_all_transcripts
from src.retrieval import (
    prepare_documents,
    create_embeddings,
    search
)
from src.llm import generate_answer, client


# --------------------------------------------------
# Page configuration
# --------------------------------------------------

st.set_page_config(
    page_title="Hasamex Expert Call Intelligence",
    page_icon="🔎",
    layout="wide"
)


# --------------------------------------------------
# Load transcripts
# --------------------------------------------------

transcripts = [
    ("france", "data/France.txt"),
    ("germany", "data/Germany.txt"),
    ("uk", "data/UK.txt"),
]


@st.cache_resource
def load_data():

    segments = load_all_transcripts(transcripts)

    documents = prepare_documents(segments)

    embeddings = create_embeddings(documents)

    return segments, documents, embeddings


segments, documents, embeddings = load_data()


# --------------------------------------------------
# Header
# --------------------------------------------------

st.title("🔎 Expert Call Intelligence")

st.write(
    "Analyze expert interviews, retrieve supporting evidence, "
    "and ask questions across the transcripts."
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Choose a section",
    [
        "Interview Guide",
        "Cross-Call Analysis",
        "Ask Questions",
        "Sources"
    ]
)


# ==================================================
# INTERVIEW GUIDE
# ==================================================

if page == "Interview Guide":

    st.header("Interview Guide")

    st.write(
        "Select an expert and an interview question."
    )

    expert = st.selectbox(
        "Expert",
        [
            "France",
            "Germany",
            "UK"
        ]
    )

    questions = [
        "What is the current adoption of robotic surgery?",
        "What are the main barriers to adoption?",
        "How important are hospital budgets and ROI?",
        "How important are surgeon training and clinical outcomes?",
        "What is the expected adoption trend over the next 3–5 years?",
        "What is the typical hospital decision-making timeline?"
    ]

    question = st.selectbox(
        "Interview Question",
        questions
    )

    if st.button("Analyze"):

        with st.spinner("Searching transcripts..."):

            expert_key = expert.lower()

            expert_question = (
                f"{question} Focus specifically on the {expert_key} expert."
            )

            results = search(
                question=expert_question,
                documents=documents,
                embeddings=embeddings,
                top_k=10
            )

            # Prefer results from the selected expert
            expert_results = [
                result
                for result in results
                if result["metadata"]["call_id"] == expert_key
            ]

            if expert_results:
                results = expert_results

            evidence_parts = []

            for result in results:

                evidence_parts.append(
                    f"""
Call: {result["metadata"]["call_id"]}
Timestamp: {result["metadata"]["timestamp"]}
Speaker: {result["metadata"]["speaker"]}
Text: {result["text"]}
"""
                )

            evidence = "\n".join(evidence_parts)

            answer = generate_answer(
                question=question,
                evidence=evidence
            )

        st.subheader("Answer")

        st.write(answer)

        st.subheader("Retrieved Evidence")

        for result in results[:5]:

            with st.expander(
                f'{result["metadata"]["call_id"].upper()} — '
                f'{result["metadata"]["timestamp"]}'
            ):

                st.write(
                    f'**Speaker:** '
                    f'{result["metadata"]["speaker"]}'
                )

                st.write(
                    f'**Similarity:** '
                    f'{result["score"]:.3f}'
                )

                st.write(result["text"])


# ==================================================
# CROSS-CALL ANALYSIS
# ==================================================

elif page == "Cross-Call Analysis":

    st.header("Cross-Call Analysis")

    st.write(
        "Compare the three expert interviews to identify "
        "common themes and differences."
    )

    if st.button("Analyze All Experts"):

        with st.spinner(
            "Analyzing France, Germany, and UK transcripts..."
        ):

            expert_segments = [
                segment
                for segment in segments
                if segment.speaker.lower() != "interviewer"
            ]

            evidence_parts = []

            for segment in expert_segments:

                evidence_parts.append(
                    f"""
Call: {segment.call_id}
Timestamp: {segment.timestamp}
Speaker: {segment.speaker}
Text: {segment.text}
"""
                )

            evidence = "\n".join(evidence_parts)

            prompt = f"""
You are analyzing three expert interview transcripts.

Your task is to compare ONLY the evidence provided below.

Do not use outside knowledge.
Do not invent facts.
Do not invent quotes.
Do not assume information that is not stated.

Identify:

1. Common Themes
   - Identify important topics that multiple experts discuss.
   - Explain how the experts describe each theme.
   - Include the relevant call and timestamp for the supporting evidence.

2. Disagreements or Differences
   - Identify areas where experts give different views, estimates,
     priorities, or conditions.
   - Clearly describe what each expert says.
   - Include the relevant call and timestamp.

3. Overall Comparison
   - Give a short factual summary of where the experts broadly
     agree and where their views differ.

Important:
Every important claim must be traceable to the transcript evidence.
Use the exact call names and timestamps provided.
Do not create quotations unless the quotation appears exactly
in the supplied transcript evidence.

Transcript Evidence:

{evidence}

Return the analysis using these headings:

## Common Themes

## Differences and Disagreements

## Overall Comparison
"""

            interaction = client.interactions.create(
                model="gemini-3.6-flash",
                input=prompt
            )

            analysis = interaction.output_text

        st.subheader("Analysis")

        st.markdown(analysis)

        st.subheader("Source Evidence")

        for segment in expert_segments:

            with st.expander(
                f"{segment.call_id.upper()} | "
                f"{segment.timestamp} | "
                f"{segment.speaker}"
            ):

                st.write(segment.text)


# ==================================================
# ASK QUESTIONS
# ==================================================

elif page == "Ask Questions":

    st.header("Ask Questions Across All Transcripts")

    question = st.text_input(
        "Enter your question",
        placeholder="What are the main barriers to robotic surgery adoption?"
    )

    if st.button("Ask") and question:

        with st.spinner("Searching expert transcripts..."):

            results = search(
                question=question,
                documents=documents,
                embeddings=embeddings,
                top_k=10
            )

            evidence_parts = []

            for result in results:

                evidence_parts.append(
                    f"""
Call: {result["metadata"]["call_id"]}
Timestamp: {result["metadata"]["timestamp"]}
Speaker: {result["metadata"]["speaker"]}
Text: {result["text"]}
"""
                )

            evidence = "\n".join(evidence_parts)

            answer = generate_answer(
                question=question,
                evidence=evidence
            )

        st.subheader("Answer")

        st.write(answer)

        st.subheader("Supporting Evidence")

        for result in results:

            with st.expander(
                f'{result["metadata"]["call_id"].upper()} | '
                f'{result["metadata"]["timestamp"]} | '
                f'{result["metadata"]["speaker"]}'
            ):

                st.write(result["text"])

                st.caption(
                    f'Similarity score: {result["score"]:.3f}'
                )


# ==================================================
# SOURCES
# ==================================================

elif page == "Sources":

    st.header("Transcript Sources")

    st.write(
        f"Loaded {len(segments)} transcript segments "
        f"across 3 expert calls."
    )

    for call_id in ["france", "germany", "uk"]:

        st.subheader(call_id.title())

        call_segments = [
            segment
            for segment in segments
            if segment.call_id == call_id
        ]

        for segment in call_segments:

            with st.expander(
                f"{segment.timestamp} — {segment.speaker}"
            ):

                st.write(segment.text)