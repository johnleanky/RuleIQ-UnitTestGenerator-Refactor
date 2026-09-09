"""Fresh synthetic 1.4 materializations, never a stored-source upgrade API."""
from copy import deepcopy
from collections import Counter
import json
from pathlib import Path

import sg_profile as sg
import validate_s2_design as b
from dp_parameters import canonical, ABSENT

ROOT = Path(__file__).resolve().parents[1]


def record(tag, **values):
    return {'tag': tag, 'values': values}


class EvidenceBuilder:
    def __init__(self, rows, sid='S1'):
        self.rows, self.sid = rows, sid

    def values(self, tag):
        return [r['values'] for r in self.rows if r['tag'] == tag and r['values'].get('scenario') == self.sid]

    def add(self, tag, prefix, **values):
        order = len(self.values(tag)) + 1
        rid = prefix + f'{order:03d}'
        self.rows.append(record(tag, scenario=self.sid, id=rid, order=str(order), **values))
        return rid

    def evidence(self, kind, source, fact):
        return self.add('EVIDENCE', 'E', kind=kind, source=source, fact=canonical(fact), support='PredictedFromRules', confidence='High')

    def execution(self, invocation, status='EXECUTED', writes=None, guard=None):
        rid = self.add('RX', 'R', source=invocation, operation='FixtureExecution', context='RunRecordPrimaryPage', guard=guard, inputs=None, result=status, writes=writes, evidence='E001')
        eid = self.evidence('EXECUTION', 'DP_EXECUTION/' + rid, {'execution': rid, 'status': status})
        return rid, eid

    def declaration(self, rule, names, scope='Thread', optional=None, defaults=None):
        meta = self.evidence('DEPENDENCY', 'FixtureMetadata/' + rule, {'description': 'Synthetic normalized metadata; no Pega field mapping asserted', 'scope': scope, 'parameters': names, 'optional': optional or [], 'defaults': defaults or {}})
        return self.evidence('DEPENDENCY', 'DP_DECLARATION/' + rule, dict(rule=rule, scope=scope, parameters=names, optional=optional or [], defaults=defaults or {}, evidence=[meta]))

    def initial(self, name, value=ABSENT):
        return self.evidence('SEED', 'DP_INITIAL/Param.' + name, value)


def materialize(name):
    """Reuse reviewed synthetic assertion facts; acquire new access evidence explicitly.

    This fixture-only function has no Memory handle/input path parameter and is never
    called by Author/Generator runtime. Historical files remain byte-identical.
    """
    path = ROOT / 'fixtures/s3/current' / (name + '.sgl')
    records = [sg.parse_profile(line, n) if line.startswith('PROFILE|') else b.parse_line(line, n)
               for n, line in enumerate(path.read_text(encoding='utf-8').splitlines(), 1)]
    records[0]['values']['version'] = '1.4'
    control = next(r for r in records if r['tag'] == 'COMPLEXITY')
    control.update(tag='CRAWL', values={'ruleCrawlerCalls': '0', 'dependencyReferencesRequested': '0', 'triggeredLimits': None})
    for r in records:
        if r['tag'] == 'SUMMARY': r['values'].pop('complexityTier')
    for scenario in [r['values'] for r in records if r['tag'] == 'SCENARIO']:
        builder = EvidenceBuilder(records, scenario['id'])
        profile = next(r['values'] for r in records if r['tag'] == 'PROFILE' and r['values']['scenario'] == scenario['id'])
        data = json.loads(profile['data']); del data['checklist']['ComplexityComputed']; profile['data'] = canonical(data)
        census = next(e for e in builder.values('EVIDENCE') if e['source'] == 'SCENARIO_SNAPSHOT/PROFILE'); census['fact'] = profile['data']
        audit = json.loads(next(e['fact'] for e in builder.values('EVIDENCE') if e['source'] == 'EXECUTION_AUDIT'))
        control['values']['ruleCrawlerCalls'] = str(len(audit['waves']))
        control['values']['dependencyReferencesRequested'] = str(sum(len(w['plan']['OUT']) for w in audit['waves']))
        declarations, initial = {}, {}
        for sim in builder.values('SIM'):
            params = [p for p in builder.values('PARAM') if p['id'] in b.ids(sim['parameterResolutions'], 'fixture')]
            rule = sim['rule']; names = sorted(p['name'] for p in params)
            if rule not in declarations: declarations[rule] = builder.declaration(rule, names)
            explicit, current = {}, {}
            for p in params:
                name = p['name']
                if name not in initial: initial[name] = builder.initial(name)
                explicit[name] = dict(valueType=p['valueType'], value=p['value'], expression=p['expression'], evidence=b.ids(p['evidence'], 'fixture'))
                current[name] = dict(ABSENT, state='ABSENT', evidence=[initial[name]])
            invocation = params[0]['invocation'] if params else 'DP-' + sim['id']
            rx, _ = builder.execution(invocation)
            access = builder.evidence('EXECUTION', 'DP_ACCESS/' + invocation, dict(rule=rule, invocation=invocation, execution=rx, declaration=declarations[rule], status='EXECUTED', explicit=explicit, current=current, parameters=sorted(p['id'] for p in params), simulation=sim['id']))
            for p in params: p['evidence'] = ','.join(sorted(set(b.ids(p['evidence'], 'fixture')) | {access, declarations[rule]}))
            sim['evidence'] = ','.join(sorted(set(b.ids(sim['evidence'], 'fixture')) | {access, declarations[rule]}))
    return finish(records)


