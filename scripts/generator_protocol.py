"""Static S3 protocol oracle. External tools are injected; no Pega runtime implementation."""
from copy import deepcopy
import json
import re

from validate_s2_design import ContractError, require

# One closed consumer catalog, to be implemented by the S4 Validator producer.
CODE_ACTIONS = {
    'JSON_SCHEMA_INVALID': {'FIX_JSON'},
    'JSON_SCHEMA_MASS_FAILURE': {'REBUILD_JSON_FROM_CURRENT_EVIDENCE'},
    'JSON_VALIDATION_TOOL_ERROR': {'HUMAN_REVIEW'},
    'MEMORY_READ_TOOL_ERROR': {'HUMAN_REVIEW'},
    'RUT_TYPE_MISMATCH': {'FIX_RUT_METADATA'},
    'TRACE_MISSING': {'REJECT_SEMANTICS'},
    'TRACE_INVALID': {'FIX_TRACE', 'REJECT_SEMANTICS'},
    'DECISION_NOT_FINALIZED': {'REJECT_SEMANTICS'},
    'ASSERT_MISSING': {'ADD_ASSERTION'},
    'ASSERT_EXTRA': {'REMOVE_ASSERTION'},
    'ASSERT_VALUE_MISMATCH': {'FIX_ASSERTION'},
    'OMIT_ASSERTED': {'REMOVE_ASSERTION'},
    'SIM_MISSING': {'ADD_SIMULATION'},
    'SIM_SHAPE_INVALID': {'FIX_SIMULATION'},
    'PARAM_SHAPE_INVALID': {'FIX_PARAM_SHAPE'},
    'ASSERT_BLOCK_INVALID': {'FIX_BLOCK_TYPE'},
    'COUNT_MISMATCH': {'FIX_COUNTS'},
    'REASONING_CONTRADICTION': {'REJECT_SEMANTICS'},
    'DOC_RESERVED_SYSTEM_PAGE_SEED': {'REJECT_SEMANTICS'},
    'DOC_DATAPAGE_IN_SETUP': {'MOVE_TO_PYSIMULATION'},
    'DOC_SIMULATION_METHOD_INVALID': {'FIX_SIMULATION'},
    'DOC_DATAPAGE_RULETYPE_INVALID': {'FIX_SIMULATION'},
    'DOC_LIST_SIMULATION_WRAPPER_MISSING': {'FIX_SIMULATION'},
    'DOC_RESULTCOUNT_FOR_NON_COUNT': {'FIX_BLOCK_TYPE', 'REJECT_SEMANTICS'},
    'DOC_PARAM_ASSERTION_SHAPE_INVALID': {'FIX_PARAM_SHAPE'},
    'DOC_REGULAR_ASSERTION_USES_PARAM_PATH': {'FIX_ASSERTION'},
    'DOC_ASSERTION_BLOCK_KIND_MISMATCH': {'FIX_BLOCK_TYPE'},
    'DOC_ERROR_MESSAGE_FORMAT_INVALID': {'FIX_ASSERTION'},
    'AMBIGUOUS': {'HUMAN_REVIEW'},
    'TRACE_PATH_CANONICALIZATION_NEEDED': {'FIX_TRACE_PATH'},
}
ISSUE_KEYS = {'code','severity','path','unit','scenario','decision','action','message'}
ROUTES = ('OK','GENERATOR_REPAIR','SEMANTIC_REJECT','HUMAN')
READ_ERRORS = {'INVALID_INPUT','UNSUPPORTED_TYPE','NOT_FOUND','ADDRESS_MISMATCH','READ_FAILED'}
WRITE_ERRORS = {'INVALID_INPUT','UNSUPPORTED_TYPE','WRITE_FAILED'}


def strict_json(raw):
    require(isinstance(raw,str),'JSON transport must be text')
    def pairs(items):
        result={}
        for key,value in items:
            require(key not in result,'duplicate JSON key');result[key]=value
        return result
    def constant(value):
        raise ContractError('non-finite JSON value')
    try:
        return json.loads(raw,object_pairs_hook=pairs,parse_constant=constant)
    except (ValueError,TypeError) as error:
        raise ContractError('invalid raw JSON') from error


