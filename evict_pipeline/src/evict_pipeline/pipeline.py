from typing import List, Dict, Any, Optional
from .models import Alert, Decision, Label
from .extractor import Extractor
from .verifier import Verifier
from .calibrator import Calibrator
from .escalator import Escalator

class EvictPipeline:
    """End-to-end EVICT pipeline."""

    def __init__(self, extractor: Extractor, verifier: Verifier, calibrator: Calibrator, escalator: Escalator):
        self.extractor = extractor
        self.verifier = verifier
        self.calibrator = calibrator
        self.escalator = escalator

    def run(self, alert: Alert, project_root: str) -> Decision:
        """
        Runs the full EVICT triage on a single alert following the 6-step workflow:
        1. Input static analyzer alert with code context
        2. EvidencePack construction: extract code slices, data flow traces, path constraint
        3. LLM reasoning: guide prompting with evidence
        4. Calibration module
        5. Selective decision
        6. Output
        """
        
        # Step 1: Input (alert is passed as argument)
        
        # Step 2: EvidencePack construction
        self.extractor.populate_evidence(alert, project_root)
        
        # Step 3: LLM reasoning: guide prompting with evidence
        llm_decision = self.verifier.get_decision(alert)
        
        # Step 4: Calibration module
        calibrated_decision = self.calibrator.calibrate(llm_decision)
        
        # Step 5: Selective decision (Abstention and Escalation)
        if calibrated_decision.label == Label.ABSTAIN:
            final_decision = self.escalator.escalate(alert, calibrated_decision)
        else:
            final_decision = calibrated_decision
            
        # Step 6: Output
        return final_decision

    def run_on_sarif(self, sarif_file: str, project_root: str) -> List[Decision]:
        """Runs the pipeline on all alerts in a SARIF file."""
        import json
        with open(sarif_file, "r") as f:
            sarif_data = json.load(f)
            
        alerts = self.extractor.extract_from_sarif(sarif_data)
        results = []
        for alert in alerts:
            results.append(self.run(alert, project_root))
            
        return results
