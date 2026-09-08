#!/usr/bin/env python3
"""Adversarial S4 protocol, trace and candidate fixtures with S3 consumer checks."""
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
import json

from jsonschema import Draft202012Validator
import validator_protocol as v
import generator_protocol as consumer
import generator_projection as projection
import validate_s3_projection as sources

ROOT=Path(__file__).resolve().parents[1]
REPORT_SCHEMA=json.loads((ROOT/'docs/contracts/VALIDATOR_REPORT_S3.schema.json').read_text())
CASES={}


def case(name):
    def register(fn):
        assert name not in CASES
        CASES[name]=fn;return fn
    return register


@lru_cache(None)
def fixture(name='standard-escaping'):
    source=sources.retained(sources.read_source(sources.FIXTURES/(name+'.sgl')))
    rut=source['header']['rutType'];cache=sources.cache_for(rut)
    raw=projection.candidate([source],cache)
    parsed=v.parse_json(raw)
    keys=consumer.knowledge_keys(rut)
    Draft202012Validator(json.loads(cache[keys[1]])).validate(parsed)
    return source,rut,cache,raw


def candidate(name='standard-escaping'):
    return v.parse_json(fixture(name)[3])


def check_report(result,source=None,when=False):
    Draft202012Validator(REPORT_SCHEMA).validate(result)
    if source is None: source=fixture('when-two-rows' if when else 'standard-escaping')[0]
    current=source if isinstance(source,list) else [source]
    consumer.validate_report(json.dumps(result),current,when)
    return result


def execute(name='standard-escaping',overrides=None,raw=None,inspect=None,case_id=' case|opaque ',uuid=' current|\\uuid ',rut=None,caller_schema=None):
    source,kind,cache,original=fixture(name);rut=kind if rut is None else rut
    calls=[]
    def tool(name_,args):
        calls.append((name_,deepcopy(args)))
        if overrides and name_ in overrides:
            result=overrides[name_]
            if isinstance(result,Exception):raise result
            return deepcopy(result)
        if name_=='JsonValidationTool':return dict(Success=True,IsValid=True,ValidationMessage='',ErrorCode='',ErrorMessage='')
        if name_=='GetMemory':return dict(Success=True,Payload=original if raw is None else raw,ErrorCode='',ErrorMessage='')
        if name_=='KnowledgeTool':return dict(pxResults=[dict(Area=k,Description=value) for k,value in cache.items()])
        raise AssertionError('forbidden tool')
    result=v.run(case_id,rut,uuid,tool,inspect=inspect,caller_schema=caller_schema)
    check_report(result,source,kind=='Rule-Obj-When')
    return result,calls


def expect_code(value,code,route=None):
    assert any(i['code']==code for i in value['issues']),(code,value)
    if route is not None:assert value['route']==route,value


def inspect_mutation(change,name='standard-escaping',code=None,route=None):
    value=candidate(name);before=deepcopy(value);change(value)
    source,rut,cache,_=fixture(name);frozen=deepcopy(value)
    result=check_report(v.report(v.inspect_candidate(value,rut,cache)),source,rut=='Rule-Obj-When')
    assert value==frozen
    if code:expect_code(result,code,route)
    assert value!=before,'mutation must change fixture'
    return result


def evidence(x,s=0):return x['UnitTestRules'][0]['Scenarios'][s]['EvidenceSummary']
def child(x):return x['UnitTestRules'][0]['RuleCode']['pyExpectedResults'][0]['pyExpectedResults'][0]
def rulecode(x):return x['UnitTestRules'][0]['RuleCode']
def cell(x,s=0,c=0):return rulecode(x)['pyExpectedResults'][0]['pyExpectedResults'][s]['pyExpectedResults'][c]


@case('exact_uuid_order_both_families')
def _():
    for name in ['standard-escaping','when-two-rows']:
        result,calls=execute(name,caller_schema='caller-wrong-schema')
        assert result['valid'] and [n for n,a in calls]==['JsonValidationTool','GetMemory','KnowledgeTool']
        assert calls[0][1]['UUID']==calls[1][1]['UUID']==' current|\\uuid '
        assert calls[0][1]['CaseID']==calls[1][1]['CaseID']==' case|opaque '
        assert set(calls[0][1])=={'CaseID','UUID','JsonSchema'}
        assert calls[1][1]['Type']=='UnitTestCandidate'
        assert calls[0][1]['JsonSchema']==consumer.knowledge_keys(fixture(name)[1])[1]
        assert calls[2][1]=={'KnowledgeAreas':','.join(consumer.knowledge_keys(fixture(name)[1]))}


@case('invalid_inputs_zero_tools')
def _():
    for key in ['case_id','rut','uuid']:
        for bad in [None,'',False,0,[],{}]:
            args={key:bad}
            if key=='rut':
                calls=[];r=v.run('c',bad,'u',lambda *a:calls.append(a));check_report(r)
            else:r,calls=execute(**args)
            expect_code(r,'JSON_VALIDATION_TOOL_ERROR','HUMAN');assert not calls


@case('schema_envelope_failures_stop')
def _():
    good=dict(Success=True,IsValid=True,ValidationMessage='',ErrorCode='',ErrorMessage='')
    bad=[None,{},dict(response='false'),dict(IsValid=True),RuntimeError('failed')]
    for k in good:
        wrong=deepcopy(good);wrong.pop(k);bad.append(wrong)
        wrong=deepcopy(good);wrong[k]=1 if isinstance(wrong[k],bool) else False;bad.append(wrong)
    bad += [dict(good,ErrorCode='READ_FAILED'),dict(good,ValidationMessage='unexpected'),dict(good,IsValid=False),dict(good,Success=False),dict(good,ErrorMessage='Execution of intent JsonValidationTool has failed'),dict(good,ValidationMessage='Required parameters cannot be blank')]
    for value in bad:
        r,c=execute(overrides={'JsonValidationTool':value});expect_code(r,'JSON_VALIDATION_TOOL_ERROR','HUMAN');assert len(c)==1
    for error in v.SCHEMA_ERRORS:
        r,c=execute(overrides={'JsonValidationTool':dict(Success=False,IsValid=False,ValidationMessage='',ErrorCode=error,ErrorMessage='tool failed')})
        expect_code(r,'JSON_VALIDATION_TOOL_ERROR');assert len(c)==1


