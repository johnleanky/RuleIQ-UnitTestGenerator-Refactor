#!/usr/bin/env python3
"""Full Draft 2020-12 plus independent immutable-source/candidate correspondence."""
from copy import deepcopy
from decimal import Decimal
import json
import re
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema import Draft202012Validator
import generator_projection as p
import generator_protocol as protocol
import validate_s3_profiles as profile_tests

ROOT=Path(__file__).resolve().parents[1]
FIXTURES=ROOT/'fixtures/s3/current'


def cache_for(rut_type):
    keys=protocol.knowledge_keys(rut_type)
    prefix='rule-test-unit-case_multInpComb-' if rut_type=='Rule-Obj-When' else 'rule-test-unit-case_'
    return {keys[0]:'Repository UTC guidance fixture',keys[1]:(ROOT/(prefix+'JsonSchema.txt')).read_text(encoding='utf-8-sig'),keys[2]:(ROOT/(prefix+'JsonExample.txt')).read_text(encoding='utf-8-sig')}


def read_source(path):
    raw=path.read_text();header=p.b.parse_line(raw.splitlines()[0],1)['values']
    return p.decode_source(raw,header['caseId'],header['rutType'],int(header['groupOrder'])-1)


def retained(source):return dict(source,scenarios=[s for s in source['scenarios'] if s['rejection'] is None])


def at_path(value,path):
    for token in p.path_tokens(path):value=value[token[1] if isinstance(token,tuple) else token]
    return value


def source_value(kind,value):
    if kind=='empty':return ''
    if kind=='string':return value
    if kind=='number':return Decimal(value)
    if kind=='absent':return None
    return json.loads(value,parse_float=Decimal)


def expected_parameter(param,when,cell=False):
    formal=param['formalType'];kind=param['valueType'];value=source_value(kind,param['value'])
    rendered=json.dumps(value,ensure_ascii=False) if formal=='String' else str(int(value)) if formal=='Integer' else format(value,'f') if formal=='Decimal' else param['value']
    out={'pyParametersParamName':param.get('name'),'pyParametersParamValue':rendered}
    if when:out['pyParametersParamType']={'String':'Text','Boolean':'TrueFalse','TrueFalse':'TrueFalse','Integer':'Integer','Decimal':'Decimal','PAGE':'PAGE'}[formal]
    elif formal=='PAGE':out['pyParametersParamType']='PAGE'
    if cell:out.pop('pyParametersParamValue')
    return out


def flat(value,prefix=()):
    if isinstance(value,dict) and value:
        return {k:v for name,item in value.items() for k,v in flat(item,prefix+(name,)).items()}
    if isinstance(value,list) and value:
        return {k:v for i,item in enumerate(value) for k,v in flat(item,prefix+(i,)).items()}
    if isinstance(value,(int,float,Decimal)) and not isinstance(value,bool):return {prefix:('number',Decimal(str(value)))}
    return {prefix:(type(value).__name__,value)}


def seed_tokens(path,page):
    import re
    if path.startswith(page+'.'):path=path[len(page):]
    tokens=[]
    for name,index in re.findall(r'([A-Za-z][A-Za-z0-9_]*)(?:\(([^)]+)\))?',path):
        tokens.append(name)
        if index:tokens.append(int(index)-1 if index.isdigit() else index)
    return tuple(tokens)


def merge_leaves(leaves,addition):
    for key,value in addition.items():
        for ancestor,old in list(leaves.items()):
            if len(ancestor)<len(key) and key[:len(ancestor)]==ancestor and old in [('list',[]),('dict',{})]:del leaves[ancestor]
        leaves[key]=value


