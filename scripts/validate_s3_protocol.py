#!/usr/bin/env python3
"""Adversarial protocol checks independent of ScenarioGroup/profile projection."""
from copy import deepcopy
import json
from pathlib import Path
import generator_protocol as p


def issue(code='ASSERT_MISSING',action='ADD_ASSERTION',unit=0,scenario=0,path='/UnitTestRules/0/Scenarios/0',decision='A001',severity='B'):
    return dict(code=code,action=action,unit=unit,scenario=scenario,path=path,decision=decision,severity=severity,message='Fixture defect.')


def report(*issues,schema=True):
    routes=[p.issue_route(i['action']) for i in issues if i['severity']=='B']
    return {'valid':not routes,'route':max(routes,key=p.ROUTES.index) if routes else 'OK','blocking':sum(i['severity']=='B' for i in issues),'warnings':sum(i['severity']=='W' for i in issues),'jsonSchemaValidation':{'isValid':schema,'message':'' if schema else 'Fixture schema failure.'},'issues':list(issues)}


def source(group, ids):
    return {'id':group,'scenarios':[{'id':sid,'decisions':['A001','M001','O001'],'rejection':None,'value':'value:'+sid} for sid in ids]}


class Harness:
    def __init__(self,groups,reports,write_ids=None):
        self.groups=deepcopy(groups);self.reports=deepcopy(reports);self.calls=[];self.payloads=[]
        self.write_ids=list(write_ids or ['new|version 1','new|version 2','new|version 3'])
        self.read_failure=None;self.write_failure=None;self.knowledge_failure=None
    def tool(self,name,args):
        self.calls.append((name,deepcopy(args)))
        if name=='GetMemory':
            if args['UUID']==self.read_failure:return {'Success':False,'Payload':'','ErrorCode':'READ_FAILED','ErrorMessage':'private fixture diagnostic'}
            index=self.uuids.index(args['UUID'])
            return {'Success':True,'Payload':json.dumps(self.groups[index]),'ErrorCode':'','ErrorMessage':'','platformMetadata':{}}
        if name=='KnowledgeTool':
            return self.knowledge_failure or {'pxResults':[{'Area':key,'Description':'fixture '+key} for key in args['KnowledgeAreas'].split(',')]}
        if name=='WriteMemory':
            self.payloads.append(args['Payload'])
            if len(self.payloads)==self.write_failure:return {'Success':False,'UUID':'','ErrorCode':'WRITE_FAILED','ErrorMessage':'private fixture diagnostic'}
            return {'Success':True,'UUID':self.write_ids.pop(0),'ErrorCode':'','ErrorMessage':''}
        if name=='UnitTestValidator':return json.dumps(self.reports.pop(0))
        raise p.ContractError('Forbidden tool.')
    def execute(self,when=True):
        self.uuids=[' source|'+str(i)+'\\opaque ' for i in range(len(self.groups))]
        def decode(raw,case,rut,index):return p.strict_json(raw)
        def project(current,cache,repair):
            return json.dumps({'UnitTestRules':[{'group':g['id'],'Scenarios':[{'id':s['id'],'value':s['value']} for s in g['scenarios']]} for g in current]})
        self.result=p.run(' CASE exact ','Rule-Obj-When' if when else 'Rule-Obj-Model',self.uuids,self.tool,decode,project)
        self.check_invariants()
        return self.result
    def check_invariants(self):
        calls=self.calls
        reads=[a for n,a in calls if n=='GetMemory'];writes=[a for n,a in calls if n=='WriteMemory'];validators=[a for n,a in calls if n=='UnitTestValidator']
        p.require([a['UUID'] for a in reads]==self.uuids[:len(reads)],'ordered exact reads')
        p.require(all(a['CaseID']==' CASE exact ' for n,a in calls if n!='KnowledgeTool'),'CaseID preservation')
        p.require(all(a['Type']=='ScenarioGroup' for a in reads) and all(a['Type']=='UnitTestCandidate' for a in writes),'closed Memory type allowlist')
        p.require(len(validators)<=3 and len(writes)<=3 and sum(n=='KnowledgeTool' for n,a in calls)<=1,'bounded tool calls')
        p.require(self.result['validationAttempts']==len(validators),'validation attempt count')
        if validators:
            first=next(i for i,(n,a) in enumerate(calls) if n=='UnitTestValidator')
            p.require(not any(n in {'KnowledgeTool','GetMemory'} for n,a in calls[first+1:]),'no reacquisition during repair')
        if self.result['status']=='Failed':p.require(self.result['candidate'] is None and not any(s['outcome']=='Successful' for g in self.result['groups'] for s in g['scenarios']),'failed report exposes old success')
        else:p.require(self.result['candidate']['UUID']==validators[-1]['UnitTestCandidateUUID'],'successful current UUID')
        for payload in self.payloads:
            candidate=json.loads(payload)
            for g in candidate['UnitTestRules']:
                original=next(x for x in self.groups if x['id']==g['group'])
                p.require(all(s['value']==next(o['value'] for o in original['scenarios'] if o['id']==s['id']) for s in g['Scenarios']),'immutable values')