@case('ordinary_mass_schema_boundaries')
def _():
    cases=[('24 schema errors','JSON_SCHEMA_INVALID'),('25 schema errors','JSON_SCHEMA_MASS_FAILURE'),('x'*2000,'JSON_SCHEMA_INVALID'),('x'*2001,'JSON_SCHEMA_MASS_FAILURE'),('/UnitTestRules/0/RuleCode: must be object','JSON_SCHEMA_MASS_FAILURE'),('/UnitTestRules/0/RuleCode/pyLabel: missing field','JSON_SCHEMA_INVALID'),('Errors: 25','JSON_SCHEMA_MASS_FAILURE'),('Number of errors: 25','JSON_SCHEMA_MASS_FAILURE'),('/UnitTestRules/0/Scenarios/0/EvidenceSummary: must be object','JSON_SCHEMA_MASS_FAILURE'),('/UnitTestRules/0/Scenarios/0/EvidenceSummary/AssertionCount: expected integer 25','JSON_SCHEMA_INVALID'),('/: expected object','JSON_SCHEMA_MASS_FAILURE')]
    cases += [('\n'.join(f'{i}. invalid field' for i in range(n)),'JSON_SCHEMA_MASS_FAILURE' if n==25 else 'JSON_SCHEMA_INVALID') for n in (24,25)]
    for msg,code in cases:
        r,c=execute(overrides={'JsonValidationTool':dict(Success=True,IsValid=False,ValidationMessage=msg,ErrorCode='',ErrorMessage='')})
        expect_code(r,code,'GENERATOR_REPAIR');assert len(c)==1 and len(r['issues'])==1 and len(r['jsonSchemaValidation']['message'])<=2000
        assert r['jsonSchemaValidation']['message']==msg if code=='JSON_SCHEMA_INVALID' else r['jsonSchemaValidation']['message']!=msg


@case('memory_envelopes_payloads_no_fallback')
def _():
    good=dict(Success=True,Payload=fixture()[3],ErrorCode='',ErrorMessage='')
    variants=[None,{},dict(response='candidate'),RuntimeError('failed')]
    for k in good:
        x=deepcopy(good);x.pop(k);variants.append(x)
        x=deepcopy(good);x[k]=0;variants.append(x)
    variants += [dict(good,ErrorCode='NOT_FOUND'),dict(good,Success=False),dict(good,Payload=''),dict(good,Payload='{"a":1,"a":2}'),dict(good,Payload='{"UnitTestRules":NaN}'),dict(good,Payload='{}')]
    variants += [dict(Success=False,Payload='',ErrorCode=e,ErrorMessage='failed') for e in consumer.READ_ERRORS]
    for value in variants:
        r,c=execute(overrides={'GetMemory':value});expect_code(r,'MEMORY_READ_TOOL_ERROR','HUMAN');assert len(c)==2 and r['jsonSchemaValidation']=={'isValid':True,'message':''}
    r,c=execute(overrides={'GetMemory':dict(good,platformMetadata='ignored')});assert r['valid']


@case('all_unit_rut_mismatch_no_knowledge')
def _():
    x=candidate();x['UnitTestRules'].append(deepcopy(x['UnitTestRules'][0]));x['UnitTestRules'][1]['RuleCode']['pyRuleUnderTest']['pyDetails']['pyRuleUnderTestType']='Rule-Obj-When'
    # Custom current map permits unit1, independently of the normal single fixture helper.
    calls=[]
    def tool(name,args):
        calls.append(name)
        return dict(Success=True,IsValid=True,ValidationMessage='',ErrorCode='',ErrorMessage='') if name=='JsonValidationTool' else dict(Success=True,Payload=projection.json_text(x),ErrorCode='',ErrorMessage='')
    r=v.run('c','Rule-Obj-Model','u',tool);check_report(r,[fixture()[0],fixture()[0]])
    assert calls==['JsonValidationTool','GetMemory'] and r['issues'][0]['unit']==1 and r['issues'][0]['scenario'] is None
    expect_code(r,'RUT_TYPE_MISMATCH','GENERATOR_REPAIR')


@case('knowledge_failures_and_complete_keys')
def _():
    source,rut,cache,raw=fixture();rows=[dict(Area=k,Description=value) for k,value in cache.items()]
    bad=[None,{},dict(pxResults=[]),dict(pxResults=rows[:-1]),dict(pxResults=rows+[rows[0]]),dict(pxResults=[dict(rows[0],Description='')]+rows[1:]),dict(pxResults=[dict(rows[0],Area='Rule-Test-Unit-Case')]+rows[1:]),RuntimeError('failed')]
    for value in bad:
        r,c=execute(overrides={'KnowledgeTool':value});expect_code(r,'AMBIGUOUS','HUMAN');assert len(c)==3


@case('real_s3_candidates_read_only')
def _():
    for name in ['standard-escaping','rut-parameter-provenance','when-key-a','when-key-b','when-no-simulation','when-formal-parameter','when-two-rows']:
        r,c=execute(name);assert r['valid'],(name,r)
    x=candidate();before=deepcopy(x)
    v.inspect_candidate(x,fixture()[1],fixture()[2]);assert x==before
    def mutation(x,*args):x.clear();return []
    r,c=execute(inspect=mutation);expect_code(r,'AMBIGUOUS','HUMAN')


