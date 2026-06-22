"""ComplianceRAG — Streamlit web application.

Run: streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))
from config import ANTHROPIC_API_KEY, TOP_K, FRAMEWORKS
from ingestion.document_loader import load_documents
from rag.vector_store import get_or_build_index
from rag.retriever import retrieve, format_context
from llm.chain import answer_question

# ──────────────────────────────────────────────────────────────── #
# Page setup
# ──────────────────────────────────────────────────────────────── #
st.set_page_config(
    page_title="ComplianceRAG",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("⚖️ ComplianceRAG")
st.caption("Ask natural-language questions against APRA CPS 234, ISO 27001, and SOC 2 documents.")

# ──────────────────────────────────────────────────────────────── #
# Sidebar configuration
# ──────────────────────────────────────────────────────────────── #
with st.sidebar:
    st.header("⚙️ Settings")

    framework = st.selectbox(
        "Regulatory Framework",
        options=list(FRAMEWORKS.keys()),
        index=3,  # Default: All
        help="Filter responses to a specific regulatory framework.",
    )

    top_k = st.slider("Chunks to Retrieve (k)", min_value=1, max_value=10, value=TOP_K)

    demo_mode = st.toggle(
        "Demo Mode (no API key needed)",
        value=not bool(ANTHROPIC_API_KEY),
        help="Demo mode uses canned answers. Disable to use live Anthropic API.",
    )

    if not demo_mode and not ANTHROPIC_API_KEY:
        st.warning("⚠️ ANTHROPIC_API_KEY not set. Please add it to .env or enable Demo Mode.")

    st.divider()
    st.subheader("📚 Loaded Frameworks")
    for fw in list(FRAMEWORKS.keys())[:-1]:  # Exclude "All"
        st.write(f"✅ {fw}")

    st.divider()
    run_eval = st.button("🧪 Run Retrieval Evaluation", use_container_width=True)

# ──────────────────────────────────────────────────────────────── #
# Index initialisation (cached)
# ──────────────────────────────────────────────────────────────── #
@st.cache_resource(show_spinner="Loading regulatory documents and building index...")
def load_rag_components():
    chunks = load_documents()
    index, metadata = get_or_build_index(chunks)
    return index, metadata


with st.spinner("Initialising ComplianceRAG..."):
    try:
        index, metadata = load_rag_components()
        index_loaded = True
    except Exception as exc:
        st.error(f"Failed to load index: {exc}")
        index_loaded = False

# ──────────────────────────────────────────────────────────────── #
# Evaluation panel
# ──────────────────────────────────────────────────────────────── #
if run_eval and index_loaded:
    from evaluation.evaluator import run_batch_eval

    with st.spinner("Running batch evaluation..."):
        eval_results = run_batch_eval(index, metadata, k=top_k)

    st.subheader("📊 Retrieval Evaluation Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Questions Evaluated", eval_results["total_questions"])
    col2.metric(f"Precision@{eval_results['k']}", f"{eval_results['mean_precision_at_k']:.1%}")
    col3.metric("Framework Accuracy", f"{eval_results['mean_framework_accuracy']:.1%}")

    import pandas as pd
    df = pd.DataFrame(eval_results["per_question"])
    st.dataframe(df[["id", "framework", "precision_at_k", "framework_accuracy"]], use_container_width=True)

# ──────────────────────────────────────────────────────────────── #
# Sample questions
# ──────────────────────────────────────────────────────────────── #
st.subheader("💡 Try a sample question")
sample_questions = [
    "What does CPS 234 require regarding information security capability?",
    "What are the notification obligations under APRA if a material breach occurs?",
    "How does ISO 27001 Annex A address access control?",
    "What logical access controls are required under SOC 2?",
    "Does CPS 234 require penetration testing?",
]
cols = st.columns(len(sample_questions))
selected_sample = None
for i, (col, q) in enumerate(zip(cols, sample_questions)):
    if col.button(f"Q{i+1}", key=f"sample_{i}", use_container_width=True, help=q):
        selected_sample = q

# ──────────────────────────────────────────────────────────────── #
# Question input
# ──────────────────────────────────────────────────────────────── #
st.subheader("🔍 Ask a compliance question")

default_question = selected_sample or ""
question = st.text_input(
    "Your question:",
    value=default_question,
    placeholder="e.g. What does CPS 234 require for third-party risk management?",
    label_visibility="collapsed",
)

ask_button = st.button("Ask", type="primary", use_container_width=False)

# ──────────────────────────────────────────────────────────────── #
# Answer display
# ──────────────────────────────────────────────────────────────── #
if (ask_button or selected_sample) and question and index_loaded:
    with st.spinner("Searching regulatory documents..."):
        framework_filter = framework if framework != "All" else None

        chunks = retrieve(
            query=question,
            index=index,
            metadata=metadata,
            top_k=top_k,
            framework_filter=framework_filter,
        )

        result = answer_question(question, chunks, demo_mode=demo_mode)

    # Answer panel
    confidence = result["confidence_notes"]
    confidence_color = {"HIGH": "🟢", "MEDIUM": "🟡", "LOW": "🔴"}.get(confidence, "⚪")

    st.subheader("📋 Answer")
    mode_badge = "🎭 Demo Mode" if result["demo_mode"] else "🤖 Live (Anthropic API)"
    st.caption(f"{mode_badge} | Confidence: {confidence_color} {confidence} | Framework filter: {framework}")

    st.markdown(result["answer"])

    # Source chunks expander
    with st.expander(f"📄 Source Chunks Retrieved ({len(chunks)} chunks)", expanded=False):
        for i, chunk in enumerate(chunks, 1):
            st.markdown(f"**Chunk {i}** — {chunk.get('framework', 'Unknown')} "
                        f"| Score: {chunk.get('score', 0):.3f}")
            st.text(chunk["text"][:400] + ("..." if len(chunk["text"]) > 400 else ""))
            st.divider()

elif not index_loaded:
    st.error("Index not loaded. Please check logs and ensure regulatory documents exist in ingestion/regulatory_docs/")

# ──────────────────────────────────────────────────────────────── #
# Footer
# ──────────────────────────────────────────────────────────────── #
st.divider()
st.caption(
    "ComplianceRAG | FAISS + Sentence-Transformers + Anthropic Claude | "
    "Frameworks: APRA CPS 234, ISO 27001:2022, SOC 2"
)