def physical_audit(code,source,sid,when):
    facts=source['profiles'][sid];root=source['root'];classes=json.loads(root['pagesAndClasses'])
    inputs=p.vals(source,sid,'INPUT');params=p.vals(source,sid,'PARAM')
    by_id={v['id']:v for v in params};actual_inputs={i['resolution']:i for i in inputs if i['path'].startswith('Param.')}
    expected=[expected_parameter(v,when,when and actual_inputs[v['id']]['role']=='DECISION_INPUT') for v in params if v['id'] in actual_inputs]
    p.b.require(code['pyRuleUnderTest'].get('pyParameters',[])==expected,'complete RUT parameter census/type/value')
    for phase,target in [('SETUP','pySetup'),('CLEANUP','pyCleanup')]:
        actions=[]
        for a in facts['actions']:
            if a['phase']!=phase:continue
            item={'pyActionType':a['type'],'pyActionName':a['name']}
            if a['page'] is not None:item['pyTargetPage']=a['page']
            if a['parameters']:item['pyParameters']=[expected_parameter(v,when) for v in a['parameters']]
            actions.append(item)
        p.b.require(code.get(target,[])==actions,'complete ordered action/argument census')
    wanted={}
    def page(name):
        wanted.setdefault(name,{('pxObjClass',):('str',classes[name])})
    if root['primarySetup']=='true':page(root['page'])
    for i in inputs:
        if i['path'].startswith('Param.') and by_id[i['resolution']]['formalType']=='PAGE':page(i['value'])
    for seed in [*p.vals(source,sid,'SETUP'),*[i for i in inputs if i['role'] not in {'PARAM','DECISION_INPUT'}]]:
        page(seed['page'])
        if seed['role']!='PAGE_AND_CLASS':merge_leaves(wanted[seed['page']],flat(source_value(seed['valueType'],seed['value']),seed_tokens(seed['path'],seed['page'])))
    emitted=code['pySetupPages']
    p.b.require(len(emitted)==len(wanted) and {v['pySetupPageName']:flat(v['pyPageDetails']) for v in emitted}==wanted,'complete physical INPUT/SETUP/PAGE page/leaf census')
    sims=p.vals(source,sid,'SIM');actual=code.get('pySimulation',[])
    p.b.require(len(actual)==len(sims),'simulation reverse census')
    for out,sim in zip(actual,sims):
        expected={'pyClassName':sim['class'],'pyMockingSupportedRuleTypes':sim['mockingRuleType'],'pyRuleNameToBeMocked':sim['rule'],'pySimulationMethod':sim['method'],'pySetupPages':out['pySetupPages']}
        if sim['referredFromClass'] is not None:expected['pxReferredFromClass']=sim['referredFromClass']
        p.b.require(out==expected,'complete simulation metadata')
        pages=json.loads(sim['setupPages']);binding=facts['simulationBindings'][sim['id']]
        p.b.require([v['pySetupPageName'] for v in out['pySetupPages']]==[v['pySetupPageName'] for v in pages],'complete ordered mock-page census')
        for emitted,src in zip(out['pySetupPages'],pages):
            leaves=flat(json.loads(sim['payload'],parse_float=Decimal)) if src['pySetupPageName']==binding else {}
            if leaves=={():('dict',{})} and src['pyPageDetails']:leaves={}
            for seed in src['pyPageDetails']:merge_leaves(leaves,flat(source_value(seed['valueType'],seed['value']),seed_tokens(seed['path'],src['pySetupPageName'])))
            p.b.require(flat(emitted['pyPageDetails'])==(leaves or {():('dict',{})}),'complete mock payload/seed leaf census')
            if sim['shape']=='list' and src['pySetupPageName']==binding:
                items=emitted['pyPageDetails']
                for token in seed_tokens(facts['simulationItemPaths'][sim['id']],''):items=items[token]
                p.b.require(isinstance(items,list) and all(isinstance(item,dict) and item.get('pxObjClass')==sim['itemClass'] for item in items),'assembled mock item-class audit')


