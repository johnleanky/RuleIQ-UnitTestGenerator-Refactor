"""Executable S3 design oracle: immutable ScenarioGroup -> schema-shaped candidate.

This is repository validation tooling, not an implementation of a Pega tool.
"""
from copy import deepcopy
from decimal import Decimal, InvalidOperation
import json
import re
from pathlib import Path
from jsonschema import Draft202012Validator

import sg_profile as sg
import validate_s2_design as b
from generator_protocol import strict_json, knowledge_keys

ROOT=Path(__file__).resolve().parents[1]
NO_VALUE={'Exists','Not exists','Is Empty','Is Not Empty','has errors','has no errors'}
NUMERIC={'Integer','Decimal','Double'}
STRING={'Text','String','Identifier','Password','TextEncrypted','Date','DateTime','TimeOfDay'}


def json_text(value, level=0):
    if isinstance(value,Decimal):
        b.require(value.is_finite(),'non-finite candidate number');return str(value)
    if isinstance(value,(dict,list)):
        left,right=('{','}') if isinstance(value,dict) else ('[',']')
        items=[json.dumps(k,ensure_ascii=False)+': '+json_text(v,level+1) for k,v in value.items()] if isinstance(value,dict) else [json_text(v,level+1) for v in value]
        return left+'\n'+',\n'.join('  '*(level+1)+item for item in items)+'\n'+'  '*level+right if items else left+right
    return json.dumps(value,ensure_ascii=False,allow_nan=False,separators=(',',':'))


def rows(source,sid,tag=None):
    return [r for r in source['records'] if r['values'].get('scenario')==sid and (tag is None or r['tag']==tag)]


def vals(source,sid,tag):return [r['values'] for r in rows(source,sid,tag)]


def typed(value_type,value):
    if value_type=='number':return Decimal(value)
    if value_type=='json':return json.loads(value,parse_float=Decimal)
    return b.typed_python(value_type,value)


def parameter(name,formal_type,value_type,value,pages,when=False):
    rendered=b.project_rut_parameter_value(formal_type,value_type,value,pages)
    b.require(rendered is not None,'SOURCE_PARAMETER_UNPROJECTABLE')
    result={'pyParametersParamName':name,'pyParametersParamValue':rendered}
    if formal_type=='PAGE':result['pyParametersParamType']='PAGE'
    elif when:
        labels={'String':'Text','Integer':'Integer','Decimal':'Decimal','Boolean':'TrueFalse','TrueFalse':'TrueFalse'}
        b.require(formal_type in labels,'SOURCE_PARAMETER_UNPROJECTABLE');result['pyParametersParamType']=labels[formal_type]
    return result


def literal_assertion(a, fact):
    value=a['value']
    b.require(fact['value']==value,'SOURCE_EXPECTED_VALUE_PROVENANCE')
    if a['comparator'] in NO_VALUE:
        b.require(fact['valueType']=='absent' and value is None,'SOURCE_COMPARATOR_VALUE_CONFLICT');return False,None
    b.require(fact['valueType']!='absent','SOURCE_EXPECTED_VALUE_MISSING')
    result=typed(fact['valueType'],value)
    if a['kind']=='ResultCount':
        b.require(fact['valueType']=='number' and re.fullmatch(r'\d+',value) is not None,'SOURCE_COUNT_VALUE');return True,value
    if a['mode']=='TrueFalse':
        b.require(type(result) is bool and a['comparator']==('Is True' if result else 'Is False'),'SOURCE_BOOLEAN_COMPARATOR')
        return True,result
    b.require(a['comparator'] not in {'Is True','Is False'},'SOURCE_STRING_BOOLEAN_COMPARATOR')
    if isinstance(result,list) or result is None:return True,result
    if a['mode'] in NUMERIC:
        b.require(fact['valueType']=='number' and isinstance(result,Decimal) and result.is_finite() and (a['mode']!='Integer' or result==result.to_integral_value()),'SOURCE_NUMBER_VALUE')
        return True,result
    b.require(a['mode'] in STRING and isinstance(result,str),'SOURCE_ASSERTION_TYPE')
    return True,result


