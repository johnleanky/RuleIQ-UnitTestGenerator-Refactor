#!/usr/bin/env python3
"""Bounded S5 prompt overlays; fixed baseline and every replacement are auditable."""
from pathlib import Path
import hashlib
import html
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
BASE='d4061046650c87b9da2c4f87141f23aa2602f082'
ANNOTATION_BASE='2c2fc195cc97ba5ab45efa6dcb90b5cdd688737a'
CHANGED=('Main_Agent_Prompt.txt','UnitTestGenerator_Prompt.txt','UnitTestGenerator.txt','Validator_Prompt.txt','JsonValidator_tool.txt')
PAIRS=(('UnitTestGenerator_Prompt.txt','UnitTestGenerator.txt'),('Validator_Prompt.txt','JsonValidator_tool.txt'))
EFFECTIVE=CHANGED

# Closed editorial substitutions: remove repository decision references while
# retaining the operative rule and a grammatical, self-contained sentence.
DECISION_REFERENCES={
    ' under DEC-020.':'.',
    ' [DEC-026]':'',
    ' under DEC-026.':'.',
    'DEC-027 extends revision 1.1 with':'Revision 1.2 extends revision 1.1 with',
    'DEC-026 value table':'formal-parameter value table',
    'DEC-026 typed-value/formal-type table':'typed-value/formal-type table',
    'DEC-029 requires producers':'The source contract requires producers',
    'DEC-020 closes its two under-specified outputs. ':'',
    ' (DEC-026)':'',
    'DTM-mode-specific DEC-016 reason':'DTM-mode-specific omission reason',
    'This narrow metadata transport interpretation is DEC-028; all other example fields':'All other example fields',
    'DEC-028 appends stable':'Append stable',
    'DEC-020 caps':'complexity caps',
    'full DEC-016 SIM':'full SIM',
    ' (DEC-030)':'',
    'DEC-016 comparison includes':'Simulation comparison includes',
}


def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def baseline(name):return git('show',BASE+':'+name)
def digest(value):return hashlib.sha256(value).hexdigest()


def tagged_expected():
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
    products={name:value.encode() for name,value in result.items()}
    verify_tagged(products)
    return products


def verify_tagged(products):
    assert set(products)==set(CHANGED)
    for name,raw in products.items():
        assert raw==git('show',ANNOTATION_BASE+':'+name),('pre-cleanup closure drift',name)


def strip_annotations(text, name, config=None):
    if config is None:config=json.loads((ROOT/'fixtures/s5/prompt-annotation-deltas.json').read_text())
    assert config['baseline']==ANNOTATION_BASE and config['decision']=='DEC-032'
    assert len(config['replacements'])==27
    inline={
        '[IPM-AUTH-035, IPM-AUTH-078; DEC-026]':'[DEC-026]',
        ' This preserves IPM-AUTH-046.':'',
        '(IPM-AUTH-035/IPM-AUTH-078; DEC-026)':'(DEC-026)',
    }
    for change in config['replacements']:
        assert set(change)=={'path','old','new'}
        assert change['path'] in {'Main_Agent_Prompt.txt','UnitTestGenerator_Prompt.txt'}
        old,new=change['old'],change['new']
        assert isinstance(old,str) and isinstance(new,str)
        if re.fullmatch(r'\[IPM-AUTH-\d{3}(?:, IPM-AUTH-\d{3})*\]\n',old):
            assert new=='','annotation line must be removed without replacement'
        else:
            assert old in inline and new==inline[old],'non-annotation replacement'
        if change['path']!=name:continue
        assert text.count(old)==1,old
        text=text.replace(old,new)
    assert 'IPM-' not in text,name
    return text


def strip_decision_references(text):
    for old,new in DECISION_REFERENCES.items():text=text.replace(old,new)
    assert not re.search(r'DEC-\d+',text),'unrecognized decision reference'
    return text


