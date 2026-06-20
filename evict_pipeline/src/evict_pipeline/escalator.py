import os
import re
import subprocess
from typing import Any, Dict, List, Optional

from z3 import And, Bool, BoolVal, Int, Not, Or, Solver, String, sat, unknown, unsat

from .models import Alert, Decision, Label


class Escalator:
    """Symbolic verification stage invoked upon abstention or high risk.

    Resolves abstained LLM decisions by checking path feasibility with Z3 and
    detecting sanitization in the code slice. SAT (feasible path) -> TP, UNSAT
    (infeasible / guarded path) -> FP, UNKNOWN -> retained abstention. An
    optional JPF backend can be enabled via the JPF_HOME environment variable for
    deeper Java path feasibility analysis; when JPF is unavailable the Z3-based
    checker is used instead.
    """

    # Common Java sanitization patterns that neutralize taint before the sink.
    SANITIZER_PATTERNS = [
        (re.compile(r"\.replaceAll\s*\("), "string replaceAll sanitization"),
        (re.compile(r"\.replace\s*\("), "string replace sanitization"),
        (re.compile(r"\.substring\s*\("), "substring truncation"),
        (re.compile(r"\.escape\w*\s*\("), "explicit escaping"),
        (re.compile(r"\.sanitize\w*\s*\("), "explicit sanitization"),
        (re.compile(r"\.encode\w*\s*\("), "encoding"),
        (re.compile(r"\.validate\w*\s*\("), "validation"),
        (re.compile(r"PreparedStatement"), "parameterized SQL query"),
        (re.compile(r"\.setParameter\s*\("), "parameterized query binding"),
        (re.compile(r"Integer\.parseInt\s*\("), "integer parsing (type narrowing)"),
        (re.compile(r"Pattern\.matches\s*\("), "regex allowlist"),
        (re.compile(r"\.matches\s*\("), "regex match guard"),
        (re.compile(r"URLEncoder\.encode\s*\("), "URL encoding"),
        (re.compile(r"StringEscapeUtils\.escape\w*\s*\("), "commons-text escaping"),
        (re.compile(r"Encrypt\b"), "encryption barrier"),
    ]

    def __init__(self, timeout_ms: int = 5000):
        self.timeout_ms = timeout_ms

    def escalate(self, alert: Alert, decision: Decision) -> Decision:
        """Runs symbolic verification to correct or confirm LLM decisions."""
        if not alert.evidence_pack:
            return decision

        ep = alert.evidence_pack
        slice_text = ep.program_slice or ""

        # 1. Check for sanitization in the code slice (taint neutralization).
        sanitization = self._detect_sanitization(slice_text)
        if sanitization is not None:
            decision.label = Label.FP
            decision.rationale += f"\n[Escalation] Sanitization detected: {sanitization}. Taint neutralized before sink."
            decision.is_escalated = True
            decision.stage = "Symbolic"
            return decision

        # 2. Try Z3 SMT solver on extracted path constraints.
        if ep.path_constraints:
            smt_result = self._solve_smt(ep.path_constraints)
            if smt_result == "SAT":
                decision.label = Label.TP
                decision.rationale += "\n[Escalation] SMT Solver: SAT. Guarded path is feasible, taint reaches sink."
                decision.is_escalated = True
                decision.stage = "Symbolic"
                return decision
            elif smt_result == "UNSAT":
                decision.label = Label.FP
                decision.rationale += "\n[Escalation] SMT Solver: UNSAT. Path to sink is infeasible under guards."
                decision.is_escalated = True
                decision.stage = "Symbolic"
                return decision
            elif smt_result == "UNKNOWN":
                decision.rationale += (
                    "\n[Escalation] SMT Solver: UNKNOWN. Continued abstention."
                )
                decision.stage = "Symbolic"
                # fall through to JPF attempt

        # 3. Optionally invoke JPF for Java symbolic execution.
        if self._jpf_available():
            jpf_result = self._run_jpf(alert)
            if jpf_result == "SAT":
                decision.label = Label.TP
                decision.rationale += "\n[Escalation] JPF: path feasible."
                decision.is_escalated = True
                decision.stage = "Symbolic"
            elif jpf_result == "UNSAT":
                decision.label = Label.FP
                decision.rationale += "\n[Escalation] JPF: path infeasible."
                decision.is_escalated = True
                decision.stage = "Symbolic"
            elif jpf_result == "UNKNOWN":
                decision.rationale += (
                    "\n[Escalation] JPF: UNKNOWN. Continued abstention."
                )
                decision.stage = "Symbolic"
        elif ep.path_constraints:
            # Z3 already reported UNKNOWN and JPF is unavailable; keep abstention.
            pass

        return decision

    def _detect_sanitization(self, slice_text: str) -> Optional[str]:
        """Returns a description of the first detected sanitizer, or None."""
        if not slice_text:
            return None
        for pattern, description in self.SANITIZER_PATTERNS:
            if pattern.search(slice_text):
                return description
        return None

    def _solve_smt(self, constraints: List[str]) -> str:
        """Solves a list of Java boolean guard conditions using Z3.

        Each constraint is a Java boolean expression (e.g. ``data < 0``). We
        translate the common comparison/equality operators to Z3 over a single
        unbounded integer proxy variable ``data`` (the taint carrier). A path is
        SAT when the guards admit at least one value of ``data`` reaching the
        sink, and UNSAT when the guards contradict (e.g. ``data < 0 && data > 0``
        from an always-blocking guard).
        """
        solver = Solver()
        solver.set("timeout", self.timeout_ms)
        data = Int("data")
        translated = []
        for cond in constraints:
            z3_expr = self._java_cond_to_z3(cond, data)
            if z3_expr is not None:
                translated.append(z3_expr)
        if not translated:
            return "UNKNOWN"
        # The path reaches the sink only when ALL guards along it are satisfiable
        # simultaneously. If they are mutually contradictory, the path is blocked.
        solver.add(And(*translated))
        try:
            result = solver.check()
        except Exception:
            return "UNKNOWN"
        if result == sat:
            return "SAT"
        elif result == unsat:
            return "UNSAT"
        else:
            return "UNKNOWN"

    def _java_cond_to_z3(self, cond: str, data):
        """Translates a Java boolean condition to a Z3 expression over ``data``.

        Handles common comparison/equality/logical operators. Returns None when
        the condition cannot be reliably translated (string operations, method
        calls, etc.), which makes the caller treat the path as UNKNOWN.
        """
        c = cond.strip()
        # Strip enclosing parentheses for uniformity.
        while c.startswith("(") and c.endswith(")"):
            c = c[1:-1].strip()

        # Logical operators (split at top-level && / ||).
        if "&&" in c:
            parts = [p.strip() for p in self._split_top(c, "&&")]
            sub = [self._java_cond_to_z3(p, data) for p in parts]
            if any(s is None for s in sub):
                return None
            return And(*sub)
        if "||" in c:
            parts = [p.strip() for p in self._split_top(c, "||")]
            sub = [self._java_cond_to_z3(p, data) for p in parts]
            if any(s is None for s in sub):
                return None
            return Or(*sub)
        if c.startswith("!"):
            inner = self._java_cond_to_z3(c[1:].strip(), data)
            return Not(inner) if inner is not None else None

        # Comparison operators against integer literals, mapped onto ``data``.
        m = re.match(r"^(\w+)\s*(<=|>=|<|>|==|!=)\s*(-?\d+)\s*$", c)
        if m:
            var, op, val = m.group(1), m.group(2), int(m.group(3))
            # Only translate when the variable looks like the taint carrier.
            if var.lower() in ("data", "taint", "input", "value", "x", "n", "num", "i"):
                if op == "<=":
                    return data <= val
                if op == ">=":
                    return data >= val
                if op == "<":
                    return data < val
                if op == ">":
                    return data > val
                if op == "==":
                    return data == val
                if op == "!=":
                    return data != val
        # Equality/null checks we cannot model over an integer proxy -> UNKNOWN.
        return None

    @staticmethod
    def _split_top(expr: str, sep: str):
        """Splits ``expr`` on ``sep`` at parenthesis depth 0."""
        parts, depth, buf = [], 0, ""
        i = 0
        while i < len(expr):
            ch = expr[i]
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
            if depth == 0 and expr[i : i + len(sep)] == sep:
                parts.append(buf)
                buf = ""
                i += len(sep)
                continue
            buf += ch
            i += 1
        if buf:
            parts.append(buf)
        return parts

    def _jpf_available(self) -> bool:
        """Checks whether Java PathFinder is installed and runnable."""
        jpf_home = os.environ.get("JPF_HOME")
        if jpf_home and os.path.isdir(jpf_home):
            return True
        return False

    def _run_jpf(self, alert: Alert) -> str:
        """Runs Java PathFinder on the alert's source file.

        Requires JPF_HOME to point at a jpf-core installation. Builds a minimal
        JPF config targeting the alert's source file and reports SAT when JPF
        reaches the sink without a guard violation, UNSAT when the guard blocks
        execution, and UNKNOWN on timeout or setup failure.
        """
        jpf_home = os.environ.get("JPF_HOME")
        if not jpf_home:
            return "UNKNOWN"
        source_path = alert.file_path
        if source_path.startswith("file://"):
            source_path = source_path[7:]
        if not os.path.exists(source_path):
            return "UNKNOWN"
        try:
            result = subprocess.run(
                [
                    "java",
                    "-jar",
                    os.path.join(jpf_home, "build", "RunJPF.jar"),
                    "+target=" + os.path.splitext(os.path.basename(source_path))[0],
                    "+sourcepath=" + os.path.dirname(source_path),
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout_ms / 1000.0,
            )
            out = (result.stdout or "") + (result.stderr or "")
            if "no path to target" in out.lower() or "infeasible" in out.lower():
                return "UNSAT"
            if "property violated" in out.lower():
                return "SAT"
            return "UNKNOWN"
        except Exception:
            return "UNKNOWN"
