#!/usr/bin/env python3
"""S6 current contract gate; --historical executes unchanged S5 at its fixed HEAD."""
from copy import deepcopy
import argparse
import hashlib
import html
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

import dp_parameters as dp
import s6_fixtures as f
import sg_profile as sg
import validate_s2_design as b
from s5_fixture_runtime import Runtime
from validate_s5_integration import trace_contract

ROOT = f.ROOT
BASELINE = '13b44c7f59c250d3a54fb11d4dfb6ecbb5db24a8'
PASSED = []


def value(raw):
    if raw is None: return {'valueType': 'null', 'value': 'null'}
    if raw == '' and isinstance(raw, str): return {'valueType': 'empty', 'value': '<EMPTY>'}
    return {'valueType': 'string' if isinstance(raw, str) else 'boolean' if type(raw) is bool else 'number', 'value': raw if isinstance(raw, str) else dp.canonical(raw)}


def fact(rows, source):
    return next(r['values'] for r in rows if r['tag'] == 'EVIDENCE' and r['values']['source'] == source)


def change_fact(rows, source, change):
    e = fact(rows, source); data = json.loads(e['fact']); change(data); e['fact'] = dp.canonical(data)


def check(rows):
    return sg.read_ledger(b.MemoryFixture('fresh-s6.sgl', sg.serialize(f.finish(rows))), revision='1.4')


def negative(name, rows, mutate, full=False):
    edited = deepcopy(rows); mutate(edited)
    try: check(edited) if full else dp.validate(edited)
    except b.ContractError:
        PASSED.append(name)
        return
    raise AssertionError('accepted invalid fixture: ' + name)


def snapshot(mode='inherited', raw='GENUT-11007', scope='Thread', names=None, defaults=None, optional=None, initial=dp.ABSENT, producers=None, repeat=False, access_status='EXECUTED'):
    """Normalized execution evidence unit fixture; not a full ScenarioGroup."""
    names = ['pyID'] if names is None else names
    rows = [f.record('SCENARIO', id='S1', testability='Testable', confidence='High')]
    bu = f.EvidenceBuilder(rows)
    bu.evidence('RUT', 'FixtureRUT', {'simulationOnly': True})
    decl = bu.declaration('D_GenUT', names, scope, optional, defaults)
    init = bu.initial('pyID', initial)
    current, state, origin = initial, ('ABSENT' if initial['valueType'] == 'absent' else 'VALUE'), [init]
    producers = [('EXECUTED', value(raw))] if producers is None and mode == 'inherited' else (producers or [])
    for idx, (status, val) in enumerate(producers):
        guard = None
        if status != 'EXECUTED': guard = bu.add('BRANCH', 'B', result='FALSE' if status == 'NOT_EXECUTED' else 'UNKNOWN')
        rx, execution = bu.execution('1.' + str(idx+1), status, 'Param.pyID', guard)
        producer_e = bu.evidence('EXECUTION', 'FixtureProducer/' + rx, val)
        bu.add('PRODUCER', 'P', target='Param.pyID', operation='SET', context='Primary', guard=guard, payload=dp.canonical(val), execution=rx, evidence=producer_e)
        if status != 'NOT_EXECUTED':
            current = dp.ABSENT if status == 'UNKNOWN' else val
            state = 'UNKNOWN' if status == 'UNKNOWN' else ('ABSENT' if current['valueType'] == 'absent' else 'VALUE')
            origin = [producer_e, execution]
    for step in (['1.3', '1.4'] if repeat else ['1.3']):
        guard = bu.add('BRANCH', 'B', result='FALSE' if access_status == 'NOT_EXECUTED' else 'UNKNOWN') if access_status != 'EXECUTED' else None
        rx, _ = bu.execution(step, access_status, guard=guard)
        current_map = {'pyID': dict(current, state=state, evidence=origin)} if names else {}
        explicit = {'pyID': dict(value(raw), expression='FixtureExplicit', evidence=['E001'])} if mode == 'explicit' else {}
        access = dict(rule='D_GenUT', invocation=step, execution=rx, declaration=decl, status=access_status, explicit=explicit, current=current_map, parameters=[], simulation=None)
        if access_status != 'EXECUTED': access.update(explicit={}, current={})
        ae = bu.evidence('EXECUTION', 'DP_ACCESS/' + step, access)
        resolved, missing = dp.resolve(json.loads(fact(rows, 'DP_DECLARATION/D_GenUT')['fact']), explicit, current_map) if access_status == 'EXECUTED' else ({}, [])
        for name, (val, binding, expression) in resolved.items():
            pid = bu.add('PARAM', 'K', invocation=step, dependency='D_GenUT', name=name, formalType=None, formalEvidence=None, mode=binding, inheritance='enabled' if binding == 'inherited' else 'n_a', expression=expression, **val, evidence=','.join(sorted([decl, ae])))
            access['parameters'].append(pid)
        if access_status == 'EXECUTED' and not missing and scope == 'Thread':
            if not bu.values('SIM'):
                bu.add('SIM', 'M', rule='D_GenUT', sig='D_GenUT' + dp.canonical({n: b.typed_python(v['valueType'], v['value']) for n, (v, _, _) in resolved.items()}), params=dp.canonical({n: b.typed_python(v['valueType'], v['value']) for n, (v, _, _) in resolved.items()}), parameterResolutions=','.join(access['parameters']) or None, evidence=','.join(sorted([decl, ae])))
            sim = bu.values('SIM')[0]; access['simulation'] = sim['id']; sim['evidence'] = ','.join(sorted(set(sim['evidence'].split(',')) | {ae}))
        elif access_status != 'NOT_EXECUTED':
            code = 'DP_ACCESS_UNRESOLVED' if access_status == 'UNKNOWN' else 'DP_PARAMETER_UNRESOLVED' if missing else 'DP_SCOPE_INELIGIBLE'
            bu.add('GAP', 'G', code=code, scope=step, evidence=ae)
            rows[0]['values'].update(testability='PartiallyTestable', confidence='Low')
        fact(rows, 'DP_ACCESS/' + step)['fact'] = dp.canonical(access)
    return rows