@case('strict_trace_complete_grammar')
def _():
    raw=evidence(candidate())['AssertionDecisionTrace'];lines=raw.splitlines()
    assert {'ASSERT','SIM'}<={x['tag'] for x in v.parse_trace(raw)}
    assert v.parse_trace('OMIT|id=O1|target=.X|reason=incorrect_candidate_assertion')[0]['tag']=='OMIT'
    bad=[raw+'\n'+lines[0],raw.replace('id=A001','id=',1),raw.replace('sig=','missing=',1),raw.replace('|params=', '|extra=x|params=',1),raw+'\nPROFILE|x=y',raw.replace('kind=Property','kind=Decision',1),raw.replace('support=','bad=',1)]
    for mutated in bad:
        try:v.parse_trace(mutated)
        except v.ContractError:pass
        else:raise AssertionError('invalid trace accepted')
    for reason in v.OMIT_REASONS:
        t='OMIT|id=O1|target=.X|reason='+reason;assert v.parse_trace(t)[0]['reason']==reason
    for reason in ['legacy','', 'inactive_evaluate_all_scalar_extra']:
        try:v.parse_trace('OMIT|id=O1|target=.X|reason='+reason)
        except v.ContractError:pass
        else:raise AssertionError('bad reason')


@case('entity_string_numeric_normalization')
def _():
    assert v.decode_field('&amp;quot;')=='&quot;'
    assert v.decode_field('&quot;a&#124;b&#10;c&#13;d&amp;')=='"a|b\nc\rd&'
    assert v.value_equal('true','"true"') and v.value_equal(' Text ','" Text "')
    assert not v.value_equal('true','"\\"true\\""')
    assert v.value_equal('[1,2]',[1,2]) and not v.value_equal('[1,2]',[2,1])
    assert not v.value_equal('true',1) and not v.value_equal('1',True)
    assert v.value_equal('0.123456789012345678901',v.Decimal('0.123456789012345678901'))
    assert not v.value_equal('0.123456789012345678901',v.Decimal('0.123456789012345678902'))
    assert v.value_equal('null',None) and v.value_equal('null','null')  # source type proof is intentionally Generator-owned.
    assert not v.value_equal('<EMPTY>','',True)


@case('canonical_paths_trace_only')
def _():
    assert v.path('Page.Items(1)','.Items(1).Name',True)==('Page.Items(1).Name',True)
    assert v.path('Page.Items(1)','.Items(1).Name')==('Page.Items(1).Items(1).Name',False)
    assert v.path('Page','Param.X',True)==('Param.X',False)
    assert v.path('Page','.Roles(3).Permission(10).Value',True)[0]=='Page.Roles(3).Permission(10).Value'
    x=candidate();e=evidence(x);line=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|'));a=v.parse_trace(line)[0]
    # Duplicate the primary page token in trace alone while RuleCode remains exact.
    new=line.replace('target='+a['target'],'target=.'+a['page']+a['target'])
    r=inspect_mutation(lambda y:evidence(y).__setitem__('AssertionDecisionTrace',evidence(y)['AssertionDecisionTrace'].replace(line,new)),code='TRACE_PATH_CANONICALIZATION_NEEDED')
    assert not any(i['code']=='ASSERT_MISSING' for i in r['issues'])


@case('bidirectional_assertion_value_and_count')
def _():
    inspect_mutation(lambda x:child(x).__setitem__('pyExpectedValue','changed'),code='ASSERT_VALUE_MISMATCH')
    inspect_mutation(lambda x:rulecode(x)['pyExpectedResults'][0]['pyExpectedResults'].clear(),code='ASSERT_MISSING')
    inspect_mutation(lambda x:rulecode(x)['pyExpectedResults'][0]['pyExpectedResults'].append(deepcopy(child(x))),code='ASSERT_EXTRA')
    inspect_mutation(lambda x:rulecode(x)['pyExpectedResults'][0].__setitem__('pyAssertionType','Page'),code='ASSERT_BLOCK_INVALID')
    inspect_mutation(lambda x:evidence(x).__setitem__('AssertionCount',999),code='COUNT_MISMATCH')


@case('missing_invalid_unfinalized_semantics')
def _():
    inspect_mutation(lambda x:evidence(x).__setitem__('AssertionDecisionTrace',''),code='TRACE_MISSING',route='SEMANTIC_REJECT')
    inspect_mutation(lambda x:evidence(x).__setitem__('AssertionDecisionTrace',evidence(x)['AssertionDecisionTrace'].replace('support=Verified','support=Structural').replace('support=PredictedFromRules','support=Structural')),code='TRACE_INVALID',route='SEMANTIC_REJECT')
    inspect_mutation(lambda x:evidence(x).__setitem__('ReasoningTrace','A candidate claim has no final ASSERT or OMIT decision.'),code='DECISION_NOT_FINALIZED',route='SEMANTIC_REJECT')


@case('omission_absence_and_trace_census')
def _():
    def mutate(x):
        a=next(t for t in v.parse_trace(evidence(x)['AssertionDecisionTrace']) if t['tag']=='ASSERT')
        evidence(x)['AssertionDecisionTrace']+='\nOMIT|id=O-new|target='+a['target']+'|reason=incorrect_candidate_assertion'
        evidence(x)['OmittedClaimCount']+=1
    # New decision ID is present in candidate but not immutable source; test inspect scope separately.
    x=candidate();mutate(x);r=v.report(v.inspect_candidate(x,fixture()[1],fixture()[2]));expect_code(r,'REASONING_CONTRADICTION','SEMANTIC_REJECT')
    Draft202012Validator(REPORT_SCHEMA).validate(r)
    assert not any(i['action']=='REMOVE_ASSERTION' for i in r['issues'])