def memory_output(result, operation):
    """S1 named fields; permitted extra platform metadata is ignored."""
    field,errors=('Payload',READ_ERRORS) if operation=='read' else ('UUID',WRITE_ERRORS)
    require(isinstance(result,dict) and {'Success',field,'ErrorCode','ErrorMessage'} <= set(result),'malformed Memory envelope')
    require(type(result['Success']) is bool and all(isinstance(result[k],str) for k in (field,'ErrorCode','ErrorMessage')),'malformed Memory field types')
    if result['Success']:
        require(result['ErrorCode']==result['ErrorMessage']=='','contradictory Memory success')
        if operation=='write':require(result[field]!='','empty candidate UUID')
        return result[field]
    require(result[field]=='' and result['ErrorCode'] in errors and result['ErrorMessage']!='','malformed Memory failure')
    raise ContractError('Memory '+operation+' failed')


def issue_route(action):
    return 'HUMAN' if action=='HUMAN_REVIEW' else 'SEMANTIC_REJECT' if action=='REJECT_SEMANTICS' else 'GENERATOR_REPAIR'


def validate_report(raw, current, when):
    """current units contain stable source group/scenario/decision IDs, never old indices."""
    report=strict_json(raw)
    require(isinstance(report,dict) and set(report)=={'valid','route','blocking','warnings','jsonSchemaValidation','issues'},'ValidatorReport root')
    require(type(report['valid']) is bool and isinstance(report['route'],str) and report['route'] in ROUTES and all(type(report[k]) is int and report[k]>=0 for k in ('blocking','warnings')),'ValidatorReport fields')
    schema=report['jsonSchemaValidation']
    require(isinstance(schema,dict) and set(schema)=={'isValid','message'} and type(schema['isValid']) is bool and isinstance(schema['message'],str),'schema report')
    require(isinstance(report['issues'],list),'issues array')
    routes=[]
    for issue in report['issues']:
        require(isinstance(issue,dict) and set(issue)==ISSUE_KEYS,'issue shape')
        require(isinstance(issue['code'],str) and issue['code'] in CODE_ACTIONS and isinstance(issue['action'],str) and issue['action'] in CODE_ACTIONS[issue['code']],'code/action mismatch')
        require(isinstance(issue['severity'],str) and issue['severity'] in {'B','W'} and isinstance(issue['message'],str) and issue['message']!='' and isinstance(issue['decision'],str),'issue fields')
        path=issue['path'];u,s=issue['unit'],issue['scenario']
        require(isinstance(path,str) and path.startswith('/') and re.search(r'~(?![01])',path) is None,'JSON Pointer')
        if u is None:
            require(s is None and path=='/' and issue['decision']=='','unscopable candidate issue')
        else:
            require(type(u) is int and 0<=u<len(current),'unit index')
            prefix='/UnitTestRules/'+str(u)
            require(path==prefix or path.startswith(prefix+'/'),'unit pointer mismatch')
            if s is None:
                require(issue['decision']=='' and not path.startswith(prefix+'/Scenarios/'),'group coordinate mismatch')
            else:
                require(type(s) is int and 0<=s<len(current[u]['scenarios']),'scenario index')
                source=current[u]['scenarios'][s]
                require(issue['decision']=='' or issue['decision'] in source['decisions'],'decision source mismatch')
                scenario_prefix=prefix+'/Scenarios/'+str(s)
                row_prefix=prefix+'/RuleCode/pyExpectedResults/0/pyExpectedResults/'+str(s)
                if when:
                    require(path==scenario_prefix or path.startswith(scenario_prefix+'/') or path==row_prefix or path.startswith(row_prefix+'/'),'shared When defect requires group scope')
                elif path.startswith(prefix+'/Scenarios/'):
                    require(path==scenario_prefix or path.startswith(scenario_prefix+'/'),'scenario pointer mismatch')
            if when and s is None:
                row= re.match(re.escape(prefix)+r'/RuleCode/pyExpectedResults/0/pyExpectedResults/(\d+)(?:/|$)',path)
                require(row is None,'When row requires scenario scope')
        if issue['severity']=='B':routes.append(issue_route(issue['action']))
    blocking=sum(i['severity']=='B' for i in report['issues'])
    warnings=len(report['issues'])-blocking
    route=max(routes,key=ROUTES.index) if routes else 'OK'
    require(report['blocking']==blocking and report['warnings']==warnings and report['valid']==(blocking==0) and report['route']==route,'report count/valid/route contradiction')
    if not schema['isValid']:
        require(blocking>0 and schema['message']!='' and all(i['severity']=='B' and i['code'] in {'JSON_SCHEMA_INVALID','JSON_SCHEMA_MASS_FAILURE','JSON_VALIDATION_TOOL_ERROR'} for i in report['issues']),'schema-invalid short circuit')
    else:
        require(not any(i['code'] in {'JSON_SCHEMA_INVALID','JSON_SCHEMA_MASS_FAILURE','JSON_VALIDATION_TOOL_ERROR'} for i in report['issues']),'schema result contradiction')
    return report


