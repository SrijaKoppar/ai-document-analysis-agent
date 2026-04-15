"""
Streamlit Frontend — Document Analysis Agent
Upload PDF/Excel/CSV → see the agent classify, plan, and analyze in real time.
"""
import streamlit as st
import requests
import json
import os

# ── Config ────────────────────────────────────────────────────
API_URL = os.getenv("API_URL", "http://localhost:8000")

# ── Page Setup ────────────────────────────────────────────────
st.set_page_config(
    page_title="Document Analysis Agent",
    page_icon="📄",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #888;
        font-size: 1.1rem;
        margin-top: 0;
    }
    .skill-badge {
        display: inline-block;
        padding: 4px 12px;
        margin: 3px;
        border-radius: 16px;
        background: #1a1a2e;
        color: #667eea;
        font-size: 0.85rem;
        border: 1px solid #667eea;
    }
    .plan-step {
        padding: 8px 16px;
        margin: 4px 0;
        border-left: 3px solid #667eea;
        background: #f8f9fa;
        border-radius: 0 8px 8px 0;
    }
    .metric-card {
        padding: 16px;
        border-radius: 12px;
        background: linear-gradient(135deg, #667eea22, #764ba222);
        border: 1px solid #667eea44;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────
st.markdown('<p class="main-header">📄 Document Analysis Agent</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">AI-powered document analysis with reusable agent skills • Powered by Ollama + Gemma</p>', unsafe_allow_html=True)
st.divider()

# ── Sidebar: Skill Registry ──────────────────────────────────
with st.sidebar:
    st.header("🧩 Skill Registry")
    try:
        skills_resp = requests.get(f"{API_URL}/skills", timeout=5)
        if skills_resp.status_code == 200:
            skills_data = skills_resp.json()
            st.metric("Registered Skills", skills_data["total_skills"])
            for skill in skills_data["skills"]:
                with st.expander(f"🔧 {skill['name']}"):
                    st.write(skill["description"])
                    st.caption(f"Input: {skill['input_schema']}")
                    st.caption(f"Output: {skill['output_schema']}")
        else:
            st.warning("Could not load skills. Is the API running?")
    except requests.exceptions.ConnectionError:
        st.error("⚠️ API not reachable. Start with:\n`uvicorn app.main:app --reload`")

    st.divider()
    st.header("ℹ️ How It Works")
    st.markdown("""
    1. **Upload** a PDF, Excel, or CSV file
    2. **Choose** your analysis query
    3. The agent **classifies** the document type
    4. A **dynamic planner** selects the right skills
    5. Skills execute in sequence
    6. A **verifier** checks the output quality
    """)

# ── Main Content ──────────────────────────────────────────────
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["pdf", "xlsx", "xls", "csv"],
        help="Supported formats: PDF, Excel (.xlsx/.xls), CSV",
    )

    query_presets = {
        "📝 Summarize document": "Summarize this document",
        "❓ Extract questions": "Extract all questions from this document",
        "📋 Extract form fields": "Extract all form fields from this document",
        "📊 Analyze tables": "Extract and analyze tables in this document",
        "🔍 Full analysis": "Provide a detailed summary and extract any questions, form fields, and tables",
    }

    selected_preset = st.selectbox("Analysis type", list(query_presets.keys()))
    custom_query = st.text_input(
        "Or write a custom query:",
        value=query_presets[selected_preset],
    )

    analyze_btn = st.button("🚀 Analyze", type="primary", use_container_width=True)

with col2:
    if uploaded_file and analyze_btn:
        with st.spinner("🤖 Agent is analyzing your document..."):
            try:
                files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                data = {"query": custom_query}
                response = requests.post(
                    f"{API_URL}/analyze",
                    files=files,
                    data=data,
                    timeout=300,  # LLM calls can be slow
                )

                if response.status_code == 200:
                    result = response.json()

                    if "error" in result:
                        st.error(f"❌ Error: {result['error']}")
                    else:
                        # ── Metrics row ──
                        m1, m2, m3, m4 = st.columns(4)
                        with m1:
                            st.metric("📄 File Type", result.get("file_type", "?").upper())
                        with m2:
                            st.metric("🏷️ Doc Type", result.get("doc_type", "?").title())
                        with m3:
                            st.metric("📄 Pages", result.get("total_pages", "N/A"))
                        with m4:
                            st.metric("🧩 Skills Used", len(result.get("plan", [])))

                        st.divider()

                        # ── Agent Plan ──
                        st.subheader("🗺️ Execution Plan")
                        for i, skill_name in enumerate(result.get("plan", []), 1):
                            st.markdown(
                                f'<div class="plan-step">Step {i}: <b>{skill_name}</b></div>',
                                unsafe_allow_html=True,
                            )

                        st.divider()

                        # ── Summary ──
                        if "summary" in result:
                            st.subheader("📝 Document Summary")
                            if result.get("method"):
                                st.caption(
                                    f"Method: {result['method']} | "
                                    f"Chunks: {result.get('chunks_processed', 'N/A')}"
                                )
                            st.markdown(result["summary"])

                        # ── Structured Summary ──
                        if "structured_summary" in result:
                            st.subheader("🔍 Structured Summary")
                            try:
                                struct = json.loads(result["structured_summary"])
                                st.json(struct)
                            except (json.JSONDecodeError, TypeError):
                                st.code(result["structured_summary"])

                        # ── Questions ──
                        if "questions" in result:
                            st.subheader("❓ Extracted Questions")
                            try:
                                q_data = result["questions"]
                                if isinstance(q_data, str):
                                    q_data = json.loads(q_data)
                                if isinstance(q_data, dict) and "questions" in q_data:
                                    questions = q_data["questions"]
                                    st.metric("Total Questions", q_data.get("total_questions", len(questions)))
                                    for q in questions:
                                        with st.expander(f"Q{q.get('question_number', '?')}: {q.get('text', '')[:80]}..."):
                                            st.write(f"**Type:** {q.get('type', 'N/A')}")
                                            st.write(f"**Section:** {q.get('section', 'N/A')}")
                                            if q.get("options"):
                                                st.write(f"**Options:** {', '.join(q['options'])}")
                                            st.write(f"**Required:** {'Yes' if q.get('required') else 'No'}")
                                else:
                                    st.json(q_data)
                            except (json.JSONDecodeError, TypeError):
                                st.code(str(result["questions"]))

                        # ── Form Fields ──
                        if "form_fields" in result:
                            st.subheader("📋 Form Fields")
                            try:
                                ff_data = result["form_fields"]
                                if isinstance(ff_data, str):
                                    ff_data = json.loads(ff_data)
                                st.json(ff_data)
                            except (json.JSONDecodeError, TypeError):
                                st.code(str(result["form_fields"]))

                        # ── Tables ──
                        if "tables" in result and result.get("total_tables", 0) > 0:
                            st.subheader("📊 Extracted Tables")
                            st.metric("Tables Found", result["total_tables"])
                            for table in result["tables"]:
                                with st.expander(f"Table {table.get('table_number', '?')} ({table.get('row_count', '?')} rows)"):
                                    if table.get("headers") and table.get("rows"):
                                        import pandas as pd
                                        df = pd.DataFrame(table["rows"], columns=table["headers"][:len(table["rows"][0])] if table.get("headers") else None)
                                        st.dataframe(df)
                                    else:
                                        st.json(table)

                        # ── Excel Sheets ──
                        if "sheets" in result:
                            st.subheader("📊 Excel Sheet Analysis")
                            for sheet in result["sheets"]:
                                with st.expander(f"📋 {sheet['sheet_name']} ({sheet['row_count']} rows, {sheet['column_count']} cols)"):
                                    st.write(f"**Columns:** {', '.join(sheet['columns'])}")
                                    if sheet.get("numeric_stats"):
                                        st.write("**Numeric Stats:**")
                                        st.json(sheet["numeric_stats"])
                                    if sheet.get("missing_values"):
                                        st.warning(f"Missing values: {sheet['missing_values']}")
                                    if sheet.get("sample_data"):
                                        st.write("**Sample Data:**")
                                        import pandas as pd
                                        st.dataframe(pd.DataFrame(sheet["sample_data"]))

                        st.divider()

                        # ── Verification ──
                        if "verification" in result:
                            st.subheader("✅ Verification Report")
                            v = result["verification"]
                            status = v.get("verification_status", "N/A")
                            if status == "PASS":
                                st.success(f"Verification: {status}")
                            elif status == "NEEDS_REVIEW":
                                st.warning(f"Verification: {status}")
                            else:
                                st.info(f"Verification: {status}")

                            if v.get("overall_score"):
                                vc1, vc2, vc3, vc4 = st.columns(4)
                                with vc1:
                                    st.metric("Accuracy", f"{v.get('accuracy_score', '?')}/10")
                                with vc2:
                                    st.metric("Completeness", f"{v.get('completeness_score', '?')}/10")
                                with vc3:
                                    st.metric("Quality", f"{v.get('quality_score', '?')}/10")
                                with vc4:
                                    st.metric("Overall", f"{v.get('overall_score', '?')}/10")

                            if v.get("issues_found"):
                                st.write("**Issues found:**")
                                for issue in v["issues_found"]:
                                    st.write(f"• {issue}")

                            if v.get("suggestions"):
                                st.info(f"💡 {v['suggestions']}")

                        # ── Agent Logs ──
                        with st.expander("📋 Agent Execution Logs"):
                            for log in result.get("logs", []):
                                icon = "✅" if log.get("status") == "ok" else "❌" if log.get("status") == "error" else "▶"
                                st.text(f"[{log['timestamp']}] {icon} {log['step']}  {log.get('detail', '')}")

                else:
                    st.error(f"API returned status {response.status_code}: {response.text}")

            except requests.exceptions.ConnectionError:
                st.error("❌ Cannot connect to API. Make sure it's running:\n`uvicorn app.main:app --reload`")
            except requests.exceptions.Timeout:
                st.error("⏱️ Request timed out. The document may be too large.")
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

    elif not uploaded_file:
        st.info("👈 Upload a document and click **Analyze** to get started.")