def finish(records):
    """Canonical serializer and exact END census for test materializations."""
    rank = {'SG': -5, 'ROOT': -4, 'TARGET': -3, 'COLUMN': -2, 'CRAWL': -1, 'SCENARIO': 0}
    header = [r for r in records if r['tag'] in rank]
    header.sort(key=lambda r: (rank[r['tag']], int(r['values'].get('order', '0'))))
    body = []
    for s in (r['values'] for r in header if r['tag'] == 'SCENARIO'):
        scoped = [r for r in records if r['values'].get('scenario') == s['id']]
        scoped.sort(key=lambda r: (-1 if r['tag'] == 'PROFILE' else b.BODY_ORDER[r['tag']], int(r['values']['order'])))
        body.extend(scoped)
    end = next(r for r in records if r['tag'] == 'END'); counts = Counter(r['tag'] for r in header + body)
    for key in end['values']:
        if key == 'complete': continue
        end['values'][key] = str(sum(counts[t] for t in ('DTM', 'DTE', 'DTA', 'DTC', 'DTRA')) if key == 'dtCount' else counts[key[:-5].upper()])
    for row in header + body + [end]:
        tag = row['tag']; values = row['values']
        fields = sg.PROFILE_FIELDS if tag == 'PROFILE' else b.FIELDS['ASSERT_DEC' if tag == 'ASSERT' and values['kind'].startswith('Decision') else 'ASSERT_STD' if tag == 'ASSERT' else tag]
        if tag == 'SUMMARY': fields = tuple(k for k in fields if k != 'complexityTier')
        row['values'] = {k: values[k] for k in fields}
    return header + body + [end]


