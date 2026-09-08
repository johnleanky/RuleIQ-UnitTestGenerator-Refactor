#!/usr/bin/env python3
"""Connected repository-only caller flows with real Generator and Validator reports."""
from copy import deepcopy
import json
from jsonschema import Draft202012Validator

import generator_protocol as g
import generator_projection as p
import scenario_author_protocol as author
import validator_protocol as v
from s5_fixture_runtime import Runtime

CASES={}


def case(name):
    def register(fn):CASES[name]=fn;return fn
    return register


def trace_contract(runtime):
    context=runtime.context;calls=runtime.calls;cid=context['pyID'];rut=context['RuleJSON']['pxObjClass']
    handoffs=[a for actor,n,a in calls if actor=='Author' and n=='UnitTestGenerator']
    assert len(handoffs)<=1
    source_reads=[a['UUID'] for actor,n,a in calls if actor=='Generator' and n=='GetMemory']
    if handoffs:assert source_reads==handoffs[0]['ScenarioGroupUUIDs'][:len(source_reads)]
    for index,(actor,name,args) in enumerate(calls):
        if 'CaseID' in args:assert args['CaseID']==cid
        if 'RUTType' in args:assert args['RUTType']==rut
        if name in {'WriteMemory','GetMemory'}:
            assert set(args)==({'CaseID','Type','Payload'} if name=='WriteMemory' else {'CaseID','Type','UUID'})
            assert args['Type']==('ScenarioGroup' if actor=='Author' or actor=='Generator' and name=='GetMemory' else 'UnitTestCandidate')
        if actor=='Author':assert name in {'WriteMemory','UnitTestGenerator'}
        if actor=='Generator':assert name in {'GetMemory','KnowledgeTool','WriteMemory','UnitTestValidator'}
        if actor=='Validator':assert name in {'GetMemory','KnowledgeTool','JsonValidationTool'}
        if name=='UnitTestValidator':
            downstream=[]
            for who,tool,values in calls[index+1:]:
                if who!='Validator':break
                downstream.append((tool,values))
            names=[n for n,a in downstream]
            assert names in [[],['JsonValidationTool'],['JsonValidationTool','GetMemory'],['JsonValidationTool','GetMemory','KnowledgeTool']]
            for n,a in downstream:
                if n in {'JsonValidationTool','GetMemory'}:assert a['UUID']==args['UnitTestCandidateUUID']
                if n=='JsonValidationTool':assert a['JsonSchema']==g.knowledge_keys(rut)[1]
    candidate_records=[r for r in runtime.records.values() if r.kind=='UnitTestCandidate']
    assert runtime.validations==[r.uuid for r in candidate_records][:len(runtime.validations)]
    assert len(runtime.validations)<=3
    assert all(r.payload==raw for r,raw in zip([r for r in runtime.records.values() if r.kind=='ScenarioGroup'],runtime.payloads))


def execute(names=('standard-escaping',),**kwargs):
    runtime=Runtime(names,**kwargs);outer=runtime.run();trace_contract(runtime);return runtime,outer


def mutate(first_change,repeat=False,schema_invalid=False):
    def fault(runtime,raw):
        if repeat or len(runtime.projects)==1:
            value=v.parse_json(raw);first_change(value)
            schema=json.loads(runtime.cache[g.knowledge_keys(runtime.context['RuleJSON']['pxObjClass'])[1]])
            errors=list(Draft202012Validator(schema).iter_errors(value))
            assert bool(errors)==schema_invalid,'fault must have its declared schema classification'
            return p.json_text(value)
        return raw
    return fault


def child(value,u=0):return value['UnitTestRules'][u]['RuleCode']['pyExpectedResults'][0]['pyExpectedResults'][0]
def trace(value,s=0,u=0):return value['UnitTestRules'][u]['Scenarios'][s]['EvidenceSummary']
def when_result(value,u=0,s=0):return value['UnitTestRules'][u]['RuleCode']['pyExpectedResults'][0]['pyExpectedResults'][s]['pyExpectedResults'][-1]


