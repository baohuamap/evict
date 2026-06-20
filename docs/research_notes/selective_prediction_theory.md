## TL;DR

Selective prediction provides formal risk versus coverage tradeoffs via a classifier-selector pair and PAC-style bounds; conformal prediction gives distribution-free, finite-sample prediction sets that convert into rejectors. Combine surrogate-consistency, conformal calibration, and score-based selection for EVICT. 

----

## Mathematical risk and PAC frameworks

Selective prediction is formalized by a prediction function and a selection (abstention) rule that trade accuracy for coverage, and several PAC-style results quantify generalization and rejection rates. The core frameworks specify selective risk (error conditioned on non‑abstention) and coverage (probability of predicting), and derive bounds on selective risk or rejection mass under realizable and agnostic regimes.

- **Selective classifier formalism** Definition of a selective classifier as a pair (f,g) with *selective risk* (error given g=1) and *coverage* (Pr[g=1]) appears in agnostic selective classification theory and is the basis for fast-rejection analyses [1].
- **Risk‑coverage guarantees** Optimal rejection strategies threshold the conditional risk/posterior; frameworks relate a target selective risk to an equivalent reject‑cost formulation [2].
- **One‑sided prediction and generalization** The one-sided prediction relaxation yields decoupled class-wise decision sets and provable generalization bounds that achieve near‑optimal coverage at high target accuracy levels [3].
- **Fast rejection rates and disagreement coefficient** In PAC settings, fast (O(1/m)) rejection mass bounds are obtained under bounds on Hanneke’s disagreement coefficient; these results link selective classification to disagreement‑based active learning [1].
- **Transductive and adversarial guarantees** Selective transductive learning provides PAC-style guarantees on test error and rejection even when test points are adversarially chosen, enabling selective classifiers with provable low rejection and error rates under bounded VC dimension [4].
- **Surrogate consistency and multiclass abstention** Predictor–rejector surrogate losses yield non‑asymptotic consistency bounds and hypothesis‑set specific guarantees for multiclass abstention, enabling rigorous two‑stage algorithms (train predictor, then learn rejector) with provable excess‑risk bounds [5].
- **Three‑way PAC generalization** Extensions of PAC learning to three‑way/abstention settings formalize learnability and generalization for three‑way decision systems, providing a theoretical bridge to selective prediction frameworks [6].

References supporting these formal statements appear above in the cited works [1] [2] [3] [4] [5] [6].

----

## Conformal prediction algorithms and finite‑sample guarantees

Conformal methods provide distribution‑free valid prediction sets and practical ways to turn set outputs into abstaining classifiers with finite‑sample error control. Inductive and full conformal variants trade computational cost for sharpness and validity.

- **Distribution‑free validity** Conformal predictors produce prediction sets with finite‑sample, distribution‑free marginal coverage guarantees, which can be converted into a rejector by accepting only singleton prediction sets for classification [7].
- **Full versus inductive conformal** Full conformal delivers sharper validity at higher computation, while inductive (split) conformal is practical and produces finite‑sample estimates of error versus reject rates; both yield error‑reject curves useful for setting operating points [7].
- **Risk control beyond miscoverage** Conformal risk control generalizes CP to control expected values of losses (not only miscoverage), enabling target guarantees for non‑monotonic and multidimensional risk measures where algorithm stability affects tightness of guarantees [8].
- **Applied conformal selection and hierarchical predictors** Hierarchical and stacked conformal predictors can produce empty sets (abstentions) or multi‑label sets and have been used to control automated decision risk and automate triage by abstaining when sets are empty or too large [9].
- **Practical conversion** Use of calibration (holdout) sets to compute nonconformity thresholds yields finite‑sample guarantees and error‑reject tradeoffs that are directly interpretable for operational decision thresholds [7].

These algorithmic and guarantee statements are grounded in the conformal prediction literature and extensions cited above [7] [8] [9].

----

## Calibration, abstention algorithms, and cost connections

Practical abstention requires calibrated confidence or learned rejectors; several algorithmic paradigms and cost‑sensitive connections are immediately adaptable for EVICT.

- **End‑to‑end rejector learning** Methods that learn predictor and rejector jointly (SelectiveNet) optimize the covered domain and empirically improve the risk‑coverage frontier by training an integrated selection head [10].
- **Score‑threshold selection and regularization** Strong performance can be achieved using classifier scores with principled selection thresholds plus entropy‑based regularizers to improve calibration and selective performance without architectural changes [11].
- **Training dynamics based selection** Monitoring disagreement over intermediate checkpoints during training yields selection signals that attain state‑of‑the‑art tradeoffs without special selection heads, useful for retrofit to existing models [12].
- **Portfolio and abstain class losses** Training with an explicit abstain class or portfolio-theory inspired loss (Deep Gamblers) provides an (m+1)-class formulation that learns to abstain end‑to‑end while quantifying disconfidence [13].
- **Discriminative uncertainty learning** Learning an uncertainty scoring function that preserves the ordering induced by conditional risk enables construction of near‑optimal rejection thresholds from discriminative models [2].
- **Cost‑sensitive mapping** The classical equivalence between a targeted selective risk and an explicit reject cost allows mapping cost‑sensitive objectives to risk‑coverage targets; surrogate‑based predictor–rejector frameworks formalize training under a predefined abstention cost [2] [5].

