import pytest
from unittest.mock import MagicMock
from evict_pipeline import (
    Alert, Label, Decision, EvidencePack,
    Extractor, Verifier, Calibrator, Escalator, EvictPipeline
)

@pytest.fixture
def mock_pipeline():
    extractor = Extractor()
    verifier = MagicMock(spec=Verifier)
    calibrator = Calibrator(threshold=0.5)
    escalator = MagicMock(spec=Escalator)
    
    # Setup mocks
    verifier.get_decision.return_value = Decision(
        alert_id="test-1", label=Label.TP, confidence=0.9, rationale="LLM reasoning", stage="LLM"
    )
    
    return EvictPipeline(extractor, verifier, calibrator, escalator)

def test_pipeline_tp(mock_pipeline):
    mock_pipeline.escalator.escalate.side_effect = lambda a, d: d # Default pass-through
    alert = Alert(
        alert_id="test-1", cwe_id="CWE-89", description="SQLi", 
        file_path="src/main.py", line_number=10, analyzer_name="CodeQL",
        raw_sarif={}
    )
    
    decision = mock_pipeline.run(alert, project_root=".")
    
    assert decision.label == Label.TP
    assert decision.confidence == 0.9
    assert decision.stage == "Calibrated"

def test_pipeline_abstain_and_escalate(mock_pipeline):
    mock_pipeline.verifier.get_decision.return_value = Decision(
        alert_id="test-2", label=Label.TP, confidence=0.2, rationale="Uncertain", stage="LLM"
    )
    mock_pipeline.escalator.escalate.return_value = Decision(
        alert_id="test-2", label=Label.FP, confidence=0.2, rationale="SMT says no", stage="Symbolic"
    )
    
    alert = Alert(
        alert_id="test-2", cwe_id="CWE-78", description="OS Command Inj", 
        file_path="src/main.py", line_number=20, analyzer_name="CodeQL",
        raw_sarif={}
    )
    
    decision = mock_pipeline.run(alert, project_root=".")
    
    # Confidence 0.2 < threshold 0.5 -> Calibrator sets to ABSTAIN
    # Escalator then sets it to FP based on SMT
    assert decision.label == Label.FP
    assert decision.stage == "Symbolic"
