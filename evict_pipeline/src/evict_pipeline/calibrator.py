import numpy as np
from typing import List, Optional
from .models import Decision, Label

class Calibrator:
    """Confidence calibration using conformal prediction."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold # This would be calibrated on a separate set (q-hat)

    def calibrate(self, decision: Decision) -> Decision:
        """Applies the calibration threshold to decide whether to accept or abstain."""
        # Nonconformity score A(x,y) = 1 - p(y|x) or 1 - v(y|x)
        # For vote share, confidence = v(y|x)
        nonconformity_score = 1.0 - decision.confidence
        
        # If the nonconformity score is too high (confidence too low), we abstain
        # In conformal prediction, we accept if A(x,y) <= threshold
        if nonconformity_score > self.threshold:
            decision.label = Label.ABSTAIN
            decision.rationale += f"\n[Calibration] Confidence {decision.confidence:.2f} below threshold (score {nonconformity_score:.2f} > {self.threshold:.2f})."
            decision.stage = "Calibrated"
        else:
            decision.stage = "Calibrated"
            
        return decision

    def fit_threshold(self, cal_scores: List[float], alpha: float = 0.1) -> float:
        """
        Computes the conformal threshold q-hat from calibration scores.
        alpha is the target error rate (e.g., 0.1 for 90% confidence).
        """
        n = len(cal_scores)
        # q-hat = ceiling((n+1)(1-alpha)) / n quantile
        q_level = np.ceil((n + 1) * (1 - alpha)) / n
        q_hat = np.quantile(cal_scores, q_level, interpolation='higher')
        self.threshold = q_hat
        return q_hat
