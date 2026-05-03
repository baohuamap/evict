import json
import sys
from pathlib import Path

# Add evict_pipeline to path
sys.path.append(str(Path(__file__).resolve().parent.parent / "evict_pipeline" / "src"))

from evict_pipeline.extractor import Extractor

def test_codeql_parsing():
    extractor = Extractor()
    sarif_path = "tests/sample_codeql.sarif"
    
    with open(sarif_path, "r") as f:
        sarif_data = json.load(f)
        
    alerts = extractor.extract_from_sarif(sarif_data)
    assert len(alerts) == 1
    alert = alerts[0]
    
    extractor.populate_evidence(alert, project_root=".")
    
    evidence = alert.evidence_pack
    print(f"Source: {evidence.source_location}")
    print(f"Sink: {evidence.sink_location}")
    print(f"Flow Path: {evidence.flow_path}")
    
    assert evidence.source_location == "src/main/java/com/example/App.java:10"
    assert evidence.sink_location == "src/main/java/com/example/App.java:50"
    assert len(evidence.flow_path) == 3
    assert "src/main/java/com/example/Utils.java:25" in evidence.flow_path
    print("Test passed!")

if __name__ == "__main__":
    test_codeql_parsing()