def assertion_block(a,binding,fact):
    kind=a['kind'];target=binding['fullPath'];step=binding['stepPage']
    block={'pyAssertionType':kind,'pyStepPageName':step,'pyStepPageClass':binding['stepClass'],**deepcopy(binding['context'])}
    has_value,value=literal_assertion(a,fact)
    if kind=='ResultCount':
        relative=target[len(step):]
        b.require(re.fullmatch(r'\.[A-Za-z][A-Za-z0-9_]*',relative) is not None,'SOURCE_NESTED_COUNT_UNREPRESENTABLE')
        block.update(pyListContext=relative,pyComparator=a['comparator'],pyExpectedValue=value)
        return block
    if kind=='Page':
        child={'pyComparator':a['comparator'],'pyPropertyAbsolutePath':target}
    elif target.startswith('Param.'):
        child={'pyComparator':a['comparator'],'pyPropertyName':target,'pyPropertyAbsolutePath':target,'pyPropertyMode':'Text','pyAssertionType':'Property'}
    else:
        relative=target[len(step):]
        leaf=target.rsplit('.',1)[-1]
        child={'pyComparator':a['comparator'],'pyPropertyName':leaf,'pyPropertyAbsolutePath':relative,'pyPropertyMode':a['mode'],'pyPageName':a['page'],'pyPropertyApplyToClass':a['class'],'pyPropertyRealName':leaf.split('(',1)[0]}
        if binding['parentMode'] is not None:child['pyParentPropertyMode']=binding['parentMode']
    if has_value:child['pyExpectedValue']=value
    if kind=='List':
        # The frozen assertion page is the list container; choosing a different
        # ancestor from a leaf path would be semantic reconstruction.
        b.require(a['page'].startswith(step+'.') and target.startswith(a['page']+'.'),'SOURCE_LIST_CONTEXT_UNAVAILABLE')
        block['pyListContext']=a['page'][len(step):]
        b.require('pyNumberOfAppearances' in block,'SOURCE_LIST_APPEARANCE_UNAVAILABLE')
    block['pyExpectedResults']=[child]
    return block


def path_tokens(path):
    b.require(isinstance(path,str) and path.startswith('.'),'SOURCE_SEED_PATH')
    tokens=[]
    for part in path[1:].split('.'):
        match=re.fullmatch(r'([A-Za-z][A-Za-z0-9_]*)(?:\(([A-Za-z0-9_]+)\))?',part)
        b.require(match is not None,'SOURCE_SEED_PATH')
        tokens.append(match[1])
        if match[2] is not None:tokens.append(int(match[2])-1 if match[2].isdigit() else ('key',match[2]))
    b.require(all(not isinstance(t,int) or t>=0 for t in tokens),'SOURCE_SEED_INDEX')
    return tokens


class Hole:pass
HOLE=Hole()


def put_seed(container,tokens,value):
    token=tokens[0];key=token[1] if isinstance(token,tuple) else token
    if isinstance(token,int):
        b.require(isinstance(container,list),'SOURCE_SEED_CONTAINER_CONFLICT')
        while len(container)<=token:container.append(HOLE)
        old=container[key]
    else:
        b.require(isinstance(container,dict),'SOURCE_SEED_CONTAINER_CONFLICT');old=container.get(key,HOLE)
    if len(tokens)==1:
        b.require(old is HOLE or json_text(old)==json_text(value),'SOURCE_SEED_VALUE_CONFLICT');container[key]=deepcopy(value);return
    if old is HOLE:
        old=[] if isinstance(tokens[1],int) else {};container[key]=old
    put_seed(old,tokens[1:],value)


