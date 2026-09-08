"""Repository-static S4 producer oracle; injected tools, never a Pega implementation."""
from copy import deepcopy
from decimal import Decimal
import json
import re

from generator_protocol import CODE_ACTIONS, ROUTES, issue_route, memory_output, knowledge_keys, knowledge_cache
from validate_s2_design import ContractError, TRACE_FIELDS, OMIT_REASONS, require

STRING_MODES = {'Text','String','Identifier','Password','TextEncrypted','DateTime','Date','TimeOfDay'}
NO_VALUE = {'Exists', 'Not exists', 'Is Empty', 'Is Not Empty', 'has errors', 'has no errors'}
RESERVED = {'pxProcess','AccessGroup','Application','OperatorID','Org','OrgDivision','pxRequestor','pxThread'}
SCHEMA_ERRORS = {'INVALID_INPUT','NOT_FOUND','ADDRESS_MISMATCH','READ_FAILED','VALIDATION_FAILED'}
TOOL_FAILURE_TEXT = ('Execution of intent JsonValidationTool has failed','Required parameters','cannot be blank')


def parse_json(raw):
    def pairs(items):
        result = {}
        for k, v in items:
            require(k not in result, 'duplicate JSON key'); result[k] = v
        return result
    def invalid(value):
        raise ContractError('non-finite JSON')
    require(isinstance(raw, str), 'JSON text required')
    try:
        return json.loads(raw, object_pairs_hook=pairs, parse_float=Decimal, parse_constant=invalid)
    except (ValueError, TypeError) as error:
        raise ContractError('unreadable JSON') from error


def issue(code, action=None, u=None, s=None, decision='', path=None, message=None, severity='B'):
    if action is None:
        require(len(CODE_ACTIONS[code]) == 1, 'explicit action required')
        action = next(iter(CODE_ACTIONS[code]))
    require(action in CODE_ACTIONS[code], 'closed action')
    if path is None:
        path = '/' if u is None else '/UnitTestRules/'+str(u)+(('/Scenarios/'+str(s)) if s is not None else '')
    return dict(code=code,severity=severity,path=path,unit=u,scenario=s,decision=decision,action=action,message=(message or code.replace('_',' ').capitalize()+'.')[:240])


def report(issues=(), schema_valid=True, message=''):
    unique = []
    for item in issues:
        if item not in unique: unique.append(item)
    blocking = sum(i['severity']=='B' for i in unique)
    routes = [issue_route(i['action']) for i in unique if i['severity']=='B']
    return dict(valid=blocking==0,route=max(routes,key=ROUTES.index) if routes else 'OK',blocking=blocking,warnings=len(unique)-blocking,jsonSchemaValidation=dict(isValid=schema_valid,message=message),issues=unique)


def schema_result(value):
    require(isinstance(value,dict) and {'Success','IsValid','ValidationMessage','ErrorCode','ErrorMessage'} <= set(value), 'schema envelope')
    require(type(value['Success']) is bool and type(value['IsValid']) is bool and all(isinstance(value[k],str) for k in ('ValidationMessage','ErrorCode','ErrorMessage')), 'schema field types')
    require(not any(phrase in value['ValidationMessage'] or phrase in value['ErrorMessage'] for phrase in TOOL_FAILURE_TEXT), 'schema invocation failure')
    if not value['Success']:
        require(value['IsValid'] is False and value['ValidationMessage']=='' and value['ErrorCode'] in SCHEMA_ERRORS and value['ErrorMessage']!='', 'schema failure envelope')
        raise ContractError('schema tool failed')
    require(value['ErrorCode']==value['ErrorMessage']=='', 'schema success errors')
    require((value['ValidationMessage']=='') == value['IsValid'], 'schema validity/message contradiction')
    return value['IsValid'], value['ValidationMessage']


