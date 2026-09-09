"""Revision 1.4 frozen Data Page evidence checks; no Pega metadata inference.

The Author acquires expression results and execution facts. This module audits
their consistency and timing; it is not an interpreter of arbitrary RUT code.
"""
import json
import math

import validate_s2_design as b


def require(ok, message):
    b.require(ok, 'DP ' + message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def carrier(value):
    require(isinstance(value, dict) and set(value) == {'valueType', 'value'}, 'typed carrier keys')
    kind, raw = value['valueType'], value['value']
    require(kind in {'string', 'empty', 'null', 'boolean', 'number', 'absent'}, 'scalar input type')
    require(raw is None if kind == 'absent' else isinstance(raw, str), 'typed carrier representation')
    b.validate_typed(kind, raw, 'DP carrier')
    if kind == 'number':
        number = json.loads(raw)
        require(type(number) is int or math.isfinite(number), 'finite number')
    return value


def typed(entry):
    return carrier({k: entry[k] for k in ('valueType', 'value')})


ABSENT = {'valueType': 'absent', 'value': None}


def resolve(declaration, explicit, current):
    """Return resolved (carrier, mechanism, expression) facts and unknown names."""
    result, unresolved = {}, []
    for name in declaration['parameters']:
        if name in explicit:
            entry = explicit[name]
            value, mode, expression = typed(entry), 'explicit', entry['expression']
        elif current[name]['state'] == 'UNKNOWN':
            unresolved.append(name)
            continue
        elif current[name]['state'] == 'VALUE':
            value, mode, expression = typed(current[name]), 'inherited', 'Param.' + name
        elif name in declaration['defaults']:
            value, mode, expression = declaration['defaults'][name], 'default', None
        elif name in declaration['optional']:
            continue
        else:
            unresolved.append(name)
            continue
        if value['valueType'] == 'absent':
            unresolved.append(name)
        else:
            result[name] = (value, mode, expression)
    return result, unresolved


def validate(records):
    for scenario in (r['values'] for r in records if r['tag'] == 'SCENARIO'):
        rows = [r for r in records if r['values'].get('scenario') == scenario['id']]
        groups = {tag: {r['values']['id']: r['values'] for r in rows if r['tag'] == tag}
                  for tag in ('EVIDENCE', 'RX', 'PRODUCER', 'PARAM', 'SIM', 'BRANCH', 'GAP')}
        evidence = groups['EVIDENCE']

        def refs(value, excluded=None):
            require(isinstance(value, list) and value and all(isinstance(x, str) and x in evidence and x != excluded for x in value), 'evidence reference')
            require(len(value) == len(set(value)), 'duplicate evidence')
            return set(value)

        def snapshots(prefix, kind):
            out = {}
            for eid, e in evidence.items():
                if not e['source'].startswith(prefix):
                    continue
                require(e['kind'] == kind, prefix + ' evidence kind')
                key = e['source'][len(prefix):]
                require(key and key not in out, prefix + ' duplicate/empty source')
                out[key] = (eid, b.canonical_json(e['fact'], prefix))
            return out

        declarations = snapshots('DP_DECLARATION/', 'DEPENDENCY')
        accesses = snapshots('DP_ACCESS/', 'EXECUTION')
        executions = snapshots('DP_EXECUTION/', 'EXECUTION')
        initial = snapshots('DP_INITIAL/Param.', 'SEED')
        for rule, (eid, decl) in declarations.items():
            require(isinstance(decl, dict) and set(decl) == {'rule', 'scope', 'parameters', 'optional', 'defaults', 'evidence'}, 'declaration keys')
            require(decl['rule'] == rule and (decl['scope'] is None or isinstance(decl['scope'], str)), 'declaration identity/scope')
            refs(decl['evidence'], eid)
            names = decl['parameters']
            require(names is None or (isinstance(names, list) and all(isinstance(n, str) and n for n in names) and names == sorted(set(names))), 'declared input names')
            require(isinstance(decl['optional'], list) and all(isinstance(n, str) for n in decl['optional']) and decl['optional'] == sorted(set(decl['optional'])) and set(decl['optional']) <= set(names or []), 'optional declarations')
            require(isinstance(decl['defaults'], dict) and set(decl['defaults']) <= set(names or []), 'default declarations')
            for default in decl['defaults'].values():
                require(carrier(default)['valueType'] != 'absent', 'absent default')

        for rid, (_, execution) in executions.items():
            require(isinstance(execution, dict) and set(execution) == {'execution', 'status'} and execution['execution'] == rid and rid in groups['RX'], 'execution identity')
            status = execution['status']
            require(status in {'EXECUTED', 'NOT_EXECUTED', 'UNKNOWN'}, 'execution status')
            guard = groups['RX'][rid]['guard']
            result = groups['BRANCH'][guard]['result'] if guard else 'TRUE'
            require((status == 'NOT_EXECUTED') == (result == 'FALSE'), 'skipped effective guard')
            require(result != 'UNKNOWN' or status == 'UNKNOWN', 'unknown effective guard')
            require(status != 'EXECUTED' or result == 'TRUE', 'executed requires true or absent guard')

        relevant = set()
        for invocation, (eid, access) in accesses.items():
            require(isinstance(access, dict) and set(access) == {'rule', 'invocation', 'execution', 'declaration', 'status', 'explicit', 'current', 'parameters', 'simulation'}, 'access keys')
            require(access['invocation'] == invocation and access['rule'] in declarations, 'access identity')
            decl_id, decl = declarations[access['rule']]
            require(access['declaration'] == decl_id, 'access declaration identity')
            rid = access['execution']
            require(rid in executions and groups['RX'][rid]['source'] == invocation and executions[rid][1]['status'] == access['status'], 'access execution proof')
            require(isinstance(access['parameters'], list) and all(isinstance(p, str) for p in access['parameters']) and access['parameters'] == sorted(set(access['parameters'])), 'access parameter references')
            require(isinstance(access['explicit'], dict) and isinstance(access['current'], dict), 'access maps')
            if access['status'] == 'EXECUTED' and decl['parameters'] is not None:
                relevant.update(decl['parameters'])

        producers = {name: [] for name in relevant}
        for name in relevant:
            require(name in initial, 'missing initial state: ' + name)
            carrier(initial[name][1])
            target = 'Param.' + name
            for rid, rx in groups['RX'].items():
                matching = [p for p in groups['PRODUCER'].values() if p['execution'] == rid and p['target'] == target]
                writes = (rx['writes'] or '').split(',')
                require(len(matching) == (1 if target in writes else 0), 'producer/write census: ' + target)
                if matching:
                    p = matching[0]
                    require(p['guard'] == rx['guard'] and rid in executions, 'producer execution/guard')
                    value = carrier(b.canonical_json(p['payload'], 'DP producer payload'))
                    producers[name].append((int(rx['order']), p, value, executions[rid]))
            producers[name].sort(key=lambda p: p[0])

        used_params, used_sims, signatures, decisions = set(), set(), {}, {}

        def gap(code, invocation, eid):
            require(any(g['code'] == code and g['scope'] == invocation and eid in b.ids(g['evidence'], 'DP gap') for g in groups['GAP'].values()), 'missing ' + code)
            require(scenario['testability'] != 'Testable' and scenario['confidence'] != 'High', 'unresolved access downgrade')

        for invocation, (eid, access) in accesses.items():
            decl_id, decl = declarations[access['rule']]
            if access['status'] != 'EXECUTED':
                require(not access['explicit'] and not access['current'] and not access['parameters'] and access['simulation'] is None, 'skipped/unknown access has values or simulation')
                if access['status'] == 'UNKNOWN': gap('DP_ACCESS_UNRESOLVED', invocation, eid)
                continue
            if decl['parameters'] is None:
                require(not access['current'] and not access['parameters'] and access['simulation'] is None, 'unknown declaration presented as resolved')
                gap('DP_PARAMETER_UNRESOLVED', invocation, eid)
                continue
            require(set(access['explicit']) <= set(decl['parameters']), 'undeclared explicit input')
            for entry in access['explicit'].values():
                require(isinstance(entry, dict) and set(entry) == {'valueType', 'value', 'expression', 'evidence'} and isinstance(entry['expression'], str) and entry['expression'], 'explicit expression')
                typed(entry); refs(entry['evidence'])
            require(set(access['current']) == set(decl['parameters']), 'current state census')
            for name, entry in access['current'].items():
                require(isinstance(entry, dict) and set(entry) == {'valueType', 'value', 'state', 'evidence'}, 'current entry keys')
                value = initial[name][1]
                state = 'ABSENT' if value['valueType'] == 'absent' else 'VALUE'
                origin = {initial[name][0]}
                for order, p, produced, (execution_id, execution) in producers[name]:
                    if order >= int(groups['RX'][access['execution']]['order']): break
                    if execution['status'] == 'NOT_EXECUTED': continue
                    value = ABSENT if execution['status'] == 'UNKNOWN' else produced
                    state = 'UNKNOWN' if execution['status'] == 'UNKNOWN' else ('ABSENT' if value['valueType'] == 'absent' else 'VALUE')
                    origin = set(b.ids(p['evidence'], 'DP producer')) | {execution_id}
                require(entry['state'] == state and canonical(typed(entry)) == canonical(value), 'stale or unproven current value: ' + name)
                require(origin <= refs(entry['evidence']), 'current state origin')
            resolved, unresolved = resolve(decl, access['explicit'], access['current'])
            parameters = []
            for pid in access['parameters']:
                require(pid in groups['PARAM'] and pid not in used_params, 'unrelated/reused PARAM reference')
                used_params.add(pid); p = groups['PARAM'][pid]; parameters.append(p)
                require(p['invocation'] == invocation and p['dependency'] == access['rule'] and p['name'] in resolved, 'PARAM access binding')
                value, mode, expression = resolved[p['name']]
                require(canonical(typed(p)) == canonical(value) and p['mode'] == mode and p['expression'] == expression, 'PARAM resolution drift')
                require(p['inheritance'] == ('enabled' if mode == 'inherited' else 'n_a') and p['formalType'] is None and p['formalEvidence'] is None, 'DP PARAM mechanism/formal fields')
                require({eid, decl_id} <= set(b.ids(p['evidence'], 'DP PARAM')), 'PARAM access/declaration evidence')
            require(len(parameters) == len(resolved) and {p['name'] for p in parameters} == set(resolved), 'parameter name census')
            if unresolved or decl['scope'] != 'Thread':
                require(access['simulation'] is None, 'unresolved/ineligible simulation')
                gap('DP_PARAMETER_UNRESOLVED' if unresolved else 'DP_SCOPE_INELIGIBLE', invocation, eid)
                continue
            mid = access['simulation']
            require(mid in groups['SIM'], 'missing access simulation')
            sim = groups['SIM'][mid]; used_sims.add(mid)
            expected = {n: b.typed_python(v['valueType'], v['value']) for n, (v, _, _) in resolved.items()}
            require(sim['rule'] == access['rule'] and sim['params'] == canonical(expected), 'SIM typed map/rule drift')
            require({eid, decl_id} <= set(b.ids(sim['evidence'], 'DP SIM')), 'SIM access/declaration evidence')
            associated = [a for _, a in accesses.values() if a['simulation'] == mid]
            selected = b.ids(sim['parameterResolutions'], 'DP SIM')
            require(any(selected == a['parameters'] for a in associated), 'SIM must select one complete access parameter set')
            key = (sim['rule'], sim['sig'])
            require(key not in signatures or signatures[key] == sim['params'], 'signature reused with different values')
            require(key not in decisions or decisions[key] == mid, 'duplicate signature simulation decision')
            signatures[key] = sim['params']
            decisions[key] = mid
        require(used_sims == set(groups['SIM']), 'simulation without access evidence')
        dp_rules = set(declarations) | {d['values']['identity'] for d in rows if d['tag'] == 'DEP' and d['values']['kind'] == 'DP'}
        require(used_params == {p['id'] for p in groups['PARAM'].values() if p['dependency'] in dp_rules}, 'orphan DP PARAM')