def check_holes(value):
    b.require(value is not HOLE,'SOURCE_SEED_INDEX_HOLE')
    if isinstance(value,(dict,list)):
        for v in (value.values() if isinstance(value,dict) else value):check_holes(v)


def setup_pages(source,sid):
    root=source['root'];classes=json.loads(root['pagesAndClasses']);pages={}
    if root['primarySetup']=='true':pages[root['page']]={'pxObjClass':root['class']}
    items=[]
    for r in rows(source,sid):
        v=r['values']
        if r['tag']=='SETUP':items.append(v)
        if r['tag']=='INPUT' and v['role'] not in {'PARAM','DECISION_INPUT'}:items.append(v)
    for v in items:
        if v.get('role')=='PAGE_AND_CLASS':
            b.require(v['page'] in classes,'SOURCE_SEED_PAGE_CLASS');pages.setdefault(v['page'],{'pxObjClass':classes[v['page']]});continue
        b.require(v['page'] in classes,'SOURCE_SEED_PAGE_CLASS')
        page=pages.setdefault(v['page'],{'pxObjClass':classes[v['page']]})
        path=v['path']
        if path.startswith(v['page']+'.'):path=path[len(v['page']):]
        b.require(v['valueType']!='absent','SOURCE_ABSENT_PHYSICAL_SEED')
        put_seed(page,path_tokens(path),typed(v['valueType'],v['value']))
    params={v['id']:v for v in vals(source,sid,'PARAM')}
    for v in vals(source,sid,'INPUT'):
        if v['path'].startswith('Param.') and params[v['resolution']]['formalType']=='PAGE':
            name=v['value'];b.require(name in classes,'SOURCE_PAGE_PARAMETER_CLASS');pages.setdefault(name,{'pxObjClass':classes[name]})
    check_holes(pages)
    return [{'pySetupPageName':name,'pyPageDetails':value} for name,value in pages.items()]


def simulations(source,sid):
    output=[];names=set()
    for sim in vals(source,sid,'SIM'):
        b.require(sim['rule'] not in names,'SOURCE_DUPLICATE_MOCK_ADDRESS');names.add(sim['rule'])
        payload=json.loads(sim['payload'],parse_float=Decimal)
        if sim['shape']=='list':
            b.require(isinstance(payload,dict) and isinstance(payload.get('pxObjClass'),str) and payload['pxObjClass'],'SOURCE_SIMULATION_WRAPPER')
            # Only the explicitly evidenced item collection establishes its class.
            selected=payload
            try:
                for token in path_tokens(source['profiles'][sid]['simulationItemPaths'][sim['id']]):
                    selected=selected[token[1] if isinstance(token,tuple) else token]
            except (KeyError,IndexError,TypeError) as error:raise b.ContractError('SOURCE_SIMULATION_ITEM_PATH') from error
            b.require(isinstance(selected,list) and all(isinstance(item,dict) and item.get('pxObjClass')==sim['itemClass'] for item in selected),'SOURCE_SIMULATION_ITEM_CLASS')
        else:b.require(isinstance(payload,dict),'SOURCE_SIMULATION_PAGE')
        seeded=[];payload_page=source['profiles'][sid]['simulationBindings'][sim['id']]
        # setupPages is the full census; payload belongs to exactly one evidenced page.
        extras=json.loads(sim['setupPages'],parse_float=Decimal)
        for extra in extras:
            details=deepcopy(payload) if extra['pySetupPageName']==payload_page else {}
            for item in extra['pyPageDetails']:
                b.validate_typed(item['valueType'],item['value'],'simulation supplemental seed')
                put_seed(details,path_tokens(item['path']),typed(item['valueType'],item['value']))
            check_holes(details)
            if sim['shape']=='list' and extra['pySetupPageName']==payload_page:
                final_items=details
                try:
                    for token in path_tokens(source['profiles'][sid]['simulationItemPaths'][sim['id']]):
                        final_items=final_items[token[1] if isinstance(token,tuple) else token]
                except (KeyError,IndexError,TypeError) as error:raise b.ContractError('SOURCE_SIMULATION_ITEM_PATH') from error
                b.require(isinstance(final_items,list) and all(isinstance(item,dict) and item.get('pxObjClass')==sim['itemClass'] for item in final_items),'SOURCE_SIMULATION_ITEM_CLASS')
            seeded.append({'pySetupPageName':extra['pySetupPageName'],'pyPageDetails':details})
        b.require(len({p['pySetupPageName'] for p in seeded})==len(seeded),'SOURCE_DUPLICATE_SIMULATION_PAGE')
        item={'pyClassName':sim['class'],'pyMockingSupportedRuleTypes':sim['mockingRuleType'],'pyRuleNameToBeMocked':sim['rule'],'pySimulationMethod':sim['method'],'pySetupPages':seeded}
        if sim['referredFromClass'] is not None:item['pxReferredFromClass']=sim['referredFromClass']
        output.append(item)
    return output


