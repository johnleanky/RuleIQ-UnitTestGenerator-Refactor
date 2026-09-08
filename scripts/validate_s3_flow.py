#!/usr/bin/env python3
"""Real revision-1.3 source, schema projection and UUID protocol combined with static tools."""
from copy import deepcopy
from decimal import Decimal
import json
from pathlib import Path
from jsonschema import Draft202012Validator

import generator_protocol as p
import generator_projection as projection
import validate_s3_projection as oracle
from validate_s3_protocol import report,issue

ROOT=Path(__file__).resolve().parents[1]


def case(paths,reports,expected_versions,status):
    raw=[path.read_text() for path in paths]
    first=projection.b.parse_line(raw[0].splitlines()[0],1)['values'];case_id=first['caseId'];rut=first['rutType']
    uuids=[' source/opaque|'+str(i)+' ' for i in range(len(paths))]
    cache=oracle.cache_for(rut);calls=[];writes=[];versions=[];pending=deepcopy(reports)
    original=list(raw)
    def tool(name,args):
        calls.append((name,deepcopy(args)))
        if name=='GetMemory':
            return {'Success':True,'Payload':raw[uuids.index(args['UUID'])],'ErrorCode':'','ErrorMessage':''}
        if name=='KnowledgeTool':return {'pxResults':[{'Area':k,'Description':v} for k,v in cache.items()]}
        if name=='WriteMemory':
            current=expected_versions[len(writes)]
            value=json.loads(args['Payload'],parse_float=Decimal);oracle.audit(value,current,cache)
            writes.append(args['Payload']);uuid=' candidate|'+str(len(writes))+'\\exact '
            versions.append(uuid);return {'Success':True,'UUID':uuid,'ErrorCode':'','ErrorMessage':''}
        if name=='UnitTestValidator':
            p.require(args['UnitTestCandidateUUID']==versions[-1] and args['RUTType']==rut and args['CaseID']==case_id,'exact current Validator address')
            value=pending.pop(0)
            Draft202012Validator(json.loads((ROOT/'docs/contracts/VALIDATOR_REPORT_S3.schema.json').read_text())).validate(value)
            return json.dumps(value)
        raise p.ContractError('Forbidden interface')
    result=p.run(case_id,rut,uuids,tool,projection.decode_source,projection.candidate,projection.preflight)
    Draft202012Validator(json.loads((ROOT/'docs/contracts/GENERATOR_RUN_REPORT_V1.schema.json').read_text())).validate(result)
    p.require(result['status']==status and len(writes)==len(expected_versions) and raw==original,'combined flow outcome/immutability: '+json.dumps(result))
    p.require([a['UUID'] for n,a in calls if n=='GetMemory']==uuids,'ordered source addressing')
    p.require(sum(n=='KnowledgeTool' for n,a in calls)==1,'one cached guidance batch')
    p.require(len([n for n,a in calls if n=='UnitTestValidator'])==len(reports),'one Validator per successful fresh write')
    p.require(result['candidate']['UUID']==versions[-1] if status!='Failed' else result['candidate'] is None,'current candidate report')
    return result


def main():
    profiled=ROOT/'fixtures/s3/current';two=ROOT/'fixtures/s3/current/when-two-rows.sgl'
    source=oracle.read_source(two);whole=oracle.retained(source);remaining=dict(whole,scenarios=whole['scenarios'][1:])
    case([two],[report()],[[whole]],'Completed')
    defect=issue('REASONING_CONTRADICTION','REJECT_SEMANTICS',0,0,'/UnitTestRules/0/Scenarios/0','A001')
    r=case([two],[report(defect),report()],[[whole],[remaining]],'PartiallyCompleted')
    p.require(r['groups'][0]['scenarios'][0]['outcome']=='Untestable' and r['groups'][0]['scenarios'][1]['scenario']==0,'source/report remapping')
    first=oracle.retained(oracle.read_source(profiled/'when-key-a.sgl'));second=oracle.retained(oracle.read_source(profiled/'when-key-b.sgl'))
    case([profiled/'when-key-a.sgl',profiled/'when-key-b.sgl'],[report()],[[first,second]],'PartiallyCompleted')
    shared=issue('REASONING_CONTRADICTION','REJECT_SEMANTICS',0,None,'/UnitTestRules/0/RuleCode/pySimulation','')
    case([profiled/'when-key-a.sgl',profiled/'when-key-b.sgl'],[report(shared),report()],[[first,second],[second]],'PartiallyCompleted')
    standard=oracle.retained(oracle.read_source(profiled/'standard-escaping.sgl'))
    repair=issue('TRACE_PATH_CANONICALIZATION_NEEDED','FIX_TRACE_PATH')
    case([profiled/'standard-escaping.sgl'],[report(repair),report()],[[standard],[standard]],'Completed')
    case([two],[report(issue()),report(issue()),report(issue())],[[whole],[whole],[whole]],'Failed')
    print('PASS: S3 complete static flows=6; real source parsing, both schema families, source audits, report schemas, pruning and UUID versions')


if __name__=='__main__':
    try:main()
    except (p.ContractError,KeyError,TypeError,ValueError) as error:raise SystemExit('FAIL: '+str(error))