@case('simulation_mapping_shared_identity')
def _():
    inspect_mutation(lambda x:rulecode(x).__setitem__('pySimulation',[]),code='SIM_MISSING')
    inspect_mutation(lambda x:rulecode(x)['pySimulation'].append(deepcopy(rulecode(x)['pySimulation'][0])),code='SIM_SHAPE_INVALID')
    inspect_mutation(lambda x:rulecode(x)['pySimulation'][0].__setitem__('pySimulationMethod','Other'),code='DOC_SIMULATION_METHOD_INVALID')
    inspect_mutation(lambda x:rulecode(x)['pySimulation'][0].__setitem__('pyMockingSupportedRuleTypes','Rule-Obj-Activity'),code='DOC_DATAPAGE_RULETYPE_INVALID')
    def setup(x):rulecode(x).setdefault('pySetup',[]).append(dict(pyActionType='LoadDataPage',pyActionName=rulecode(x)['pySimulation'][0]['pyRuleNameToBeMocked']))
    inspect_mutation(setup,code='DOC_DATAPAGE_IN_SETUP')
    def params(x):evidence(x,1)['AssertionDecisionTrace']=evidence(x,1)['AssertionDecisionTrace'].replace('params={&quot;Customer&quot;:&quot;A&quot;}','params={&quot;Customer&quot;:&quot;B&quot;}')
    r=inspect_mutation(params,'when-two-rows',code='TRACE_INVALID',route='SEMANTIC_REJECT')
    assert any(i['scenario'] is None and i['code']=='TRACE_INVALID' for i in r['issues'])


@case('when_rows_cells_and_scope')
def _():
    inspect_mutation(lambda x:cell(x,1).__setitem__('pyExpectedValue','different'),'when-two-rows',code='ASSERT_VALUE_MISMATCH')
    r=inspect_mutation(lambda x:cell(x,1).__setitem__('pyDisplayLabel','wrong'),'when-two-rows',code='DOC_ASSERTION_BLOCK_KIND_MISMATCH')
    assert any(i['scenario'] is None for i in r['issues'])
    inspect_mutation(lambda x:rulecode(x)['pyExpectedResults'][0]['pyExpectedResults'].pop(),'when-two-rows',code='COUNT_MISMATCH')
    inspect_mutation(lambda x:evidence(x,1).__setitem__('AssertionDecisionTrace',evidence(x,1)['AssertionDecisionTrace'].replace('row=2','row=1')),'when-two-rows',code='TRACE_INVALID',route='GENERATOR_REPAIR')
    def remove(x):
        rows=evidence(x)['AssertionDecisionTrace'].splitlines();rows.remove(next(line for line in rows if line.startswith('ASSERT|')));evidence(x)['AssertionDecisionTrace']='\n'.join(rows)
    inspect_mutation(remove,'when-two-rows',code='TRACE_INVALID',route='SEMANTIC_REJECT')
    inspect_mutation(lambda x:cell(x).__setitem__('pyPropertyAbsolutePath','.Short'),'when-two-rows',code='ASSERT_VALUE_MISMATCH')


@case('reserved_roots_and_safe_literals')
def _():
    for root in v.RESERVED:
        r=inspect_mutation(lambda x:rulecode(x)['pySetupPages'].append(dict(pySetupPageName=root,pyPageDetails={})),code='DOC_RESERVED_SYSTEM_PAGE_SEED',route='SEMANTIC_REJECT')
        assert any(i['scenario'] is None for i in r['issues'])
        assert not v.reserved('.'+root) and not v.reserved('Page.'+root) and not v.reserved(root+'Custom')
        inspect_mutation(lambda x:cell(x).__setitem__('pyPropertyAbsolutePath',root+'.X'),'when-two-rows',code='DOC_RESERVED_SYSTEM_PAGE_SEED')
    x=candidate();child(x)['pyExpectedValue']='pxThread';r=v.inspect_candidate(x,fixture()[1],fixture()[2]);assert not any(i['code']=='DOC_RESERVED_SYSTEM_PAGE_SEED' for i in r)


@case('synthetic_dependency_contradiction')
def _():
    inspect_mutation(lambda x:evidence(x).__setitem__('ReasoningTrace','IsInPageListWhen was blocked only because Name is absent from pxRuleReferences[].'),'when-two-rows',code='REASONING_CONTRADICTION',route='SEMANTIC_REJECT')
    x=candidate('when-two-rows');evidence(x)['ReasoningTrace']='IsInPageListWhen synthetic dependency is absent from pxRuleReferences[]; dependency was fetched successfully.'
    assert not any(i['code']=='REASONING_CONTRADICTION' for i in v.inspect_candidate(x,'Rule-Obj-When',fixture('when-two-rows')[2]))


@case('report_catalog_precedence_warnings_atomic')
def _():
    for code,actions in consumer.CODE_ACTIONS.items():
        for action in actions:
            schema_code=code in {'JSON_SCHEMA_INVALID','JSON_SCHEMA_MASS_FAILURE','JSON_VALIDATION_TOOL_ERROR'}
            r=v.report([v.issue(code,action)],not schema_code,'bounded diagnostic' if schema_code else '')
            check_report(r)
    warning=v.issue('AMBIGUOUS',severity='W');r=check_report(v.report([warning]));assert r['valid'] and r['route']=='OK' and r['warnings']==1
    mechanical=v.issue('ASSERT_MISSING',u=0,s=0,decision='A001')
    semantic=v.issue('REASONING_CONTRADICTION',u=0,s=0)
    human=v.issue('AMBIGUOUS')
    for items,route in [([mechanical],'GENERATOR_REPAIR'),([mechanical,semantic],'SEMANTIC_REJECT'),([mechanical,semantic,human],'HUMAN')]:
        r=check_report(v.report(items));assert r['route']==route and r['blocking']==len(items)
    assert v.report([mechanical,mechanical])['blocking']==1


@case('current_coordinates_reject_stale_reports')
def _():
    source=fixture('when-two-rows')[0]
    for problem in [v.issue('ASSERT_MISSING',u=0,s=0,path='/UnitTestRules/0/RuleCode/pySimulation'),v.issue('ASSERT_MISSING',u=0,s=1,path='/UnitTestRules/0/Scenarios/0'),v.issue('ASSERT_MISSING',u=9),v.issue('ASSERT_MISSING',u=0,s=0,decision='unknown')]:
        try:consumer.validate_report(json.dumps(v.report([problem])),[source],True)
        except v.ContractError:pass
        else:raise AssertionError('stale/shared coordinate accepted')



