import streamlit as st
from ddgs import DDGS
from datetime import datetime
from urllib.parse import urlparse
import re

st.set_page_config(
    page_title="ProofPilot AI",
    page_icon="🔎",
    layout="wide"
)

st.title("🔎 ProofPilot AI")
st.caption("Research. Compare Evidence. Reveal Uncertainty.")

st.write(
    "An AI research agent that collects multiple sources, "
    "compares their claims, and highlights evidence that needs "
    "further verification."
)

question = st.text_area(
    "What would you like to research?",
    placeholder="Example: What are the environmental effects of electric vehicles?"
)

max_results = st.slider(
    "Number of sources to collect",
    min_value=3,
    max_value=8,
    value=5
)


def make_queries(question):
    """Create several search queries around the user's question."""
    q = question.strip()
    return [
        q,
        f"{q} evidence research study",
        f"{q} limitations criticism"
    ]


def collect_sources(question, max_results):
    """Collect results from multiple searches and deduplicate URLs."""
    found = {}
    errors = []

    queries = make_queries(question)
    per_query = max(2, (max_results + len(queries) - 1) // len(queries))

    for query in queries:
        try:
            results = DDGS().text(query, max_results=per_query)

            for item in results:
                url = item.get("href", "").strip()
                if not url.startswith(("https://", "http://")):
                    continue

                if url not in found:
                    found[url] = {
                        "title": item.get("title", "Untitled"),
                        "body": item.get("body", "No summary available."),
                        "url": url,
                        "query": query
                    }

                if len(found) >= max_results:
                    break

        except Exception as error:
            errors.append(f"{query}: {error}")

        if len(found) >= max_results:
            break

    return list(found.values()), errors


def get_domain(url):
    """Return the hostname for display, not a trust score."""
    try:
        return urlparse(url).netloc.removeprefix("www.")
    except Exception:
        return "Unknown domain"


def find_shared_terms(text_a, text_b):
    """Find overlapping meaningful words as a simple comparison signal."""
    stop_words = {
        "about", "after", "again", "also", "among", "because",
        "before", "being", "between", "could", "does", "during",
        "from", "have", "into", "more", "most", "other", "over",
        "such", "than", "that", "their", "there", "these", "they",
        "this", "those", "through", "under", "using", "very",
        "what", "when", "where", "which", "while", "with", "would",
        "your", "study", "research", "evidence", "results"
    }

    words_a = set(re.findall(r"[a-zA-Z]{4,}", text_a.lower())) - stop_words
    words_b = set(re.findall(r"[a-zA-Z]{4,}", text_b.lower())) - stop_words

    return sorted(words_a & words_b)


if st.button("Start Investigation", type="primary"):
    if len(question.strip()) < 8:
        st.warning("Please enter a clear research question.")
    else:
        with st.spinner("Searching multiple queries for evidence..."):
            sources, errors = collect_sources(question, max_results)

        st.subheader("Investigation Summary")
        st.write(f"**Research question:** {question.strip()}")
        st.write(f"**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        st.write(f"**Unique sources collected:** {len(sources)}")

        if errors:
            st.warning(
                f"{len(errors)} search attempt(s) failed. "
                "The investigation will continue with available results."
            )

        if not sources:
            st.error(
                "No sources were collected. Check your internet connection "
                "or try a different question."
            )
        else:
            st.subheader("Collected Evidence")

            for index, source in enumerate(sources, start=1):
                st.markdown(f"### {index}. {source['title']}")
                st.caption(f"Source domain: {get_domain(source['url'])}")
                st.write(source["body"])
                st.markdown(f"[Open original source]({source['url']})")
                st.caption(f"Search query: {source['query']}")
                st.divider()

            st.subheader("Evidence Comparison")

            if len(sources) < 2:
                st.info(
                    "At least two sources are needed for comparison. "
                    "Try again with a broader question."
                )
            else:
                comparison_count = 0

                for i in range(len(sources)):
                    for j in range(i + 1, len(sources)):
                        shared = find_shared_terms(
                            sources[i]["title"] + " " + sources[i]["body"],
                            sources[j]["title"] + " " + sources[j]["body"]
                        )

                        with st.expander(
                            f"Compare source {i + 1} and source {j + 1}"
                        ):
                            st.write(f"**Source A:** {sources[i]['title']}")
                            st.write(f"**Source B:** {sources[j]['title']}")

                            if shared:
                                st.write(
                                    "**Overlapping terms:** "
                                    + ", ".join(shared[:12])
                                )
                                st.caption(
                                    "Shared terms indicate possible topic overlap, "
                                    "not proof that the sources agree."
                                )
                            else:
                                st.write(
                                    "No substantial shared terms detected by "
                                    "the basic comparison method."
                                )

                        comparison_count += 1

                        if comparison_count >= 10:
                            break

                    if comparison_count >= 10:
                        break

            report = [
                "# ProofPilot AI Research Report",
                "",
                f"Question: {question.strip()}",
                f"Generated: {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## Important limitation",
                (
                    "This prototype collects search-result summaries and "
                    "compares overlapping words. It does not establish truth, "
                    "source credibility, or factual agreement."
                ),
                "",
                "## Sources",
                ""
            ]

            for index, source in enumerate(sources, start=1):
                report.extend([
                    f"### {index}. {source['title']}",
                    source["body"],
                    f"Domain: {get_domain(source['url'])}",
                    f"URL: {source['url']}",
                    f"Search query: {source['query']}",
                    ""
                ])

            st.download_button(
                "Download Research Report",
                data="\n".join(report),
                file_name="proofpilot_research_report.md",
                mime="text/markdown"
            )

            st.info(
                "Evidence comparison is currently a simple keyword-overlap "
                "check, not an AI fact-check. Always open original sources "
                "before relying on a claim."
            )

