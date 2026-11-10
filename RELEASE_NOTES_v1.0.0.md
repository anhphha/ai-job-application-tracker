# v1.0.0 — Portfolio Release Candidate

AI-assisted, human-in-the-loop job opportunity evaluation.

## Included
- Structured extraction and evidence-based seven-criterion assessment
- Rubric 2.1, assessment prompt 1.2-candidate, GPT-5.6
- Deterministic weighted scoring, human override/approval, SQLite persistence
- Frozen 10-job, 70-reference calibration dataset and repeat-run evaluation

## Evaluation
Three repeated runs: 194/210 agreements (92.38%). This is repeated calibration agreement, not held-out accuracy. Two case/criterion disagreements persisted in all runs (R04 Data Relevance and R07 Leadership Potential).

## Limitations
Small calibration set, ambiguous rubric boundaries, stochastic model outputs, and no held-out generalization study. Human review is required. Not an autonomous hiring decision system.

## Verification Status

Release verification was completed by the project maintainer on November 10, 2026.

The following checks were reported as successfully completed:

- Fresh environment installation and dependency checks
- Automated pytest suite
- Python syntax validation
- Streamlit application smoke test
- End-to-end workflow validation, including SQLite persistence

The release retains documented limitations regarding calibration dataset size, rubric ambiguity, and model variability.

**Release decision:** Approved for portfolio publication, subject to final Git repository security checks.
