"""Frozen Rubric 2.1 Strict Hybrid, approved 2026-11-08."""

RUBRIC_VERSION = '2.1'

CAREER_CRITERIA = {
 'transformation':
    {
        'weight': .25,
        'description': 'Does the role materially change processes, operating models, technology adoption or ways of working? Score 0: routine delivery/maintenance without explicit change. Score 1: contributes to a defined improvement, migration or change initiative. Score 2: transformation or material modernization is central to responsibilities, with explicit delivery of changed processes, capabilities or ways of working. Do not infer organization-wide authority from participation.'
    },
 'business_ownership':
    {
        'weight': .20,
        'description': 'Score 0: executes assigned tasks without meaningful business problem responsibility. Score 1: identifies business problems, recommends solutions or owns technical/analytics delivery, but business outcome or business-workstream accountability is unclear. Score 2: explicitly accountable for a business outcome, business priority, measurable benefit or end-to-end business workstream. Ownership of an analytics domain, dashboard or technical workflow alone is not business ownership unless explicit business accountability is attached.'
    },
 'stakeholder_exposure':
    {
        'weight': .15,
        'description': 'Score 0: mainly independent or within a technical team; generic communication does not establish business stakeholder exposure. Score 1: explicit cross-functional engagement with business stakeholders or occasional senior leadership contact. Score 2: explicit sustained or role-inherent collaboration with senior leaders, executives, steering groups or enterprise decision makers. A named ongoing partnership/reporting line can establish regularity; mere mention of presenting once or communicating with leadership cannot.'
    },
 'data_relevance':
    {
        'weight': .15,
        'description': 'HYBRID: score the importance of an explicit data/analytics/AI mandate AND its connection to business decisions, performance or transformation. Score 0: no meaningful mandate or substantive use of data/analytics capabilities; generic research, finance or strategy analysis alone is insufficient. Score 1: substantive hands-on data/AI/analytics delivery without an explicit business decision/transformation remit, OR explicit business/strategy responsibilities using analytics as a meaningful supporting capability without owning an analytics mandate. Score 2: an explicit and substantial analytics/data/AI mandate integrated with business decision-making, performance management, analytics strategy/governance, or transformation. Hands-on coding is not required; owning analytics capabilities, KPIs, data products, governance or data-driven management can qualify. Generic use of AI tools or analytical thinking alone does not.'
    },
 'decision_influence':
    {
        'weight': .10,
        'description': 'Score 0: no clear involvement in recommendations or decisions beyond prescribed task execution. Score 1: produces decision-support information, identifies options, makes implementation-level recommendations, or advises stakeholders without explicit material influence on business choices. Score 2: explicitly shapes significant business recommendations, prioritization, resource allocation or strategic/operational choices through accountable advisory or decision-making responsibility. Final approval authority is NOT required, but merely reporting to decision makers is insufficient.'
    },
 'change_adoption':
    {
        'weight': .10, 'description': 'Score 0: builds/deploys technical solutions without explicit responsibility for users changing behavior. Score 1: contributes to rollout, process change, training, user enablement or adoption. Score 2: explicitly owns significant change adoption, organizational implementation or measurable adoption outcomes. Production deployment alone is not adoption.'
    },
 'leadership_potential':
    {
        'weight': .05,
        'description': 'Score 0: no credible explicit project, workstream, team, vendor or people leadership responsibility or path. Autonomy and end-to-end individual delivery alone are insufficient. Score 1: a credible path to leading projects, workstreams, vendors or colleagues is explicitly described. Score 2: meaningful leadership responsibility is explicitly part of the role. General career development or mentorship alone is insufficient.'
    },
}


assert abs(sum(v['weight'] for v in CAREER_CRITERIA.values())-1)<1e-9
