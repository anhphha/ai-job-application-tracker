RUBRIC_VERSION = "2.0"

CAREER_CRITERIA = {
    "transformation": {
        "weight": 0.25,
        "description": (
            "Does the role involve changing business processes, "
            "operating models, technology adoption, or ways of working?"
        )
    },

    "business_ownership": {
        "weight": 0.20,
        "description": (
            "Evaluate ownership of business problems and outcomes. "
            "Score 0 if the role mainly executes assigned technical tasks. "
            "Score 1 if the role identifies problems, recommends solutions, "
            "or contributes to outcomes but final ownership is unclear. "
            "Score 2 only if the role explicitly owns business outcomes, "
            "priorities, workstreams, or measurable results."
        )
    },

    "stakeholder_exposure": {
        "weight": 0.15,
        "description": (
        "Evaluate the level of stakeholder exposure. "
        "Score 0 if the role is mainly individual or technical-team work. "
        "Score 1 if the role works cross-functionally with business and "
        "technical stakeholders. "
        "Score 2 only if there is clear evidence of regular exposure to "
        "senior leaders, executives, steering groups, or enterprise-level "
        "decision makers."
        )
    },

    "data_relevance": {
        "weight": 0.15,
        "description": (
            "Does the role allow me to leverage my data and analytics "
            "background as an important part of the work?"
        )
    },

    "decision_influence": {
        "weight": 0.10,
        "description": (
            "Does the role influence recommendations, prioritization, "
            "resource allocation, or business decisions?"
        )
    },

    "change_adoption": {
        "weight": 0.10,
        "description": (
        "Evaluate responsibility for changing how people work and "
        "ensuring solutions are adopted. "
        "Score 0 if the role mainly builds or deploys technical solutions "
        "without explicit adoption responsibility. "
        "Score 1 if the role contributes to rollout, process change, "
        "training, user enablement, or adoption. "
        "Score 2 if the role explicitly owns significant change adoption, "
        "organizational implementation, or measurable adoption outcomes. "
        "Do not treat technical deployment to production alone as "
        "evidence of change adoption."
        )
    },

    "leadership_potential": {
        "weight": 0.05,
        "description": (
        "Evaluate leadership responsibility available through the role. "
        "Score 0 if no credible project, workstream, team, vendor, or "
        "people leadership responsibility is described. "
        "Score 1 if there is a credible path to leading projects, "
        "workstreams, vendors, or colleagues. "
        "Score 2 if meaningful leadership responsibility is explicitly "
        "part of the role. "
        "General company career development, training, or mentorship "
        "programs are not sufficient evidence of leadership potential."
        )
    }
}

total_weight = sum(
    criterion["weight"]
    for criterion in CAREER_CRITERIA.values()
)