def mass_failure(message):
    if len(message)>2000: return True
    # Counts must be diagnostic statements, never echoed quoted field values.
    counts = re.findall(r'^\s*(?:(?:there (?:are|were)|found|total:?|(?:schema |JsonValidationTool )?validation (?:failed with|reported))\s+)?(\d+)\s+(?:schema\s+)?errors?\b',message,re.I|re.M)
    counts += re.findall(r'^\s*(?:number of\s+)?(?:schema\s+)?errors?\s*[:=]\s*(\d+)\b',message,re.I|re.M)
    if any(int(n)>=25 for n in counts): return True
    lines = [x for x in message.splitlines() if re.match(r'^\s*(?:\d+[.)]\s+|(?:[-*]\s+)?/UnitTestRules(?:/[^:\s]+)*\s*:)',x)]
    if len(lines)>=25: return True
    # Only named root/container diagnostics, not isolated fields or numbers in values.
    container=r'(?:/|/UnitTestRules(?:/\d+(?:/Scenarios(?:/\d+(?:/EvidenceSummary)?)?|/EvidenceSummary|/RuleCode)?)?)'
    return bool(re.search(r'(?:^|\n)\s*'+container+r'\s*:\s*(?:must be (?:an? )?(?:object|array)|expected (?:object|array)|broadly malformed)',message,re.I))


def candidate_view(value):
    """Guard only nodes traversed by the inspection pass, not schema keywords."""
    def object_list(parent,key,required=False):
        if key not in parent:
            require(not required,'candidate container unavailable');return []
        items=parent[key]
        require(isinstance(items,list) and all(isinstance(x,dict) for x in items),'candidate node unavailable')
        return items
    def assertions(parent,required=False):
        for block in object_list(parent,'pyExpectedResults',required):
            assertions(block)
    require(isinstance(value,dict),'candidate root unavailable')
    units=object_list(value,'UnitTestRules',True);require(units,'candidate root unavailable')
    for unit in units:
        require(isinstance(unit.get('RuleCode'),dict),'candidate code unavailable');code=unit['RuleCode']
        scenarios=object_list(unit,'Scenarios',True);require(scenarios,'candidate Scenario unavailable')
        for scenario in scenarios:require(isinstance(scenario.get('EvidenceSummary'),dict),'candidate evidence unavailable')
        require(isinstance(code.get('pyRuleUnderTest'),dict),'candidate RUT unavailable')
        rut=code['pyRuleUnderTest']
        if 'pyDetails' in rut:require(isinstance(rut['pyDetails'],dict),'candidate details unavailable')
        assertions(code,True)
        object_list(code,'pyPagesAndClasses');object_list(code,'pySetupPages');object_list(rut,'pyParameters')
        for sim in object_list(code,'pySimulation'):object_list(sim,'pySetupPages')
        for key in ('pySetup','pyCleanup'):
            for action in object_list(code,key):object_list(action,'pyParameters')
    return value


def run(case_id,rut_type,uuid,tools,inspect=None,caller_schema=None):
    """One schema/read/Knowledge sequence; caller_schema is deliberately ignored."""
    failure=lambda:report([issue('JSON_VALIDATION_TOOL_ERROR')],False,'Schema validation could not be completed.')
    if not all(isinstance(x,str) and x!='' for x in (case_id,rut_type,uuid)) or not rut_type.strip(): return failure()
    schema='Rule-Test-Unit-Case_'+('MultInpComb-' if rut_type=='Rule-Obj-When' else '')+'JsonSchema'
    try:
        valid,message=schema_result(tools('JsonValidationTool',dict(CaseID=case_id,UUID=uuid,JsonSchema=schema)))
    except Exception:
        return failure()
    if not valid:
        mass=mass_failure(message)
        return report([issue('JSON_SCHEMA_MASS_FAILURE' if mass else 'JSON_SCHEMA_INVALID')],False,'Candidate has broad or numerous schema defects; rebuild projection from unchanged evidence.' if mass else message)
    try:
        raw=memory_output(tools('GetMemory',dict(CaseID=case_id,Type='UnitTestCandidate',UUID=uuid)),'read')
        candidate=candidate_view(parse_json(raw))
    except Exception:
        return report([issue('MEMORY_READ_TOOL_ERROR',message='GetMemory could not return the exact candidate.')])
    mismatches=[]
    for u,unit in enumerate(candidate['UnitTestRules']):
        rut=unit['RuleCode']['pyRuleUnderTest'];details=rut.get('pyDetails',{})
        found=details.get('pyRuleUnderTestType') if isinstance(details,dict) else None
        if found is None: found=rut.get('pyRuleUnderTestType')
        if not isinstance(found,str) or not found: return report([issue('MEMORY_READ_TOOL_ERROR')])
        if found!=rut_type:
            mismatches.append(issue('RUT_TYPE_MISMATCH',u=u,path=f'/UnitTestRules/{u}/RuleCode/pyRuleUnderTest'))
    if mismatches: return report(mismatches)
    try:
        keys=knowledge_keys(rut_type)
        cache=knowledge_cache(tools('KnowledgeTool',dict(KnowledgeAreas=','.join(keys))),keys)
    except Exception:
        return report([issue('AMBIGUOUS',message='Required UTC documentation is unavailable.')])
    before=deepcopy(candidate)
    try:
        issues=(inspect or inspect_candidate)(candidate,rut_type,cache)
        require(candidate==before,'Validator mutated candidate')
        return report(issues)
    except Exception:
        return report([issue('AMBIGUOUS',message='Candidate checks could not be completed safely.')])