def semantic_tests():
    cases = {
        'implicit earlier assignment': snapshot(repeat=True),
        'explicit wins over current': snapshot(mode='explicit', raw='EXPLICIT', initial=value('CURRENT')),
        'explicit wins over unknown current': snapshot(mode='explicit', raw='EXPLICIT', producers=[('UNKNOWN',value('unknown'))]),
        'overwrite': snapshot(producers=[('EXECUTED', value('old')), ('EXECUTED', value('new'))]),
        'skipped producer': snapshot(initial=value('initial'), producers=[('NOT_EXECUTED', value('skipped'))]),
        'unknown producer': snapshot(producers=[('UNKNOWN', value('unknown'))]),
        'unknown overwritten': snapshot(producers=[('UNKNOWN', value('unknown')), ('EXECUTED', value('known'))]),
        'default': snapshot(mode='default', defaults={'pyID': value('default')}),
        'parameterless': snapshot(mode='none', names=[]),
        'optional omitted': snapshot(mode='none', optional=['pyID']),
        'missing required input': snapshot(mode='none'),
        'skipped access': snapshot(access_status='NOT_EXECUTED', producers=[]),
        'unknown access': snapshot(access_status='UNKNOWN', producers=[]),
        'Requestor excluded': snapshot(scope='Requestor'),
        'Node excluded': snapshot(scope='Node'),
        'unknown scope excluded': snapshot(scope=None),
    }
    for raw in ('', None, 12, False): cases['typed ' + repr(raw)] = snapshot(raw=raw)
    for name, rows in cases.items(): dp.validate(rows); PASSED.append(name)
    rows = cases['implicit earlier assignment']
    negative('stale snapshot', rows, lambda r: change_fact(r,'DP_ACCESS/1.3',lambda a:a['current']['pyID'].update(value='stale')))
    negative('missing current name', rows, lambda r: change_fact(r,'DP_ACCESS/1.3',lambda a:a['current'].clear()))
    negative('duplicate access PARAM', rows, lambda r: change_fact(r,'DP_ACCESS/1.3',lambda a:a['parameters'].append(a['parameters'][0])))
    negative('missing PARAM', rows, lambda r: change_fact(r,'DP_ACCESS/1.3',lambda a:a['parameters'].clear()))
    negative('cross-access references', rows, lambda r: change_fact(r,'DP_ACCESS/1.3',lambda a:a.update(parameters=['K002'])))
    negative('extra SIM references', rows, lambda r: next(x['values'] for x in r if x['tag']=='SIM').update(parameterResolutions='K001,K002'))
    negative('missing producer census', rows, lambda r:r.__setitem__(slice(None),[x for x in r if x['tag']!='PRODUCER']))
    negative('invented skip', rows, lambda r:change_fact(r,'DP_EXECUTION/R001',lambda a:a.update(status='NOT_EXECUTED')))
    negative('wrong Data Page identity', rows, lambda r:next(x['values'] for x in r if x['tag']=='SIM').update(rule='D_Unrelated'))
    negative('numeric Boolean coercion', cases['typed False'], lambda r:next(x['values'] for x in r if x['tag']=='SIM').update(params='{"pyID":0}'))
    negative('missing declaration becomes empty', cases['parameterless'], lambda r:change_fact(r,'DP_DECLARATION/D_GenUT',lambda a:a.update(parameters=None)))
    negative('unknown silently falls back', cases['unknown producer'], lambda r:change_fact(r,'DP_ACCESS/1.3',lambda a:a['current']['pyID'].update(state='ABSENT')))
    negative('false branch has simulation', cases['skipped access'], lambda r:change_fact(r,'DP_ACCESS/1.3',lambda a:a.update(simulation='M001')))
    negative('promoted missing evidence', cases['missing required input'], lambda r:r[0]['values'].update(testability='Testable',confidence='High'))
    unresolved = snapshot(mode='explicit', initial=value('fallback'))
    change_fact(unresolved,'DP_ACCESS/1.3',lambda a:a['explicit']['pyID'].update(dp.ABSENT))
    negative('unresolved explicit cannot fall back', unresolved, lambda r:None)
    unknown = snapshot(mode='none')
    change_fact(unknown,'DP_DECLARATION/D_GenUT',lambda a:a.update(parameters=None))
    change_fact(unknown,'DP_ACCESS/1.3',lambda a:a.update(current={}))
    dp.validate(unknown); PASSED.append('unknown declaration stays unresolved')
    # Insert an overwrite between two accesses: each freezes its own map/signature.
    changed=deepcopy(rows);bu=f.EvidenceBuilder(changed)
    rx,execution=bu.execution('between-accesses',writes='Param.pyID')
    next(r for r in bu.values('RX') if r['id']==rx)['order']='3'
    next(r for r in bu.values('RX') if r['source']=='1.4')['order']='4'
    produced=bu.evidence('EXECUTION','FixtureProducer/'+rx,value('SECOND'))
    bu.add('PRODUCER','P',target='Param.pyID',operation='SET',context='Primary',guard=None,payload=dp.canonical(value('SECOND')),execution=rx,evidence=produced)
    change_fact(changed,'DP_ACCESS/1.4',lambda a:a.update(current={'pyID':dict(value('SECOND'),state='VALUE',evidence=[produced,execution])},simulation='M002'))
    bu.values('PARAM')[1].update(value('SECOND'))
    access_id=fact(changed,'DP_ACCESS/1.4')['id'];decl_id=fact(changed,'DP_DECLARATION/D_GenUT')['id']
    bu.add('SIM','M',rule='D_GenUT',sig='D_GenUT[SECOND]',params='{"pyID":"SECOND"}',parameterResolutions='K002',evidence=','.join(sorted([access_id,decl_id])))
    dp.validate(changed);PASSED.append('access before and after value change')
    negative('distinct maps cannot share signature',changed,lambda r:next(x['values'] for x in r if x['tag']=='SIM' and x['values']['id']=='M002').update(sig=bu.values('SIM')[0]['sig']))
    negative('duplicate producer for RX target',rows,lambda r:r.append(dict(tag='PRODUCER',values=dict(next(x['values'] for x in r if x['tag']=='PRODUCER'),id='P002'))))
    negative('non-finite number',cases['typed 12'],lambda r:change_fact(r,'DP_INITIAL/Param.pyID',lambda a:a.update(valueType='number',value='NaN')))
    # The supplied RUT expectation is deliberately a string-function simulation.
    case_key='RULEIQ-WORK GENUT-11007'
    produced=case_key.split('K',1)[1].strip()
    assert produced=='GENUT-11007'
    assert all(json.loads(e['values']['fact'])['current']['pyID']['value']==produced for e in rows if e['tag']=='EVIDENCE' and e['values']['source'].startswith('DP_ACCESS/'))
    assert not any(r['tag']=='SIM' for r in cases['skipped access'])
    PASSED.append('GetCaseData labeled mock expectations 1.1/1.3/1.4 and FALSE')