@case('nominal_both_families_and_multiple_groups')
def _():
    for names in [('standard-escaping',),('when-two-rows',),('when-no-simulation',),('when-formal-parameter',),('when-key-a','when-key-b')]:
        r,out=execute(names)
        assert out==author.outer('Completed') and r.generator_report['status']==('PartiallyCompleted' if len(names)==2 else 'Completed')
        assert len(r.reports)==len(r.projects)==1 and r.reports[0]['route']=='OK'
        assert [n for actor,n,a in r.calls if actor=='Author']==['WriteMemory']*len(names)+['UnitTestGenerator']
        assert len([1 for actor,n,a in r.calls if actor=='Generator' and n=='KnowledgeTool'])==1


@case('author_write_failure_and_uncertain_write_no_partial_handoff')
def _():
    for failure_at in [1,2]:
        for uncertain in [False,True]:
            def hook(r,actor,name,args,actual):
                if actor=='Author' and name=='WriteMemory' and sum(a=='Author' and n=='WriteMemory' for a,n,x in r.calls)==failure_at:
                    if uncertain:actual();raise RuntimeError('uncertain fixture write')
                    return r.failure(name,'WRITE_FAILED')
                return actual()
            r,out=execute(('when-key-a','when-key-b'),hook=hook)
            assert out==author.outer('Failed','Scenario group storage failed.')
            assert len(r.calls)==failure_at and not r.generator_report and not r.validations
            assert len(r.records)==failure_at if uncertain else len(r.records)==failure_at-1


@case('author_source_gate_before_any_write')
def _():
    r=Runtime(('standard-escaping',));calls=[]
    for payloads in [[],[r.payloads[0]+'\n'],['\ufeff'+r.payloads[0]],[r.payloads[0].replace('version=1.3','version=1.2',1)]]:
        assert author.run(r.context,payloads,lambda *args:calls.append(args))==author.outer('Failed','Scenario group validation failed.')
    assert not calls


@case('closed_author_status_and_errors')
def _():
    valid=execute()[0].generator_report
    partial=execute(('when-key-a','when-key-b'))[0].generator_report
    failed=execute(('standard-not-testable',))[0].generator_report
    for report,expected in [(valid,'Completed'),(partial,'Completed'),(failed,'Failed')]:
        assert author.terminal_report(report)['AIAgentResponseStatus']==expected
        assert author.terminal_report(json.dumps(report))['AIAgentResponseStatus']==expected
    for bad in [{},dict(valid,status='Unknown'),dict(valid,status=True),dict(valid,extra='secret'),json.dumps(valid)+' prose',dict(valid,candidate={'UUID':'secret'})]:
        def hook(r,a,n,args,actual):return bad if n=='UnitTestGenerator' else actual()
        r,out=execute(hook=hook)
        assert out==author.outer('Failed','Unit test generator returned an invalid response.')
        assert 'secret' not in json.dumps(out) and not r.validations