ENTITIES={'&amp;':'&','&quot;':'"','&#124;':'|','&#13;':'\r','&#10;':'\n'}


def decode_field(text):
    return re.sub(r'&amp;|&quot;|&#124;|&#13;|&#10;',lambda m:ENTITIES[m[0]],text)


def parse_trace(text):
    require(isinstance(text,str) and text.strip()!='','trace missing')
    output=[];ids=set()
    for line in text.split('\n'):
        if not line: continue
        pieces=line.split('|');tag=pieces[0]
        pairs=[piece.split('=',1) for piece in pieces[1:]]
        require(all(len(p)==2 for p in pairs),'trace framing')
        fields=dict(pairs)
        schema='ASSERT_DEC' if tag=='ASSERT' and fields.get('kind') in {'DecisionInput','DecisionResult'} else 'ASSERT_STD' if tag=='ASSERT' else tag
        require(schema in TRACE_FIELDS and tuple(p[0] for p in pairs)==TRACE_FIELDS[schema],'trace grammar')
        fields={k:decode_field(v) for k,v in pairs}
        require(fields['id'] and fields['id'] not in ids,'trace ID');ids.add(fields['id'])
        if tag=='ASSERT':
            require(fields['kind'] in {'Property','Page','List','ResultCount','DecisionInput','DecisionResult'},'assert kind')
            require(fields['support'] in {'Verified','PredictedFromRules','Structural'},'assert support')
        elif tag=='OMIT': require(fields['reason'] in OMIT_REASONS,'omission reason')
        else:
            require(fields['sig'] not in {'','-'} and fields['shape'] in {'page','list'},'simulation identity')
            require(isinstance(parse_json(fields['params']),dict),'simulation params')
            require(fields['shape']!='list' or fields['itemClass'] not in {'','-'},'list item class')
        output.append(dict(tag=tag,**fields))
    require(output,'trace missing');return output


def path(page,target,canonicalize=False):
    if target.startswith('Param.') or not target.startswith('.'): return target,False
    suffix=target[1:];duplicate=False
    if canonicalize and suffix.split('.',1)[0]==page.rsplit('.',1)[-1]:
        suffix=suffix.split('.',1)[1] if '.' in suffix else '';duplicate=True
    return page+('.'+suffix if suffix else ''),duplicate


def value_equal(trace,value,cell=False,mode=None):
    if cell: return isinstance(value,str) and trace==value
    # Explicit scalar boolean/string constraints precede legacy normalization.
    # Other hidden typed source facts (including arrays/null) remain Generator-owned.
    if mode in STRING_MODES and type(value) is bool:return False
    if mode=='TrueFalse' and type(value) is not bool:return False
    if isinstance(value,str):
        if trace.strip()==value.strip():return True
        # Only an unmatched value may use one legacy JSON-string layer.
        try:
            decoded=parse_json(value)
            if isinstance(decoded,str): value=decoded
        except ContractError: pass
        return trace.strip()==value.strip()
    try:
        expected=parse_json(trace)
    except ContractError: return False
    def same(a,b):
        if isinstance(a,bool) or isinstance(b,bool):return type(a) is type(b) and a==b
        if isinstance(a,(int,Decimal)) and isinstance(b,(int,Decimal)):return Decimal(a)==Decimal(b)
        if type(a) is not type(b):return False
        if isinstance(a,list):return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
        if isinstance(a,dict):return set(a)==set(b) and all(same(a[k],b[k]) for k in a)
        return a==b
    return same(expected,value)


