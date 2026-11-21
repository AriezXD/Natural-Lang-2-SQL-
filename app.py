
import streamlit as st

from llm import generate_sql
from database import execute_query, get_schema, format_schema


# -------------------- PAGE CONFIGURATION --------------------

st.set_page_config(
    page_title="NL2SQL | AI SQL Assistant",
    page_icon="🗄️",
    layout="wide"
)


# -------------------- SESSION STATE --------------------

if "generated_sql" not in st.session_state:
    st.session_state.generated_sql = ""

if "query_results" not in st.session_state:
    st.session_state.query_results = None


# -------------------- HEADER --------------------

st.title("🗄️ NL2SQL")
st.caption(
    "Ask questions about your database in natural language "
    "and convert them into SQL queries using AI."
)

st.divider()


# -------------------- SIDEBAR --------------------

with st.sidebar:
    st.header("Database")

    st.success("Chinook SQLite Connected")

    if st.button("View Database Schema"):
        st.session_state.show_schema = not st.session_state.get(
            "show_schema", False
        )

    if st.session_state.get("show_schema", False):
        with st.expander("Database Schema", expanded=True):
            st.text(format_schema(get_schema()))

    st.divider()
    st.caption("AI Model: Google Gemini")
    st.caption("Database: SQLite")


# -------------------- QUESTION INPUT --------------------

st.subheader("Ask your database")

question = st.text_area(
    "Enter your question",
    placeholder=(
        "Example: Show me the top 5 customers by total spending\n"
        "Example: Brazil ke saare customers dikhao"
    ),
    height=110
)

if st.button("✨ Generate SQL", type="primary"):

    if not question.strip():
        st.warning("Please enter a question first.")

    else:
        try:
            with st.spinner("Understanding your question and generating SQL..."):
                sql = generate_sql(question)

            st.session_state.generated_sql = sql
            st.session_state.query_results = None

            st.success("SQL query generated successfully!")

        except Exception as e:
            st.error(f"SQL generation failed: {e}")


# -------------------- GENERATED SQL --------------------

if st.session_state.generated_sql:

    st.subheader("Generated SQL")

    edited_sql = st.text_area(
        "Review or edit the SQL query before execution",
        value=st.session_state.generated_sql,
        height=150
    )

    if st.button("▶ Execute SQL Query", type="primary"):

        try:
            with st.spinner("Executing SQL query..."):
                results = execute_query(edited_sql)

            st.session_state.query_results = results
            st.success("Query executed successfully!")

        except Exception as e:
            st.session_state.query_results = None
            st.error(f"Query execution failed: {e}")


# -------------------- QUERY RESULTS --------------------

if st.session_state.query_results is not None:

    st.subheader("Query Results")

    results = st.session_state.query_results

    if results:
        st.dataframe(results, use_container_width=True)
        st.caption(f"Returned {len(results)} rows.")

    else:
        st.info("The query executed successfully but returned no results.")


# -------------------- FOOTER --------------------

st.divider()

st.caption(
    "Built with Streamlit, Google Gemini, SQLite and SQLGlot."
)