def actions(source,sid,when):
    profile=source['profiles'][sid];pages=json.loads(source['root']['pagesAndClasses']);result={'SETUP':[],'CLEANUP':[]}
    for action in profile['actions']:
        row={'pyActionType':action['type'],'pyActionName':action['name']}
        if action['page'] is not None:row['pyTargetPage']=action['page']
        if action['parameters']:row['pyParameters']=[parameter(p['name'],p['formalType'],p['valueType'],p['value'],pages,when) for p in action['parameters']]
        result[action['phase']].append(row)
    return result


def rut_parameters(source,sid,when):
    inputs={i['resolution']:i for i in vals(source,sid,'INPUT') if i['path'].startswith('Param.')}
    pages=json.loads(source['root']['pagesAndClasses']);output=[]
    for param in vals(source,sid,'PARAM'):
        if param['id'] not in inputs:continue
        item=parameter(param['name'],param['formalType'],param['valueType'],param['value'],pages,when)
        if when and inputs[param['id']]['role']=='DECISION_INPUT':item.pop('pyParametersParamValue')
        output.append(item)
    return output


def when_row(source,sid):
    row=[]
    for a in vals(source,sid,'ASSERT'):
        b.require(a['kind'] in {'DecisionInput','DecisionResult'},'SOURCE_WHEN_NON_CELL_ASSERTION')
        result=a['kind']=='DecisionResult';target=a['target']
        cell={'pyPropertyType':'result' if result else 'input','pyPropertyName':target,'pyPropertyAbsolutePath':target,'pyPropertyMode':'text','pyDisplayLabel':target}
        if a['value']!='<EMPTY>':
            b.require(isinstance(a['value'],str),'SOURCE_WHEN_CELL_VALUE');cell['pyExpectedValue']=a['value']
        row.append(cell)
    b.require(len(row)>=2 and row[-1]['pyPropertyType']=='result','SOURCE_WHEN_EMPTY_SIGNATURE')
    return {'pyPageName':'rowLevelPage','pyExpectedResults':row}