def physical_assertions(code):
    result=[]
    for bi,block in enumerate(code['pyExpectedResults']):
        kind=block.get('pyAssertionType');page=block.get('pyStepPageName','')
        if kind=='ResultCount':
            target,_=path(page,block.get('pyListContext',''))
            result.append(dict(kind=kind,target=target,comparator=block.get('pyComparator'),item=block,block=block,index=bi))
        elif kind!='Decision':
            for child in block.get('pyExpectedResults',[]):
                target,_=path(page,child.get('pyPropertyAbsolutePath',''))
                result.append(dict(kind=kind,target=target,comparator=child.get('pyComparator'),item=child,block=block,index=bi))
    return result



def final_decisions(code,trace,u,s,when):
    """Only explicit contradictions; no branch/expected-value inference."""
    items=[t for t in trace if t['tag']=='ASSERT'];out=[]
    physical=[] if when else physical_assertions(code)
    def target(a):
        if when:return a['target']
        raw,_=path(a['page'],a['target']);canonical,_=path(a['page'],a['target'],True)
        return raw if any(x['target']==raw for x in physical) else canonical
    def add(a,message):out.append(issue('REASONING_CONTRADICTION',u=u,s=s,decision=a['id'],message=message))
    if not when:
        for a in items:
            if a['comparator'] in NO_VALUE:continue
            invalid_boolean=a['mode']=='TrueFalse' and (a['value'] not in {'true','false'} or a['comparator']!=('Is True' if a['value']=='true' else 'Is False'))
            invalid_text=a['mode'] in STRING_MODES and a['comparator'] in {'Is True','Is False'}
            if invalid_boolean or invalid_text:
                out.append(issue('TRACE_INVALID','REJECT_SEMANTICS',u,s,a['id'],message='Final scalar type and comparator contradict each other; projection cannot choose a new decision.'))
    for omit in [t for t in trace if t['tag']=='OMIT']:
        omitted=omit['target'] if when else path(code.get('pyPrimaryPageForRUT',''),omit['target'])[0]
        for a in items:
            if target(a)==omitted:add(a,'Final ASSERT and OMIT contradict each other; no projection repair may choose a decision.')
    opposites=[{'Exists','Not exists'},{'Is Empty','Is Not Empty'},{'has errors','has no errors'},{'Is True','Is False'}]
    for i,a in enumerate(items):
        for other in items[i+1:]:
            if target(a)!=target(other) or a['kind']!=other['kind']:continue
            if {a['comparator'],other['comparator']} in opposites:
                add(a,'Final decisions assert mutually exclusive states of the same target.')
            elif a['comparator']==other['comparator'] and a['comparator'] in {'Is Equals To','Input Value'}:
                def family(t):
                    if t['kind']=='ResultCount' or t['mode'] in {'Integer','Decimal','Double'}:return 'number'
                    return 'boolean' if t['mode']=='TrueFalse' else 'text'
                left_family,right_family=family(a),family(other)
                equal=a['value']==other['value']
                if not when:
                    if left_family!=right_family:equal=False
                    elif left_family=='number' and not equal:
                        try:
                            left,right=parse_json(a['value']),parse_json(other['value'])
                            equal=all(isinstance(x,(int,Decimal)) and not isinstance(x,bool) for x in (left,right)) and Decimal(left)==Decimal(right)
                        except ContractError:equal=False
                if not equal:add(a,'Final decisions assign incompatible exact values or types to the same target.')
    return out