@case('param_page_list_count_boolean_shapes')
def _():
    def make(kind='Property',target='.Value',mode='Text',comparator='Is Equals To',value='text'):
        x=candidate();code=rulecode(x);page=code['pyPrimaryPageForRUT'];cls=code['pyClassName']
        fields=dict(id='A001',kind=kind,target=target,page=page,class_=cls,mode=mode,comparator=comparator,value=value,support='Structural' if comparator in v.NO_VALUE else 'Verified')
        a='ASSERT|'+'|'.join(k+'='+projection.b.trace_escape(val) for k,val in fields.items()).replace('class_=', 'class=')
        block=dict(pyAssertionType=kind,pyStepPageName=page,pyStepPageClass=cls)
        item=dict(pyComparator=comparator,pyPropertyAbsolutePath=target)
        if kind=='ResultCount':block.update(pyListContext=target,pyComparator=comparator,pyExpectedValue=value)
        else:
            if kind=='Page':item['pyPropertyAbsolutePath']=page+target
            elif target.startswith('Param.'):
                item.update(pyPropertyName=target,pyPropertyMode='Text',pyAssertionType='Property')
            else:item.update(pyPropertyName=target.rsplit('.',1)[-1],pyPropertyMode=mode,pyPageName=page,pyPropertyApplyToClass=cls,pyPropertyRealName='Value')
            if comparator not in v.NO_VALUE:item['pyExpectedValue']=value=='true' if mode=='TrueFalse' else value
            block['pyExpectedResults']=[item]
        if kind=='List':block.update(pyListContext='.Items',pyNumberOfAppearances='InAllInstances')
        code['pyExpectedResults']=[block];code['pySimulation']=[]
        e=evidence(x);exact=int(comparator not in v.NO_VALUE and kind!='ResultCount')
        e.update(AssertionDecisionTrace=a,AssertionCount=1,ExactValueAssertionCount=exact,StructuralAssertionCount=1-exact,OmittedClaimCount=0,SimulatedDependencyCount=0)
        return x
    vectors=[dict(target='Param.Name'),dict(kind='Page',target='.Items(1)',comparator='Exists',value=None),dict(kind='ResultCount',target='.Items',mode='-',value='2'),dict(mode='TrueFalse',comparator='Is True',value='true'),dict(mode='TrueFalse',comparator='Is False',value='false'),dict(value='true'),dict(kind='List',target='.Items.Value')]
    for params in vectors:
        x=make(**params);r=check_report(v.report(v.inspect_candidate(x,fixture()[1],fixture()[2])));assert r['valid'],(params,r)
    x=make(target='Param.Name');child(x)['pyPageName']='Wrong';expect_code(v.report(v.inspect_candidate(x,fixture()[1],fixture()[2])),'DOC_PARAM_ASSERTION_SHAPE_INVALID')
    x=make(mode='TrueFalse',comparator='Is True',value='true');child(x)['pyExpectedValue']='true';expect_code(v.report(v.inspect_candidate(x,fixture()[1],fixture()[2])),'ASSERT_VALUE_MISMATCH')
    x=make(kind='List',target='.Items.Value');rulecode(x)['pyExpectedResults'][0]['pyNumberOfAppearances']='InAnyInstance';assert not v.inspect_candidate(x,fixture()[1],fixture()[2])
    x=make(kind='ResultCount',target='.Items',mode='-',value='2');rulecode(x)['pyExpectedResults'][0]['pyExpectedValue']='3';expect_code(v.report(v.inspect_candidate(x,fixture()[1],fixture()[2])),'ASSERT_VALUE_MISMATCH')


@case('empty_cell_preserved_and_parent_contradiction')
def _():
    x=candidate('when-two-rows');e=evidence(x);a=next(t for t in v.parse_trace(e['AssertionDecisionTrace']) if t['tag']=='ASSERT' and t['kind']=='DecisionInput')
    original=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|id='+a['id']+'|'))
    altered=original.replace('|value='+a['value']+'|','|value=<EMPTY>|')
    e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(original,altered);cell(x).pop('pyExpectedValue')
    base=deepcopy(x);r=check_report(v.report(v.inspect_candidate(x,'Rule-Obj-When',fixture('when-two-rows')[2])),when=True);assert r['valid'],r
    for present in [None,'','<EMPTY>']:
        y=deepcopy(base);cell(y)['pyExpectedValue']=present;expect_code(v.report(v.inspect_candidate(y,'Rule-Obj-When',fixture('when-two-rows')[2])),'ASSERT_VALUE_MISMATCH')
    evidence(x)['ReasoningTrace']='The omitted input value means parent page absence.'
    r=v.report(v.inspect_candidate(x,'Rule-Obj-When',fixture('when-two-rows')[2]));expect_code(r,'REASONING_CONTRADICTION','SEMANTIC_REJECT')


@case('list_mock_wrapper_and_provenance_limit')
def _():
    x=candidate();e=evidence(x);line=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('SIM|'))
    e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(line,line.replace('shape=page','shape=list').replace('itemClass=-','itemClass=App-Data-Item'))
    sim=rulecode(x)['pySimulation'][0]
    sim['pySetupPages']=[dict(pySetupPageName='Payload',pyPageDetails=dict(pxObjClass='App-Data-Wrapper',Items=[dict(pxObjClass='App-Data-Item')]))]
    r=check_report(v.report(v.inspect_candidate(x,fixture()[1],fixture()[2])));assert r['valid'],r
    y=deepcopy(x);y['UnitTestRules'][0]['RuleCode']['pySimulation'][0]['pySetupPages'][0]['pyPageDetails'].pop('pxObjClass')
    expect_code(v.report(v.inspect_candidate(y,fixture()[1],fixture()[2])),'DOC_LIST_SIMULATION_WRAPPER_MISSING')
    y=deepcopy(x);y['UnitTestRules'][0]['RuleCode']['pySimulation'][0]['pySetupPages'][0]['pyPageDetails']['Items'][0]['pxObjClass']='Wrong'
    expect_code(v.report(v.inspect_candidate(y,fixture()[1],fixture()[2])),'SIM_SHAPE_INVALID')
    sim['pySetupPages'][0]['pyPageDetails']['Unrelated']=[dict(pxObjClass='Other')]
    assert not v.inspect_candidate(x,fixture()[1],fixture()[2])  # No invented payloadPage/itemPath choice.