def evidence_summary(source,sid,row_number=None):
    summary=vals(source,sid,'SUMMARY')[0];profile=source['profiles'][sid];assertions=vals(source,sid,'ASSERT')
    output={key[0].upper()+key[1:]:summary[key] for key in ('supportLevel','dependencyState','branchState','simulationState','dependencyClosureStatus')}
    for key in ('maxDependencyWaveReached','queuedDependencyCount','unscannedFetchedRuleJsonCount'):output[key[0].upper()+key[1:]]=int(summary[key])
    exact=sum(a['value'] is not None and a['comparator'] not in NO_VALUE and a['kind']!='ResultCount' for a in assertions)
    deps=vals(source,sid,'DEP');actual=[d for d in deps if d['state']!='NOT_APPLICABLE']
    output.update(AssertionCount=len(assertions),ExactValueAssertionCount=exact,StructuralAssertionCount=len(assertions)-exact,OmittedClaimCount=len(vals(source,sid,'OMIT')),ResolvedDependencyCount=sum(d['state']=='CLOSED' for d in actual),UnresolvedDependencyCount=sum(d['state']!='CLOSED' for d in actual),BranchEvaluationCount=sum(v['result']!='NOT_APPLICABLE' for v in vals(source,sid,'BRANCH')),ParameterResolutionCount=len(vals(source,sid,'PARAM')),PropertyTraceCount=len(vals(source,sid,'PROPERTY')),SimulatedDependencyCount=len(vals(source,sid,'SIM')))
    output['InternalChecklist']=dict(profile['checklist'],RuleCodeConsistentWithLedger=True,SchemaSelfCheckPassed=True)
    output['ReasoningTrace']=profile['reasoningTrace'];output['DependencyClosureTrace']=profile['dependencyClosureTrace']
    trace=[]
    for r in rows(source,sid):
        if r['tag'] not in {'ASSERT','SIM','OMIT'}:continue
        copy=deepcopy(r)
        if row_number is not None and copy['tag']=='ASSERT':copy['values']['row']=str(row_number)
        trace.append(b.project_trace(copy))
    output['AssertionDecisionTrace']='\n'.join(trace)
    gaps=vals(source,sid,'GAP')
    if gaps:output['BlockingGaps']=[{'pyValue':g['code']+': '+g['scope']+' ('+g['effect']+')'} for g in gaps]
    return output


def scenario_name(name):
    clean=re.sub(r'[^A-Za-z0-9 _]','_',name).strip()[:50]
    b.require(clean and not clean.startswith('TC_'),'SOURCE_SCENARIO_NAME_UNPROJECTABLE')
    return clean


def rule_name(source,scenario):
    # Stable source group order disambiguates equal semantic labels; pruning never renames.
    label=''.join(part[:1].upper()+part[1:] for part in re.split(r'[ _]+',scenario_name(scenario['name'])))
    suffix='G'+source['header']['groupOrder'];label=label[:32-len(suffix)]+suffix
    base=re.sub(r'\s','',source['header']['rutName']);base=re.sub(r'[^A-Za-z0-9_]','_',base)
    return 'TC_'+base[:49-len(label)]+'_'+label


def scenario_json(source,sid,row_number=None):
    meta=next(s for s in source['meta'] if s['id']==sid)
    description=' '.join(n['text'] for n in vals(source,sid,'NARRATIVE'))
    return {'Status':'New','Name':scenario_name(meta['name']),'Type':source['profiles'][sid]['scenarioType'],'ReasoningConfidence':meta['confidence'],'Testability':'FullyTestable' if meta['testability']=='Testable' else meta['testability'],'Description':description,'InputsNarrative':'Uses the recorded inputs and initial data.','AssertionsNarrative':'Checks the recorded expected outcomes.','SimulationsNarrative':'Uses the recorded simulated data.' if vals(source,sid,'SIM') else 'No simulated data is required.','EvidenceSummary':evidence_summary(source,sid,row_number)}


def scenario_parts(source,sid):
    header=source['header'];when=header['kind']=='WHEN';profile=source['profiles'][sid]
    b.require(profile['singlePage'] is not None,'SOURCE_EXECUTION_MODE_UNAVAILABLE')
    b.require(not any(g['code']=='RUT_PARAMETER_PROJECTION_UNAVAILABLE' for g in vals(source,sid,'GAP')),'SOURCE_PARAMETER_UNPROJECTABLE')
    setup=setup_pages(source,sid);sim=simulations(source,sid);action=actions(source,sid,when);params=rut_parameters(source,sid,when)
    if when:expected=[when_row(source,sid)]
    else:
        bindings={v['assertion']:v for v in profile['bindings']}
        expected=[assertion_block(a,bindings[a['id']],profile['expectedValues'][a['id']]) for a in vals(source,sid,'ASSERT')]
        b.require(expected,'SOURCE_NO_ASSERTIONS')
    return {'setup':setup,'simulations':sim,'actions':action,'parameters':params,'expected':expected}