def audit(value,current,cache):
    """Check independent source coordinates, raw carriers and reverse decision census."""
    when=current[0]['header']['kind']=='WHEN';keys=protocol.knowledge_keys(current[0]['header']['rutType'])
    schema=protocol.strict_json(cache[keys[1]])
    errors=list(Draft202012Validator(schema).iter_errors(value))
    p.b.require(not errors,'selected schema: '+('; '.join(e.message for e in errors[:2])))
    units=value['UnitTestRules'];p.b.require(len(units)==len(current),'group count')
    for unit,source in zip(units,current):
        code=unit['RuleCode'];root=source['root'];header=source['header']
        p.b.require(len(unit['Scenarios'])==len(source['scenarios']),'Scenario census')
        p.b.require(unit['Name']==code['pyPurpose']==code['pyLabel'],'name equality')
        p.b.require(code['pyTypeOfSetupPageSelection']=='CUSTOMPAGES','setup selection')
        original=source['meta'][0];label=''.join(w[:1].upper()+w[1:] for w in re.split('[ _]+',re.sub('[^A-Za-z0-9 _]','_',original['name']).strip()[:50]));suffix='G'+header['groupOrder'];label=label[:32-len(suffix)]+suffix;stem=re.sub('[^A-Za-z0-9_]','_',re.sub(r'\s','',header['rutName']));name='TC_'+stem[:49-len(label)]+'_'+label
        p.b.require(unit['Name']==name,'stable source rule name')
        target=json.loads(cache[keys[2]])['UnitTestRules'][0]['RuleCode']
        p.b.require(all(code[k]==target[k] for k in ('pyRuleSet','pyRuleSetVersion')),'Pega selected metadata copy')
        p.b.require(code['pyClassName']==root['class'] and code['pyPrimaryPageForRUT']==root['page'],'primary root')
        details=code['pyRuleUnderTest']['pyDetails']
        p.b.require(details['pyRuleUnderTestType']==header['rutType'] and details['pyRuleUnderTestName']==header['rutName'] and details['pyRuleUnderTestObjClass']==header['rutClass'],'RUT metadata')
        p.b.require(details['pyRuleUnderTestInsName']=='!'.join(source['profiles'][source['scenarios'][0]['id']]['caseKey'].split()[1:3]) and details['pyIsSinglePageImplementation']==source['profiles'][source['scenarios'][0]['id']]['singlePage'],'InsName/execution mode')
        p.b.require(len(code['pyPagesAndClasses'])==len(json.loads(root['pagesAndClasses'])),'P&C reverse census')
        p.b.require({x['pyPagesAndClassesPage']:x['pyPagesAndClassesClass'] for x in code['pyPagesAndClasses']}==json.loads(root['pagesAndClasses']),'P&C map')
        for index,(scenario,selected) in enumerate(zip(unit['Scenarios'],source['scenarios'])):
            sid=selected['id'];summary=scenario['EvidenceSummary'];facts=source['profiles'][sid]
            meta=next(s for s in source['meta'] if s['id']==sid)
            p.b.require(scenario['ReasoningConfidence']==meta['confidence'] and scenario['Testability']=={'Testable':'FullyTestable','PartiallyTestable':'PartiallyTestable','NotTestable':'NotTestable'}[meta['testability']],'confidence/testability preservation')
            p.b.require(all(summary['InternalChecklist'][k]==v for k,v in facts['checklist'].items()),'Author checklist preservation')
            p.b.require(summary['ReasoningTrace']==facts['reasoningTrace'] and summary['DependencyClosureTrace']==facts['dependencyClosureTrace'],'factual traces')
            expected_trace=[]
            for record in p.rows(source,sid):
                if record['tag'] not in {'ASSERT','SIM','OMIT'}:continue
                copy=deepcopy(record)
                if when and copy['tag']=='ASSERT':copy['values']['row']=str(index+1)
                expected_trace.append(p.b.project_trace(copy))
            p.b.require(summary['AssertionDecisionTrace']=='\n'.join(expected_trace),'trace source bijection')
            assertions=p.vals(source,sid,'ASSERT')
            p.b.require(summary['AssertionCount']==len(assertions) and summary['OmittedClaimCount']==len(p.vals(source,sid,'OMIT')) and summary['SimulatedDependencyCount']==len(p.vals(source,sid,'SIM')),'summary counts')
            if when:
                block=code['pyExpectedResults'][0];combos=block['pyExpectedResults']
                p.b.require(len(combos)==len(source['scenarios']),'When row census')
                cells=combos[index]['pyExpectedResults']
                p.b.require(len(cells)==len(assertions),'cell/trace census')
                for cell,a in zip(cells,assertions):
                    p.b.require(cell['pyPropertyAbsolutePath']==cell['pyPropertyName']==cell['pyDisplayLabel']==a['target'],'exact cell path/label')
                    p.b.require((cell['pyPropertyType']=='result')==(a['kind']=='DecisionResult'),'cell kind order')
                    p.b.require('pyExpectedValue' not in cell if a['value']=='<EMPTY>' else cell.get('pyExpectedValue')==a['value'],'cell value/empty preservation')
            else:
                blocks=code['pyExpectedResults'];p.b.require(len(blocks)==len(assertions),'assertion reverse census')
                for block,a in zip(blocks,assertions):
                    p.b.require(block['pyAssertionType']==a['kind'],'assertion block kind')
                    child=block if a['kind']=='ResultCount' else block['pyExpectedResults'][0]
                    p.b.require(child['pyComparator']==a['comparator'],'comparator preservation')
                    binding=next(v for v in facts['bindings'] if v['assertion']==a['id']);fact=facts['expectedValues'][a['id']]
                    optional={k:v for k,v in block.items() if k in p.sg.CONTEXT_FIELDS}
                    # ResultCount comparator is its required core field, not optional context.
                    if a['kind']=='ResultCount':optional.pop('pyComparator',None)
                    p.b.require(optional==binding['context'],'exact optional assertion context')
                    p.b.require(block['pyStepPageName']==binding['stepPage'] and block['pyStepPageClass']==binding['stepClass'],'assertion block root/class')
                    if a['kind'] in {'List','ResultCount'}:
                        context=(a['page'] if a['kind']=='List' else binding['fullPath'])[len(binding['stepPage']):]
                        p.b.require(block['pyListContext']==context,'list/count context')
                    if a['kind']!='ResultCount':
                        p.b.require(len(block['pyExpectedResults'])==1,'scalar assertion item census')
                        path=binding['fullPath'] if a['kind']=='Page' or a['target'].startswith('Param.') else binding['fullPath'][len(binding['stepPage']):]
                        p.b.require(child['pyPropertyAbsolutePath']==path,'assertion full/relative path')
                        if a['kind']!='Page':
                            leaf=binding['fullPath'].rsplit('.',1)[-1]
                            p.b.require(child['pyPropertyName']==(a['target'] if a['target'].startswith('Param.') else leaf) and child['pyPropertyMode']==a['mode'],'property name/mode')
                            if not a['target'].startswith('Param.'):
                                p.b.require(child['pyPageName']==a['page'] and child['pyPropertyApplyToClass']==a['class'] and child['pyPropertyRealName']==leaf.split('(',1)[0] and child.get('pyParentPropertyMode')==binding['parentMode'],'property page/class/parent context')
                    if fact['valueType']=='absent':p.b.require('pyExpectedValue' not in child,'absent value')
                    else:
                        wanted=a['value'] if a['kind']=='ResultCount' else source_value(fact['valueType'],fact['value'])
                        p.b.require(flat(child['pyExpectedValue'])==flat(wanted),'typed expected value exactness')
            physical_audit(code,source,sid,when)