@case('visible_doc_context_and_catalog_limits')
def _():
    inspect_mutation(lambda x:rulecode(x)['pyPagesAndClasses'][0].__setitem__('pyPagesAndClassesClass','Wrong-Class'),code='AMBIGUOUS',route='HUMAN')
    # Remaining free-text documented behaviors are validated by source-clause review,
    # not falsely represented as an executable natural-language documentation engine.
    for code,action in [('DOC_ERROR_MESSAGE_FORMAT_INVALID','FIX_ASSERTION'),('DOC_RESULTCOUNT_FOR_NON_COUNT','FIX_BLOCK_TYPE'),('DOC_RESULTCOUNT_FOR_NON_COUNT','REJECT_SEMANTICS'),('PARAM_SHAPE_INVALID','FIX_PARAM_SHAPE')]:
        check_report(v.report([v.issue(code,action,u=0,s=0,decision='A001')]))


@case('final_conflicts_both_families_reject')
def _():
    for name in ['standard-escaping','when-two-rows']:
        x=candidate(name);e=evidence(x);a=next(t for t in v.parse_trace(e['AssertionDecisionTrace']) if t['tag']=='ASSERT')
        e['AssertionDecisionTrace']+='\nOMIT|id=O-conflict|target='+a['target']+'|reason=incorrect_candidate_assertion'
        e['OmittedClaimCount']+=1
        r=v.report(v.inspect_candidate(x,fixture(name)[1],fixture(name)[2]));expect_code(r,'REASONING_CONTRADICTION','SEMANTIC_REJECT')
        assert not any(i['action']=='REMOVE_ASSERTION' for i in r['issues'])
    x=candidate();e=evidence(x);a=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|'))
    e['AssertionDecisionTrace']+='\n'+a.replace('id=A001','id=A999').replace('Ada Lovelace','different')
    block=deepcopy(rulecode(x)['pyExpectedResults'][0]);block['pyExpectedResults'][0]['pyExpectedValue']='different';rulecode(x)['pyExpectedResults'].append(block)
    e['AssertionCount']+=1;e['ExactValueAssertionCount']+=1
    expect_code(v.report(v.inspect_candidate(x,fixture()[1],fixture()[2])),'REASONING_CONTRADICTION','SEMANTIC_REJECT')


@case('literal_quotes_and_genuine_repeated_paths')
def _():
    assert v.value_equal('"literal"','"literal"')
    assert v.value_equal('a\\"b','a\\"b')
    assert v.value_equal('literal','"literal"')
    assert not v.value_equal('literal','"\\"literal\\""')
    x=candidate();e=evidence(x);a=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|'));fields=v.parse_trace(a)[0]
    replacement=a.replace('value='+projection.b.trace_escape(fields['value']),'value=&quot;literal&quot;')
    e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(a,replacement);child(x)['pyExpectedValue']='"literal"'
    assert not v.inspect_candidate(x,fixture()[1],fixture()[2])
    x=candidate();e=evidence(x);page=rulecode(x)['pyPrimaryPageForRUT'];original=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|'));fields=v.parse_trace(original)[0]
    e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(original,original.replace('target='+fields['target'],'target=.'+page+'.Repeated'))
    child(x)['pyPropertyAbsolutePath']='.'+page+'.Repeated';child(x)['pyPropertyName']=child(x)['pyPropertyRealName']='Repeated'
    assert not v.inspect_candidate(x,fixture()[1],fixture()[2])
    # A physically present genuine repeat has priority even when the fallback path also exists.
    extra=deepcopy(rulecode(x)['pyExpectedResults'][0]);extra['pyExpectedResults'][0]['pyPropertyAbsolutePath']='.Repeated';rulecode(x)['pyExpectedResults'].append(extra)
    r=v.report(v.inspect_candidate(x,fixture()[1],fixture()[2]));expect_code(r,'ASSERT_EXTRA')
    assert not any(i['code'] in {'ASSERT_MISSING','TRACE_PATH_CANONICALIZATION_NEEDED'} for i in r['issues'])


@case('visible_context_alignment')
def _():
    for key,value in [('pyPropertyApplyToClass','Wrong-Class'),('pyPageName','WrongPage'),('pyPropertyMode','Integer')]:
        inspect_mutation(lambda x:child(x).__setitem__(key,value),code='DOC_ASSERTION_BLOCK_KIND_MISMATCH')
    inspect_mutation(lambda x:rulecode(x)['pyExpectedResults'][0].__setitem__('pyStepPageClass','Wrong-Class'),code='DOC_ASSERTION_BLOCK_KIND_MISMATCH')
    inspect_mutation(lambda x:rulecode(x)['pyExpectedResults'][0].__setitem__('pyClassContext','Wrong-Class'),'when-two-rows',code='DOC_ASSERTION_BLOCK_KIND_MISMATCH')
    inspect_mutation(lambda x:rulecode(x)['pyExpectedResults'][0]['pyExpectedResults'][0].__setitem__('pyPageName','WrongPage'),'when-two-rows',code='DOC_ASSERTION_BLOCK_KIND_MISMATCH')
    for old,new in [('page=rowLevelPage','page=WrongPage'),('mode=text','mode=wrong')]:
        inspect_mutation(lambda x:evidence(x).__setitem__('AssertionDecisionTrace',evidence(x)['AssertionDecisionTrace'].replace(old,new)),'when-two-rows',code='TRACE_INVALID',route='SEMANTIC_REJECT')
    # Source input mode Decimal is legitimate while physical cell mode stays text.
    assert execute('when-formal-parameter')[0]['valid']