def parameter_variant(mode, carrier=None):
    """Complete Standard source with an independently frozen parameter mechanism."""
    rows = materialize('standard-escaping'); bu = EvidenceBuilder(rows)
    param = next(p for p in bu.values('PARAM') if p['dependency'] == 'D_Customer')
    sim = bu.values('SIM')[0]
    access_e = next(e for e in bu.values('EVIDENCE') if e['source'].startswith('DP_ACCESS/'))
    access = json.loads(access_e['fact'])
    decl_e = next(e for e in bu.values('EVIDENCE') if e['source'].startswith('DP_DECLARATION/'))
    decl = json.loads(decl_e['fact'])
    val = carrier or {'valueType': 'string', 'value': 'Ada Lovelace'}
    if mode == 'parameterless':
        decl['parameters'] = []; access.update(current={}, explicit={}, parameters=[])
        rows.remove(next(r for r in rows if r['tag']=='PARAM' and r['values']['id']==param['id']))
        sim.update(params='{}', parameterResolutions=None, sig='D_Customer[]')
    else:
        param.update(val)
        sim['params'] = canonical({'Customer': b.typed_python(val['valueType'], val['value'])})
        sim['sig'] = 'D_Customer' + sim['params']
        if mode == 'implicit':
            rx, execution = bu.execution('ModelStep2', writes='Param.Customer')
            # Insert this produced value immediately before the existing access.
            next(r for r in bu.values('RX') if r['id']==rx)['order']='2'
            next(r for r in bu.values('RX') if r['id']==access['execution'])['order']='3'
            produced = bu.evidence('EXECUTION','FixtureProducer/'+rx,val)
            bu.add('PRODUCER','P',target='Param.Customer',operation='SET',context='RunRecordPrimaryPage',guard=None,payload=canonical(val),execution=rx,evidence=produced)
            access['current']['Customer']=dict(val,state='VALUE',evidence=[produced,execution])
            access['explicit']={}; param.update(mode='inherited',inheritance='enabled',expression='Param.Customer')
        elif mode == 'default':
            decl['defaults']={'Customer':val}; access['explicit']={}; param.update(mode='default',inheritance='n_a',expression=None)
            meta = next(e for e in bu.values('EVIDENCE') if e['source']=='FixtureMetadata/D_Customer')
            metadata=json.loads(meta['fact']);metadata['defaults']=decl['defaults'];meta['fact']=canonical(metadata)
        else:
            access['explicit']['Customer'].update(val)
    if mode=='parameterless':
        meta=next(e for e in bu.values('EVIDENCE') if e['source']=='FixtureMetadata/D_Customer')
        metadata=json.loads(meta['fact']);metadata['parameters']=[];meta['fact']=canonical(metadata)
    access_e['fact']=canonical(access);decl_e['fact']=canonical(decl)
    return finish(rows)


def crawl_fixture(calls, requests):
    rows=materialize('standard-escaping');bu=EvidenceBuilder(rows)
    for name in ['FunctionA','FunctionB']:
        bu.add('DEP','D',kind='RUF',identity=name,state='CLOSED',parameters=None,proof='Synthetic nested deterministic function closure',evidence='E001')
    names=[d['identity'] for d in bu.values('DEP')]
    waves=[];remaining=requests
    for n in range(1,calls+1):
        count=min(3,remaining-(calls-n));remaining-=count
        out=names[:count]
        waves.append(dict(wave=n,state=dict(open=count,ready=count,ctx=0,unscanned=0,gaps=0),plan=dict(OUT=out,BLK=[],ACT=[],CHK='PASS'),delta=dict(returned=out,new=[],ready=[] if n==calls else names[:min(3,remaining)],closed=out,next='AUTHOR' if n==calls else 'CRAWL')))
    assert remaining==0
    control=next(r['values'] for r in rows if r['tag']=='CRAWL')
    control.update(ruleCrawlerCalls=str(calls),dependencyReferencesRequested=str(requests),triggeredLimits=','.join(sorted((['RULECRAWLER_CALL_CAP'] if calls==120 else [])+(['RULES_TOTAL_REQUESTED_CAP'] if requests==260 else []))) or None)
    bu.values('SUMMARY')[0]['maxDependencyWaveReached']=str(calls)
    audit_e=next(e for e in bu.values('EVIDENCE') if e['source']=='EXECUTION_AUDIT')
    audit=json.loads(audit_e['fact']);audit['waves']=waves;audit_e['fact']=canonical(audit)
    profile=next(r['values'] for r in rows if r['tag']=='PROFILE');data=json.loads(profile['data'])
    data['reasoningTrace'],data['dependencyClosureTrace']=sg.trace_projection([r for r in rows if r['values'].get('scenario')=='S1'],json.loads(audit_e['fact']))
    profile['data']=canonical(data)
    next(e for e in bu.values('EVIDENCE') if e['source']=='SCENARIO_SNAPSHOT/PROFILE')['fact']=profile['data']
    return finish(rows)
