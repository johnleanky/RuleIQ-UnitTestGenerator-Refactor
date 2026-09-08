"""Static Author storage boundary over already audited source fixtures; no RUT analysis."""
from pathlib import Path
import json

from jsonschema import Draft202012Validator
import generator_protocol as g
import generator_projection as p

ROOT=Path(__file__).resolve().parents[1]
REPORT_SCHEMA=json.loads((ROOT/'docs/contracts/GENERATOR_RUN_REPORT_V1.schema.json').read_text())


def outer(status, message=''):
    return {'AIAgentResponseStatus':status,'AIAgentErrorResponseMessage':message}


def terminal_report(value, case_id=None, uuids=None, sources=None):
    report=g.strict_json(value) if isinstance(value,str) else value
    Draft202012Validator(REPORT_SCHEMA).validate(report)
    status=report['status'];groups=report['groups']
    checks=[s for group in groups for s in group['scenarios']]
    successful=[s for s in checks if s['outcome']=='Successful']
    rejected=[s for s in checks if s['outcome']=='Untestable']
    attempts=report['validationAttempts'];repairs=report['repairAttempts']
    g.require(repairs<=attempts<=repairs+1,'Contradictory attempt counts.')
    if uuids is not None:
        # G9 permits an empty report only for rejected invocation arguments.
        invalid_input=len(set(uuids))!=len(uuids)
        g.require([group['sourceUUID'] for group in groups]==uuids or
                  invalid_input and status=='Failed' and not groups and attempts==repairs==0,
                  'Wrong source addresses.')
    g.require(len({group['sourceUUID'] for group in groups})==len(groups),'Repeated source address.')
    for index,group in enumerate(groups):
        if group['readState']=='Ready':
            g.require(group['groupId'] is not None and group['scenarios'],'Missing parsed source identity.')
            g.require(len({s['id'] for s in group['scenarios']})==len(group['scenarios']),'Repeated Scenario identity.')
            if sources is not None:
                g.require(group['groupId']==sources[index]['id'] and
                          [s['id'] for s in group['scenarios']]==[s['id'] for s in sources[index]['scenarios']],
                          'Wrong parsed source identity.')
        else:g.require(group['groupId'] is None and not group['scenarios'],'Fabricated unread source.')
    if status=='Failed':
        g.require(not successful,'Failed report contains success.')
    else:
        g.require(groups and all(group['readState']=='Ready' for group in groups),'Incomplete successful report.')
        g.require(successful and all(s['outcome']!='NotValidated' for s in checks),'Missing successful outcome.')
        g.require(bool(rejected)==(status=='PartiallyCompleted'),'Contradictory terminal status.')
        g.require(attempts==repairs+1,'Unvalidated successful revision.')
        if case_id is not None:g.require(report['candidate']['CaseID']==case_id,'Wrong candidate CaseID.')
        unit=0
        for group in groups:
            retained=[s for s in group['scenarios'] if s['outcome']=='Successful']
            for index,s in enumerate(retained):
                g.require((s['unit'],s['scenario'])==(unit,index),'Wrong current coordinates.')
            if retained:unit+=1
    return outer('Completed') if status in {'Completed','PartiallyCompleted'} else outer('Failed','Unit test generation failed.')


def run(case_data, payloads, tools):
    """Inputs represent original GetCaseData and fully formed Author payloads.

    Parsing proves the shared source grammar at this boundary, not arbitrary
    semantic authoring. All source payloads are checked before any Memory write.
    """
    try:
        case_id=case_data['pyID'];rut=case_data['RuleJSON']['pxObjClass']
        g.require(isinstance(case_id,str) and case_id!='' and isinstance(rut,str) and rut.strip(),'Invalid source context.')
        g.require(isinstance(payloads,list) and payloads,'No final groups.')
        sources=[p.decode_source(raw,case_id,rut,index) for index,raw in enumerate(payloads)]
        g.require(len({s['id'] for s in sources})==len(sources),'Duplicate source group.')
        for s in sources[1:]:
            g.require(all(s['header'][k]==sources[0]['header'][k] for k in ('rutClass','rutName','ruleset')),'Conflicting source context.')
        if rut=='Rule-Obj-When':g.require(len({s['header']['simulationGroupKey'] for s in sources})==len(sources),'Duplicate physical groups.')
    except Exception:
        return outer('Failed','Scenario group validation failed.')
    uuids=[]
    for payload in payloads:
        try:
            result=tools('WriteMemory',{'CaseID':case_id,'Type':'ScenarioGroup','Payload':payload})
            uuids.append(g.memory_output(result,'write'))
        except Exception:
            return outer('Failed','Scenario group storage failed.')
    try:
        result=tools('UnitTestGenerator',{'CaseID':case_id,'RUTType':rut,'ScenarioGroupUUIDs':uuids})
    except Exception:
        return outer('Failed','Unit test generation failed.')
    try:return terminal_report(result,case_id,uuids,sources)
    except Exception:return outer('Failed','Unit test generator returned an invalid response.')
