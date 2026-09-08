"""Local immutable Memory doubles connecting the existing Generator and Validator oracles."""
from copy import deepcopy
from dataclasses import dataclass
import json

from jsonschema import Draft202012Validator
import scenario_author_protocol as author
import generator_protocol as generator
import generator_projection as projection
import validator_protocol as validator
import validate_s3_projection as audit


@dataclass(frozen=True)
class Record:
    case_id: str
    kind: str
    uuid: str
    payload: str


class Runtime:
    """Fault hooks alter designated responses/projections, never stored records.

    Log attempted calls before hook injection. Addresses reaching the storage
    double are logged separately; neither fixture log is a real Pega trace.
    """
    def __init__(self,names,hook=None,projection_fault=None):
        self.payloads=[(audit.FIXTURES/(name+'.sgl')).read_text() for name in names]
        header=projection.b.parse_line(self.payloads[0].splitlines()[0],1)['values']
        self.context={'pyID':header['caseId'],'RuleJSON':{'pxObjClass':header['rutType']}}
        self.cache=audit.cache_for(header['rutType']);self.hook=hook;self.projection_fault=projection_fault
        self.records={};self.calls=[];self.addresses=[];self.reports=[];self.generator_report=None
        self.projects=[];self.validations=[];self.original_sources=[];self._counter=0

    def success(self,**fields):return dict(Success=True,ErrorCode='',ErrorMessage='',platformMetadata={'fixture':True},**fields)

    def failure(self,name,code):
        return dict(Success=False,ErrorCode=code,ErrorMessage='Fixture transport failure.',**({'UUID':''} if name=='WriteMemory' else {'Payload':''} if name=='GetMemory' else {'IsValid':False,'ValidationMessage':''}))

    def resolve(self,args,kind=None):
        actual_kind=kind or args.get('Type')
        self.addresses.append((args['CaseID'],actual_kind,args['UUID']))
        record=self.records.get(args['UUID'])
        if record is None:return None,'NOT_FOUND'
        if (record.case_id,record.kind)!=(args['CaseID'],actual_kind):return None,'ADDRESS_MISMATCH'
        return record,None

    def invoke(self,actor,name,args):
        permitted={'Author':{'WriteMemory','UnitTestGenerator'},'Generator':{'GetMemory','KnowledgeTool','WriteMemory','UnitTestValidator'},'Validator':{'JsonValidationTool','GetMemory','KnowledgeTool'}}
        assert name in permitted[actor],(actor,name)
        expected_keys={'WriteMemory':{'CaseID','Type','Payload'},'GetMemory':{'CaseID','Type','UUID'},'KnowledgeTool':{'KnowledgeAreas'},'JsonValidationTool':{'CaseID','UUID','JsonSchema'},'UnitTestGenerator':{'CaseID','RUTType','ScenarioGroupUUIDs'},'UnitTestValidator':{'CaseID','RUTType','UnitTestCandidateUUID'}}
        assert set(args)==expected_keys[name]
        if name in {'WriteMemory','GetMemory'}:
            kind='ScenarioGroup' if actor=='Author' or actor=='Generator' and name=='GetMemory' else 'UnitTestCandidate'
            assert args['Type']==kind
        self.calls.append((actor,name,deepcopy(args)))
        def actual(changed=None):return self.dispatch(actor,name,args if changed is None else changed)
        return self.hook(self,actor,name,deepcopy(args),actual) if self.hook else actual()

    def dispatch(self,actor,name,args):
        if name=='WriteMemory':
            self._counter+=1;uuid=' opaque|'+args['Type']+'/'+str(self._counter)+'\\version '
            assert uuid not in self.records
            self.records[uuid]=Record(args['CaseID'],args['Type'],uuid,args['Payload'])
            return self.success(UUID=uuid)
        if name=='GetMemory':
            record,error=self.resolve(args)
            return self.failure(name,error) if error else self.success(Payload=record.payload)
        if name=='KnowledgeTool':
            assert args['KnowledgeAreas']==','.join(generator.knowledge_keys(self.context['RuleJSON']['pxObjClass']))
            return {'pxResults':[{'Area':key,'Description':text} for key,text in self.cache.items()]}
        if name=='JsonValidationTool':
            record,error=self.resolve(args,'UnitTestCandidate')
            if error:return self.failure(name,error)
            assert args['JsonSchema']==generator.knowledge_keys(self.context['RuleJSON']['pxObjClass'])[1]
            try:
                parsed=validator.parse_json(record.payload)
                errors=list(Draft202012Validator(json.loads(self.cache[args['JsonSchema']])).iter_errors(parsed))
            except Exception:
                return self.success(IsValid=False,ValidationMessage='/: invalid JSON text')
            message='\n'.join('/'+('/'.join(str(x) for x in e.absolute_path))+': '+e.message for e in errors)
            return self.success(IsValid=not errors,ValidationMessage=message)
        if name=='UnitTestGenerator':
            self.original_sources=[self.records[u] for u in args['ScenarioGroupUUIDs']]
            result=generator.run(args['CaseID'],args['RUTType'],args['ScenarioGroupUUIDs'],lambda n,a:self.invoke('Generator',n,a),projection.decode_source,self.project,projection.preflight)
            Draft202012Validator(author.REPORT_SCHEMA).validate(result)
            self.generator_report=deepcopy(result)
            assert self.original_sources==[self.records[r.uuid] for r in self.original_sources]
            return json.dumps(result)
        if name=='UnitTestValidator':
            record=self.records.get(args['UnitTestCandidateUUID'])
            self.validations.append(args['UnitTestCandidateUUID'])
            result=validator.run(args['CaseID'],args['RUTType'],args['UnitTestCandidateUUID'],lambda n,a:self.invoke('Validator',n,a))
            Draft202012Validator(json.loads((author.ROOT/'docs/contracts/VALIDATOR_REPORT_S3.schema.json').read_text())).validate(result)
            if record:assert self.records[record.uuid]==record
            self.reports.append(deepcopy(result));return json.dumps(result)
        raise AssertionError('unexpected dispatch')

    def project(self,current,cache,report):
        raw=projection.candidate(current,cache,report)
        audit.audit(validator.parse_json(raw),current,cache)
        self.projects.append((deepcopy(current),raw))
        # Explicit fault boundary follows a successful unmodified projection audit.
        return self.projection_fault(self,raw) if self.projection_fault else raw

    def run(self):
        original=list(self.payloads)
        result=author.run(deepcopy(self.context),list(self.payloads),lambda n,a:self.invoke('Author',n,a))
        assert self.payloads==original
        assert set(result)=={'AIAgentResponseStatus','AIAgentErrorResponseMessage'}
        assert len(result['AIAgentErrorResponseMessage'])<=180 and len(result['AIAgentErrorResponseMessage'].split())<=20
        if self.generator_report and self.generator_report['status']!='Failed':
            uuid=self.generator_report['candidate']['UUID']
            assert uuid==self.validations[-1] and self.reports[-1]['valid'] and self.reports[-1]['route']=='OK'
            audit.audit(validator.parse_json(self.records[uuid].payload),self.projects[-1][0],self.cache)
        return result
