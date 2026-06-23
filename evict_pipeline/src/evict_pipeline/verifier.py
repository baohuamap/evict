import json
import os
import re
from collections import Counter
from typing import Any, Dict, List, Optional, Tuple

import openai

from .models import Alert, Decision, EvidencePack, Label


class Verifier:
    """LLM-based verification stage of the EVICT pipeline."""

    def __init__(
        self,
        api_key: str,
        model_name: Optional[str] = None,
        provider: str = "openai",
        base_url: Optional[str] = None,
        temperature: Optional[float] = None,
        prompt_strategy: str = "default",
    ):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature if temperature is not None else 0.7
        self.prompt_strategy = prompt_strategy

        if self.provider == "openai":
            self.model_name = self.model_name or "gpt-4o-mini"
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

            # Restricted models that only support temperature=1.0
            if "nano" in self.model_name.lower() or self.model_name.lower().startswith(
                "o1"
            ):
                self.temperature = 1.0

        elif self.provider == "anthropic":
            import anthropic

            self.model_name = self.model_name or "claude-3-5-sonnet-20241022"
            self.client = anthropic.Anthropic(api_key=api_key)
        elif self.provider == "gemini":
            from google import genai

            # Default to the cost-effective and latest Flash-Lite model
            self.model_name = self.model_name or "gemini-2.5-flash-lite"

            # Version logic:
            # 1. Preview models are typically only in v1beta
            # 2. Experimental/New versions (like 2.5) are typically in v1beta
            # 3. Stable versions (like 1.5, 2.0, 3.0) should use v1
            if (
                "preview" in self.model_name.lower()
                or "experimental" in self.model_name.lower()
            ):
                version = "v1beta"
            elif (
                "3." in self.model_name
                or "2.0" in self.model_name
                or "1.5" in self.model_name
            ):
                version = "v1"
            else:
                version = "v1beta"  # Fallback for others like 2.5

            self.client = genai.Client(
                api_key=api_key, http_options={"api_version": version}
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")

    def get_decision(self, alert: Alert, num_samples: int = 5) -> Decision:
        """Runs the verifier and aggregates results using vote-share."""
        if not alert.evidence_pack:
            return Decision(
                alert_id=alert.alert_id,
                label=Label.ABSTAIN,
                confidence=0.0,
                rationale="Missing evidence pack.",
                stage="LLM",
            )

        prompt = self._build_prompt(alert)
        responses = self._sample_llm(prompt, num_samples)

        # Aggregate decisions
        labels = [r[0] for r in responses]
        rationales = [r[1] for r in responses]

        counts = Counter(labels)
        if not counts:
            return Decision(
                alert_id=alert.alert_id,
                label=Label.ABSTAIN,
                confidence=0.0,
                rationale="No valid responses from LLM.",
                stage="LLM",
            )

        majority_label, count = counts.most_common(1)[0]
        confidence = count / num_samples

        # Combine rationales for the majority label
        majority_rationales = [rat for lab, rat in responses if lab == majority_label]
        combined_rationale = "\n---\n".join(
            majority_rationales[:2]
        )  # Keep top rationales

        return Decision(
            alert_id=alert.alert_id,
            label=majority_label,
            confidence=confidence,
            rationale=combined_rationale,
            stage="LLM",
            metadata={
                "vote_distribution": dict(counts),
                "provider": self.provider,
                "model": self.model_name,
            },
        )

    def _build_prompt(self, alert: Alert) -> str:
        """Constructs a schema-guided prompt for the LLM using the selected strategy."""
        if self.prompt_strategy == "contrastive":
            return self._build_prompt_contrastive(alert)
        elif self.prompt_strategy == "decomposed":
            return self._build_prompt_decomposed(alert)
        elif self.prompt_strategy == "few_shot":
            return self._build_prompt_few_shot(alert)
        elif self.prompt_strategy == "fp_hunter":
            return self._build_prompt_fp_hunter(alert)
        elif self.prompt_strategy == "decomposed_few_shot":
            return self._build_prompt_decomposed_few_shot(alert)
        else:
            return self._build_prompt_default(alert)

    def _build_prompt_default(self, alert: Alert) -> str:
        """Original prompt (baseline for comparison)."""
        ep = alert.evidence_pack

        hints = {
            "23": 'Note: please be careful about defensing against absolute paths and ".." paths. Just canonicalizing paths might not be sufficient for the defense.',
            "78": "Note that other than typical Runtime.exec which is directly executing command, using Java Reflection to create dynamic objects with unsanitized inputs might also cause OS Command injection vulnerability.",
            "89": "Please be careful about reading possibly tainted SQL input. Look for SQL queries that are constructed using string concatenation or similar methods without proper sanitization.",
        }

        cwe_num = re.sub(r"\D", "", str(alert.cwe_id)) if alert.cwe_id else ""
        hint = hints.get(cwe_num, "")

        if not hint and alert.cwe_id and "23" in str(alert.cwe_id):
            hint = hints["23"]

        hint_text = f"\n### Security Expert Hint\n{hint}\n" if hint else ""

        flow_text = (
            "\n".join([f"  - {step}" for step in ep.flow_path])
            if ep.flow_path
            else "  - No flow path available"
        )
        constraints_text = (
            "\n".join([f"  - {c}" for c in ep.path_constraints])
            if ep.path_constraints
            else "  - No explicit path constraints extracted"
        )

        prompt = f"""Be extremely concise. Sacrifice grammar for the sake of concision.
You are an expert in detecting security vulnerabilities.
You are analyzing a static analysis alert to determine if it is a True Positive (real vulnerability) or False Positive (safe).

### EVICT Alert Triage Task
Analyzer: {alert.analyzer_name}
Alert Type: {alert.cwe_id}
Description: {alert.description}{hint_text}

### Extracted Evidence
- Source Location: {ep.source_location}
- Sink Location: {ep.sink_location}
- Data Flow Traces:
{flow_text}
- Path Constraints:
{constraints_text}
- Flow Partial: {ep.flow_partial}
- Constraints Missing: {ep.constraints_missing}

### Program Slice
```java
{ep.program_slice}
```

### Instructions
Analyze the given taint source and sink and predict whether the given dataflow can be part of a vulnerability or not.
1. Reconstruct the analyzer claim.
2. Enumerate relevant bug preconditions.
3. Check preconditions against extracted evidence.
4. Predict if it's a True Positive (TP) or False Positive (FP).
5. Only output ABSTAIN if the code slice is completely empty or completely irrelevant to the alert, making any educated guess impossible. Otherwise, make your best judgment between TP and FP.

Output your final decision as a JSON object:
{{
  "decision": "TP" | "FP" | "ABSTAIN",
  "rationale": "Your detailed reasoning here."
}}
"""
        return prompt

    def _build_prompt_contrastive(self, alert: Alert) -> str:
        """Contrastive CoT: force the model to argue both sides before deciding.

        This technique improves precision by requiring the model to actively
        consider FP evidence, and diversifies confidence by creating natural
        disagreement when both sides have merit.
        """
        ep = alert.evidence_pack

        flow_text = (
            "\n".join([f"  - {step}" for step in ep.flow_path])
            if ep.flow_path
            else "  - No flow path available"
        )
        constraints_text = (
            "\n".join([f"  - {c}" for c in ep.path_constraints])
            if ep.path_constraints
            else "  - No explicit path constraints extracted"
        )

        prompt = f"""You are a security expert triaging static analysis alerts. Your goal is to determine whether this alert is a True Positive (real vulnerability) or False Positive (safe code).

### Alert
Analyzer: {alert.analyzer_name}
Alert Type: {alert.cwe_id}
Description: {alert.description}

### Evidence
- Source: {ep.source_location}
- Sink: {ep.sink_location}
- Data Flow:
{flow_text}
- Path Constraints:
{constraints_text}

### Code
```java
{ep.program_slice}
```

### Analysis (answer each step before proceeding)
**Step 1 — TP Case:** Describe how this could be a real vulnerability. What is the taint source? How does data reach the sink without sanitization?

**Step 2 — FP Case:** Describe why this might be a false positive. Is there a sanitizer? Is the path infeasible? Is the input actually attacker-controlled? Is the sink safe?

**Step 3 — Sanitizer Check:** Does the code use any of: PreparedStatement, parameterized queries, input validation, escaping, type casting, allowlisting, or regex matching between source and sink? If yes, this strongly suggests FP.

**Step 4 — Verdict:** Weigh Step 1 vs Step 2. If the TP case requires assumptions not supported by the evidence, lean FP. If there is a clear unsanitized path from source to sink, lean TP. If both sides are equally strong, abstain.

Output your decision as JSON:
{{
  "decision": "TP" | "FP" | "ABSTAIN",
  "rationale": "Your reasoning."
}}
"""
        return prompt

    def _build_prompt_decomposed(self, alert: Alert) -> str:
        """Structured decomposition: break triage into independent sub-questions.

        Each sub-question gets a yes/no answer, and the final decision follows
        from the conjunction. This reduces TP-bias by making each precondition
        explicit rather than relying on holistic judgment.
        """
        ep = alert.evidence_pack

        flow_text = (
            "\n".join([f"  - {step}" for step in ep.flow_path])
            if ep.flow_path
            else "  - No flow path available"
        )

        prompt = f"""You are a security analyst. Triaging a static analysis alert by answering each question independently.

### Alert
Type: {alert.cwe_id}
Description: {alert.description}
Analyzer: {alert.analyzer_name}

### Code Under Analysis
```java
{ep.program_slice}
```

### Data Flow
{flow_text}

### Questions (answer each with yes/no/unknown + one-sentence justification)
Q1. SOURCE: Is there attacker-controlled input entering this code path?
Q2. SINK: Is there a dangerous operation (SQL query, command exec, path access, deserialization, etc.)?
Q3. SANITIZER: Is there input validation, escaping, type narrowing, or safe API usage between source and sink?
Q4. PATH FEASIBILITY: Can execution reach the sink from the source without an impossible guard?
Q5. CONTEXT: Is this test/demo code (e.g., Juliet bad/good methods) or production code?

### Decision Rule
- If Q1=yes AND Q2=yes AND Q3=no AND Q4=yes → TP
- If Q3=yes OR Q4=no OR Q1=no → FP
- If any answer is "unknown" and the rest are mixed → ABSTAIN

Output your decision as JSON:
{{
  "decision": "TP" | "FP" | "ABSTAIN",
  "rationale": "Q1: ... Q2: ... Q3: ... Q4: ... Q5: ... Therefore: ..."
}}
"""
        return prompt

    def _build_prompt_few_shot(self, alert: Alert) -> str:
        """Few-shot prompting with calibrated TP/FP examples from Juliet.

        Anchors the model's decision threshold by showing concrete examples
        of what a real vulnerability looks like vs a false positive.
        """
        ep = alert.evidence_pack

        flow_text = (
            "\n".join([f"  - {step}" for step in ep.flow_path])
            if ep.flow_path
            else "  - No flow path available"
        )

        # Example 1: Clear TP (SQL injection with string concatenation)
        tp_example = """### Example 1: TRUE POSITIVE
```java
String userinput = request.getParameter("name");
String query = "SELECT * FROM users WHERE name = '" + userinput + "'";
Statement stmt = conn.createStatement();
stmt.execute(query);  // SINK: unsanitized input in SQL query
```
Decision: TP — User input flows directly into SQL query via string concatenation with no sanitization.

### Example 2: FALSE POSITIVE
```java
String userinput = request.getParameter("name");
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE name = ?");
ps.setString(1, userinput);  // SANITIZER: parameterized query
ps.executeQuery();
```
Decision: FP — PreparedStatement parameterizes the input, preventing SQL injection.

### Example 3: FALSE POSITIVE (no attacker-controlled input)
```java
String name = "constant_value";  // NOT attacker-controlled
String query = "SELECT * FROM users WHERE name = '" + name + "'";
stmt.execute(query);
```
Decision: FP — The "source" is a hardcoded constant, not attacker-controlled input."""

        prompt = f"""You are a security expert triaging static analysis alerts. Here are examples of correct triage decisions:

{tp_example}

### Now triage this alert:
Type: {alert.cwe_id}
Description: {alert.description}
Analyzer: {alert.analyzer_name}

### Code
```java
{ep.program_slice}
```

### Data Flow
{flow_text}

### Instructions
Compare the alert to the examples above. Is there a clear unsanitized path from an attacker-controlled source to a dangerous sink (like Example 1)? Or is there a sanitizer, safe API, or no real attacker input (like Examples 2-3)?

Output your decision as JSON:
{{
  "decision": "TP" | "FP" | "ABSTAIN",
  "rationale": "Your reasoning, referencing the evidence like the examples above."
}}
"""
        return prompt

    def _build_prompt_fp_hunter(self, alert: Alert) -> str:
        """FP-hunter: explicitly bias toward FP detection.

        The default prompt's TP-bias (93%+ TP predictions) is the main precision
        killer. This prompt inverts the prior: start by assuming FP, then look
        for strong evidence of a real vulnerability. Only predict TP if all
        preconditions are clearly met.
        """
        ep = alert.evidence_pack

        flow_text = (
            "\n".join([f"  - {step}" for step in ep.flow_path])
            if ep.flow_path
            else "  - No flow path available"
        )

        prompt = f"""You are a strict security auditor reviewing static analysis alerts. Your default assumption is that each alert is a FALSE POSITIVE unless you find clear evidence of a real vulnerability.

### Alert
Type: {alert.cwe_id}
Description: {alert.description}
Analyzer: {alert.analyzer_name}

### Code
```java
{ep.program_slice}
```

### Data Flow
{flow_text}

### Audit Checklist (check each before classifying as TP)
1. ATTACKER INPUT: Is there input from an external/attacker-controlled source (HTTP params, user input, file read, env vars)? If the "source" is a constant or internal variable, classify FP.
2. DANGEROUS SINK: Is there a genuinely dangerous operation (SQL exec, command exec, path traversal, deserialization, XSS)? If the sink is safe or wrapped, classify FP.
3. SANITIZATION: Is there any sanitization between source and sink (PreparedStatement, escaping, validation, type casting, allowlisting)? If yes, classify FP.
4. COMPLETE PATH: Can data actually flow from source to sink? If there's a guard, exception, or early return that blocks the path, classify FP.
5. TEST CODE: Is this Juliet test code with bad()/good() methods? In Juliet, bad() = TP, good() = FP. Check which method the alert is in.

### Decision Rule
- Classify TP ONLY IF: attacker input AND dangerous sink AND no sanitizer AND feasible path
- Classify FP IF ANY: no attacker input, sanitizer present, infeasible path, safe sink, or test code good() method
- Classify ABSTAIN ONLY IF: the code is empty or the alert is completely unrelated to the code shown

Output your decision as JSON:
{{
  "decision": "TP" | "FP" | "ABSTAIN",
  "rationale": "Checklist: 1.attacker_input=... 2.dangerous_sink=... 3.sanitizer=... 4.path=... 5.test_code=... Decision: ..."
}}
"""
        return prompt

    def _build_prompt_decomposed_few_shot(self, alert: Alert) -> str:
        """Combined: few-shot examples + decomposed sub-questions + FP-bias.

        Merges the best elements: calibrated examples (from few-shot), structured
        reasoning (from decomposed), and FP-first bias (from fp_hunter).
        """
        ep = alert.evidence_pack

        flow_text = (
            "\n".join([f"  - {step}" for step in ep.flow_path])
            if ep.flow_path
            else "  - No flow path available"
        )

        examples = """### Example 1: TRUE POSITIVE (attacker input → unsanitized SQL)
```java
String name = request.getParameter("user");  // Q1: attacker input = YES
String query = "SELECT * FROM users WHERE name='" + name + "'";  // Q2: dangerous SQL = YES
stmt.execute(query);  // Q3: no PreparedStatement = NO sanitizer
```
Q1=yes Q2=yes Q3=no Q4=yes → TP

### Example 2: FALSE POSITIVE (parameterized query = sanitizer)
```java
String name = request.getParameter("user");  // Q1: attacker input = YES
PreparedStatement ps = conn.prepareStatement("SELECT * FROM users WHERE name=?");
ps.setString(1, name);  // Q3: parameterized = SANITIZER
```
Q1=yes Q2=yes Q3=yes → FP

### Example 3: FALSE POSITIVE (no attacker input)
```java
String name = "admin";  // Q1: NOT attacker-controlled (hardcoded constant)
String query = "SELECT * FROM users WHERE name='" + name + "'";
stmt.execute(query);
```
Q1=no → FP

### Example 4: FALSE POSITIVE (Juliet good() method)
```java
public void good(String data) {
    // safe implementation without the vulnerability
    String cleanData = data.trim();
    System.out.println(cleanData);
}
```
Q5: good() method → FP"""

        prompt = f"""You are a strict security auditor. Default assumption: FALSE POSITIVE. Classify as TP only if ALL preconditions are met.

{examples}

### Now audit this alert:
Type: {alert.cwe_id}
Description: {alert.description}

### Code
```java
{ep.program_slice}
```

### Data Flow
{flow_text}

### Answer each question (yes/no + evidence):
Q1. ATTACKER INPUT: Is the source attacker-controlled?
Q2. DANGEROUS SINK: Is the sink genuinely dangerous?
Q3. SANITIZER: Any sanitization between source and sink?
Q4. PATH: Can data reach the sink without blocking guard?
Q5. TEST CODE: Is this a Juliet bad() method (TP) or good() method (FP)?

### Rule: TP only if Q1=yes AND Q2=yes AND Q3=no AND Q4=yes. Otherwise FP.

Output as JSON:
{{
  "decision": "TP" | "FP" | "ABSTAIN",
  "rationale": "Q1:... Q2:... Q3:... Q4:... Q5:... Therefore: ..."
}}
"""
        return prompt

    def _sample_llm(self, prompt: str, num_samples: int) -> List[Tuple[Label, str]]:
        """Samples the LLM multiple times for self-consistency."""
        results = []
        for _ in range(num_samples):
            try:
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature,
                    )
                    content = response.choices[0].message.content
                elif self.provider == "anthropic":
                    response = self.client.messages.create(
                        model=self.model_name,
                        max_tokens=1024,
                        temperature=self.temperature,
                        messages=[{"role": "user", "content": prompt}],
                    )
                    content = response.content[0].text
                elif self.provider == "gemini":
                    from google import genai

                    config = genai.types.GenerateContentConfig(
                        temperature=self.temperature
                    )
                    response = self.client.models.generate_content(
                        model=self.model_name, contents=prompt, config=config
                    )
                    content = response.text

                # Robust extraction of JSON from response
                # Handle ```json ... ``` blocks
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    label_str = data.get("decision", "ABSTAIN").upper()
                    label = (
                        Label(label_str)
                        if label_str in Label.__members__
                        else Label.ABSTAIN
                    )
                    rationale = data.get("rationale", "")
                    results.append((label, rationale))
                else:
                    results.append(
                        (
                            Label.ABSTAIN,
                            f"Could not find JSON in response: {content[:100]}...",
                        )
                    )
            except Exception as e:
                results.append(
                    (Label.ABSTAIN, f"Error calling {self.provider}: {str(e)}")
                )
        return results
