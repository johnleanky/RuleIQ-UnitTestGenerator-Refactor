#!/usr/bin/env python3
"""Repository-static DEC-027 handoff checks, including independent source snapshots."""
from copy import deepcopy
from pathlib import Path
import json

import sg_profile as p
import validate_s2_design as b

ROOT=Path(__file__).resolve().parents[1]
FIXTURES=ROOT/'fixtures/s3/profiled'


def values(records, tag):
    return next(r['values'] for r in records if r['tag']==tag)


def validate(records):
    return p.read_ledger(b.MemoryFixture('profile-mutation.sgl',p.serialize(records)))


def edit(records, mutate, refresh=True):
    profile=values(records,'PROFILE')
    data=json.loads(profile['data'])
    mutate(data)
    profile['data']=p.canonical(data)
    if refresh:
        proof=next(r['values'] for r in records if r['tag']=='EVIDENCE' and r['values']['scenario']==profile['scenario'] and r['values']['source']=='SCENARIO_SNAPSHOT/PROFILE')
        proof['fact']=p.canonical(data)


def expect_rejection(name, action, message):
    try: action()
    except b.ContractError as error:
        b.require(message in str(error),f'{name}: unexpected rejection: {error}')
    else: raise b.ContractError('accepted invalid profile: '+name)


def add_evidence(records,kind,source,fact):
    profile=values(records,'PROFILE');sid=profile['scenario']
    evidence=[r['values'] for r in records if r['tag']=='EVIDENCE' and r['values']['scenario']==sid]
    index=max(int(e['id'][1:]) for e in evidence)+1
    row={'tag':'EVIDENCE','values':{'scenario':sid,'id':f'E{index:03d}','order':str(index),'kind':kind,'source':source,'fact':p.canonical(fact),'support':'Verified','confidence':'High'}}
    after=max(i for i,r in enumerate(records) if r['tag']=='EVIDENCE' and r['values']['scenario']==sid)+1
    records.insert(after,row);profile['evidence']+=','+row['values']['id']
    values(records,'END')['evidenceCount']=str(int(values(records,'END')['evidenceCount'])+1)
    return row['values']['id']


def update_source(records,source,mutate):
    row=next(r['values'] for r in records if r['tag']=='EVIDENCE' and r['values']['source']==source)
    fact=json.loads(row['fact']);mutate(fact);row['fact']=p.canonical(fact)


def refresh_traces(records):
    sid=values(records,'PROFILE')['scenario'];rows=[r for r in records if r['values'].get('scenario')==sid]
    audit=json.loads(next(r['values']['fact'] for r in rows if r['tag']=='EVIDENCE' and r['values']['source']=='EXECUTION_AUDIT'))
    reasoning,closure=p.trace_projection(rows,audit)
    edit(records,lambda d:d.update(reasoningTrace=reasoning,dependencyClosureTrace=closure))


def extended_cases(records,action_records):
    count=0
    empty=deepcopy(action_records)
    edit(empty,lambda d:d['actions'][0].update(parameters=[]))
    update_source(empty,'ACTION_ARGUMENTS/0',lambda f:f.clear())
    validate(empty);count+=1
    def rejected(name,copy,message):
        nonlocal count
        expect_rejection(name,lambda:validate(copy),message);count+=1
    cell=p.read_ledger(FIXTURES/'when-no-simulation.sgl')['records']
    edit(cell,lambda d:d.update(bindings=[None]));rejected('cell_null_binding',cell,'bindings object array')
    for source,mutation,message in [
        ('ActionRule/ApplyDataTransform/PrepareCustomer/pyParameters',lambda f:f.append(deepcopy(f[0])),'unique action formal declaration'),
        ('ACTION_ARGUMENTS/0',lambda f:f[0].update(value='different'),'source mismatch')]:
        copy=deepcopy(action_records);update_source(copy,source,mutation);rejected(source,copy,message)
    copy=p.read_ledger(FIXTURES/'standard-not-testable.sgl')['records']
    update_source(copy,'EXECUTION_AUDIT',lambda f:f['waves'][0]['delta'].update(returned=['Helper@App-Work-Order@ExternalStatus']))
    refresh_traces(copy);rejected('missing_returned_as_fetched',copy,'fetched RuleJSON outcome')
    copy=p.read_ledger(FIXTURES/'standard-not-testable.sgl')['records']
    update_source(copy,'EXECUTION_AUDIT',lambda f:f['waves'][0].update(wave=42));refresh_traces(copy);rejected('invented_wave',copy,'wave identity')
    copy=p.read_ledger(FIXTURES/'when-key-a.sgl')['records'];update_source(copy,'EXECUTION_AUDIT',lambda f:f.update(seeds=[]));refresh_traces(copy);rejected('seed_proof_missing',copy,'seed coverage proof missing')
    # Change only fixture assertion kind/context, leaving source decision identity/value intact.
    listing=deepcopy(records);values(listing,'ASSERT')['kind']='List'
    edit(listing,lambda d:d['bindings'][0]['context'].update(pyNumberOfAppearances='InAnyInstance'))
    update_source(listing,'ASSERTION_CONTEXT/A001',lambda f:f.update(producerIndex='Unknown',payloadProven=True,context=dict(f['context'],pyNumberOfAppearances='InAnyInstance')))
    refresh_traces(listing);validate(listing);count+=1
    copy=deepcopy(listing);update_source(copy,'ASSERTION_CONTEXT/A001',lambda f:f.update(payloadProven=False));rejected('unknown_unproven_payload',copy,'unknown index requires proven InAnyInstance')
    copy=deepcopy(listing);edit(copy,lambda d:d['bindings'][0]['context'].update(pyNumberOfAppearances='InAllInstances'));update_source(copy,'ASSERTION_CONTEXT/A001',lambda f:f['context'].update(pyNumberOfAppearances='InAllInstances'));rejected('unknown_index_all_instances',copy,'unknown index requires proven InAnyInstance')
    copy=deepcopy(listing);edit(copy,lambda d:d['bindings'][0]['context'].update(pyNumberOfAppearances='InAllInstances'));update_source(copy,'ASSERTION_CONTEXT/A001',lambda f:f.update(producerIndex='Known',context=dict(f['context'],pyNumberOfAppearances='InAllInstances')));validate(copy);count+=1
    # Non-Model execution mode requires original RuleJSON metadata; both booleans work.
    for mode in ('true','false'):
        copy=deepcopy(records);values(copy,'SG')['rutType']='Rule-Obj-Activity'
        key=json.loads(values(copy,'PROFILE')['data'])['caseKey'].replace('RULE-OBJ-MODEL','RULE-OBJ-ACTIVITY')
        update_source(copy,'GetCaseData/TestedRuleKey',lambda f:f.update(TestedRuleKey=key))
        edit(copy,lambda d:d.update(caseKey=key,singlePage=mode))
        rejected('non_model_unproven_'+mode,deepcopy(copy),'single-page provenance')
        add_evidence(copy,'RUT','RuleJSON/pyIsSinglePageImplementation',{'pyIsSinglePageImplementation':mode});validate(copy);count+=1
    return count


