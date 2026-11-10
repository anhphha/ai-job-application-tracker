from pathlib import Path
import json,hashlib,importlib.util

p=Path(__file__).resolve().parent
d=json.loads((p/'regression_cases.json').read_text(encoding='utf-8'))
a=json.loads((p/'dataset_1_2_frozen_audit.json').read_text(encoding='utf-8'))
spec=importlib.util.spec_from_file_location('rubric',p/'criteria.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

assert d['dataset_version']=='1.2' and d['rubric_version']==m.RUBRIC_VERSION=='2.1'
assert a['status']=='frozen' and len(d['cases'])==len(a['cases'])==10
assert abs(sum(v['weight'] for v in m.CAREER_CRITERIA.values())-1)<1e-9

ids=set();total=0

for c,meta in zip(d['cases'],a['cases']):

  assert c['case_id']==meta['case_id'] and c['case_id'] not in ids
  ids.add(c['case_id'])

  assert set(c['reviewed_reference'])==set(m.CAREER_CRITERIA)
  jd=(p/c['job_description_file']).read_bytes()

  assert hashlib.sha256(jd).hexdigest()==meta['jd_sha256']

  for criterion,r in c['reviewed_reference'].items():
    assert type(r['score']) is int and r['score'] in (0,1,2)
    assert r['status']=='reviewed' and r['rationale'].strip()
    total+=1

assert total==70

print('PASS: 10 cases, 70 reviewed references, JD hashes, weights, rubric and schema.')