def knowledge_keys(rut_type):
    prefix='Rule-Test-Unit-Case_MultInpComb-' if rut_type=='Rule-Obj-When' else 'Rule-Test-Unit-Case_'
    return [prefix+'KnowledgeArea',prefix+'JsonSchema',prefix+'JsonExample']


def knowledge_cache(result, keys):
    require(isinstance(result,dict) and isinstance(result.get('pxResults'),list),'Knowledge response')
    cache={}
    for row in result['pxResults']:
        require(isinstance(row,dict) and row.get('Area') in keys and row['Area'] not in cache and isinstance(row.get('Description'),str) and row['Description']!='','Knowledge area')
        cache[row['Area']]=row['Description']
    require(set(cache)==set(keys),'missing Knowledge area')
    return cache


def run(case_id, rut_type, uuids, tools, decode, project, prepare=None):
    """Inject pure source decoder/projector and mock named tools for static flow tests.

    decode returns {id,scenarios:[{id,decisions:[IDs],rejection:null|code}],...}.
    project(current,cache,repair_report) builds from unchanged frozen source handles;
    semantic rejection is handled here and never delegated as an edit instruction.
    """
    groups=[];current=[];rejected={};validation_attempts=0;repair_attempts=0
    candidate_uuid=None;seen=set();error=None
    def finish(success=False):
        successful_map={}
        if success:
            for u,g in enumerate(current):
                for s,scenario in enumerate(g['scenarios']):successful_map[(g['sourceIndex'],scenario['id'])]=(u,s)
        result=deepcopy(groups)
        for gi,g in enumerate(result):
            for scenario in g['scenarios']:
                key=(gi,scenario['id']);location=successful_map.get(key)
                scenario.update(outcome='Successful' if location is not None else 'Untestable' if key in rejected else 'NotValidated',unit=location[0] if location is not None else None,scenario=location[1] if location is not None else None,code=rejected.get(key,''))
        status=('PartiallyCompleted' if rejected else 'Completed') if success else 'Failed'
        return {'status':status,'candidate':{'CaseID':case_id,'Type':'UnitTestCandidate','UUID':candidate_uuid} if success else None,'groups':result,'validationAttempts':validation_attempts,'repairAttempts':repair_attempts,'errorMessage':error or ''}
    original_tools=tools
    def tools(name,args):
        try:return original_tools(name,args)
        except Exception as failure:raise ContractError('Tool invocation failed.') from failure
    try:
        require(isinstance(case_id,str) and case_id!='' and isinstance(rut_type,str) and rut_type!='' and isinstance(uuids,list) and uuids and all(isinstance(u,str) and u!='' for u in uuids) and len(set(uuids))==len(uuids),'Invalid Generator input.')
        groups=[{'sourceUUID':uuid,'groupId':None,'readState':'NotRead','scenarios':[]} for uuid in uuids]
        frozen=[]
        for index,uuid in enumerate(uuids):
            groups[index]['readState']='ReadFailed'
            raw=memory_output(tools('GetMemory',{'CaseID':case_id,'Type':'ScenarioGroup','UUID':uuid}),'read')
            groups[index]['readState']='InvalidSource'
            source=decode(raw,case_id,rut_type,index)
            require(source['id'] not in {g['id'] for g in frozen},'Duplicate source group identity.')
            if 'header' in source and frozen:
                require(all(source['header'][k]==frozen[0]['header'][k] for k in ('rutType','rutClass','rutName','ruleset')),'Cross-group RUT identity mismatch.')
                require(next(iter(source['profiles'].values()))['caseKey']==next(iter(frozen[0]['profiles'].values()))['caseKey'],'Cross-group case key mismatch.')
                if rut_type=='Rule-Obj-When':
                    require(source['header']['simulationGroupKey'] not in {g['header']['simulationGroupKey'] for g in frozen},'Duplicate physical simulation group.')
            source=deepcopy(source);source.update(sourceIndex=index,sourceUUID=uuid)
            frozen.append(source)
            groups[index].update(groupId=source['id'],readState='Ready',scenarios=[{'id':s['id']} for s in source['scenarios']])
        for g in frozen:
            keep=[]
            for s in g['scenarios']:
                if s['rejection'] is not None:rejected[(g['sourceIndex'],s['id'])]=s['rejection']
                else:keep.append(s)
            if keep:current.append(dict(g,scenarios=keep))
        require(current,'No projectable scenarios remain.')
        keys=knowledge_keys(rut_type)
        cache=knowledge_cache(tools('KnowledgeTool',{'KnowledgeAreas':','.join(keys)}),keys)
        repair_report=None
        frozen_guard=deepcopy(frozen)
        if prepare is not None:
            current,pre_rejected=prepare(deepcopy(current),deepcopy(cache))
            rejected.update(pre_rejected)
            require(frozen==frozen_guard,'Immutable source changed.')
            require(current,'No projectable scenarios remain.')
        while True:
            payload=project(deepcopy(current),deepcopy(cache),deepcopy(repair_report))
            require(frozen==frozen_guard,'Immutable source changed.')
            require(isinstance(payload,str) and payload!='','Projection failed.')
            written=memory_output(tools('WriteMemory',{'CaseID':case_id,'Type':'UnitTestCandidate','Payload':payload}),'write')
            require(written not in seen,'Candidate UUID was reused.')
            seen.add(written);candidate_uuid=written
            validation_attempts+=1
            report=validate_report(tools('UnitTestValidator',{'CaseID':case_id,'RUTType':rut_type,'UnitTestCandidateUUID':candidate_uuid}),current,rut_type=='Rule-Obj-When')
            if report['route']=='OK':return finish(True)
            hint=next((' '.join(i['message'].split()[:20])[:180] for i in report['issues'] if i['severity']=='B'),'Validator rejected the candidate.')
            require(report['route']!='HUMAN',hint)
            require(not any(i['severity']=='B' and i['action']=='REJECT_SEMANTICS' and i['unit'] is None for i in report['issues']),'Candidate-wide semantic rejection.')
            remove=set()
            for issue in report['issues']:
                if issue['severity']!='B' or issue['action']!='REJECT_SEMANTICS':continue
                g=current[issue['unit']]
                targets=g['scenarios'] if issue['scenario'] is None else [g['scenarios'][issue['scenario']]]
                for s in targets:
                    key=(g['sourceIndex'],s['id']);remove.add(key);rejected[key]=issue['code']
            survivors=[]
            for g in current:
                kept=[s for s in g['scenarios'] if (g['sourceIndex'],s['id']) not in remove]
                if kept:survivors.append(dict(g,scenarios=kept))
            current=survivors
            require(current,'All scenarios were rejected.')
            require(repair_attempts<2,'Projection repair budget exhausted.')
            repair_attempts+=1
            # Rebuild from unchanged sources using current indices. Report is diagnostic
            # only: no Validator message becomes an expected value or semantic input.
            repair_report=report
    except (ContractError,KeyError,TypeError,ValueError,IndexError,AttributeError) as failure:
        # Stable bounded messages; external diagnostics/payloads are never copied.
        error=str(failure)[:180] if isinstance(failure,ContractError) else 'Malformed source or tool response.'
        return finish(False)