def main():
    sources=json.loads((ROOT/'fixtures/s3/profile-source-facts.json').read_text())
    count=0
    for fixture in sorted(FIXTURES.glob('*.sgl')):
        result=p.read_ledger(fixture)
        for sid,profile in result['profiles'].items():
            actual=[{'kind':r['values']['kind'],'source':r['values']['source'],'fact':json.loads(r['values']['fact'])} for r in result['records'] if r['tag']=='EVIDENCE' and r['values'].get('scenario')==sid and r['values']['source'] in {x['source'] for x in sources[fixture.name+':'+sid]}]
            b.require(actual==sources[fixture.name+':'+sid], 'profile acquisition source snapshot drift')
            count+=1
    records=p.read_ledger(FIXTURES/'standard-escaping.sgl')['records']
    probes=[]
    def probe(name, mutate, message, refresh=True):
        copy=deepcopy(records);edit(copy,mutate,refresh);probes.append((name,copy,message))
    probe('case_key_mismatch',lambda d:d.update(caseKey='RULE-OBJ-MODEL OTHER DIFFERENT'), 'case/RUT identity')
    probe('case_key_no_proof',lambda d:d.update(caseKey=d['caseKey']+' changed'), 'case key provenance')
    probe('mode_mismatch',lambda d:d.update(singlePage='true'), 'fixed single-page mode')
    probe('scenario_type',lambda d:d.update(scenarioType='Speculative'), 'scenario type')
    probe('frozen_profile_changed',lambda d:d.update(scenarioType='Edge'), 'frozen census evidence',False)
    probe('checklist_missing',lambda d:d['checklist'].pop('NoSpeculation'), 'checklist')
    probe('checklist_false',lambda d:d['checklist'].update(NoSpeculation=False), 'false gate without downgrade')
    probe('trace_missing',lambda d:d.update(reasoningTrace=''), 'factual trace')
    probe('binding_missing',lambda d:d.update(bindings=[]), 'ASSERT binding census')
    probe('binding_duplicate',lambda d:d['bindings'].append(deepcopy(d['bindings'][0])), 'ASSERT binding census')
    probe('type_drift',lambda d:d['bindings'][0].update(scalarType='TrueFalse'), 'scalar type drift')
    probe('page_class_drift',lambda d:d['bindings'][0].update(stepClass='Other-Class'), 'step page/class')
    probe('target_drift',lambda d:d['bindings'][0].update(fullPath='RunRecordPrimaryPage.Other'), 'full target')
    probe('page_as_scalar',lambda d:d['bindings'][0].update(structure='PageList'), 'page target as Property')
    probe('parent_missing',lambda d:d['bindings'][0].update(structure='ValueList'), 'collection parent mode')
    probe('context_override',lambda d:d['bindings'][0]['context'].update(pyExpectedValue='guessed'), 'optional context')
    probe('wrong_filter',lambda d:d['bindings'][0]['context'].update(pyListFilter='x'), 'filter context')
    probe('evidence_missing',lambda d:d['bindings'][0].update(evidence=['E999']), 'binding evidence')
    probe('binding_null_tail',lambda d:d['bindings'].append(None), 'bindings object array')
    probe('binding_census_proof',lambda d:d['bindings'][0].update(evidence=[values(records,'PROFILE')['evidence'].split(',')[-1]]), 'source snapshot')
    action={'phase':'SETUP','type':'ApplyDataTransform','name':'PrepareCustomer','page':'RunRecordPrimaryPage','parameters':[{'name':'Message','formalType':'String','valueType':'string','value':'A"B\\C','evidence':[]}],'evidence':[]}
    action_records=deepcopy(records)
    action_id=next(r['values']['id'] for r in action_records if r['tag']=='EVIDENCE' and r['values']['source']=='EXECUTION_ACTIONS')
    action['evidence']=[action_id]
    declarations=[{'pyParametersParamName':'Message','pyParametersParamType':'String'}]
    did=add_evidence(action_records,'DEPENDENCY','ActionRule/ApplyDataTransform/PrepareCustomer/pyParameters',declarations)
    vid=add_evidence(action_records,'EXECUTION','ACTION_ARGUMENTS/0',[{'name':'Message','valueType':'string','value':action['parameters'][0]['value']}])
    action['parameters'][0]['evidence']=[did,vid]
    next(r['values'] for r in action_records if r['tag']=='EVIDENCE' and r['values']['source']=='EXECUTION_ACTIONS')['fact']=p.canonical([{k:action[k] for k in ('phase','type','name','page')}])
    edit(action_records,lambda d:d.update(actions=[action]));validate(action_records)
    def action_probe(name,mutate,message):
        copy=deepcopy(action_records);edit(copy,mutate);probes.append((name,copy,message))
    action_probe('action_all_arguments_removed',lambda d:d['actions'][0].update(parameters=[]), 'source mismatch: ACTION_ARGUMENTS')
    action_probe('action_missing_evidence',lambda d:d['actions'][0].update(evidence=[]), 'action evidence')
    action_probe('action_wrong_page',lambda d:d['actions'][0].update(page='pxRequestor'), 'action page')
    action_probe('action_unknown',lambda d:d['actions'][0].update(type='Guess'), 'action identity')
    action_probe('action_phase_order',lambda d:d.update(actions=[dict(d['actions'][0],phase='CLEANUP'),d['actions'][0]]), 'action phase order')
    action_probe('action_unknown_type',lambda d:d['actions'][0]['parameters'][0].update(formalType='Unknown'), 'unprojectable action parameter')
    action_probe('action_duplicate_parameter',lambda d:d['actions'][0]['parameters'].append(deepcopy(d['actions'][0]['parameters'][0])), 'duplicate action parameter')
    for i,value in enumerate([123,True,[],{},None]):
        action_probe('action_bad_carrier_'+str(i),lambda d,v=value:d['actions'][0]['parameters'][0].update(value=v), 'action value carrier')
    action_probe('action_incompatible_type',lambda d:d['actions'][0]['parameters'][0].update(formalType='Integer'), 'unprojectable action parameter')
    action_probe('action_unrelated_evidence',lambda d:d['actions'][0].update(evidence=['E001']), 'source snapshot')
    action_probe('action_invented_name',lambda d:d['actions'][0].update(name='InventedActivity'), 'source mismatch')
    action_probe('action_wrong_formal_evidence',lambda d:d['actions'][0]['parameters'][0].update(evidence=['E001']), 'source snapshot')
    action_probe('action_census_only',lambda d:d['actions'][0].update(evidence=[values(action_records,'PROFILE')['evidence'].split(',')[-1]]), 'source snapshot')
    for field in ('reasoningTrace','dependencyClosureTrace'):
        probe('invented_'+field,lambda d,f=field:d.update({f:d[f]+' STATE W42: fetched=UnrecordedRule.'}), 'cross-trace source mismatch')
    for name,copy,message in probes:
        expect_rejection(name,lambda:validate(copy),message)
    for name,mutate,message in [
        ('legacy_version',lambda raw:raw.replace(b'version=1.2',b'version=1.1',1),'requires revision 1.2'),
        ('crlf',lambda raw:raw.replace(b'\n',b'\r\n'),'raw framing'),
        ('missing_final_lf',lambda raw:raw[:-1],'raw framing'),
        ('extra_lf',lambda raw:raw+b'\n','blank record'),
        ('bom',lambda raw:b'\xef\xbb\xbf'+raw,'raw framing'),
    ]:
        raw=mutate(p.serialize(records))
        expect_rejection(name,lambda:p.read_ledger(b.MemoryFixture(name,raw)),message)
    copy=[r for r in deepcopy(records) if r['tag']!='PROFILE']
    expect_rejection('missing_profile',lambda:validate(copy),'PROFILE scenario census')
    extra=extended_cases(records,action_records)
    print(f'PASS: DEC-027 profiles; ledgers=7 scenarios={count} typed_action=1 profile_mutations={len(probes)} framing_mutations=5 missing_profile=1 extended={extra}')


if __name__=='__main__':
    try:main()
    except (b.ContractError,KeyError,TypeError,ValueError) as error:raise SystemExit(f'FAIL: {error}')