def connected_tests(write=False):
    sources = {}
    for name in ('standard-escaping','standard-not-testable','when-key-a','when-key-b','when-no-simulation'):
        rows=f.materialize(name); check(deepcopy(rows)); sources[name]=rows
        raw=sg.serialize(rows)
        path=ROOT/'fixtures/s6'/(name+'.sgl')
        if write: path.parent.mkdir(exist_ok=True); path.write_bytes(raw)
        else: assert path.read_bytes()==raw, 'fresh fixture drift: '+name
        PASSED.append('full source '+name)
    for names in (['standard-escaping'], ['when-key-a','when-key-b'], ['when-no-simulation']):
        rt=Runtime(names); rt.payloads=[sg.serialize(sources[n]).decode() for n in names]
        assert rt.run()['AIAgentResponseStatus']=='Completed'
        trace_contract(rt)
        assert rt.generator_report['status'] in {'Completed','PartiallyCompleted'}
        candidate=rt.records[rt.generator_report['candidate']['UUID']].payload
        assert 'ComplexityTier' not in candidate and 'ComplexityComputed' not in candidate
        PASSED.append('connected immutable flow '+','.join(names))
    for mode, raw in [('implicit','Ada Lovelace'),('default','default'),('parameterless','unused'),('explicit',''),('explicit',None),('explicit',42),('explicit',False)]:
        rows=f.parameter_variant(mode,value(raw));check(deepcopy(rows))
        rt=Runtime(['standard-escaping']);rt.payloads=[sg.serialize(rows).decode()]
        assert rt.run()['AIAgentResponseStatus']=='Completed'
        assert rt.generator_report['status']=='Completed';trace_contract(rt)
        assert not any(r['tag']=='INPUT' and r['values']['path']=='Param.Customer' for r in rows), 'produced value became formal RUT input'
        PASSED.append('connected parameter '+mode+' '+repr(raw))
    for calls,requests in [(1,1),(119,259),(120,120),(87,260),(120,260)]:
        rows=f.crawl_fixture(calls,requests);check(deepcopy(rows))
        assert next(r['values'] for r in rows if r['tag']=='SCENARIO')['testability']=='Testable'
        PASSED.append('crawler boundary '+str((calls,requests)))
    rows=sources['standard-escaping']
    negative('obsolete source version', rows, lambda r:r[0]['values'].update(version='1.3'), full=True)
    raw=sg.serialize(rows).decode()
    try:sg.read_ledger(b.MemoryFixture('obsolete',raw.replace('|assertionCount=', '|complexityTier=STANDARD|assertionCount=').encode()),revision='1.4')
    except b.ContractError:PASSED.append('obsolete summary field rejected')
    else:raise AssertionError('obsolete field accepted')
    for field, limit, code in [('ruleCrawlerCalls',120,'RULECRAWLER_CALL_CAP'),('dependencyReferencesRequested',260,'RULES_TOTAL_REQUESTED_CAP')]:
        negative('over budget '+field, rows, lambda r, k=field,n=limit:next(x['values'] for x in r if x['tag']=='CRAWL').update({k:str(n+1)}), full=True)
        negative('false limit code '+field, rows, lambda r,c=code:next(x['values'] for x in r if x['tag']=='CRAWL').update(triggeredLimits=c), full=True)
    negative('wave census mismatch', rows, lambda r:next(x['values'] for x in r if x['tag']=='CRAWL').update(ruleCrawlerCalls='1'), full=True)
    negative('request census mismatch', rows, lambda r:next(x['values'] for x in r if x['tag']=='CRAWL').update(dependencyReferencesRequested='1'), full=True)
    # Current processing never invokes historical scoring, even with nested DT calls.
    original=b.derive_complexity
    b.derive_complexity=lambda _: (_ for _ in ()).throw(AssertionError('obsolete scoring invoked'))
    try:
        for rows in sources.values():check(deepcopy(rows))
    finally:b.derive_complexity=original
    PASSED.append('no current scoring invocation')


