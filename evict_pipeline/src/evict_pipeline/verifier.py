import json
import os
import re
from typing import List, Optional, Tuple, Dict, Any
from collections import Counter
import openai
from .models import Alert, Decision, Label, EvidencePack

class Verifier:
    """LLM-based verification stage of the EVICT pipeline."""

    def __init__(self, api_key: str, model_name: Optional[str] = None, provider: str = "openai", base_url: Optional[str] = None, temperature: Optional[float] = None):
        self.api_key = api_key
        self.provider = provider.lower()
        self.model_name = model_name
        self.temperature = temperature if temperature is not None else 0.7

        if self.provider == "openai":
            self.model_name = self.model_name or "gpt-4o-mini"
            self.client = openai.OpenAI(api_key=api_key, base_url=base_url)

            # Restricted models that only support temperature=1.0
            if "nano" in self.model_name.lower() or self.model_name.lower().startswith("o1"):
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
            if "preview" in self.model_name.lower() or "experimental" in self.model_name.lower():
                version = "v1beta"
            elif "3." in self.model_name or "2.0" in self.model_name or "1.5" in self.model_name:
                version = "v1"
            else:
                version = "v1beta" # Fallback for others like 2.5

            self.client = genai.Client(api_key=api_key, http_options={"api_version": version})
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
                stage="LLM"
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
                stage="LLM"
            )

        majority_label, count = counts.most_common(1)[0]
        confidence = count / num_samples

        # Combine rationales for the majority label
        majority_rationales = [rat for lab, rat in responses if lab == majority_label]
        combined_rationale = "\n---\n".join(majority_rationales[:2]) # Keep top rationales

        return Decision(
            alert_id=alert.alert_id,
            label=majority_label,
            confidence=confidence,
            rationale=combined_rationale,
            stage="LLM",
            metadata={"vote_distribution": dict(counts), "provider": self.provider, "model": self.model_name}
        )

    def _build_prompt(self, alert: Alert) -> str:
        """Constructs a schema-guided prompt for the LLM."""
        ep = alert.evidence_pack

        # CWE-specific hints from IRIS
        hints = {
            "23": "Note: please be careful about defensing against absolute paths and \"..\" paths. Just canonicalizing paths might not be sufficient for the defense.",
            "78": "Note that other than typical Runtime.exec which is directly executing command, using Java Reflection to create dynamic objects with unsanitized inputs might also cause OS Command injection vulnerability.",
            "89": "Please be careful about reading possibly tainted SQL input. Look for SQL queries that are constructed using string concatenation or similar methods without proper sanitization."
        }

        # Extract numeric CWE to find hint (handling both "CWE89" and "CWE-89" or "89")
        cwe_num = re.sub(r'\D', '', str(alert.cwe_id)) if alert.cwe_id else ""
        hint = hints.get(cwe_num, "")

        # Juliet fallback for CWE23 (often labeled as CWE23 or CWE23_Relative_Path_Traversal)
        if not hint and alert.cwe_id and "23" in str(alert.cwe_id):
            hint = hints["23"]

        hint_text = f"\n### Security Expert Hint\n{hint}\n" if hint else ""

        # Build Evidence strings
        flow_text = "\n".join([f"  - {step}" for step in ep.flow_path]) if ep.flow_path else "  - No flow path available"
        constraints_text = "\n".join([f"  - {c}" for c in ep.path_constraints]) if ep.path_constraints else "  - No explicit path constraints extracted"

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

    def _sample_llm(self, prompt: str, num_samples: int) -> List[Tuple[Label, str]]:
        """Samples the LLM multiple times for self-consistency."""
        results = []
        for _ in range(num_samples):
            try:
                if self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model_name,
                        messages=[{"role": "user", "content": prompt}],
                        temperature=self.temperature
                    )
                    content = response.choices[0].message.content
                elif self.provider == "anthropic":
                    response = self.client.messages.create(
                        model=self.model_name,
                        max_tokens=1024,
                        temperature=self.temperature,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    content = response.content[0].text
                elif self.provider == "gemini":
                    from google import genai
                    config = genai.types.GenerateContentConfig(temperature=self.temperature)
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=config
                    )
                    content = response.text

                # Robust extraction of JSON from response
                # Handle ```json ... ``` blocks
                json_match = re.search(r"\{.*\}", content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group(0))
                    label_str = data.get("decision", "ABSTAIN").upper()
                    label = Label(label_str) if label_str in Label.__members__ else Label.ABSTAIN
                    rationale = data.get("rationale", "")
                    results.append((label, rationale))
                else:
                    results.append((Label.ABSTAIN, f"Could not find JSON in response: {content[:100]}..."))
            except Exception as e:
                results.append((Label.ABSTAIN, f"Error calling {self.provider}: {str(e)}"))
        return results