def rejected(action):
    try:action()
    except (p.b.ContractError,KeyError,IndexError,TypeError,ValueError):return
    raise p.b.ContractError('adversarial projection accepted')


def helper_block(a,binding):
    # These are explicit test-vector decisions, not the production source reader.
    kind='absent' if a['value'] is None else 'number' if a['kind']=='ResultCount' or a['mode'] in p.NUMERIC else 'boolean' if a['mode']=='TrueFalse' else 'string'
    return p.assertion_block(a,binding,{'valueType':kind,'value':a['value']})


def semantic_helpers():
    standard=json.loads(cache_for('Rule-Obj-Model')['Rule-Test-Unit-Case_JsonSchema'])
    def block_ok(block):
        schema={'$ref':'#/$defs/AssertionBlock','$defs':standard['$defs']}
        p.b.require(Draft202012Validator(schema).is_valid(block),'helper block schema')
    a={'id':'A001','kind':'Property','target':'.Enabled','page':'RunRecordPrimaryPage','class':'App-Work-Order','mode':'TrueFalse','comparator':'Is True','value':'true','support':'Verified'}
    binding={'fullPath':'RunRecordPrimaryPage.Enabled','stepPage':'RunRecordPrimaryPage','stepClass':'App-Work-Order','context':{'pyCardApplyToClass':'App-Work-Order'},'parentMode':None}
    boolean=helper_block(a,binding);block_ok(boolean)
    p.b.require(boolean['pyExpectedResults'][0]['pyExpectedValue'] is True,'boolean exact JSON carrier')
    for v,cmp in [('false','Is False')]:
        block=helper_block(dict(a,value=v,comparator=cmp),binding);block_ok(block);p.b.require(block['pyExpectedResults'][0]['pyExpectedValue'] is False,'false carrier')
    rejected(lambda:helper_block(dict(a,comparator='Exists'),binding))
    text=helper_block(dict(a,mode='Text',comparator='Is Equals To'),binding);block_ok(text)
    p.b.require(text['pyExpectedResults'][0]['pyExpectedValue']=='true','text true remains string')
    rejected(lambda:helper_block(dict(a,mode='Text'),binding))
    param=helper_block(dict(a,target='Param.Flag',mode='Text',comparator='Is Equals To'),dict(binding,fullPath='Param.Flag'))
    block_ok(param);child=param['pyExpectedResults'][0]
    p.b.require(child['pyPropertyName']==child['pyPropertyAbsolutePath']=='Param.Flag' and not {'pyPageName','pyPropertyRealName','pyParentPropertyMode'}&set(child),'Param path shape')
    nested=helper_block(dict(a,target='.Items(1).Name',page='RunRecordPrimaryPage.Items(1)',mode='Text',comparator='Is Equals To',value='name'),dict(binding,fullPath='RunRecordPrimaryPage.Items(1).Name'))
    block_ok(nested);p.b.require(nested['pyExpectedResults'][0]['pyPropertyAbsolutePath']=='.Items(1).Name' and nested['pyExpectedResults'][0]['pyPageName']=='RunRecordPrimaryPage.Items(1)','nested context preservation')
    page=helper_block(dict(a,kind='Page',target='.Items(1)',comparator='Exists',value=None),dict(binding,fullPath='RunRecordPrimaryPage.Items(1)'))
    block_ok(page);p.b.require(set(page['pyExpectedResults'][0])=={'pyComparator','pyPropertyAbsolutePath'},'compact Page shape')
    count=helper_block(dict(a,kind='ResultCount',target='.Items',comparator='Is Equals To',value='2'),dict(binding,fullPath='RunRecordPrimaryPage.Items'))
    block_ok(count);p.b.require(count['pyExpectedValue']=='2' and count['pyListContext']=='.Items','ResultCount')
    for appearance in ['InAnyInstance','InAllInstances']:
        listing=helper_block(dict(a,kind='List',target='.Name',page='RunRecordPrimaryPage.Items',mode='Text',comparator='Is Equals To',value='name'),dict(binding,fullPath='RunRecordPrimaryPage.Items.Name',context=dict(binding['context'],pyNumberOfAppearances=appearance)))
        block_ok(listing);p.b.require(listing['pyListContext']=='.Items' and listing['pyNumberOfAppearances']==appearance,'List context and appearance')
    exact='12345678901234567890.1234567890123456789'
    decimal=helper_block(dict(a,mode='Decimal',comparator='Is Equals To',value=exact),binding);raw=p.json_text(decimal)
    p.b.require(exact in raw and json.loads(raw,parse_float=Decimal)['pyExpectedResults'][0]['pyExpectedValue']==Decimal(exact),'decimal precision')
    seeds={};p.put_seed(seeds,p.path_tokens('.Items(2).Value'),'second');p.put_seed(seeds,p.path_tokens('.Items(1).Value'),'first');p.put_seed(seeds,p.path_tokens('.Groups(Key).Amount'),Decimal('1.2'));p.check_holes(seeds)
    p.b.require(seeds=={'Items':[{'Value':'first'},{'Value':'second'}],'Groups':{'Key':{'Amount':Decimal('1.2')}}},'seed path projection')
    rejected(lambda:p.put_seed(seeds,p.path_tokens('.Items(1).Value'),'changed'))
    missing={};p.put_seed(missing,p.path_tokens('.Items(2).Value'),'x');rejected(lambda:p.check_holes(missing))
    # Typed simulation wrapper and supplemental context seeds are direct frozen
    # projection vectors, not claims about re-executing the historical RUT.
    sim_source=read_source(FIXTURES/'standard-escaping.sgl')
    sim=next(r['values'] for r in sim_source['records'] if r['tag']=='SIM')
    payload={'pxObjClass':'Code-Pega-List','pxResults':[{'pxObjClass':'App-Data-Item','Amount':7}]}
    sim.update(shape='list',itemClass='App-Data-Item',payload=p.sg.canonical(payload),setupPages=p.sg.canonical([{'pySetupPageName':'PrimaryPage','pyPageDetails':[]},{'pySetupPageName':'ContextPage','pyPageDetails':[{'path':'.Locale','valueType':'string','value':'nl_NL'}]}]))
    sim_source['profiles']['S1']['simulationItemPaths']['M001']='.pxResults'
    out=p.simulations(sim_source,'S1')[0]
    Draft202012Validator({'$ref':'#/$defs/SimulationRule','$defs':standard['$defs']}).validate(out)
    p.b.require(out['pySetupPages'][0]['pyPageDetails']==payload and out['pySetupPages'][1]['pyPageDetails']=={'Locale':'nl_NL'},'list wrapper/supplemental path preservation')
    original=sim['payload'];sim['payload']=p.sg.canonical(['naked array']);rejected(lambda:p.simulations(sim_source,'S1'));sim['payload']=original
    vector=read_source(FIXTURES/'when-no-simulation.sgl')
    next(r['values'] for r in vector['records'] if r['tag']=='ASSERT' and r['values']['kind']=='DecisionInput')['value']='<EMPTY>'
    row=p.when_row(vector,'S1');when_schema=json.loads(cache_for('Rule-Obj-When')['Rule-Test-Unit-Case_MultInpComb-JsonSchema'])
    Draft202012Validator({'$ref':'#/$defs/MultiInputCombinationRow','$defs':when_schema['$defs']}).validate(row)
    p.b.require('pyExpectedValue' not in row['pyExpectedResults'][0] and row['pyExpectedResults'][-1]['pyExpectedValue']=='true','empty cell and Result placement')
    param=p.rut_parameters(read_source(FIXTURES/'when-formal-parameter.sgl'),'S1',True)
    p.b.require(param==[{'pyParametersParamName':'Amount','pyParametersParamType':'Decimal'}],'When formal declaration retains type without fixed row override')
    return 22


