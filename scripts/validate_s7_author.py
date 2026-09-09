"""Instruction-only correction gate. No runtime consumer uses the policy oracle."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import s6_fixtures as f
import sg_profile as sg
from s5_fixture_runtime import Runtime
from validate_s5_integration import trace_contract

ROOT=Path(__file__).resolve().parents[1]


def policy(case):
    """Test-only interpretation of the policy examples, not a Pega interpreter."""
    presence=case['initial']
    if case.get('initialAncestorPresence')=='ABSENT':presence='ABSENT'
    for status,effect in case['events']:
        assert status in {'SKIPPED','UNKNOWN','EXECUTED'} and effect in {'MATERIALIZE','REMOVE','UNRESOLVED'}
        if status=='SKIPPED':continue
        presence='UNKNOWN' if status=='UNKNOWN' or effect=='UNRESOLVED' else 'PRESENT' if effect=='MATERIALIZE' else 'ABSENT'
    if not case.get('representable',True):decision='OMIT_UNREPRESENTABLE'
    elif case.get('inputOnly') and all(s=='SKIPPED' for s,_ in case['events']):decision='OMIT_INPUT_ONLY'
    elif presence=='UNKNOWN':decision='OMIT_UNRESOLVED'
    elif presence=='ABSENT':decision='Not exists'
    else:decision='LADDER'
    return presence,decision


def instruction_checks():
    text=(ROOT/'Main_Agent_Prompt.txt').read_text(encoding='utf-8')
    gate=text.split('### 6.0-PRE SKIPPED_BRANCH_EXISTENCE_GATE',1)[1].split('### 6.0 RUT Producer Catalog Lock',1)[0]
    seed=text.split('STEP 4 — Separate seed eligibility from final presence:',1)[1].split('STEP 5 —',1)[0]
    for clause in ('A skipped write preserves the','PRESENT, ABSENT or UNKNOWN','final absence is proven','input-only','UNKNOWN presence','OMIT','unresolvable_runtime_input','Proven absence of an ancestor','initialization premise established','takes precedence over those shortcuts','Generator alone formats AssertionDecisionTrace','not new mandatory source fields','later execution does not prove'):
        assert clause in gate, 'missing policy clause: '+clause
    assert 'does not prove runtime absence' in seed
    assert 'not establish initial or final presence' in text
    assert 'input-only and has no output assertion' in text
    for forbidden in ('false  UNCONDITIONALLY','false \u00a0UNCONDITIONALLY','Proceed directly to gate rule: emit Not exists','IF Write-Reachable(P, S) = false','All segments must be Write-Reachable=true','only allowed assertion for P is','one physical group containing exactly one final Scenario','one physical ScenarioGroup containing exactly one final Scenario'):
        assert forbidden not in text, 'contradictory old rule: '+forbidden
    assert '|gate=' not in gate, 'non-whitelisted candidate trace annotation'
    assert 'For each frozen non-Rule-Obj-When scenario, create exactly one ScenarioGroup' in text
    assert 'local scenario order is 1' in text and 'Standard group count equals frozen scenario count' in text
    assert 'Grouping must not merge, remove, or reidentify frozen scenarios' in text


def preservation():
    baseline=json.loads((ROOT/'docs/execution/evidence/S7-baseline.json').read_text(encoding='utf-8'))
    for name,digest in baseline['protected'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest, 'outside Author batch changed: '+name
    return len(baseline['protected'])


def grouping():
    # Two fresh synthetic Standard sources exercise existing serializers,
    # source checks, Memory transport, projection and candidate validation.
    # They are grouping witnesses, not a claim of complete GetCaseData execution.
    first=f.materialize('standard-escaping');second=f.materialize('standard-escaping')
    second[0]['values'].update(groupId='G002',groupOrder='2')
    for row in second:
        v=row['values']
        if v.get('scenario')=='S1':v['scenario']='S2'
        if row['tag']=='SCENARIO':v.update(id='S2',order='1')
    rt=Runtime(['standard-escaping'])
    rt.payloads=[sg.serialize(rows).decode() for rows in (first,second)]
    assert rt.run()['AIAgentResponseStatus']=='Completed';trace_contract(rt)
    report=rt.generator_report
    assert report['status']=='Completed'
    assert [(g['groupId'],[(s['id'],s['unit'],s['scenario']) for s in g['scenarios']]) for g in report['groups']]==[('G001',[('S1',0,0)]),('G002',[('S2',1,0)])]


def main():
    cases=json.loads((ROOT/'fixtures/s7/presence-policy.json').read_text(encoding='utf-8'))
    for case in cases['cases']:
        assert policy(case)==(case['expectedPresence'],case['expectedDecision']),case['name']
    sim=cases['getCaseDataS2']
    assert sim['scenario']=='S2' and sim['simulations']==[] and len(sim['paths'])==4
    for variant in sim['variants']:
        _,decision=policy({'initial':variant['initialPresence'],'events':[['SKIPPED','MATERIALIZE']]})
        assert decision==variant['decision']
    instruction_checks();grouping();count=preservation()
    result=subprocess.run([sys.executable,'-B','scripts/validate_s6_parameters.py'],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    print(f'S7 PASS: {len(cases["cases"])} policy examples, 2 S2 variants, Standard handoff, S6 gate, {count} preserved files (static only)')


if __name__=='__main__':main()