def author_anchors():
    """Recover the historical marker-to-instruction mapping outside runtime prompts."""
    name='Main_Agent_Prompt.txt';text=tagged_expected()[name].decode()
    lines=text.splitlines();anchors={};section=None
    for i,line in enumerate(lines):
        if re.match(r'^#{2,6} ',line):section=line
        ids=re.findall(r'IPM-AUTH-\d{3}',line)
        if not ids:continue
        assert section is not None
        if line.startswith('[IPM-'):
            anchor=next(v for v in lines[i+1:] if v.strip() and not v.startswith('#'))
        else:
            clean=strip_annotations(text,name).splitlines()
            # Inline annotations retain their surrounding instruction verbatim.
            config=json.loads((ROOT/'fixtures/s5/prompt-annotation-deltas.json').read_text())
            anchor=line
            for change in config['replacements']:
                if change['path']==name and change['old'] in anchor:
                    anchor=anchor.replace(change['old'],change['new'])
            assert anchor in clean and 'IPM-' not in anchor
        for ident in ids:
            entry={'section':section,'anchor':strip_decision_references(anchor)}
            if entry not in anchors.setdefault(ident,[]):anchors[ident].append(entry)
    assert set(anchors)=={f'IPM-AUTH-{n:03d}' for n in range(1,107)}
    return anchors


def expected():
    result=tagged_expected()
    for name in ('Main_Agent_Prompt.txt','UnitTestGenerator_Prompt.txt'):
        result[name]=strip_annotations(result[name].decode(),name).encode()
    for name in ('Main_Agent_Prompt.txt','UnitTestGenerator_Prompt.txt','Validator_Prompt.txt'):
        result[name]=strip_decision_references(result[name].decode()).encode()
    for prompt,export in PAIRS:
        raw=result[export].decode()
        start=raw.index('<pySystemPrompt>')+len('<pySystemPrompt>');end=raw.index('</pySystemPrompt>')
        result[export]=(raw[:start]+'\n'.join('<p>'+html.escape(line,quote=False)+'</p>' for line in result[prompt].decode().splitlines())+raw[end:]).encode()
    return result


def decode(raw):
    element=ET.fromstring(raw).find('pyGenAIDef/pySystemPrompt')
    assert element is not None
    return ('\n'.join(''.join(p.itertext()) for p in element.findall('p'))+'\n').encode()


def verify(products=None):
    current=products if products is not None else {name:(ROOT/name).read_bytes() for name in EFFECTIVE}
    predicted=expected()
    for name in EFFECTIVE:
        assert current[name]==predicted.get(name,baseline(name)),name
        assert not any(term in current[name] for term in [b'MemoryTemp',b'CreateAIAgentResponseRecord',b'GetAIAgentResponseRecord',b'IPM-',b'DEC-']),name
    for prompt,export in PAIRS:assert decode(current[export])==current[prompt],(prompt,export)
    assert (ROOT/'Main_Agent.txt').read_bytes()==baseline('Main_Agent.txt')
    def outside(raw):return raw[:raw.index(b'<pySystemPrompt>')]+raw[raw.index(b'</pySystemPrompt>'):]
    for _,export in PAIRS:
        old=baseline(export);new=current[export]
        for raw in [old,new]:assert raw.count(b'<pySystemPrompt>')==raw.count(b'</pySystemPrompt>')==1
        assert outside(old)==outside(new),(export,'metadata drift')
    return predicted


def main():
    products=expected()
    verify({name:products.get(name,baseline(name)) for name in EFFECTIVE})
    for name,raw in products.items():(ROOT/name).write_bytes(raw)
    (ROOT/'fixtures/s5/artifact-manifest.json').write_text(json.dumps({name:digest((ROOT/name).read_bytes()) for name in EFFECTIVE},indent=2)+'\n')
    verify();print('PASS: bounded S5 artifacts generated; both pairs decode exactly and unrelated export bytes preserved')


if __name__=='__main__':main()