def artifact_checks():
    for prompt,export in [('UnitTestGenerator_Prompt.txt','UnitTestGenerator.txt'),('Validator_Prompt.txt','JsonValidator_tool.txt')]:
        raw=(ROOT/export).read_bytes(); start=raw.index(b'<pySystemPrompt>')+len(b'<pySystemPrompt>'); end=raw.index(b'</pySystemPrompt>',start)
        expected='\n'.join('<p>'+html.escape(line,quote=False)+'</p>' for line in (ROOT/prompt).read_text(encoding='utf-8').splitlines()).encode()
        assert raw[start:end]==expected, 'export parity '+export
        old=subprocess.check_output(['git','show',BASELINE+':'+export],cwd=ROOT)
        def outside(blob):return re.sub(b'<pySystemPrompt>.*?</pySystemPrompt>',b'<pySystemPrompt/>',blob,flags=re.S).replace(b'\r\n',b'\n')
        assert outside(raw)==outside(old),'external metadata changed '+export
    for path in ['Main_Agent_Prompt.txt','UnitTestGenerator_Prompt.txt','Validator_Prompt.txt']+[p.name for p in ROOT.glob('rule-test-unit-case*Json*.txt')]:
        text=(ROOT/path).read_text(encoding='utf-8')
        assert not re.search(r'weightedScore|ComplexityTier|complexityTier|ComplexityComputed|COMPLEXITY\||confidenceCap|testabilityCap',text),path
    # Everything outside the declared combined S6 scope retains the lean baseline bytes.
    manifest=json.loads((ROOT/'docs/execution/evidence/lean-execution-baseline.json').read_text(encoding='utf-8'))
    allowed=set(json.loads((ROOT/'fixtures/s6/scope.json').read_text())['modified'])
    for path,digest in manifest['protected'].items():
        if path not in allowed:
            raw=(ROOT/path).read_bytes()
            if path=='docs/decisions/DECISIONS.md':
                # Preserve both the historical mixed-line-ending bytes and the
                # LF-only working copy observed before the reporting amendment.
                original=(ROOT/'docs/execution/evidence/decision-index-preserved.txt').read_bytes()
                assert hashlib.sha256(original).hexdigest()==digest
                assert raw in (original,original.replace(b'\r\n',b'\n')), 'decision index content changed'
            else:
                assert hashlib.sha256(raw).hexdigest().lower()==digest.lower(), 'outside S6 scope changed '+path
    PASSED.append('exports, obsolete fields, and preservation')


