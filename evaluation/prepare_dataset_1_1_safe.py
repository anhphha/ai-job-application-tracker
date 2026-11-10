"""Build Dataset 1.1 proposal without changing the frozen Dataset 1.0.
Run from project root: python evaluation/prepare_dataset_1_1_safe.py
"""
import json
from copy import deepcopy
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CRITERIA = (
    'transformation', 'business_ownership', 'stakeholder_exposure',
    'data_relevance', 'decision_influence', 'change_adoption',
    'leadership_potential',
)
SOURCE = ROOT / 'regression_cases.json'
REVIEW = ROOT / 'candidate_references_1_1_adjudicated.json'
OUTPUT = ROOT / 'regression_cases_1_1_proposed.json'


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def validate_reference(case):
    cid = case['case_id']
    ref = case.get('reviewed_reference')
    if not isinstance(ref, dict) or set(ref) != set(CRITERIA):
        raise ValueError(f'{cid}: expected exactly seven reviewed criteria')
    for name in CRITERIA:
        item = ref[name]
        if type(item.get('score')) is not int or item['score'] not in (0, 1, 2):
            raise ValueError(f'{cid}/{name}: score must be integer 0, 1, or 2')
        if item.get('status') != 'reviewed':
            raise ValueError(f'{cid}/{name}: not reviewed')
        if not isinstance(item.get('rationale'), str) or not item['rationale'].strip():
            raise ValueError(f'{cid}/{name}: missing rationale')


def build(base, candidate):
    if base.get('dataset_version') != '1.0':
        raise ValueError('Expected original Dataset 1.0')
    originals = deepcopy(base['cases'])
    if [c['case_id'] for c in originals] != [f'R{i:02d}' for i in range(1, 6)]:
        raise ValueError('Dataset 1.0 must contain R01–R05 in order')
    for case in originals:
        validate_reference(case)
        if not case.get('job_description_file'):
            raise ValueError(f"{case['case_id']}: missing job_description_file")

    candidates = {c['case_id']: c for c in candidate['cases']}
    if candidate.get('rubric_version') != '2.0':
        raise ValueError('Expected candidate rubric version 2.0')
    additions = []
    for i in range(6, 11):
        cid = f'R{i:02d}'
        source = candidates[cid]
        case = {k: deepcopy(source[k]) for k in ('case_id', 'company', 'role', 'reviewed_reference')}
        case['job_description_file'] = f'job_descriptions/{cid}_original.txt'
        validate_reference(case)
        additions.append(case)
    merged = deepcopy(base)
    merged['dataset_version'] = '1.1'
    merged['rubric_version'] = '2.0'
    merged['description'] = 'Human-reviewed career-direction regression dataset, expanded from 5 to 10 cases.'
    merged['cases'] = originals + additions
    merged['notes'] = [
        'R01–R05 preserved unchanged from frozen Dataset 1.0.',
        'R06–R10 adjudicated under Rubric 2.0.',
        'Evaluation requires original-only JD fixtures for every case.',
    ]
    if len(merged['cases']) != 10 or len({c['case_id'] for c in merged['cases']}) != 10:
        raise ValueError('Expected ten unique cases')
    return merged


def main():
    if OUTPUT.exists():
        raise SystemExit(f'Refusing to overwrite existing output: {OUTPUT}')
    merged = build(load(SOURCE), load(REVIEW))
    OUTPUT.write_text(json.dumps(merged, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    missing = [c['job_description_file'] for c in merged['cases']
               if not (ROOT / c['job_description_file']).is_file()]
    print(f'Created {OUTPUT.name}: 10 cases, 70 reviewed judgments')
    print('Original Dataset 1.0 unchanged')
    if missing:
        print('NOT READY TO RUN: missing original JD fixtures:')
        for item in missing:
            print('  -', item)
    else:
        print('All JD fixtures present; verify they contain original JD text only.')


if __name__ == '__main__':
    main()