def main():
    passed=0;mutations=0;outputs={}
    for path in sorted(FIXTURES.glob('*.sgl')):
        source=read_source(path);current=retained(source)
        if not current['scenarios']:
            p.b.require(path.name=='standard-not-testable.sgl' and source['scenarios'][0]['rejection']=='SOURCE_NO_ASSERTIONS','explicit source rejection');continue
        cache=cache_for(source['header']['rutType']);raw=p.candidate([current],cache)
        value=json.loads(raw,parse_float=Decimal);audit(value,[current],cache);passed+=1
        outputs[path.stem]=value
        probes=[]
        for mutate in [lambda d:d['UnitTestRules'][0]['Scenarios'][0]['EvidenceSummary'].update(AssertionCount=999),lambda d:d['UnitTestRules'][0]['RuleCode']['pyRuleUnderTest']['pyDetails'].update(pyRuleUnderTestType='Other'),lambda d:d['UnitTestRules'][0]['Scenarios'][0]['EvidenceSummary'].update(AssertionDecisionTrace='OMIT|id=O999'),lambda d:d['UnitTestRules'][0]['RuleCode'].update(MemoryTemp='forbidden')]:
            copy=deepcopy(value);mutate(copy);probes.append(copy)
        for copy in probes:rejected(lambda:audit(copy,[current],cache));mutations+=1
    # Two physical When groups remain ordered; one unsupported source Scenario is explicit.
    a=read_source(FIXTURES/'when-key-a.sgl');b=read_source(FIXTURES/'when-key-b.sgl')
    p.b.require(a['scenarios'][0]['rejection']=='SOURCE_WHEN_NON_CELL_ASSERTION','non-cell When rejection scope')
    current=[retained(a),retained(b)];cache=cache_for(a['header']['rutType']);value=json.loads(p.candidate(current,cache),parse_float=Decimal);audit(value,current,cache);passed+=1
    reversed_value=deepcopy(value);reversed_value['UnitTestRules'].reverse();rejected(lambda:audit(reversed_value,current,cache));mutations+=1
    for path in [FIXTURES/'when-no-simulation.sgl',FIXTURES/'standard-escaping.sgl']:
        raw=path.read_text();h=p.b.parse_line(raw.splitlines()[0],1)['values']
        for wrong in [('wrong',h['rutType'],int(h['groupOrder'])-1),(h['caseId'],'Other',int(h['groupOrder'])-1),(h['caseId'],h['rutType'],99)]:
            rejected(lambda:p.decode_source(raw,*wrong));mutations+=1
    full=read_source(FIXTURES/'when-two-rows.sgl');cache=cache_for(full['header']['rutType'])
    pruned=dict(full,scenarios=full['scenarios'][1:]);v=json.loads(p.candidate([pruned],cache),parse_float=Decimal);audit(v,[pruned],cache)
    p.b.require('row=1|' in v['UnitTestRules'][0]['Scenarios'][0]['EvidenceSummary']['AssertionDecisionTrace'] and 'row=2|' not in v['UnitTestRules'][0]['Scenarios'][0]['EvidenceSummary']['AssertionDecisionTrace'],'pruned trace row remapping');passed+=1
    helpers=semantic_helpers()
    # Original examples are illustrative; full validation is explicitly local evidence.
    for rut in ['Rule-Obj-Model','Rule-Obj-When']:
        cache=cache_for(rut);keys=protocol.knowledge_keys(rut);schema=json.loads(cache[keys[1]])
        Draft202012Validator.check_schema(schema);p.b.require(Draft202012Validator(schema).is_valid(json.loads(cache[keys[2]])),'original example full schema')
    print(f'PASS: S3 projection; full Draft202012Validator candidates={passed} schema_families=2 examples=2 helper_cases={helpers} mutations={mutations}')


if __name__=='__main__':
    try:main()
    except (p.b.ContractError,KeyError,TypeError,ValueError) as error:raise SystemExit('FAIL: '+str(error))
