from unittest.mock import MagicMock

import pytest

from evict_pipeline import (
    Alert,
    Calibrator,
    Decision,
    Escalator,
    EvictPipeline,
    EvidencePack,
    Extractor,
    Label,
    Verifier,
)


@pytest.fixture
def mock_pipeline():
    extractor = Extractor()
    verifier = MagicMock(spec=Verifier)
    calibrator = Calibrator(threshold=0.5)
    escalator = MagicMock(spec=Escalator)

    # Setup mocks
    verifier.get_decision.return_value = Decision(
        alert_id="test-1",
        label=Label.TP,
        confidence=0.9,
        rationale="LLM reasoning",
        stage="LLM",
    )

    return EvictPipeline(extractor, verifier, calibrator, escalator)


def test_pipeline_tp(mock_pipeline):
    mock_pipeline.escalator.escalate.side_effect = (
        lambda a, d: d
    )  # Default pass-through
    alert = Alert(
        alert_id="test-1",
        cwe_id="CWE-89",
        description="SQLi",
        file_path="src/main.py",
        line_number=10,
        analyzer_name="CodeQL",
        raw_sarif={},
    )

    decision = mock_pipeline.run(alert, project_root=".")

    assert decision.label == Label.TP
    assert decision.confidence == 0.9
    assert decision.stage == "Calibrated"


def test_pipeline_abstain_and_escalate(mock_pipeline):
    mock_pipeline.verifier.get_decision.return_value = Decision(
        alert_id="test-2",
        label=Label.TP,
        confidence=0.2,
        rationale="Uncertain",
        stage="LLM",
    )
    mock_pipeline.escalator.escalate.return_value = Decision(
        alert_id="test-2",
        label=Label.FP,
        confidence=0.2,
        rationale="SMT says no",
        stage="Symbolic",
    )

    alert = Alert(
        alert_id="test-2",
        cwe_id="CWE-78",
        description="OS Command Inj",
        file_path="src/main.py",
        line_number=20,
        analyzer_name="CodeQL",
        raw_sarif={},
    )

    decision = mock_pipeline.run(alert, project_root=".")

    # Confidence 0.2 < threshold 0.5 -> Calibrator sets to ABSTAIN
    # Escalator then sets it to FP based on SMT
    assert decision.label == Label.FP
    assert decision.stage == "Symbolic"


# --- Tests for the real symbolic escalation (Z3 + sanitization) ---


def _make_alert(slice_text, constraints):
    return Alert(
        alert_id="esc-test",
        cwe_id="CWE-89",
        description="SQLi",
        file_path="f.java",
        line_number=10,
        analyzer_name="CodeQL",
        raw_sarif={},
        evidence_pack=EvidencePack(
            source_location="s",
            sink_location="k",
            flow_path=["s", "k"],
            program_slice=slice_text,
            path_constraints=constraints,
        ),
    )


def test_escalator_unsat_guarded_path_is_fp():
    """Contradictory guards (UNSAT) -> FP (path infeasible)."""
    esc = Escalator()
    alert = _make_alert(
        "if (data < 0 && data > 0) { sink(data); }", ["data < 0 && data > 0"]
    )
    d = Decision(
        alert_id="esc-test",
        label=Label.ABSTAIN,
        confidence=0.3,
        rationale="uncertain",
        stage="LLM",
    )
    r = esc.escalate(alert, d)
    assert r.label == Label.FP
    assert r.is_escalated is True
    assert r.stage == "Symbolic"


def test_escalator_sat_feasible_path_is_tp():
    """Satisfiable guard (SAT) -> TP (vulnerability reachable)."""
    esc = Escalator()
    alert = _make_alert("if (data > 0) { sink(data); }", ["data > 0"])
    d = Decision(
        alert_id="esc-test",
        label=Label.ABSTAIN,
        confidence=0.3,
        rationale="uncertain",
        stage="LLM",
    )
    r = esc.escalate(alert, d)
    assert r.label == Label.TP
    assert r.is_escalated is True


def test_escalator_sanitization_detected_is_fp():
    """Sanitizer in the code slice -> FP (taint neutralized)."""
    esc = Escalator()
    alert = _make_alert(
        "String safe = data.replaceAll(bad, good); stmt.execute(safe);", []
    )
    d = Decision(
        alert_id="esc-test",
        label=Label.ABSTAIN,
        confidence=0.3,
        rationale="uncertain",
        stage="LLM",
    )
    r = esc.escalate(alert, d)
    assert r.label == Label.FP
    assert r.is_escalated is True


def test_escalator_no_signal_stays_abstain():
    """No constraints and no sanitizer -> remains ABSTAIN (no forced guess)."""
    esc = Escalator()
    alert = _make_alert("sink(data);", [])
    d = Decision(
        alert_id="esc-test",
        label=Label.ABSTAIN,
        confidence=0.3,
        rationale="uncertain",
        stage="LLM",
    )
    r = esc.escalate(alert, d)
    assert r.label == Label.ABSTAIN
    assert r.is_escalated is False


def test_escalator_prepared_statement_is_fp():
    """PreparedStatement is a sanitization pattern -> FP."""
    esc = Escalator()
    alert = _make_alert(
        "PreparedStatement ps = conn.prepareStatement(sql); ps.setString(1, data);", []
    )
    d = Decision(
        alert_id="esc-test",
        label=Label.ABSTAIN,
        confidence=0.3,
        rationale="uncertain",
        stage="LLM",
    )
    r = esc.escalate(alert, d)
    assert r.label == Label.FP


# --- Tests for the real conformal calibration ---


def test_calibrator_fit_threshold():
    """fit_threshold computes the q-hat quantile from calibration scores."""
    cal = Calibrator()
    scores = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    q_hat = cal.fit_threshold(scores, alpha=0.1)
    # q-hat should be a high quantile (>= 0.9 for alpha=0.1, n=10)
    assert q_hat >= 0.8
    assert q_hat <= 1.0


def test_calibrator_abstains_below_threshold():
    """Confidence below threshold -> ABSTAIN."""
    cal = Calibrator(threshold=0.5)
    d = Decision(
        alert_id="c", label=Label.TP, confidence=0.3, rationale="low conf", stage="LLM"
    )
    r = cal.calibrate(d)
    assert r.label == Label.ABSTAIN
    assert r.stage == "Calibrated"


def test_calibrator_accepts_above_threshold():
    """Confidence above threshold -> label retained."""
    cal = Calibrator(threshold=0.5)
    d = Decision(
        alert_id="c", label=Label.TP, confidence=0.8, rationale="high conf", stage="LLM"
    )
    r = cal.calibrate(d)
    assert r.label == Label.TP
    assert r.stage == "Calibrated"