@case('simulated_dp_roots_all_visible_carriers')
def _():
    for name in ['D_Customer','D_Customer[Customer=A]']:
        r=inspect_mutation(lambda x:rulecode(x)['pySetupPages'].append(dict(pySetupPageName=name,pyPageDetails={})), 'when-two-rows',code='REASONING_CONTRADICTION',route='SEMANTIC_REJECT')
        assert all(i['scenario'] is None for i in r['issues'])
    x=candidate('when-two-rows')
    for s in [0,1]:
        e=evidence(x,s);a=next(t for t in v.parse_trace(e['AssertionDecisionTrace']) if t['tag']=='ASSERT' and t['kind']=='DecisionInput')
        e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace('target='+a['target'],'target=D_Customer[Customer=A].X')
        for key in ['pyPropertyName','pyPropertyAbsolutePath','pyDisplayLabel']:cell(x,s)[key]='D_Customer[Customer=A].X'
    r=v.report(v.inspect_candidate(x,'Rule-Obj-When',fixture('when-two-rows')[2]));expect_code(r,'REASONING_CONTRADICTION','SEMANTIC_REJECT')
    assert any(i['scenario'] is None for i in r['issues'])
    assert v.page_root('.D_Customer.X') is None and v.page_root('Page.D_Customer')=='Page'
    assert execute('when-two-rows')[0]['valid']  # Physical mock setup is allowed.


@case('mass_diagnostics_and_untraversable_views')
def _():
    msg='\n'.join('- /UnitTestRules/0/Name: error '+str(i) for i in range(25))
    r,c=execute(overrides={'JsonValidationTool':dict(Success=True,IsValid=False,ValidationMessage=msg,ErrorCode='',ErrorMessage='')});expect_code(r,'JSON_SCHEMA_MASS_FAILURE');assert len(c)==1
    assert not v.mass_failure('/UnitTestRules/0/Name: value 25 is invalid')
    for key in ['pyExpectedResults','pySimulation','pySetupPages','pyPagesAndClasses','pySetup','pyCleanup']:
        for value in [[None],{},[7]]:
            x=candidate();rulecode(x)[key]=value
            r,c=execute(raw=projection.json_text(x));expect_code(r,'MEMORY_READ_TOOL_ERROR','HUMAN');assert len(c)==2
    x=candidate();child(x)['pyExpectedResults']=[None]
    r,c=execute(raw=projection.json_text(x));expect_code(r,'MEMORY_READ_TOOL_ERROR');assert len(c)==2


@case('canonical_final_values_order_independent')
def _():
    for values in [('literal','"literal"'),('"literal"','literal')]:
        x=candidate();e=evidence(x);line=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|'));a=v.parse_trace(line)[0]
        first=line.replace('value='+projection.b.trace_escape(a['value']),'value='+projection.b.trace_escape(values[0]));second=first.replace('id=A001','id=A999').replace('value='+projection.b.trace_escape(values[0]),'value='+projection.b.trace_escape(values[1]))
        e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(line,first)+'\n'+second
        e['AssertionCount']+=1;e['ExactValueAssertionCount']+=1;child(x)['pyExpectedValue']=values[0]
        extra=deepcopy(rulecode(x)['pyExpectedResults'][0]);extra['pyExpectedResults'][0]['pyExpectedValue']=values[1];rulecode(x)['pyExpectedResults'].append(extra)
        r=v.report(v.inspect_candidate(x,fixture()[1],fixture()[2]));expect_code(r,'REASONING_CONTRADICTION','SEMANTIC_REJECT')


@case('literal_omit_path_and_assertion_multiplicity')
def _():
    x=candidate();e=evidence(x);page=rulecode(x)['pyPrimaryPageForRUT'];a=next(t for t in v.parse_trace(e['AssertionDecisionTrace']) if t['tag']=='ASSERT')
    e['AssertionDecisionTrace']+='\nOMIT|id=O-repeat|target=.'+page+a['target']+'|reason=incorrect_candidate_assertion';e['OmittedClaimCount']+=1
    assert not v.inspect_candidate(x,fixture()[1],fixture()[2])
    x=candidate();e=evidence(x);line=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|'));a=v.parse_trace(line)[0]
    line2=line.replace('target='+a['target'],'target=.'+page+'.Repeated')
    e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(line,line2)+'\n'+line2.replace('id=A001','id=A999');e['AssertionCount']+=1;e['ExactValueAssertionCount']+=1
    child(x)['pyPropertyAbsolutePath']='.'+page+'.Repeated';extra=deepcopy(rulecode(x)['pyExpectedResults'][0]);extra['pyExpectedResults'][0]['pyPropertyAbsolutePath']='.Repeated';rulecode(x)['pyExpectedResults'].append(extra)
    r=v.report(v.inspect_candidate(x,fixture()[1],fixture()[2]));expect_code(r,'ASSERT_MISSING');expect_code(r,'ASSERT_EXTRA')
    assert not any(i['code']=='TRACE_PATH_CANONICALIZATION_NEEDED' for i in r['issues'])


@case('reported_error_counts_not_echoed_values')
def _():
    for text in ['25 errors','Errors: 25','Number of errors: 25']:
        msg='/UnitTestRules/0/RuleCode/pyLabel: value "'+text+'" does not match ^TC_'
        assert not v.mass_failure(msg)
        r,c=execute(overrides={'JsonValidationTool':dict(Success=True,IsValid=False,ValidationMessage=msg,ErrorCode='',ErrorMessage='')});expect_code(r,'JSON_SCHEMA_INVALID');assert len(c)==1
        assert v.mass_failure(text)
    assert not v.mass_failure('/UnitTestRules/0/Name: value 25 errors')


