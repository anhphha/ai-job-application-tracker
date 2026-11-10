"""Offline checks. Run from project root: python evaluation/validate_dataset_1_1.py"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BASE = json.loads((ROOT / 'regression_cases.json').read_text(encoding='utf-8'))
NEW = json.loads((ROOT / 'regression_cases_1_1_proposed.json').read_text(encoding='utf-8'))


CRITERIA = {'transformation', 'business_ownership', 'stakeholder_exposure', 'data_relevance',
            'decision_influence', 'change_adoption', 'leadership_potential'}



assert BASE['dataset_version'] == '1.0'
assert NEW['dataset_version'] == '1.1'
assert NEW['rubric_version'] == '2.0'
assert len(NEW['cases']) == 10
assert [c['case_id'] for c in NEW['cases']] == [f'R{i:02d}' for i in range(1, 11)]
assert NEW['cases'][:5] == BASE['cases'], 'R01–R05 must be preserved exactly'


for c in NEW['cases']:
    ref = c['reviewed_reference']
    assert set(ref) == CRITERIA
    for name, value in ref.items():

        assert type(value['score']) is int and value['score'] in (0, 1, 2)
        assert value['status'] == 'reviewed'
        assert isinstance(value['rationale'], str) and value['rationale'].strip()

    assert c['job_description_file'].startswith('job_descriptions/')
    assert c['job_description_file'].endswith('.txt')


print('PASS: 10 cases / 70 reviewed judgments / Dataset 1.0 unchanged')

missing = [c['job_description_file'] for c in NEW['cases']
           if not (ROOT / c['job_description_file']).is_file()]


if missing:
    print('MISSING JD FIXTURES (must add original JD only):')
    for path in missing:
        print(' -', path)
    raise SystemExit(2)


for c in NEW['cases']:
    content = (ROOT / c['job_description_file']).read_text(encoding='utf-8')
    assert len(content.strip()) > 100, f"{c['case_id']}: JD is suspiciously short"


print('PASS: all JD fixture files exist and are nonempty; manually check no AI scores leaked')