def decode_source(raw,case_id,rut_type,index):
    b.require(isinstance(raw,str),'ScenarioGroup Payload type')
    source=sg.read_ledger(b.MemoryFixture('ordered-source.sgl',raw.encode('utf-8')),revision='1.4')
    source.pop('path',None)  # Local validation handle is not part of immutable semantic data.
    source['header']=source['records'][0]['values'];source['root']=source['records'][1]['values'];source['meta']=[r['values'] for r in source['records'] if r['tag']=='SCENARIO']
    header=source['header']
    b.require(header['caseId']==case_id and header['rutType']==rut_type and int(header['groupOrder'])==index+1,'Source address/type/order mismatch.')
    source['id']=header['groupId'];source['scenarios']=[]
    parts={}
    for meta in source['meta']:
        sid=meta['id'];rejection=None
        try:parts[sid]=scenario_parts(source,sid)
        except b.ContractError as error:rejection=str(error)
        source['scenarios'].append({'id':sid,'decisions':[r['values']['id'] for r in rows(source,sid) if r['tag'] in {'ASSERT','SIM','OMIT'}],'rejection':rejection})
    if header['kind']=='WHEN':
        shared=[{k:v for k,v in part.items() if k!='expected'} for part in parts.values()]
        shared_rejected=any(s['rejection'] is not None and s['rejection'] not in {'SOURCE_WHEN_NON_CELL_ASSERTION','SOURCE_WHEN_EMPTY_SIGNATURE','SOURCE_WHEN_CELL_VALUE'} for s in source['scenarios'])
        if shared_rejected or (shared and any(json_text(s)!=json_text(shared[0]) for s in shared[1:])):
            for scenario in source['scenarios']:scenario['rejection']='SOURCE_WHEN_SHARED_CONTEXT_CONFLICT'
    return source


def guidance(current,cache):
    keys=knowledge_keys(current[0]['header']['rutType'])
    template=strict_json(cache[keys[2]])
    b.require(isinstance(template,dict) and set(template)=={'UnitTestRules'} and isinstance(template['UnitTestRules'],list) and template['UnitTestRules'] and all(isinstance(u,dict) and isinstance(u.get('RuleCode'),dict) for u in template['UnitTestRules']),'Malformed UTC template.')
    schema=strict_json(cache[keys[1]])
    try:
        Draft202012Validator.check_schema(schema)
        validator=Draft202012Validator(schema)
        b.require(not list(validator.iter_errors(template)),'Malformed UTC template.')
    except Exception as error:raise b.ContractError('Malformed structural guidance.') from error
    return template['UnitTestRules'][0]['RuleCode'],validator


def preflight(current,cache):
    """Finish representability after cached Knowledge, before any combined write."""
    guidance(current,cache);survivors=[];rejections={}
    for source in current:
        kept=[];shared_failure=False
        for scenario in source['scenarios']:
            one=dict(source,scenarios=[scenario])
            try:value,validator=candidate([one],cache,validate=False)
            except b.ContractError as error:
                # Guidance already passed globally. Construction errors now refer
                # to frozen source fields, including names and narrative shape.
                rejections[(source['sourceIndex'],scenario['id'])]=str(error)
                if source['header']['kind']=='WHEN':
                    try:rule_name(source,source['meta'][0])
                    except b.ContractError:shared_failure=True
                    if str(error)!='SOURCE_SCENARIO_NAME_UNPROJECTABLE':shared_failure=True
                continue
            errors=list(validator.iter_errors(json.loads(value,parse_float=Decimal)))
            if errors:
                # A When row or Scenario narrative is local; the rest is shared.
                if source['header']['kind']=='WHEN':
                    prefixes=[['UnitTestRules',0,'Scenarios',0],['UnitTestRules',0,'RuleCode','pyExpectedResults',0,'pyExpectedResults',0]]
                    shared_failure|=any(not any(list(e.absolute_path)[:len(p)]==p for p in prefixes) for e in errors)
                rejections[(source['sourceIndex'],scenario['id'])]='SOURCE_SCHEMA_UNREPRESENTABLE'
            else:kept.append(scenario)
        if shared_failure:
            for scenario in source['scenarios']:rejections[(source['sourceIndex'],scenario['id'])]='SOURCE_WHEN_SHARED_SCHEMA_UNREPRESENTABLE'
        elif kept:survivors.append(dict(source,scenarios=kept))
    return survivors,rejections