@case('author_report_consistency_and_known_handoff')
def _():
    valid=execute()[0].generator_report
    changes=[lambda r:r.update(groups=[]),
             lambda r:r.update(status='PartiallyCompleted'),
             lambda r:r.update(repairAttempts=2),
             lambda r:r['candidate'].update(CaseID='another case'),
             lambda r:r['groups'][0].update(sourceUUID='unknown source'),
             lambda r:r['groups'][0].update(groupId='unknown group'),
             lambda r:r['groups'][0]['scenarios'][0].update(id='unknown Scenario'),
             lambda r:r['groups'][0]['scenarios'][0].update(unit=1),
             lambda r:r['groups'][0]['scenarios'][0].update(scenario=1),
             lambda r:r['groups'][0].update(readState='NotRead'),
             lambda r:r['groups'][0]['scenarios'][0].update(outcome='NotValidated',unit=None,scenario=None),
             lambda r:r['groups'][0]['scenarios'][0].update(outcome='Untestable',unit=None,scenario=None,code='SOURCE_REJECTED'),
             lambda r:r.update(status='Failed',candidate=None,errorMessage='failure with Successful outcome')]
    for change in changes:
        bad=deepcopy(valid);change(bad)
        Draft202012Validator(author.REPORT_SCHEMA).validate(bad)
        for response in [bad,json.dumps(bad)]:
            def hook(r,a,n,args,actual):return response if n=='UnitTestGenerator' else actual()
            r,out=execute(hook=hook)
            assert out==author.outer('Failed','Unit test generator returned an invalid response.')
            assert not r.validations and not [x for x in r.records.values() if x.kind=='UnitTestCandidate']
    # The source-address contract may legitimately reject duplicate tool-returned UUIDs.
    def reuse(r,a,n,args,actual):
        if a=='Author' and n=='WriteMemory':
            result=actual();result['UUID']=next(iter(r.records.values())).uuid;return result
        return actual()
    r,out=execute(('when-key-a','when-key-b'),hook=reuse)
    assert out==author.outer('Failed','Unit test generation failed.')
    assert r.generator_report['groups']==[] and not r.validations


@case('ordinary_schema_and_projection_repair_versions')
def _():
    def schema_bad(x):x['UnitTestRules'][0].pop('Name')
    def projection_bad(x):child(x)['pyExpectedValue']='wrong fixture value'
    for fault,code in [(schema_bad,'JSON_SCHEMA_INVALID'),(projection_bad,'ASSERT_VALUE_MISMATCH')]:
        r,out=execute(projection_fault=mutate(fault,schema_invalid=fault==schema_bad))
        assert out==author.outer('Completed') and [x['route'] for x in r.reports]==['GENERATOR_REPAIR','OK']
        assert any(i['code']==code for i in r.reports[0]['issues'])
        assert len(set(r.validations))==2 and r.generator_report['repairAttempts']==1
        records=[x for x in r.records.values() if x.kind=='UnitTestCandidate'];assert records[0].payload!=records[1].payload
        if fault==schema_bad:
            windows=[n for a,n,args in r.calls if a=='Validator'];assert windows[:2]==['JsonValidationTool','JsonValidationTool']


@case('scenario_pruning_current_rows_and_source_ids')
def _():
    r,out=execute(('when-two-rows',),projection_fault=mutate(lambda x:trace(x).__setitem__('AssertionDecisionTrace','ASSERT|id=A001')))
    assert out==author.outer('Completed') and r.generator_report['status']=='PartiallyCompleted'
    assert [x['route'] for x in r.reports]==['SEMANTIC_REJECT','OK']
    scenarios=r.generator_report['groups'][0]['scenarios'];assert [s['outcome'] for s in scenarios]==['Untestable','Successful']
    assert scenarios[1]['scenario']==0 and scenarios[1]['id']=='S2'
    final=v.parse_json(r.records[r.validations[-1]].payload);assert len(final['UnitTestRules'][0]['Scenarios'])==1
    assert all(t['row']=='1' for t in v.parse_trace(trace(final)['AssertionDecisionTrace']) if t['tag']=='ASSERT')


@case('shared_group_and_mixed_issue_pruning')
def _():
    def fault(x):
        code=x['UnitTestRules'][0]['RuleCode'];seed=deepcopy(code['pySetupPages'][0])
        seed['pySetupPageName']=code['pySimulation'][0]['pyRuleNameToBeMocked'];code['pySetupPages'].append(seed)
        c=when_result(x,1);c['pyExpectedValue']='false' if c['pyExpectedValue']=='true' else 'true'
    r,out=execute(('when-key-a','when-key-b'),projection_fault=mutate(fault))
    assert out==author.outer('Completed') and r.generator_report['status']=='PartiallyCompleted'
    first=r.reports[0];assert first['route']=='SEMANTIC_REJECT'
    assert any(i['action']=='REJECT_SEMANTICS' and i['unit']==0 and i['scenario'] is None for i in first['issues'])
    assert any(i['action']=='FIX_ASSERTION' and i['unit']==1 for i in first['issues'])
    assert all(s['outcome']=='Untestable' for s in r.generator_report['groups'][0]['scenarios'])
    assert all(s['unit']==0 for s in r.generator_report['groups'][1]['scenarios'] if s['outcome']=='Successful')
    assert r.generator_report['repairAttempts']==1


