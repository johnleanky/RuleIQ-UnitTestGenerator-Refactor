#!/usr/bin/env python3
"""Bounded S5 prompt overlays; fixed baseline and every replacement are auditable."""
from pathlib import Path
import hashlib
import html
import json
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE='d4061046650c87b9da2c4f87141f23aa2602f082'
CHANGED=('Main_Agent_Prompt.txt','UnitTestGenerator_Prompt.txt','UnitTestGenerator.txt')
PAIRS=(('UnitTestGenerator_Prompt.txt','UnitTestGenerator.txt'),('Validator_Prompt.txt','JsonValidator_tool.txt'))
EFFECTIVE=CHANGED+('Validator_Prompt.txt','JsonValidator_tool.txt')


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def baseline(name):return git('show',BASE+':'+name)
def digest(value):return hashlib.sha256(value).hexdigest()


def expected():
    config=json.loads((ROOT/'fixtures/s5/product-deltas.json').read_text())
    assert config['baseline']==BASE
    result={name:baseline(name).decode() for name in CHANGED}
    for change in config['replacements']:
        text=result[change['path']];assert text.count(change['old'])==change['count'],change['id']
        assert change['old']!=change['new'] and change['rows'] and change['reason']
        result[change['path']]=text.replace(change['old'],change['new'])
    # Terminal report schema is a read-only response contract, never a candidate schema.
    result['Main_Agent_Prompt.txt']+='\n## 15. Generator terminal report contract\n\nAfter UnitTestGenerator returns, validate its complete raw JSON report against this closed structural contract before using its status. A malformed report follows Section 1A\'s invalid-response path. Interpret only the validated terminal status for the fixed external mapping; do not expose report fields, derive semantics, parse candidates or initiate further calls. This report-only schema does not authorize UTC candidate-schema acquisition or validation. Before mapping status, also apply these report-only G9 consistency checks: repairAttempts <= validationAttempts <= repairAttempts + 1; supplied sourceUUID order must match the handoff exactly (only rejected duplicate-UUID invocation arguments may yield Failed with empty groups and zero attempts); sourceUUIDs and parsed Scenario IDs are unique in their respective scopes. Ready groups have the original groupId and complete original ordered Scenario IDs; unread/invalid groups have null groupId and no fabricated Scenarios. Failed has no Successful Scenario. Success requires all groups Ready, at least one Successful Scenario, no NotValidated Scenario, candidate.CaseID equal to original CaseID, and validationAttempts = repairAttempts + 1. Completed has no Untestable Scenario; PartiallyCompleted has at least one. Successful unit/scenario coordinates are contiguous zero-based positions in surviving original group/Scenario order. Any contradiction follows the same invalid-response path. These checks validate only visible report facts and known handoff identities; they do not independently prove the claimed Validator OK or inspect candidate bytes.\n\n```json\n'+(ROOT/'docs/contracts/GENERATOR_RUN_REPORT_V1.schema.json').read_text().strip()+'\n```\n'
    # Generator export: preserve every byte outside its single pySystemPrompt body.
    raw=result['UnitTestGenerator.txt'];start=raw.index('<pySystemPrompt>')+len('<pySystemPrompt>');end=raw.index('</pySystemPrompt>')
    result['UnitTestGenerator.txt']=raw[:start]+'\n'.join('<p>'+html.escape(line,quote=False)+'</p>' for line in result['UnitTestGenerator_Prompt.txt'].splitlines())+raw[end:]
    return {name:value.encode() for name,value in result.items()}


def decode(raw):
    element=ET.fromstring(raw).find('pyGenAIDef/pySystemPrompt')
    assert element is not None
    return ('\n'.join(''.join(p.itertext()) for p in element.findall('p'))+'\n').encode()


def verify(products=None):
    current=products if products is not None else {name:(ROOT/name).read_bytes() for name in EFFECTIVE}
    predicted=expected()
    for name in EFFECTIVE:
        assert current[name]==predicted.get(name,baseline(name)),name
        assert not any(term in current[name] for term in [b'MemoryTemp',b'CreateAIAgentResponseRecord',b'GetAIAgentResponseRecord']),name
    for prompt,export in PAIRS:assert decode(current[export])==current[prompt],(prompt,export)
    assert (ROOT/'Main_Agent.txt').read_bytes()==baseline('Main_Agent.txt')
    old=baseline('UnitTestGenerator.txt');new=current['UnitTestGenerator.txt']
    for raw in [old,new]:assert raw.count(b'<pySystemPrompt>')==raw.count(b'</pySystemPrompt>')==1
    def outside(raw):return raw[:raw.index(b'<pySystemPrompt>')]+raw[raw.index(b'</pySystemPrompt>'):]
    assert outside(old)==outside(new),'Generator metadata drift'
    return predicted


def main():
    products=expected()
    verify({name:products.get(name,baseline(name)) for name in EFFECTIVE})
    for name,raw in products.items():(ROOT/name).write_bytes(raw)
    (ROOT/'fixtures/s5/artifact-manifest.json').write_text(json.dumps({name:digest((ROOT/name).read_bytes()) for name in EFFECTIVE},indent=2)+'\n')
    verify();print('PASS: bounded S5 artifacts generated; both pairs decode exactly and unrelated export bytes preserved')


if __name__=='__main__':main()