def candidate(current,cache,repair=None,validate=True):
    b.require(current,'No projectable scenarios remain.')
    when=current[0]['header']['kind']=='WHEN';keys=knowledge_keys(current[0]['header']['rutType'])
    # Pega owns target selection; copy its existing UTC template metadata unchanged.
    # Repository examples exercise formatting only and establish no deployment target.
    target,validator=guidance(current,cache)
    b.require(isinstance(target.get('pyRuleSet'),str) and target['pyRuleSet'] and isinstance(target.get('pyRuleSetVersion'),str) and re.fullmatch(r'\d{2}-\d{2}-\d{2}',target['pyRuleSetVersion']),'Pega target metadata unavailable.')
    units=[]
    for source in current:
        header=source['header'];root=source['root'];sid=source['scenarios'][0]['id'];profile=source['profiles'][sid]
        part=scenario_parts(source,sid);original_first=source['meta'][0];name=rule_name(source,original_first)
        details={'pyRuleUnderTestName':header['rutName'],'pyRuleUnderTestObjClass':header['rutClass'],'pyRuleUnderTestType':header['rutType'],'pyRuleUnderTestInsName':'!'.join(profile['caseKey'].split()[1:3]),'pyIsSinglePageImplementation':profile['singlePage']}
        rule={'pyLabel':name,'pyPurpose':name,'pyRuleSet':target['pyRuleSet'],'pyRuleSetVersion':target['pyRuleSetVersion'],'pyClassName':root['class'],'pyPrimaryPageForRUT':root['page'],'pyRuleUnderTest':{'pyDetails':details},'pyPagesAndClasses':[{'pyPagesAndClassesPage':p,'pyPagesAndClassesClass':c} for p,c in json.loads(root['pagesAndClasses']).items()],'pyTypeOfSetupPageSelection':'CUSTOMPAGES','pySetupPages':part['setup']}
        if part['parameters']:rule['pyRuleUnderTest']['pyParameters']=part['parameters']
        if part['simulations']:rule['pySimulation']=part['simulations']
        if part['actions']['SETUP']:rule['pySetup']=part['actions']['SETUP']
        if part['actions']['CLEANUP']:rule['pyCleanup']=part['actions']['CLEANUP']
        if when:
            combination_rows=[scenario_parts(source,s['id'])['expected'][0] for s in source['scenarios']]
            rule['pyExpectedResults']=[{'pyAllowMultipleInputCombinations':'true','pyAssertionType':'Decision','pyClassContext':header['rutClass'],'pyPropertyType':'Decision Result','pyExpectedResults':combination_rows}]
        else:rule['pyExpectedResults']=part['expected']
        scenarios=[scenario_json(source,s['id'],i+1 if when else None) for i,s in enumerate(source['scenarios'])]
        units.append({'Name':name,'Scenarios':scenarios,'RuleCode':rule})
    serialized=json_text({'UnitTestRules':units})
    if not validate:return serialized,validator
    errors=list(validator.iter_errors(json.loads(serialized,parse_float=Decimal)))
    b.require(not errors,'Projection schema self-check failed.')
    return serialized