def assertions(code,trace,u,s):
    issues=[];actual=physical_assertions(code);used=set()
    for a in [t for t in trace if t['tag']=='ASSERT']:
        raw_target,_=path(a['page'],a['target'])
        target,duplicate=path(a['page'],a['target'],True)
        if any(x['target']==raw_target for x in actual):
            target,duplicate=raw_target,False
        same_target=[i for i,x in enumerate(actual) if i not in used and x['target']==target]
        exact=[i for i in same_target if actual[i]['kind']==a['kind'] and actual[i]['comparator']==a['comparator']]
        if not same_target:
            issues.append(issue('ASSERT_MISSING',u=u,s=s,decision=a['id']));continue
        i=next((i for i in exact if ('pyExpectedValue' not in actual[i]['item'] if a['comparator'] in NO_VALUE else 'pyExpectedValue' in actual[i]['item'] and value_equal(a['value'],actual[i]['item']['pyExpectedValue'],mode=a['mode']))),exact[0] if exact else same_target[0])
        used.add(i);x=actual[i];child=x['item']
        if duplicate:issues.append(issue('TRACE_PATH_CANONICALIZATION_NEEDED',u=u,s=s,decision=a['id']))
        if x['kind']!=a['kind']:issues.append(issue('ASSERT_BLOCK_INVALID',u=u,s=s,decision=a['id']))
        elif x['comparator']!=a['comparator']:issues.append(issue('ASSERT_VALUE_MISMATCH',u=u,s=s,decision=a['id']))
        elif a['comparator'] in NO_VALUE:
            if 'pyExpectedValue' in child:issues.append(issue('ASSERT_VALUE_MISMATCH',u=u,s=s,decision=a['id']))
        elif 'pyExpectedValue' not in child or not value_equal(a['value'],child['pyExpectedValue'],mode=a['mode']):issues.append(issue('ASSERT_VALUE_MISMATCH',u=u,s=s,decision=a['id']))
        if target.startswith('Param.'):
            if child.get('pyPropertyName')!=target or child.get('pyPropertyAbsolutePath')!=target or child.get('pyPropertyMode')!='Text' or any(k in child for k in ('pyPageName','pyParentPropertyMode','pyPropertyRealName')):
                issues.append(issue('DOC_PARAM_ASSERTION_SHAPE_INVALID',u=u,s=s,decision=a['id']))
        elif child.get('pyPropertyName','').startswith('Param.'):
            issues.append(issue('DOC_REGULAR_ASSERTION_USES_PARAM_PATH',u=u,s=s,decision=a['id']))
        elif a['kind'] in {'Property','List'}:
            if child.get('pyPageName')!=a['page'] or child.get('pyPropertyApplyToClass')!=a['class'] or child.get('pyPropertyMode')!=a['mode']:
                issues.append(issue('DOC_ASSERTION_BLOCK_KIND_MISMATCH',u=u,s=s,decision=a['id']))
        classes={entry.get('pyPagesAndClassesPage'):entry.get('pyPagesAndClassesClass') for entry in code.get('pyPagesAndClasses',[])}
        classes.setdefault(code.get('pyPrimaryPageForRUT'),code.get('pyClassName'))
        step=x['block'].get('pyStepPageName')
        if step in classes and x['block'].get('pyStepPageClass')!=classes[step]:
            issues.append(issue('DOC_ASSERTION_BLOCK_KIND_MISMATCH',u=u,s=s,decision=a['id']))
    for i in set(range(len(actual)))-used:issues.append(issue('ASSERT_EXTRA',u=u,s=s))
    for omit in [t for t in trace if t['tag']=='OMIT']:
        target,_=path(code.get('pyPrimaryPageForRUT',''),omit['target'])
        if any(x['target']==target for x in actual):issues.append(issue('OMIT_ASSERTED',u=u,s=s,decision=omit['id']))
    return issues


