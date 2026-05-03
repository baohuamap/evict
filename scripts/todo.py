Planner Code plan:
```python
def main():
    # 1. Perform a deep literature search for state-of-the-art techniques relevant to the proposal
    # Focus on LLMs for static analysis, conformal prediction in alert triage, noise-robust learning for code, and SMT handling.
    search_scholarly_literature(query="LLM-based static analysis alert triage conformal prediction noise-robust learning SMT handling")

    # 2. Conduct a fresh NeurIPS-standard peer review on the existing proposal
    # This will generate a novelty report, reviewer reports, and a meta-review.
    review_paths = conduct_peer_review(file_path="/home/sandbox/Evidence-Conditioned LLM Investigation for Static-Analysis Alert Triage.pdf")

    # 3. Extract insights from the search results to strengthen the technical sections of the proposal
    # Specifically looking for details on conformal prediction algorithms and noise-robust learning in SE.
    extract_insights_from_search_results(
        questions=[
            "What are the best conformal prediction algorithms for classification/triage tasks in software engineering?",
            "How can LLM-based tools effectively handle SMT UNKNOWN results and extracted constraints for program analysis?",
            "Provide state-of-the-art methods for noise-robust learning and developer feedback loops in alert triage."
        ],
        return_reply_to_user=False
    )

    # 4. Use the write_report tool to generate the final improved research proposal
    # This step integrates:
    # - Original proposal content
    # - New peer review feedback (meta-review and reviewer reports)
    # - Literature search insights
    # - All MUST and SHOULD conditions (JPF instead of KLEE, conformal prediction, preliminary results, user studies, etc.)
    write_report(
        user_request="""Improve the research proposal 'Evidence-Conditioned LLM Investigation for Static-Analysis Alert Triage' for NeurIPS submission. 
        Address all feedback from the fresh peer review reports.
        Incorporate the following specific improvements:
        1. Add a Preliminary Results section with expected outcomes.
        2. Replace KLEE with JPF (Java PathFinder) to fix tool mismatch.
        3. Integrate a specific conformal prediction algorithm for alert triage.
        4. Detail constraint extraction processes and SMT UNKNOWN handling.
        5. Implement noise-robust learning strategies and a developer feedback mechanism.
        6. Expand on user study plans and considerations for real-world data.
        7. Ensure high-quality citations from the recent literature search results."""
    )

if __name__ == "__main__":
    main()
```