@case('all_failed_source_and_all_rejected_candidate')
def _():
    r,out=execute(('standard-not-testable',));assert out['AIAgentResponseStatus']=='Failed' and not r.projects and not r.validations
    def fault(x):
        for s in x['UnitTestRules'][0]['Scenarios']:s['EvidenceSummary']['AssertionDecisionTrace']='ASSERT|id=A001'
    r,out=execute(('when-two-rows',),projection_fault=mutate(fault))
    assert out['AIAgentResponseStatus']=='Failed' and len(r.validations)==1 and r.generator_report['candidate'] is None
    assert all(s['outcome']=='Untestable' for s in r.generator_report['groups'][0]['scenarios'])


@case('budget_exhaustion_and_failed_repair_write')
def _():
    fault=mutate(lambda x:child(x).__setitem__('pyExpectedValue','wrong'),repeat=True)
    r,out=execute(projection_fault=fault)
    assert out['AIAgentResponseStatus']=='Failed' and len(r.validations)==3
    assert r.generator_report['repairAttempts']==2 and r.generator_report['candidate'] is None
    def hook(r,actor,name,args,actual):
        if actor=='Generator' and name=='WriteMemory' and len(r.projects)==2:return r.failure(name,'WRITE_FAILED')
        return actual()
    r,out=execute(projection_fault=fault,hook=hook)
    assert out['AIAgentResponseStatus']=='Failed' and len(r.validations)==1 and r.generator_report['candidate'] is None


@case('wrong_addresses_and_no_latest_fallback')
def _():
    for actor,name in [('Generator','GetMemory'),('Validator','JsonValidationTool'),('Validator','GetMemory')]:
        for key,value in [('CaseID','wrong-case'),('UUID','unknown-uuid')]+([('Type','WrongType')] if name=='GetMemory' else []):
            def hook(r,a,n,args,actual):
                return actual(dict(args,**{key:value})) if (a,n)==(actor,name) else actual()
            r,out=execute(hook=hook)
            assert out['AIAgentResponseStatus']=='Failed' and r.generator_report['candidate'] is None
            failed=[x for x in r.calls if x[:2]==(actor,name)];assert len(failed)==1
            assert len(r.addresses)==(1 if actor=='Generator' else 2 if name=='JsonValidationTool' else 3)


@case('tool_envelopes_and_knowledge_stop')
def _():
    for actor,name in [('Author','WriteMemory'),('Generator','GetMemory'),('Generator','WriteMemory'),('Validator','JsonValidationTool'),('Validator','GetMemory'),('Generator','KnowledgeTool'),('Validator','KnowledgeTool')]:
        for bad in [{},{'response':'generic failure'},RuntimeError('private payload')]:
            def hook(r,a,n,args,actual):
                if (a,n)==(actor,name):
                    if isinstance(bad,Exception):raise bad
                    return bad
                return actual()
            r,out=execute(hook=hook)
            assert out['AIAgentResponseStatus']=='Failed' and 'private' not in json.dumps(out)
            failed=[i for i,x in enumerate(r.calls) if x[:2]==(actor,name)];assert len(failed)==1
            assert failed[0]==len(r.calls)-1


