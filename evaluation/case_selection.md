# Regression Case Selection

## Purpose

The regression dataset is intentionally selected to test
career-direction rubric boundaries rather than represent a
random sample of job vacancies.

| Case | Archetype | Primary boundary |
|---|---|---|
| R01 | Data + AI Automation | Ownership / leadership |
| R02 | Data & AI Engineering | Deployment vs adoption |
| R03 | Data Platform / Fabric | Transformation vs technical modernization |
| R04 | AI Business Analysis | Decision influence |
| R05 | AI + Analytics | Decision influence / leadership |
| R06 | Pure Data Engineering | Technical vs business ownership |
| R07 | BI / Reporting | Decision support vs decision influence |
| R08 | Data/Digital Transformation | Genuine transformation and adoption |
| R09 | Strategy / Business Transformation | Strategic ownership and influence |
| R10 | Data + Business Hybrid | Ambiguity and confidence calibration |


R06
Company: Tribedo
Role: Senior Data Engineer

Archetype:
Pure / primarily technical Data Engineering

Primary stress tests:
- technical ownership vs business ownership
- technical modernization vs transformation
- decision support vs decision influence
- migration/deployment vs change adoption
- seniority vs leadership

Boundary case:
Transformation = 2 under Rubric 2.0,
but technical modernization vs broader
business transformation should be revisited
when evaluating Rubric 2.1.


R07 | Senior BI / Data-driven Management |
Decision support vs decision influence;
analytics responsibility vs business ownership

{
  "transformation": 2,
  "business_ownership": 1,
  "stakeholder_exposure": 2,
  "data_relevance": 2,
  "decision_influence": 1,
  "change_adoption": 1,
  "leadership_potential": 1
}

# Regression Dataset 1.1 — Review Package

This is a **candidate** reference package, not a frozen regression dataset.

- Existing R01–R05 reviewed references must be preserved from Dataset 1.0. Their full rationales are not reproduced here.
- New R06–R10 candidate references include evidence-based rationales.
- Three criterion reviews remain open: R08 stakeholder exposure; R10 business ownership; R10 decision influence.
- Do not expose AI assessment pages to the extraction/assessment model.
- Use the original job descriptions only as model input.
- After human adjudication, merge into your existing `evaluation/regression_cases.json`, bump `dataset_version` to `1.1`, and update the snapshot test to 10 cases / 70 criteria.
- Preserve rubric 2.0 and original scoring weights for the first run.
- The package does not claim to contain the complete original JDs or your local codebase.
