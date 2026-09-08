#!/usr/bin/env python3
"""Raw-source regressions for every first S3 design-review bypass (DEC-029)."""
from copy import deepcopy
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator
import generator_projection as p
import generator_protocol as protocol
import validate_s3_projection as audit
import validate_s3_profiles as fixtures
from validate_s3_protocol import report

ROOT=Path(__file__).resolve().parents[1]
CURRENT=ROOT/'fixtures/s3/current'
COUNT=0


def records(name='standard-escaping'):
    return p.sg.read_ledger(CURRENT/(name+'.sgl'),revision='1.3')['records']


def value(rows,tag):return next(r['values'] for r in rows if r['tag']==tag)


def source(rows):
    header=rows[0]['values']
    return p.decode_source(p.sg.serialize(rows).decode(),header['caseId'],header['rutType'],int(header['groupOrder'])-1)


def assert_value(rows,kind,carrier,mode='Text',comparator='Is Equals To'):
    a=value(rows,'ASSERT');a.update(value=carrier,mode=mode,comparator=comparator)
    fixtures.update_source(rows,'ASSERTION_VALUE/'+a['id'],lambda f:f.update(valueType=kind,value=carrier))
    fixtures.edit(rows,lambda f:f['bindings'][0].update(scalarType=mode))
    fixtures.update_source(rows,'PROPERTY_DEFINITION/'+a['id'],lambda f:f.update(pyStringType=mode))
    fixtures.refresh_traces(rows)


def page_parameter(rows,when=False):
    root=value(rows,'ROOT');pages=json.loads(root['pagesAndClasses']);pages['InputPage']='App-Data-Context'
    root.update(pagesAndClasses=p.sg.canonical(pages),namedPageEvidence=p.sg.canonical([{'page':'InputPage','runtimeUse':'PAGE_PARAMETER','evidence':'E001'}]))
    arg=value(rows,'PARAM');arg.update(name='Context',formalType='PAGE',valueType='string',value='InputPage',expression='Param.Context')
    inp=value(rows,'INPUT');inp.update(path='Param.Context',mode='Text',valueType='string',value='InputPage')
    formal=next(r['values'] for r in rows if r['tag']=='EVIDENCE' and r['values']['id']==arg['formalEvidence'])
    formal['fact']=p.sg.canonical({'pyParametersParamName':'Context','pyParametersParamType':'PAGE'})
    if when:
        col=value(rows,'COLUMN');col.update(path='Param.Context',mode='Text')
        a=value(rows,'ASSERT');a.update(target='Param.Context',mode='Text',value='InputPage')
        fixtures.refresh_traces(rows)


def invoke(raws,cache=None,arguments=None):
    global COUNT
    calls=[];writes=[]
    first=p.b.parse_line(raws[0].splitlines()[0],1)['values'] if raws else {'caseId':'Case','rutType':'Rule-Obj-Model'}
    args=arguments or (first['caseId'],first['rutType'],['UUID'+str(i) for i in range(len(raws))])
    cache=deepcopy(cache or audit.cache_for(first['rutType']))
    def tool(name,params):
        calls.append(name)
        if name=='GetMemory':return {'Success':True,'Payload':raws[int(params['UUID'][4:])],'ErrorCode':'','ErrorMessage':''}
        if name=='KnowledgeTool':return {'pxResults':[{'Area':k,'Description':v} for k,v in cache.items()]}
        if name=='WriteMemory':writes.append(json.loads(params['Payload'],parse_float=p.Decimal));return {'Success':True,'UUID':'candidate/'+str(len(writes)),'ErrorCode':'','ErrorMessage':''}
        if name=='UnitTestValidator':return json.dumps(report())
        raise AssertionError(name)
    result=protocol.run(*args,tool,p.decode_source,p.candidate,p.preflight)
    Draft202012Validator(json.loads((ROOT/'docs/contracts/GENERATOR_RUN_REPORT_V1.schema.json').read_text())).validate(result)
    COUNT+=1
    return result,calls,writes


def encoded(rows):return p.sg.serialize(rows).decode()