@case('record_type_isolation_and_reused_candidate_uuid')
def _():
    def hook(r,a,n,args,actual):
        if a=='Validator' and n=='JsonValidationTool':
            source=next(x for x in r.records.values() if x.kind=='ScenarioGroup')
            return actual(dict(args,UUID=source.uuid))
        return actual()
    r,out=execute(hook=hook);assert out['AIAgentResponseStatus']=='Failed' and len(r.reports)==1 and r.reports[0]['route']=='HUMAN'
    def reused(r,a,n,args,actual):
        if a=='Generator' and n=='WriteMemory' and len(r.projects)==2:return r.success(UUID=r.validations[0])
        return actual()
    r,out=execute(hook=reused,projection_fault=mutate(lambda x:child(x).__setitem__('pyExpectedValue','wrong')))
    assert out['AIAgentResponseStatus']=='Failed' and len(r.validations)==1 and r.generator_report['candidate'] is None


@case('trace_monitor_negative_controls')
def _():
    r,out=execute()
    base=deepcopy(r.calls)
    for change in ['uuid','case','type','allowlist']:
        r.calls=deepcopy(base)
        index=next(i for i,(a,n,x) in enumerate(r.calls) if a=='Validator' and n=='GetMemory')
        a,n,args=r.calls[index]
        if change=='uuid':args['UUID']='old-version'
        elif change=='case':args['CaseID']='different-case'
        elif change=='type':args['Type']='ScenarioGroup'
        else:r.calls[index]=(a,'WriteMemory',args)
        try:trace_contract(r)
        except AssertionError:pass
        else:raise AssertionError('trace monitor accepted '+change)
    r.calls=base


@case('shared_budget_pruning_then_repair')
def _():
    for exhausted in [False,True]:
        def fault(r,raw):
            x=v.parse_json(raw)
            if len(r.projects)==1:trace(x)['AssertionDecisionTrace']='ASSERT|id=A001'
            elif len(r.projects)==2 or exhausted:
                c=when_result(x);c['pyExpectedValue']='false' if c['pyExpectedValue']=='true' else 'true'
            Draft202012Validator(json.loads(r.cache[g.knowledge_keys('Rule-Obj-When')[1]])).validate(x)
            return p.json_text(x)
        r,out=execute(('when-two-rows',),projection_fault=fault)
        assert r.generator_report['repairAttempts']==2 and len(r.validations)==3
        assert [report['route'] for report in r.reports]==['SEMANTIC_REJECT','GENERATOR_REPAIR','GENERATOR_REPAIR' if exhausted else 'OK']
        assert out['AIAgentResponseStatus']==('Failed' if exhausted else 'Completed')
        assert r.generator_report['groups'][0]['scenarios'][0]['outcome']=='Untestable'
        assert r.generator_report['candidate'] is None if exhausted else r.generator_report['groups'][0]['scenarios'][1]['scenario']==0


@case('author_exact_required_fields_and_metadata')
def _():
    success=dict(Success=True,UUID='opaque',ErrorCode='',ErrorMessage='')
    bad=[]
    for key in success:
        x=dict(success);x.pop(key);bad.append(x)
        x=dict(success);x[key]=1 if key=='Success' else False;bad.append(x)
    bad.extend([dict(success,ErrorCode='WRITE_FAILED'),dict(success,UUID=''),dict(success,Success=False),dict(Success=False,UUID='',ErrorCode='UNKNOWN',ErrorMessage='private')])
    for value in bad:
        def hook(r,a,n,args,actual):return value if a=='Author' and n=='WriteMemory' else actual()
        r,out=execute(hook=hook)
        assert out==author.outer('Failed','Scenario group storage failed.') and len(r.calls)==1 and not r.records
    # Nominal Runtime.success includes extra platform metadata on every Memory result.
    assert execute()[1]==author.outer('Completed')


def main():
    for name,fn in CASES.items():
        try:fn()
        except Exception as error:raise AssertionError(name+': '+str(error)) from error
    print(f'PASS: S5 connected integration groups={len(CASES)}; actual Author boundary + Generator + Validator; full schemas/source audits; static doubles only')


if __name__=='__main__':main()