def simulations(code,traces,u,when):
    result=[];actual=code.get('pySimulation',[]);base=None
    for s,trace in enumerate(traces):
        if trace is None:continue
        sims=[t for t in trace if t['tag']=='SIM']
        identity=[{k:v for k,v in t.items() if k not in {'id','tag'}} for t in sims]
        if when and base is not None and identity!=base:
            result.append(issue('TRACE_INVALID','REJECT_SEMANTICS',u,path=f'/UnitTestRules/{u}/RuleCode/pySimulation',message='Shared When SIM identities, including sig/params, conflict.'))
        if base is None:base=identity
        scope=None if when else s
        def add(code_,action=None,decision='',message=None):
            result.append(issue(code_,action,u,scope,'' if when else decision,path=f'/UnitTestRules/{u}/RuleCode/pySimulation',message=message))
        matched=set();names=set()
        for t in sims:
            if t['rule'] in names:add('TRACE_INVALID','REJECT_SEMANTICS',t['id']);continue
            names.add(t['rule'])
            indices=[i for i,x in enumerate(actual) if x.get('pyRuleNameToBeMocked')==t['rule']]
            if not indices:
                action_load=any(x.get('pyActionType')=='LoadDataPage' and x.get('pyActionName')==t['rule'] for x in code.get('pySetup',[]))
                add('DOC_DATAPAGE_IN_SETUP' if action_load else 'SIM_MISSING',decision=t['id']);continue
            if len(indices)!=1:add('SIM_SHAPE_INVALID',decision=t['id']);continue
            i=indices[0];matched.add(i);x=actual[i]
            if x.get('pyClassName')!=t['class']:add('SIM_SHAPE_INVALID',decision=t['id'])
            if x.get('pySimulationMethod')!=t['method'] or t['method']!='DefineData':add('DOC_SIMULATION_METHOD_INVALID',decision=t['id'])
            if x.get('pyMockingSupportedRuleTypes')!='Rule-Declare-Pages':add('DOC_DATAPAGE_RULETYPE_INVALID',decision=t['id'])
            if any(y.get('pyActionType')=='LoadDataPage' and y.get('pyActionName')==t['rule'] for y in code.get('pySetup',[])):add('DOC_DATAPAGE_IN_SETUP',decision=t['id'])
            pages=x.get('pySetupPages',[])
            if not pages or len({p.get('pySetupPageName') for p in pages})!=len(pages):add('SIM_SHAPE_INVALID',decision=t['id'])
            if t['shape']=='list':
                def arrays(value):
                    if isinstance(value,list):yield value
                    if isinstance(value,dict):
                        for item in value.values():yield from arrays(item)
                wrappers=[p.get('pyPageDetails') for p in pages if isinstance(p.get('pyPageDetails'),dict)]
                collections=[a for wrapper in wrappers if wrapper.get('pxObjClass') for a in arrays(wrapper)]
                if not collections:add('DOC_LIST_SIMULATION_WRAPPER_MISSING',decision=t['id'])
                # Only a unique observable collection can identify item-class alignment.
                elif len(collections)==1 and any(not isinstance(item,dict) or item.get('pxObjClass')!=t['itemClass'] for item in collections[0]):add('SIM_SHAPE_INVALID',decision=t['id'])
        if len(matched)!=len(actual):add('SIM_SHAPE_INVALID',message='Physical simulation has no unique final SIM decision.')
    return result


