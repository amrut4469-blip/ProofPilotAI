
import streamlit as st
from ddgs import DDGS
from datetime import datetime

st.set_page_config(
    page_title="ProofPilot AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 ProofPilot AI")
st.caption("Research. Verify. Improve.")
st.write(
    "An AI research agent that gathers web sources, "
    "organizes evidence, and helps identify claims needing verification."
)

question = st.text_area(
    "What would you like to research?",
    placeholder="Example: What are the environmental effects of electric vehicles?"
)

max_results = st.slider(
    "Number of web sources to collect",
    min_value=3,
    max_value=8,
    value=5
)

if st.button("Start Investigation", type="primary"):
    if not question.strip():
        st.warning("Please enter a research question.")
    else:
        try:
            with st.spinner("Searching the web for relevant sources..."):
                results = list(
                    DDGS().text(
                        question.strip(),
                        max_results=max_results
                    )
                )

            st.subheader("Research Results")
            st.write(f"**Question:** {question.strip()}")
            st.write(f"**Search time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            if not results:
                st.warning(
                    "No results returned. Try a different question "
                    "or investigate again later."
                )
            else:
                for index, result in enumerate(results, start=1):
                    st.markdown(f"### {index}. {result.get('title', 'Untitled')}")
                    st.write(result.get("body", "No summary provided."))
                    url = result.get("href", "")
                    if url.startswith(("https://", "http://")):
                        st.markdown(f"[Open source]({url})")
                    st.divider()

                report = [
                    f"# ProofPilot AI Research Report",
                    f"Question: {question.strip()}",
                    f"Generated: {datetime.now().isoformat(timespec='seconds')}",
                    "",
                    "## Collected sources",
                    ""
                ]

                for index, result in enumerate(results, start=1):
                    report.extend([
                        f"### {index}. {result.get('title', 'Untitled')}",
                        result.get("body", "No summary provided."),
                        f"URL: {result.get('href', 'Unavailable')}",
                        ""
                    ])

                st.download_button(
                    "Download Research Report",
                    data="\n".join(report),
                    file_name="proofpilot_research_report.md",
                    mime="text/markdown"
                )

                st.info(
                    "These are collected search results, not independently "
                    "verified facts. Check the original sources before relying "
                    "on any claim. Claim comparison and automated verification "
                    "will be added in the next stage."
                )

        except Exception as error:
            st.error(
                "The web search failed. Check your internet connection "
                "and try again."
            )
            st.caption(f"Technical details: {error}")

