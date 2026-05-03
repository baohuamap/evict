from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class Label(str, Enum):
    TP = "TP"
    FP = "FP"
    ABSTAIN = "ABSTAIN"

class EvidencePack(BaseModel):
    """Structured evidence extracted from analyzer output and code."""
    source_location: str
    sink_location: str
    flow_path: List[str]
    program_slice: str
    path_constraints: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Completeness flags
    flow_partial: bool = False
    constraints_missing: bool = False

class Alert(BaseModel):
    """Represents a static analysis alert."""
    alert_id: str
    cwe_id: str
    description: str
    file_path: str
    line_number: int
    analyzer_name: str
    raw_sarif: Dict[str, Any]
    evidence_pack: Optional[EvidencePack] = None

class Decision(BaseModel):
    """Final output of the EVICT pipeline."""
    alert_id: str
    label: Label
    confidence: float
    rationale: str
    stage: str # 'LLM', 'Calibrated', 'Symbolic'
    is_escalated: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