def when_alignment(unit,traces,u,conflicted=()):
    code=unit['RuleCode'];out=[];blocks=code['pyExpectedResults'];prefix=f'/UnitTestRules/{u}/RuleCode/pyExpectedResults'
    def group(code_,action=None,message=None):out.append(issue(code_,action,u,path=prefix,message=message))
    if len(blocks)!=1 or blocks[0].get('pyAssertionType')!='Decision':
        group('DOC_ASSERTION_BLOCK_KIND_MISMATCH');return out
    block=blocks[0];rows=block.get('pyExpectedResults',[])
    if len(rows)!=len(unit['Scenarios']):group('COUNT_MISMATCH')
    if block.get('pyAllowMultipleInputCombinations')!='true' or block.get('pyPropertyType')!='Decision Result' or block.get('pyClassContext')!=code['pyRuleUnderTest']['pyDetails']['pyRuleUnderTestObjClass']:group('DOC_ASSERTION_BLOCK_KIND_MISMATCH')
    sig=None;trace_columns=None
    mocks={m.get('pyRuleNameToBeMocked') for m in code.get('pySimulation',[])}
    for s,row in enumerate(rows):
        cells=row.get('pyExpectedResults',[])
        signature=[tuple(c.get(k) for k in ('pyPropertyType','pyPropertyName','pyPropertyAbsolutePath','pyDisplayLabel')) for c in cells]
        if sig is not None and signature!=sig:group('DOC_ASSERTION_BLOCK_KIND_MISMATCH',message='Keep identical input cells in every row; omit only pyExpectedValue for empty input.')
        sig=signature if sig is None else sig
        if not cells or [c.get('pyPropertyType') for c in cells]!=['input']*(len(cells)-1)+['result']:group('DOC_ASSERTION_BLOCK_KIND_MISMATCH')
        if s>=len(traces) or traces[s] is None or s in conflicted:continue
        loc=f'{prefix}/0/pyExpectedResults/{s}'
        def add(code_,action=None,decision='',message=None):out.append(issue(code_,action,u,s,decision,loc,message))
        decisions=[t for t in traces[s] if t['tag']=='ASSERT']
        if row.get('pyPageName')!='rowLevelPage':add('DOC_ASSERTION_BLOCK_KIND_MISMATCH')
        columns=[tuple(a[k] for k in ('kind','target','page','class','mode','comparator')) for a in decisions]
        complete_columns=len(decisions)==len(cells) and all(a['target']==c.get('pyPropertyAbsolutePath') for a,c in zip(decisions,cells))
        if complete_columns and trace_columns is not None and len(columns)==len(trace_columns) and columns!=trace_columns:
            group('TRACE_INVALID','REJECT_SEMANTICS','Shared When trace column context conflicts; preserve original column facts.')
        if complete_columns and trace_columns is None:trace_columns=columns
        if any(page_root(a['target']) in mocks for a in decisions if a['kind']=='DecisionInput') or any(page_root(c.get('pyPropertyAbsolutePath','')) in mocks for c in cells if c.get('pyPropertyType')=='input'):
            group('REASONING_CONTRADICTION',message='Shared When signature uses a simulated DP as writable input.')
        for omit in [t for t in traces[s] if t['tag']=='OMIT']:
            if any(c.get('pyPropertyAbsolutePath')==omit['target'] for c in cells):add('OMIT_ASSERTED',decision=omit['id'])
        if len(decisions)<len(cells):add('TRACE_INVALID','REJECT_SEMANTICS',message='A physical cell lacks a final decision; do not invent it.')
        if len(decisions)>len(cells):add('ASSERT_MISSING',decision=decisions[-1]['id'])
        for pos,(a,c) in enumerate(zip(decisions,cells)):
            result=pos==len(cells)-1
            if a['kind']!=('DecisionResult' if result else 'DecisionInput'):add('TRACE_INVALID','REJECT_SEMANTICS',a['id'])
            if a.get('row')!=str(s+1):add('TRACE_INVALID','FIX_TRACE',a['id'])
            if a['page']!='rowLevelPage' or (result and (a['class']!=code['pyRuleUnderTest']['pyDetails']['pyRuleUnderTestObjClass'] or a['mode']!='text')) or (not result and (a['class'] in {'','-'} or a['mode'] in {'','-'})):
                add('TRACE_INVALID','REJECT_SEMANTICS',a['id'])
            if a['target']!=c.get('pyPropertyAbsolutePath'):add('ASSERT_VALUE_MISMATCH',decision=a['id'])
            if a['value']=='<EMPTY>' and not result:
                if 'pyExpectedValue' in c:add('ASSERT_VALUE_MISMATCH',decision=a['id'])
            elif 'pyExpectedValue' not in c or not value_equal(a['value'],c['pyExpectedValue'],True):add('ASSERT_VALUE_MISMATCH',decision=a['id'])
            if c.get('pyPropertyName')!=c.get('pyPropertyAbsolutePath') or c.get('pyDisplayLabel')!=c.get('pyPropertyAbsolutePath') or c.get('pyPropertyMode')!='text':add('DOC_ASSERTION_BLOCK_KIND_MISMATCH',decision=a['id'])
            if result and (a['target']!='Result' or a['comparator']!='Is Equals To' or a['value'] not in {'true','false'}):add('TRACE_INVALID','REJECT_SEMANTICS',a['id'])
            if not result and a['comparator']!='Input Value':add('TRACE_INVALID','REJECT_SEMANTICS',a['id'])
            if reserved(c.get('pyPropertyAbsolutePath','')):add('DOC_RESERVED_SYSTEM_PAGE_SEED',decision=a['id'])

    return out


def page_root(name):
    if not isinstance(name,str) or name.startswith('.'):return None
    return re.split(r'[.\[(]',name,1)[0]


def reserved(name):
    return page_root(name) in RESERVED


def visible_pages(code):
    yield code.get('pyPrimaryPageForRUT','')
    for p in code.get('pyPagesAndClasses',[]):yield p.get('pyPagesAndClassesPage','')
    for p in code.get('pySetupPages',[]):yield p.get('pySetupPageName','')
    for p in code.get('pySimulation',[]):
        for page in p.get('pySetupPages',[]):yield page.get('pySetupPageName','')
    for action in code.get('pySetup',[])+code.get('pyCleanup',[]):
        yield action.get('pyTargetPage','')
        for p in action.get('pyParameters',[]):
            if p.get('pyParametersParamType')=='PAGE':yield p.get('pyParametersParamValue','')
    for p in code['pyRuleUnderTest'].get('pyParameters',[]):
        if p.get('pyParametersParamType')=='PAGE':yield p.get('pyParametersParamValue','')