def review_regressions():
    # A referenced NOT_APPLICABLE branch is not an absent guard. Exercise the
    # complete wire parser, not only the normalized evidence validator.
    def attach_inapplicable_guard(rows):
        producer=next(r['values'] for r in rows if r['tag']=='PRODUCER' and r['values']['target']=='Param.Customer')
        rx=next(r['values'] for r in rows if r['tag']=='RX' and r['values']['id']==producer['execution'])
        assert next(r['values'] for r in rows if r['tag']=='BRANCH' and r['values']['id']=='B001')['result']=='NOT_APPLICABLE'
        producer['guard']=rx['guard']='B001'
    negative('executed producer with inapplicable guard',f.parameter_variant('implicit'),attach_inapplicable_guard,full=True)
    def attach_access_guard(rows):
        access=json.loads(fact(rows,'DP_ACCESS/DP-1')['fact'])
        next(r['values'] for r in rows if r['tag']=='RX' and r['values']['id']==access['execution'])['guard']='B001'
    negative('executed access with inapplicable guard',f.parameter_variant('implicit'),attach_access_guard,full=True)
    # Validate the historical orchestration using the CURRENT common checker;
    # the isolated unchanged S5 gate alone cannot catch regressions in this code.
    ledgers={}
    for path in sorted((ROOT/'fixtures/s2').glob('*.sgl')):
        blob=subprocess.check_output(['git','show',BASELINE+':'+path.relative_to(ROOT).as_posix()],cwd=ROOT)
        ledgers[path.name]=b.validate_ledger(b.MemoryFixture(path.name,blob))
    b.validate_orchestration(ledgers)
    PASSED.append('current common checker historical orchestration')


def historical():
    env=dict(os.environ,GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='core.autocrlf',GIT_CONFIG_VALUE_0='false',PYTHONUTF8='1')
    with tempfile.TemporaryDirectory(prefix='ruleiq-s6-history-') as temp:
        subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(ROOT),temp],check=True,env=env)
        subprocess.run(['git','checkout','--quiet',BASELINE],cwd=temp,check=True,env=env)
        result=subprocess.run([sys.executable,'-B','scripts/validate_s5_design.py'],cwd=temp,env=env,capture_output=True,text=True)
        if result.returncode: raise AssertionError('historical S5 failed:\n'+result.stdout[-4000:]+result.stderr[-2000:])
        print('Historical fixed-baseline S5 PASS')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--historical',action='store_true');parser.add_argument('--write-fixtures',action='store_true');args=parser.parse_args()
    semantic_tests();connected_tests(args.write_fixtures);review_regressions();artifact_checks()
    if args.historical:historical()
    print('S6 PASS: '+str(len(PASSED))+' cases/check groups (repository-static and labeled simulation only)')


if __name__=='__main__':main()