These algorithmic motifs and their theoretical or empirical justifications are supported in the cited works [10] [11] [12] [13] [2] [5].

----

## Evaluation metrics and experimental design

Designing evaluation metrics for selective systems should center on risk‑coverage tradeoffs and operating‑point visualizations; standard metrics map directly to the theoretical guarantees and calibration methods above.

Below is a concise comparison of commonly used selective evaluation metrics

| Metric | What it measures | Typical theoretical guarantee or use |
|---|---:|---|
| Selective risk | Error conditioned on examples the model chooses to predict | Targets are enforced in PAC or surrogate frameworks; used to set target risk constraints [1] [5] |
| Coverage | Fraction of instances the model predicts on | Direct complement to selective risk; used to read off operating points on risk‑coverage curves [7] |
| Error‑reject curve | Error as a function of rejection rate across thresholds | Empirical tool to visualize tradeoffs; conformal methods provide finite‑sample error estimates along this curve [7] |
| Rejection mass | Probability mass of points rejected by a pointwise‑competitive selective classifier | Appears in PCS analyses; fast rejection bounds (O(1/m)) are provable under disagreement coefficient assumptions [1] |
| Hierarchical risk‑coverage | Risk and coverage measured at different granularity levels (coarse to fine labels) | Formalized for hierarchical selective classification and used when varying specificity is permitted [14] |

- **Protocol recommendations** Use a held‑out calibration set for thresholding (inductive conformal or score calibration), report risk‑coverage and error‑reject curves, and evaluate Pareto fronts (degree of automation versus error) for operational choices [7] [9] [15].
- **Statistical reporting** When theoretical guarantees exist (conformal finite‑sample or PAC bounds), report the confidence level, sample sizes used for calibration, and any distributional assumptions or stability dependencies affecting the guarantee tightness [7] [8] [1].

The metrics and protocol guidance above are grounded in the cited works on selective and conformal evaluation and hierarchical variants [1] [7] [8] [9] [14].

----

## Recent deep learning advances and adaptation suggestions

Recent (2022–2025) empirical and theoretical advances produce practical building blocks for EVICT that combine deep models, calibration, and provable control.

- **Training dynamics and retrofit selection** Methods that use model training trajectories to compute selection signals enable integrating abstention without architectural changes and show strong empirical coverage gains on common benchmarks [12].
- **Representation‑level regularization** Confidence‑aware contrastive learning improves selective risk by shaping feature geometry, indicating that feature training can materially improve abstention performance in deep nets [16].
- **Model‑integrated rejectors and surrogate consistency** Joint predictor–rejector training with provable surrogate consistency gives an algorithmic recipe for multiclass abstention with non‑asymptotic guarantees [5].
- **Conformal deployments for automation** Hierarchical and practical conformal pipelines have been applied to automate decision processes while abstaining on high‑uncertainty cases, illustrating a path to combine CP calibration with selective classifiers for operational risk limits [9] [15].
- **PAC‑Bayes and certificate approaches** Recent PAC‑Bayes style certificates for large models offer another route to provable selective guarantees by comparing model scores to structured baselines and producing PAC‑valid bounds for selective coverage in LLM outputs [17].

Adaptation suggestions for EVICT
- **Combine conformal calibration with a learned selector** Use inductive conformal thresholds to get finite‑sample marginal guarantees and train a discriminator or rejector (selective head or score threshold) to respect desired coverage/risk tradeoffs [7] [10].
- **Use surrogate‑consistent two‑stage training** Train a high‑quality predictor with standard losses, then learn a rejector using surrogate losses with proven consistency to obtain hypothesis‑specific excess‑risk bounds [5].
- **Evaluate with risk‑coverage and error‑reject curves** Report Pareto fronts, use held‑out calibration for CP, and include hierarchical metrics when multi‑granularity decisions are relevant [7] [9] [14].
- **Leverage feature‑level regularizers** Adopt contrastive or entropy regularization to improve the separation of confident vs uncertain examples before constructing selection thresholds [16] [11].

The recent-methods and adaptation recommendations above are supported by the cited recent literature [12] [16] [5] [9] [15] [17].