def inspect_candidate(candidate,rut_type,cache):
    """Executable visible checks; free-text UTC reasoning is a prompt/reviewer obligation."""
    out=[];when=rut_type=='Rule-Obj-When'
    for u,unit in enumerate(candidate['UnitTestRules']):
        code=unit['RuleCode'];traces=[];conflicted=set()
        if not when and len(unit['Scenarios'])!=1:out.append(issue('COUNT_MISMATCH',u=u))
        for s,scenario in enumerate(unit['Scenarios']):
            evidence=scenario['EvidenceSummary'];raw=evidence.get('AssertionDecisionTrace')
            if not isinstance(raw,str) or not raw.strip():
                out.append(issue('TRACE_MISSING',u=u,s=s));traces.append(None);continue
            try:trace=parse_trace(raw)
            except ContractError:
                out.append(issue('TRACE_INVALID','REJECT_SEMANTICS',u,s));traces.append(None);continue
            traces.append(trace)
            conflicts=final_decisions(code,trace,u,s,when);out.extend(conflicts)
            if conflicts:conflicted.add(s)
            assertions_=[t for t in trace if t['tag']=='ASSERT'];sims=[t for t in trace if t['tag']=='SIM'];omits=[t for t in trace if t['tag']=='OMIT']
            for a in assertions_:
                exact=a['comparator'] not in NO_VALUE and a['kind']!='ResultCount' and not (a['kind']=='DecisionInput' and a['value']=='<EMPTY>')
                if exact and a['support']=='Structural':out.append(issue('TRACE_INVALID','REJECT_SEMANTICS',u,s,a['id']))
            exact_count=sum(a['comparator'] not in NO_VALUE and a['kind']!='ResultCount' for a in assertions_)
            counts=dict(AssertionCount=len(assertions_),ExactValueAssertionCount=exact_count,StructuralAssertionCount=len(assertions_)-exact_count,OmittedClaimCount=len(omits),SimulatedDependencyCount=len(sims))
            if any(evidence.get(k)!=v for k,v in counts.items()):out.append(issue('COUNT_MISMATCH',u=u,s=s))
            prose=' '.join(str(evidence.get(k,'')) for k in ('ReasoningTrace','BlockingGaps','DependencyClosureTrace'))
            # Bounded contradiction fixtures; arbitrary narrative interpretation stays with agent review.
            if re.search(r'IsInPageListWhen.*(?:blocked|unresolved).*only.*(?:absent|missing|not (?:in|present)).*pxRuleReferences',prose,re.I):out.append(issue('REASONING_CONTRADICTION',u=u,s=s,message='IsInPageListWhen string names are synthetic dependencies; missing pxRuleReferences is not a valid blocker.'))
            if when and any(a['kind']=='DecisionInput' and a['value']=='<EMPTY>' for a in assertions_) and re.search(r'(?:omitted|empty).*value.*means.*(?:parent|page|list).*absen',prose,re.I):out.append(issue('REASONING_CONTRADICTION',u=u,s=s))
            if re.search(r'candidate claim.*no final (?:ASSERT|OMIT|decision)',prose,re.I):out.append(issue('DECISION_NOT_FINALIZED',u=u,s=s))
            if not when and s not in conflicted:out.extend(assertions(code,trace,u,s))
        out.extend(simulations(code,traces,u,when))
        if when:
            out.extend(when_alignment(unit,traces,u,conflicted))
            mocks={m.get('pyRuleNameToBeMocked') for m in code.get('pySimulation',[])}
            if any(page_root(p.get('pySetupPageName','')) in mocks for p in code.get('pySetupPages',[])):
                out.append(issue('REASONING_CONTRADICTION',u=u,path=f'/UnitTestRules/{u}/RuleCode/pySetupPages',message='A simulated DP cannot be an ordinary top-level setup seed.'))
        if any(reserved(page) for page in visible_pages(code)):out.append(issue('DOC_RESERVED_SYSTEM_PAGE_SEED',u=u,path=f'/UnitTestRules/{u}/RuleCode'))
        primary=code.get('pyPrimaryPageForRUT');classes={p.get('pyPagesAndClassesPage'):p.get('pyPagesAndClassesClass') for p in code.get('pyPagesAndClasses',[])}
        if primary in classes and classes[primary]!=code.get('pyClassName'):out.append(issue('AMBIGUOUS',u=u,path=f'/UnitTestRules/{u}/RuleCode',message='Primary page class contradicts Pages and Classes.'))
    return out