def main():
    p.require(p.knowledge_keys('Rule-Obj-When')==['Rule-Test-Unit-Case_MultInpComb-KnowledgeArea','Rule-Test-Unit-Case_MultInpComb-JsonSchema','Rule-Test-Unit-Case_MultInpComb-JsonExample'],'exact When composite keys')
    p.require(p.knowledge_keys('Rule-Obj-Model')==['Rule-Test-Unit-Case_KnowledgeArea','Rule-Test-Unit-Case_JsonSchema','Rule-Test-Unit-Case_JsonExample'],'exact standard composite keys')
    groups=[source('G1',['S1','S2']),source('G2',['S3'])]
    current=[dict(g,sourceIndex=i) for i,g in enumerate(groups)]
    rejected=0
    def invalid(value,message=''):
        nonlocal rejected
        try:p.validate_report(json.dumps(value) if not isinstance(value,str) else value,current,True)
        except p.ContractError as error:
            p.require(not message or message in str(error),'unexpected report rejection: '+str(error));rejected+=1
        else:raise p.ContractError('invalid report accepted')
    good=report();p.validate_report(json.dumps(good),current,True)
    for field,value in [('blocking',True),('warnings',-1),('valid',False),('route','AUTHOR_REPAIR'),('extra',0)]:
        copy=deepcopy(good);copy[field]=value;invalid(copy)
    for text in ['prefix '+json.dumps(good),json.dumps(good)+' suffix','{"valid":true,"valid":false}','NaN']:
        invalid(text)
    for change in [dict(unit=8),dict(unit=True),dict(scenario=9),dict(scenario=True),dict(path='/UnitTestRules/1/Scenarios/0'),dict(path='/UnitTestRules/0/Scenarios/1'),dict(path='/UnitTestRules/0/RuleCode/pySimulation'),dict(decision='A999'),dict(action='AUTHOR_RERUN'),dict(code='UNKNOWN'),dict(severity='INFO'),dict(path='/bad~9'),dict(scenario=None),dict(unit=None,scenario=0),dict(unit=None,scenario=None,path='/',decision='A001')]:
        i=issue();i.update(change);invalid(report(i))
    invalid(report(issue(),schema=False),'schema-invalid short circuit')
    invalid(report(issue('JSON_SCHEMA_INVALID','FIX_JSON',None,None,'/','')),'schema result contradiction')
    # Both shared metadata and current per-row coordinates are accepted at their true scope.
    p.validate_report(json.dumps(report(issue('SIM_SHAPE_INVALID','FIX_SIMULATION',0,None,'/UnitTestRules/0/RuleCode/pySimulation',''))),current,True)
    p.validate_report(json.dumps(report(issue(path='/UnitTestRules/0/RuleCode/pyExpectedResults/0/pyExpectedResults/1',scenario=1))),current,True)
    flows=0
    def run(h,status,attempts):
        nonlocal flows
        r=h.execute();p.require(r['status']==status and r['validationAttempts']==attempts,'flow outcome');flows+=1;return r
    run(Harness(groups,[report()]),'Completed',1)
    run(Harness(groups,[report(issue(severity='W'))]),'Completed',1)
    run(Harness(groups,[report(issue()),report()]),'Completed',2)
    schema_issue=issue('JSON_SCHEMA_MASS_FAILURE','REBUILD_JSON_FROM_CURRENT_EVIDENCE',None,None,'/','')
    run(Harness(groups,[report(schema_issue,schema=False),report()]),'Completed',2)
    semantic=issue('REASONING_CONTRADICTION','REJECT_SEMANTICS',0,0,'/UnitTestRules/0/Scenarios/0','A001')
    r=run(Harness(groups,[report(semantic),report()]),'PartiallyCompleted',2)
    p.require(r['groups'][0]['scenarios'][0]['outcome']=='Untestable' and r['groups'][0]['scenarios'][1]['scenario']==0,'When prune remapping')
    shared=issue('REASONING_CONTRADICTION','REJECT_SEMANTICS',0,None,'/UnitTestRules/0/RuleCode/pySimulation','')
    r=run(Harness(groups,[report(shared),report()]),'PartiallyCompleted',2)
    p.require(r['groups'][1]['scenarios'][0]['unit']==0,'group prune remapping')
    # After G1 disappears, unit 0 is G2: old unit 1 must be rejected.
    stale=issue(unit=1,path='/UnitTestRules/1/Scenarios/0')
    run(Harness(groups,[report(shared),report(stale)]),'Failed',2)
    mixed=issue(unit=1,path='/UnitTestRules/1/Scenarios/0')
    run(Harness(groups,[report(semantic,mixed),report()]),'PartiallyCompleted',2)
    human=issue('AMBIGUOUS','HUMAN_REVIEW',None,None,'/','')
    h=Harness(groups,[report(semantic,human)]);r=run(h,'Failed',1)
    p.require(not any(s['outcome']=='Untestable' for g in r['groups'] for s in g['scenarios']),'atomic HUMAN precedence')
    global_semantic=issue('REASONING_CONTRADICTION','REJECT_SEMANTICS',None,None,'/','')
    run(Harness(groups,[report(global_semantic)]),'Failed',1)
    run(Harness([groups[0]],[report(shared)]),'Failed',1)
    run(Harness(groups,[report(issue()),report(issue()),report(issue())]),'Failed',3)
    # Prune and mechanical fix draw from the same two-revision budget.
    run(Harness(groups,[report(semantic),report(issue()),report(issue())]),'Failed',3)
    run(Harness(groups,[report(issue()),report()],['same','same']),'Failed',1)
    h=Harness(groups,[report()]);h.read_failure=' source|1\\opaque ';run(h,'Failed',0)
    p.require(not h.payloads,'write after failed ordered read')
    h=Harness(groups,[report()]);h.write_failure=1;run(h,'Failed',0)
    h=Harness(groups,[report(issue()),report()]);h.write_failure=2;run(h,'Failed',1)
    h=Harness(groups,[report()]);h.knowledge_failure={'pxResults':[]};run(h,'Failed',0)
    untestable=deepcopy(groups);untestable[0]['scenarios'][0]['rejection']='SOURCE_NOT_TESTABLE'
    run(Harness(untestable,[report()]),'PartiallyCompleted',1)
    all_failed=deepcopy(groups)
    for g in all_failed:
        for s in g['scenarios']:s['rejection']='SOURCE_NOT_TESTABLE'
    run(Harness(all_failed,[]),'Failed',0)
    h=Harness([source('G1',['S1'])],[report(issue()),report()]);r=h.execute(False)
    p.require(r['status']=='Completed','standard repair');flows+=1
    for args in [('', 'Rule-Obj-When',['x']),('case','',['x']),('case','Rule-Obj-When',[]),('case','Rule-Obj-When',['x','x']),('case','Rule-Obj-When',[None])]:
        r=p.run(*args,lambda *a:(_ for _ in ()).throw(AssertionError('unexpected tool')),None,None)
        p.require(r['status']=='Failed' and r['validationAttempts']==0,'invalid input terminal');flows+=1
    for operation,field in [('read','Payload'),('write','UUID')]:
        for result in [{}, {'response':'success'}, {'Success':True,field:'x','ErrorCode':'READ_FAILED','ErrorMessage':''}, {'Success':False,field:'','ErrorCode':'UNKNOWN','ErrorMessage':'x'}, {'Success':False,field:'x','ErrorCode':'READ_FAILED','ErrorMessage':'x'}, {'Success':1,field:'x','ErrorCode':'','ErrorMessage':''}]:
            try:p.memory_output(result,operation)
            except p.ContractError:rejected+=1
            else:raise p.ContractError('malformed Memory accepted')
    print(f'PASS: S3 independent protocol flows={flows} rejected_reports_and_envelopes={rejected}; no runtime or candidate-schema claim')


if __name__=='__main__':
    try:main()
    except (p.ContractError,KeyError,TypeError,ValueError) as error:raise SystemExit('FAIL: '+str(error))