@case('symmetric_explicit_final_value_types')
def _():
    for modes,values,expected in [(['Text','Decimal'],['1','1.0'],'SEMANTIC_REJECT'),(['Decimal','Text'],['1.0','1'],'SEMANTIC_REJECT'),(['Decimal','Decimal'],['1','1.0'],'OK'),(['Decimal','Decimal'],['1.0','1'],'OK')]:
        x=candidate();e=evidence(x);line=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|'));a=v.parse_trace(line)[0]
        rows=[line.replace('id=A001','id='+ident).replace('mode='+a['mode'],'mode='+mode).replace('value='+projection.b.trace_escape(a['value']),'value='+value) for ident,mode,value in zip(['A001','A999'],modes,values)]
        e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(line,rows[0])+'\n'+rows[1];e['AssertionCount']+=1;e['ExactValueAssertionCount']+=1
        extra=deepcopy(rulecode(x)['pyExpectedResults'][0]);rulecode(x)['pyExpectedResults'].append(extra)
        for block,mode,value in zip(rulecode(x)['pyExpectedResults'],modes,values):
            item=block['pyExpectedResults'][0];item['pyPropertyMode']=mode;item['pyExpectedValue']=v.Decimal(value) if mode=='Decimal' else value
        r=v.report(v.inspect_candidate(x,fixture()[1],fixture()[2]));assert r['route']==expected,r

@case('blank_rut_zero_tools_opaque_addresses')
def _():
    for blank in [' ', '\t\n', '\u00a0']:
        r,calls=execute(rut=blank)
        expect_code(r,'JSON_VALIDATION_TOOL_ERROR','HUMAN');assert not calls
        i=r['issues'][0];assert (i['unit'],i['scenario'],i['decision'],i['path'])==(None,None,'','/')
    for name in ['standard-escaping','when-two-rows']:
        r,calls=execute(name,case_id=' \t ',uuid=' \n ')
        assert r['valid'] and calls[0][1]['CaseID']==calls[1][1]['CaseID']==' \t '
        assert calls[0][1]['UUID']==calls[1][1]['UUID']==' \n '


@case('explicit_scalar_constraints_before_matching')
def _():
    def evaluate(mode,comparator,text,value,target=None,physical_comparator=None):
        x=candidate();e=evidence(x);a=next(t for t in v.parse_trace(e['AssertionDecisionTrace']) if t['tag']=='ASSERT')
        old=next(line for line in e['AssertionDecisionTrace'].splitlines() if line.startswith('ASSERT|id='+a['id']+'|'))
        updated=old.replace('mode='+a['mode'],'mode='+mode).replace('comparator='+a['comparator'],'comparator='+comparator).replace('value='+projection.b.trace_escape(a['value']),'value='+projection.b.trace_escape(text))
        if target:updated=updated.replace('target='+a['target'],'target='+target)
        e['AssertionDecisionTrace']=e['AssertionDecisionTrace'].replace(old,updated)
        child(x).update(pyPropertyMode=mode,pyExpectedValue=value,pyComparator=physical_comparator or comparator)
        Draft202012Validator(json.loads(fixture()[2][consumer.knowledge_keys(fixture()[1])[1]])).validate(x)
        r,calls=execute(raw=projection.json_text(x))
        assert [n for n,args in calls]==['JsonValidationTool','GetMemory','KnowledgeTool']
        return r
    # Fixed supported-mode census from the unchanged S3 source/candidate contract,
    # deliberately independent of the Validator implementation's mode constant.
    string_modes=['Text','String','Identifier','Password','TextEncrypted','Date','DateTime','TimeOfDay']
    assert set(string_modes)==v.STRING_MODES
    for text,boolean in [('true',True),('false',False)]:
        assert evaluate('TrueFalse','Is True' if boolean else 'Is False',text,boolean)['valid']
        for mode in string_modes:
            assert evaluate(mode,'Is Equals To',text,text)['valid']
            r=evaluate(mode,'Is Equals To',text,boolean)
            expect_code(r,'ASSERT_VALUE_MISMATCH','GENERATOR_REPAIR')
            assert any((i['unit'],i['scenario'],i['decision'],i['action'])==(0,0,'A001','FIX_ASSERTION') for i in r['issues'])
            r=evaluate(mode,'Is Equals To',text,text,physical_comparator='Is True' if boolean else 'Is False')
            expect_code(r,'ASSERT_VALUE_MISMATCH','GENERATOR_REPAIR')
            for target in [None,'.Other']:
                r=evaluate(mode,'Is True' if boolean else 'Is False',text,text,target)
                expect_code(r,'TRACE_INVALID','SEMANTIC_REJECT')
                assert any((i['unit'],i['scenario'],i['decision'],i['action'])==(0,0,'A001','REJECT_SEMANTICS') for i in r['issues'])
                assert not any(i['action'] in {'ADD_ASSERTION','REMOVE_ASSERTION','FIX_ASSERTION'} for i in r['issues'])
        for target in [None,'.Other']:
            r=evaluate('TrueFalse','Is Equals To',text,boolean,target)
            expect_code(r,'TRACE_INVALID','SEMANTIC_REJECT')
            assert not any(i['action'] in {'ADD_ASSERTION','REMOVE_ASSERTION','FIX_ASSERTION'} for i in r['issues'])
    for mode in string_modes:
        assert not v.value_equal('true',True,mode=mode)
        assert v.value_equal('true','true',mode=mode)
        assert v.value_equal('null',None,mode=mode) and v.value_equal('[1,2]',[1,2],mode=mode)
    for text,value in [('null',None),('[1,2]',[1,2]),('null','null'),('[1,2]','[1,2]'),('"literal"','"literal"')]:
        assert evaluate('Text','Is Equals To',text,value)['valid']


def main():
    for name,fn in CASES.items():
        try:fn()
        except Exception as error:raise AssertionError(name+': '+str(error)) from error
    print(f'PASS: S4 producer/trace/alignment groups={len(CASES)}; exact tools, both families, malformed envelopes, closed reports and current coordinates; repository-static only')


if __name__=='__main__':main()
