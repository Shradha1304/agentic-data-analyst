import pandas as pd
import streamlit as st

from analyst.agent import run_agent

st.set_page_config(page_title="Agentic Data Analyst", page_icon="📊")
st.title("Agentic Data Analyst")

uploaded_file = st.file_uploader("Upload a CSV dataset", type=["csv"])
custom_task = st.text_area(
    "Analysis task",
    value="Explore the dataset and find the most interesting patterns and data quality issues.",
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    if st.button("Run analysis"):
        with st.spinner("Analyzing dataset..."):
            result = run_agent(df, custom_task)

        st.subheader("Summary")
        st.write(result["summary"])

        st.subheader("Grounding check")
        st.json(result["grounding_check"])

        st.subheader("Report")
        st.markdown(result["report"])

        if result.get("run_log_path"):
            st.caption(f"Run log: {result['run_log_path']}")

        with st.expander("Tool evidence"):
            for citation in result.get("citations", []):
                st.write(citation)
else:
    st.info("Upload a CSV file to begin.")