def main():
    global COUNT
    # Full raw source, full selected schema, then independent reverse audit.
    vectors=[('json','["Ada","Grace"]','Text','Is In',['Ada','Grace']),('string','["Ada","Grace"]','Text','Is In','["Ada","Grace"]'),('null','null','Text','Is Equals To',None),('string','null','Text','Is Equals To','null'),('empty','<EMPTY>','Text','Is Equals To',''),('string','<EMPTY>','Text','Is Equals To','<EMPTY>'),('boolean','false','TrueFalse','Is False',False),('number','12345678901234567890.1234567890123456789','Decimal','Is Equals To',p.Decimal('12345678901234567890.1234567890123456789'))]
    for kind,carrier,mode,cmp,wanted in vectors:
        rows=records();assert_value(rows,kind,carrier,mode,cmp);s=source(rows)
        result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']=='Completed' and audit.flat(writes[0]['UnitTestRules'][0]['RuleCode']['pyExpectedResults'][0]['pyExpectedResults'][0]['pyExpectedValue'])==audit.flat(wanted),'raw typed ASSERT value')
        audit.audit(writes[0],[s],audit.cache_for(s['header']['rutType']))
    for name,when in [('standard-escaping',False),('when-formal-parameter',True)]:
        rows=records(name);page_parameter(rows,when);s=source(rows)
        result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']=='Completed','PAGE complete flow: '+str(result))
        code=writes[0]['UnitTestRules'][0]['RuleCode']
        p.b.require({'pySetupPageName':'InputPage','pyPageDetails':{'pxObjClass':'App-Data-Context'}} in code['pySetupPages'],'PAGE argument initialized without incidental seed')
        audit.audit(writes[0],[s],audit.cache_for(s['header']['rutType']))
        bad=deepcopy(writes[0]);bad['UnitTestRules'][0]['RuleCode']['pySetupPages']=[v for v in code['pySetupPages'] if v['pySetupPageName']!='InputPage'];audit.rejected(lambda:audit.audit(bad,[s],audit.cache_for(s['header']['rutType'])));COUNT+=1
    for wrapper,collection in [('Code-Pega-List','Items'),('Code-Pega-List','pxResults'),('App-Data-Catalog','DomainItems')]:
        rows=records();sim=value(rows,'SIM');payload={'pxObjClass':wrapper,collection:[{'pxObjClass':'App-Data-Item','Name':'one'}]}
        sim.update(shape='list',itemClass='App-Data-Item',payload=p.sg.canonical(payload))
        fixtures.update_source(rows,'SIMULATION_BINDING/M001',lambda f:f.update(itemPath='.'+collection))
        sim['setupPages']=p.sg.canonical([{'pySetupPageName':'LocalePage','pyPageDetails':[{'path':'.Locale','valueType':'string','value':'nl_NL'}]},{'pySetupPageName':'PrimaryPage','pyPageDetails':[]}])
        s=source(rows);result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']=='Completed','evidenced wrapper complete flow')
        out=writes[0]['UnitTestRules'][0]['RuleCode']['pySimulation'][0]['pySetupPages']
        p.b.require([v['pySetupPageName'] for v in out]==['LocalePage','PrimaryPage'] and out[1]['pyPageDetails']==payload,'exact census and non-first payload binding')
        audit.audit(writes[0],[s],audit.cache_for('Rule-Obj-Model'))
    # Follow-up review: strict TrueFalse semantics precede generic null/array typing.
    for kind,carrier in [('null','null'),('json','[true,false]')]:
        rows=records();assert_value(rows,kind,carrier,'TrueFalse','Is Equals To');source(rows)
        result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']=='Failed' and result['groups'][0]['scenarios'][0]['code']=='SOURCE_BOOLEAN_COMPARATOR' and not writes,'TrueFalse array/null lock')
    good=records();bad=deepcopy(good);bad[0]['values'].update(groupId='G002',groupOrder='2');value(bad,'SCENARIO')['name']='TC_bad';source(bad)
    result,calls,writes=invoke([encoded(good),encoded(bad)])
    p.b.require(result['status']=='PartiallyCompleted' and len(writes[0]['UnitTestRules'])==1 and result['groups'][1]['scenarios'][0]['code']=='SOURCE_SCENARIO_NAME_UNPROJECTABLE','local construction rejection')
    bad_when=records('when-two-rows');value(bad_when,'SCENARIO')['name']='TC_bad';source(bad_when)
    result,calls,writes=invoke([encoded(bad_when)])
    p.b.require(result['status']=='Failed' and not writes and all(s['outcome']=='Untestable' for s in result['groups'][0]['scenarios']),'shared When source-name failure')
    local_when=records('when-two-rows');[r['values'] for r in local_when if r['tag']=='SCENARIO'][1]['name']='TC_bad';source(local_when)
    result,calls,writes=invoke([encoded(local_when)])
    p.b.require(result['status']=='PartiallyCompleted' and len(writes[0]['UnitTestRules'][0]['Scenarios'])==1,'local When narrative-name failure retains first row')
    for unused in [[],[{'pxObjClass':'App-Data-Item'}]]:
        rows=records();sim=value(rows,'SIM');sim.update(shape='list',itemClass='App-Data-Item',payload=p.sg.canonical({'pxObjClass':'Code-Pega-List','Items':[{'pxObjClass':'Wrong-Class'}],'Unused':unused}))
        fixtures.update_source(rows,'SIMULATION_BINDING/M001',lambda f:f.update(itemPath='.Items'));source(rows)
        result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']=='Failed' and not writes and result['groups'][0]['scenarios'][0]['code']=='SOURCE_SIMULATION_ITEM_CLASS','unrelated collection cannot establish item class')
    rows=records();sim=value(rows,'SIM');payload={'pxObjClass':'App-Data-Catalog','Domain':{'Items':[{'pxObjClass':'App-Data-Item','Children':[{'pxObjClass':'App-Data-Child'}]}]},'Unused':[{'pxObjClass':'Other'}]}
    sim.update(shape='list',itemClass='App-Data-Item',payload=p.sg.canonical(payload));fixtures.update_source(rows,'SIMULATION_BINDING/M001',lambda f:f.update(itemPath='.Domain.Items'))
    s=source(rows);result,calls,writes=invoke([encoded(rows)]);p.b.require(result['status']=='Completed','nested selected collection preserves unrelated arrays');audit.audit(writes[0],[s],audit.cache_for('Rule-Obj-Model'))
    for field,carrier,success in [('.Items(1).pxObjClass','Wrong-Class',False),('.Items(1).Name','missing class',False),('.Items(1).pxObjClass','App-Data-Item',True)]:
        rows=records();sim=value(rows,'SIM');sim.update(shape='list',itemClass='App-Data-Item',payload=p.sg.canonical({'pxObjClass':'Code-Pega-List','Items':[]}))
        sim['setupPages']=p.sg.canonical([{'pySetupPageName':'PrimaryPage','pyPageDetails':[{'path':field,'valueType':'string','value':carrier}]}])
        fixtures.update_source(rows,'SIMULATION_BINDING/M001',lambda f:f.update(itemPath='.Items'));s=source(rows)
        result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']==('Completed' if success else 'Failed'),'assembled seeded item class')
        if success:audit.audit(writes[0],[s],audit.cache_for('Rule-Obj-Model'))
        else:p.b.require(not writes and result['groups'][0]['scenarios'][0]['code']=='SOURCE_SIMULATION_ITEM_CLASS','bad assembled class rejects before write')
    # Original system-page ban: every named carrier, both families, all eight roots.
    banned={'pxProcess','AccessGroup','Application','OperatorID','Org','OrgDivision','pxRequestor','pxThread'}
    for name in ['standard-escaping','when-formal-parameter','when-two-rows']:
        baseline=encoded(records(name))
        for root in banned:
            result,calls,writes=invoke([baseline.replace('RunRecordPrimaryPage',root)])
            p.b.require(result['status']=='Failed' and calls==['GetMemory'] and not writes and result['errorMessage']=='SOURCE_RESERVED_SYSTEM_PAGE','reserved primary/P&C/root rejection')
        if name=='when-two-rows':continue
        # PAGE parameter root also appears in P&C/named-page evidence.
        rows=records(name);page_parameter(rows,name.startswith('when'));baseline=encoded(rows)
        for root in banned:
            result,calls,writes=invoke([baseline.replace('InputPage',root)])
            p.b.require(result['status']=='Failed' and calls==['GetMemory'],'reserved PAGE argument/named-page rejection')
    for name in ['standard-escaping','when-key-b']:
        rows=records(name)
        # Make this a standalone first group; source identity is otherwise unchanged.
        rows[0]['values'].update(groupOrder='1',groupId='G001')
        baseline=encoded(rows)
        for root in banned:
            result,calls,writes=invoke([re.sub(r'\bPrimaryPage\b',root,baseline)])
            p.b.require(result['status']=='Failed' and calls==['GetMemory'] and result['errorMessage']=='SOURCE_RESERVED_SYSTEM_PAGE','reserved simulation root rejection')
    # Absolute When cell roots are separate from its valid primary page.
    for root in banned:
        rows=records('when-no-simulation')
        for record in rows:
            v=record['values']
            if record['tag']=='COLUMN':v['path']=root+'.Amount'
            if record['tag']=='INPUT':v['path']=root+'.Amount'
            if record['tag']=='ASSERT' and v['kind']=='DecisionInput':v['target']=root+'.Amount'
        fixtures.refresh_traces(rows);result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']=='Failed' and calls==['GetMemory'] and result['errorMessage']=='SOURCE_RESERVED_SYSTEM_PAGE','reserved absolute When cell')
    for root in banned:
        rows=records();seed=value(rows,'SETUP');seed['path']=root+'.Notes'
        result,calls,writes=invoke([encoded(rows)])
        p.b.require(result['status']=='Failed' and calls==['GetMemory'] and result['errorMessage']=='SOURCE_RESERVED_SYSTEM_PAGE','reserved absolute setup path')
    for name in ['standard-escaping','when-no-simulation']:
        rows=records(name)
        if name.startswith('standard'):
            value(rows,'SETUP').update(path='.pxThread.OperatorID',value='AccessGroup')
            value(rows,'SIM')['payload']=p.sg.canonical({'pxThread':{'OperatorID':'safe nested data'}})
        else:
            for record in rows:
                v=record['values']
                if record['tag']=='COLUMN':v['path']='.pxThread.Amount'
                if record['tag']=='INPUT':v['path']='.pxThread.Amount'
                if record['tag']=='ASSERT' and v['kind']=='DecisionInput':v['target']='.pxThread.Amount'
            fixtures.refresh_traces(rows)
        result,calls,writes=invoke([encoded(rows)]);p.b.require(result['status']=='Completed','nested reserved-token data stays valid')
    for name in ['standard-escaping','when-two-rows']:
        for root in banned:
            rows=records(name);header=value(rows,'ROOT');classes=json.loads(header['pagesAndClasses']);classes[root]='App-Data-Context'
            header.update(pagesAndClasses=p.sg.canonical(classes),namedPageEvidence=p.sg.canonical([{'page':root,'runtimeUse':'EXECUTABLE_PATH','evidence':'E001'}]))
            result,calls,writes=invoke([encoded(rows)]);p.b.require(result['status']=='Failed' and calls==['GetMemory'] and result['errorMessage']=='SOURCE_RESERVED_SYSTEM_PAGE','reserved extra P&C declaration')
            rows=records(name);sim=value(rows,'SIM');sim['setupPages']=p.sg.canonical([{'pySetupPageName':'PrimaryPage','pyPageDetails':[{'path':root+'.Value','valueType':'string','value':'seed'}]}])
            if name.startswith('when'):
                # Keep every scenario and the complete physical key synchronized.
                for record in rows:
                    if record['tag']=='SIM':record['values']['setupPages']=sim['setupPages']
                key=json.loads(rows[0]['values']['simulationGroupKey'])
                for item in key['simulations']:item['setupPages']=json.loads(sim['setupPages'])
                rows[0]['values']['simulationGroupKey']=p.sg.canonical(key)
            result,calls,writes=invoke([encoded(rows)]);p.b.require(result['status']=='Failed' and calls==['GetMemory'] and result['errorMessage']=='SOURCE_RESERVED_SYSTEM_PAGE','reserved absolute simulation seed')
    for root in banned:
        rows=records('when-two-rows');next(r['values'] for r in rows if r['tag']=='SETUP' and r['values']['scenario']=='S2')['path']=root+'.Discount'
        result,calls,writes=invoke([encoded(rows)]);p.b.require(result['status']=='Failed' and calls==['GetMemory'] and result['errorMessage']=='SOURCE_RESERVED_SYSTEM_PAGE','reserved absolute When setup')
    # Full same-case standard sources: schema-specific comparator rejects only second.
    first=records();second=deepcopy(first);second[0]['values'].update(groupId='G002',groupOrder='2')
    a=value(second,'ASSERT');a['comparator']='Unsupported Comparator';fixtures.refresh_traces(second);source(second)
    result,calls,writes=invoke([encoded(first),encoded(second)])
    p.b.require(result['status']=='PartiallyCompleted' and len(writes)==1 and len(writes[0]['UnitTestRules'])==1 and result['groups'][1]['scenarios'][0]['code']=='SOURCE_SCHEMA_UNREPRESENTABLE','local schema rejection before combined write')
    # Invalid arguments are never echoed into structurally invalid group addresses.
    for args in [('Case','Model',['']),('Case','Model',[]),('Case','Model',['x','x']),('Case','Model',[None]),('', 'Model',['x']),(None,'Model',['x']),('Case',None,['x']),('Case','Model',None)]:
        result,calls,writes=invoke([],arguments=args)
        p.b.require(result['status']=='Failed' and result['groups']==[] and calls==[],'invalid input terminal representation')
    for template in [{'UnitTestRules':[]},{'UnitTestRules':[{'RuleCode':None}]},{'UnitTestRules':[{'RuleCode':[]}]},{'UnitTestRules':[None]},[],None,{}, {'UnitTestRules':'bad'}]:
        cache=audit.cache_for('Rule-Obj-Model');cache[protocol.knowledge_keys('Rule-Obj-Model')[2]]=json.dumps(template)
        result,calls,writes=invoke([encoded(first)],cache=cache)
        p.b.require(result['status']=='Failed' and 'WriteMemory' not in calls and 'UnitTestValidator' not in calls,'malformed template terminal')
    # Raw provenance bypasses; no decoding normalization or type guessing.
    for mutation in [lambda r:fixtures.update_source(r,'ASSERTION_VALUE/A001',lambda f:f.update(value='different')),lambda r:fixtures.update_source(r,'ASSERTION_VALUE/A001',lambda f:f.update(valueType='unknown')),lambda r:fixtures.update_source(r,'ASSERTION_VALUE/A001',lambda f:f.update(value=['Ada'])),lambda r:fixtures.edit(r,lambda f:f['bindings'][0].update(evidence=f['bindings'][0]['evidence'][:-1])),lambda r:value(r,'SIM').update(setupPages='[]'),lambda r:fixtures.update_source(r,'SIMULATION_BINDING/M001',lambda f:f.update(payloadPage='InventedPage'))]:
        copy=deepcopy(first);mutation(copy);result,calls,writes=invoke([encoded(copy)])
        p.b.require(result['status']=='Failed' and 'WriteMemory' not in calls,'malformed provenance rejected');COUNT+=1
    # Reverse-census mutations exercise omissions that still satisfy JSON Schema.
    s=source(first);cache=audit.cache_for('Rule-Obj-Model');v=json.loads(p.candidate([s],cache),parse_float=p.Decimal)
    probes=[lambda c:c['pyRuleUnderTest'].pop('pyParameters'),lambda c:c['pyExpectedResults'][0].pop('pyCardApplyToClass'),lambda c:c['pyRuleUnderTest']['pyDetails'].update(pyRuleUnderTestInsName='WRONG!NAME'),lambda c:c['pySetupPages'][0]['pyPageDetails'].update(Extra='unevidenced'),lambda c:c['pySimulation'][0]['pySetupPages'][0].update(pySetupPageName='D_Customer'),lambda c:c['pySimulation'][0]['pySetupPages'][0]['pyPageDetails'].update(Extra='unevidenced'),lambda c:c.update(pySetup=[{'pyActionType':'ApplyDataTransform','pyActionName':'Invented'}])]
    for mutate in probes:
        copy=deepcopy(v);mutate(copy['UnitTestRules'][0]['RuleCode']);audit.rejected(lambda:audit.audit(copy,[s],cache));COUNT+=1
    # Actual ordered action/argument source, not a target-only invented-action test.
    action={'phase':'SETUP','type':'ApplyDataTransform','name':'PrepareCustomer','page':'RunRecordPrimaryPage','parameters':[{'name':'Message','formalType':'String','valueType':'string','value':'A"B\\C','evidence':[]}],'evidence':[]}
    action_rows=records();eid=next(r['values']['id'] for r in action_rows if r['tag']=='EVIDENCE' and r['values']['source']=='EXECUTION_ACTIONS')
    did=fixtures.add_evidence(action_rows,'DEPENDENCY','ActionRule/ApplyDataTransform/PrepareCustomer/pyParameters',[{'pyParametersParamName':'Message','pyParametersParamType':'String'}]);vid=fixtures.add_evidence(action_rows,'EXECUTION','ACTION_ARGUMENTS/0',[{'name':'Message','valueType':'string','value':action['parameters'][0]['value']}])
    action['evidence']=[eid];action['parameters'][0]['evidence']=[did,vid]
    fixtures.update_source(action_rows,'EXECUTION_ACTIONS',lambda f:f.append({k:action[k] for k in ('phase','type','name','page')}));fixtures.edit(action_rows,lambda f:f.update(actions=[action]))
    s=source(action_rows);result,calls,writes=invoke([encoded(action_rows)]);p.b.require(result['status']=='Completed','action source complete flow');audit.audit(writes[0],[s],cache)
    for mutate in [lambda c:c.pop('pySetup'),lambda c:c['pySetup'][0].pop('pyParameters'),lambda c:c['pySetup'][0]['pyParameters'][0].update(pyParametersParamValue='changed')]:
        copy=deepcopy(writes[0]);mutate(copy['UnitTestRules'][0]['RuleCode']);audit.rejected(lambda:audit.audit(copy,[s],cache));COUNT+=1
    p.b.require('\n  "UnitTestRules": [' in p.candidate([s],cache),'pretty-print source preference')
    print(f'PASS: S3 design-review correction regressions={COUNT}; raw 1.3 values, PAGE, wrappers/census, scoped schema, all terminal reports, reverse audits')


if __name__=='__main__':
    main()
