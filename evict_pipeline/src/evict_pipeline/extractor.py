import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from .models import Alert, EvidencePack


class Extractor:
    """Base class for evidence extraction from analyzer outputs."""

    def extract_from_sarif(self, sarif_data: Dict[str, Any]) -> List[Alert]:
        """Parses a SARIF file and returns a list of Alert objects."""
        alerts = []
        runs = sarif_data.get("runs", [])
        for run in runs:
            analyzer_name = run.get("tool", {}).get("driver", {}).get("name", "unknown")
            results = run.get("results", [])
            for res in results:
                alert_id = res.get("ruleId", "unknown")
                message = res.get("message", {}).get("text", "")

                # Basic location extraction
                locations = res.get("locations", [])
                primary_loc = locations[0] if locations else {}
                physical_loc = primary_loc.get("physicalLocation", {})
                artifact_loc = physical_loc.get("artifactLocation", {})
                file_path = artifact_loc.get("uri", "")
                region = physical_loc.get("region", {})
                line_number = region.get("startLine", 0)

                alert = Alert(
                    alert_id=alert_id,
                    cwe_id=self._extract_cwe_id(res),
                    description=message,
                    file_path=file_path,
                    line_number=line_number,
                    analyzer_name=analyzer_name,
                    raw_sarif=res,
                )
                alerts.append(alert)
        return alerts

    def _extract_cwe_id(self, result: Dict[str, Any]) -> str:
        """Heuristic for extracting CWE ID from SARIF results."""
        rule_id = result.get("ruleId", "")
        if "CWE" in rule_id:
            return rule_id.split("-")[-1]  # e.g. "CWE-89" -> "89"
        return "Unknown"

    def populate_evidence(self, alert: Alert, project_root: str):
        """
        Populates EvidencePack with data from SARIF and source code.
        Following Step 2 of the EVICT workflow:
        - Extract code slices
        - Extract data flow traces
        - Extract path constraints
        """
        # 1. Extract Data Flow Traces (from SARIF codeFlows)
        flow_path = []
        raw_sarif = alert.raw_sarif
        code_flows = raw_sarif.get("codeFlows", [])
        if code_flows:
            thread_flows = code_flows[0].get("threadFlows", [])
            if thread_flows:
                locations = thread_flows[0].get("locations", [])
                for loc_wrapper in locations:
                    loc = loc_wrapper.get("location", {})
                    phys_loc = loc.get("physicalLocation", {})
                    art_loc = phys_loc.get("artifactLocation", {})
                    uri = art_loc.get("uri", "unknown")
                    line = phys_loc.get("region", {}).get("startLine", 0)
                    flow_path.append(f"{uri}:{line}")

        if not flow_path:
            flow_path = [f"{alert.file_path}:{alert.line_number}"]

        # 2. Extract Code Slices
        program_slice = self._get_code_context(alert, project_root)

        # 3. Extract Path Constraints (from code slice guard conditions)
        path_constraints = self._extract_path_constraints(
            alert, flow_path, program_slice
        )

        alert.evidence_pack = EvidencePack(
            source_location=flow_path[0],
            sink_location=flow_path[-1],
            flow_path=flow_path,
            program_slice=program_slice,
            path_constraints=path_constraints,
            flow_partial=len(flow_path) <= 1,
            constraints_missing=not path_constraints,
        )

    def _extract_path_constraints(
        self, alert: Alert, flow_path: List[str], program_slice: str
    ) -> List[str]:
        """
        Extracts path constraints (guard conditions) from the code slice along
        the taint flow. A path constraint is a boolean condition from an
        if/while/for statement that must hold for execution to reach the sink.

        Constraints are returned as normalized Java boolean expressions so the
        Escalator can translate them to SMT. This is a lightweight regex-based
        extraction rather than a full AST traversal (JDT/Clang), which suffices
        for the structured Juliet test cases and provides a useful signal for
        real-world alerts where codeFlows identify the guarded region.
        """
        constraints: List[str] = []
        slice_text = alert.evidence_pack.program_slice if alert.evidence_pack else ""
        if not slice_text or slice_text.startswith("//"):
            return constraints

        sink_line = alert.line_number
        # Match if/while/for conditions: keyword ( ... )
        guard_re = re.compile(
            r"^\s*(?:if|while|for)\s*\((.+)\)\s*\{?\s*$",
            re.MULTILINE,
        )
        for m in guard_re.finditer(slice_text):
            cond = m.group(1).strip()
            # 'for' loops often include init/update clauses; keep only the condition
            if cond.count(";") >= 2:
                parts = cond.split(";")
                cond = parts[1].strip() if len(parts) > 1 and parts[1].strip() else ""
            if not cond:
                continue
            # Skip trivially-true conditions
            if cond in ("true", "false"):
                continue
            constraints.append(cond)
        return constraints

    def _get_code_context(
        self, alert: Alert, project_root: str, context_lines: int = 50
    ) -> str:
        """Reads code around the alert location for initial evidence."""
        try:
            path = alert.file_path
            if path.startswith("file://"):
                path = path[7:]

            # If path is absolute, use it directly. Otherwise, join with project_root.
            if os.path.isabs(path):
                full_path = path
            else:
                full_path = os.path.join(project_root, path)

            # Fast path for Juliet Java sources: SARIF URIs look like
            # 'juliet/testcases/CWE89_.../Foo.java' but the actual files live
            # under data/juliet_java/juliet-cwe{N}/src/main/java/{uri}.
            # Trying this prefix first avoids a slow rglob over ~40k files.
            if not os.path.exists(full_path):
                cwe_match = re.search(r"CWE(\d+)", path)
                if cwe_match:
                    cwe_num = cwe_match.group(1)
                    juliet_candidate = os.path.join(
                        project_root,
                        "data",
                        "juliet_java",
                        f"juliet-cwe{cwe_num}",
                        "src",
                        "main",
                        "java",
                        path,
                    )
                    if os.path.exists(juliet_candidate):
                        full_path = juliet_candidate

            # Fallback search if file is not found
            if not os.path.exists(full_path):
                filename = os.path.basename(path)
                # Search specifically in data/juliet_java first for speed, then project_root
                juliet_root = os.path.join(project_root, "data", "juliet_java")
                matches = (
                    list(Path(juliet_root).rglob(filename))
                    if os.path.exists(juliet_root)
                    else []
                )
                if not matches:
                    matches = list(Path(project_root).rglob(filename))

                if matches:
                    full_path = str(matches[0])
                else:
                    return f"// Could not read source file: {path}"

            with open(full_path, "r") as f:
                lines = f.readlines()
                # Juliet files are typically small enough to include entirely (~100-300 lines)
                if len(lines) < 600:
                    return "".join(lines)

                start = max(0, alert.line_number - context_lines)
                end = min(len(lines), alert.line_number + context_lines)
                return "".join(lines[start:end])
        except Exception as e:
            return f"// Error reading source file: {e}"
