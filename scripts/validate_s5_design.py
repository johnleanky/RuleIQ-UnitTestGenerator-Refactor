#!/usr/bin/env python3
"""Complete S5 current integration plus fixed historical preservation gate."""
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import re
import subprocess
import sys

import build_s5_artifacts as builder
import validate_s5_integration as flows

ROOT=Path(__file__).resolve().parents[1]
BASE=builder.BASE
GLOBAL={'docs/execution/CONTINUITY.md','docs/execution/ROADMAP.md','docs/execution/plans/S4-validator-refactor.md','docs/decisions/DECISIONS.md'}
DOCS=['docs/execution/CONTINUITY.md','docs/execution/ROADMAP.md','docs/execution/plans/S5-integration-legacy-cleanup.md','docs/contracts/S5_INTEGRATION.md','docs/execution/design/S5-instruction-reverse-audit.md']


def table(name):
    rows={}
    for line in (ROOT/name).read_text().splitlines():
        if line.startswith(('| IPM-AUTH-','| IPM-VAL-')):
            cells=[v.strip() for v in line.strip('|').split('|')]
            assert cells[0] not in rows;rows[cells[0]]=cells
    return rows


def preservation():
    manifest=json.loads((ROOT/'fixtures/s5/preservation-manifest.json').read_text())
    allowed=set(builder.CHANGED)|GLOBAL
    files=set(builder.git('ls-tree','-r','--name-only',BASE).decode().splitlines())
    assert manifest['baseline']==BASE and set(manifest['excluded'])==allowed
    assert set(manifest['protected'])==files-allowed
    for name,h in manifest['protected'].items():
        assert builder.digest(builder.baseline(name))==h,name
        assert builder.digest((ROOT/name).read_bytes())==h,name
    # Main reference-only export is protected independently, never compared for prompt parity.
    assert 'Main_Agent.txt' in manifest['protected']
    return len(manifest['protected'])


def matrix(catalog=None, documented=None):
    source=table('docs/execution/plans/S0-baseline-contracts.md');s2=table('docs/execution/design/S2-instruction-implementation-slice.md');s3=table('docs/execution/design/S3-instruction-implementation-slice.md');s4=table('docs/execution/design/S4-instruction-implementation-slice.md')
    if documented is None:documented=table('docs/execution/design/S5-instruction-reverse-audit.md')
    if catalog is None:catalog=json.loads((ROOT/'fixtures/s5/reverse-matrix.json').read_text())
    rows={row['id']:row for row in catalog}
    additions=json.loads((ROOT/'fixtures/s5/current-role-additions.json').read_text())
    added={(a['id'],a['role']):a for a in additions}
    assert len(added)==len(additions)==36
    for a in additions:
        assert a['id'] in source and a['responsibility']
        expected_path='UnitTestGenerator_Prompt.txt' if a['role']=='UNIT_TEST_GENERATOR' else 'Validator_Prompt.txt'
        assert a['role'] in {'UNIT_TEST_GENERATOR','VALIDATOR'} and a['path']==expected_path
        prompt=(ROOT/a['path']).read_text()
        section=next(block for block in prompt.split('\n## ') if block.startswith(a['section']+'.'))
        assert a['anchor'] in section,(a['id'],a['anchor'])
    assert len(catalog)==len(rows)==len(source)==len(documented)==150 and set(rows)==set(source)==set(documented)
    removed=[]
    for ident,original in source.items():
        row=rows[ident];doc=documented[ident]
        assert row['source']==original[1] and row['obligation']==original[2] and row['originalOwner']==original[4],ident
        assert len(doc)==9 and doc[1:5]==[row['source'],row['originalOwner'],row['authority'],row['disposition']] and doc[6]==row['obligation'],ident
        destinations='; '.join(role+': '+dest for role,dest in row['destinations'].items()) or 'NONE: obsolete transport removed under accepted decisions'
        assert doc[5]==destinations and doc[7]==', '.join(row['evidence']),ident
        assert {'DEC-011','DEC-016','DEC-019','DEC-030','DEC-031'}<=set(row['decisions'])
        assert row['evidence']==['historical-source-and-prompt-preservation','current-exact-overlay','reverse-source-census']
        assert set(row['roles'])==set(row['destinations'])
        for role,stage in [('UNIT_TEST_GENERATOR',s3),('VALIDATOR',s4)]:
            historical=stage[ident][3] in {'IMPLEMENT','CONSUME_SHARED'}
            addition=added.get((ident,role))
            assert (role in row['roles'])==(historical or addition is not None),(ident,role)
            if role in row['roles']:
                path='UnitTestGenerator_Prompt.txt' if role=='UNIT_TEST_GENERATOR' else 'Validator_Prompt.txt'
                if historical:
                    assert addition is None and stage[ident][4] in row['roles'][role]
                    section=re.search(r'\b[GV]\d+\b',stage[ident][4]).group()
                else:
                    section=addition['section'];assert row['roles'][role]==addition['responsibility']
                assert row['destinations'][role]==path+': '+section
                assert '\n## '+section+'.' in (ROOT/path).read_text()
        author_role=ident in s2 and s2[ident][3]!='REMOVE_FROM_AUTHOR'
        assert ('SCENARIO_AUTHOR' in row['roles'])==(author_role or ident in {'IPM-VAL-043','IPM-VAL-044'})
        if author_role:assert row['roles']['SCENARIO_AUTHOR']==s2[ident][4],ident
        if 'SCENARIO_AUTHOR' in row['roles']:
            dest=('Main_Agent_Prompt.txt: '+ident+'; Sections 1/1A/1B/13/14') if author_role else 'Main_Agent_Prompt.txt: Section 13; IPM-AUTH-090'
            assert row['destinations']['SCENARIO_AUTHOR']==dest,ident
            prompt=(ROOT/'Main_Agent_Prompt.txt').read_text()
            assert (ident if author_role else 'IPM-AUTH-090') in prompt
        if row['disposition']=='REMOVED_LEGACY':
            removed.append(ident);assert row['authority']=='NONE' and not row['roles']
        else:assert row['disposition']=='PRESERVED' and row['authority'] in row['roles'],ident
    assert removed==['IPM-VAL-005']
    return len(rows)


def matrix_mutations():
    catalog=json.loads((ROOT/'fixtures/s5/reverse-matrix.json').read_text())
    documented=table('docs/execution/design/S5-instruction-reverse-audit.md')
    for mutation in ['missing-role','invalid-path','documented-destination','wrong-section']:
        bad=deepcopy(catalog);doc=deepcopy(documented)
        if mutation=='missing-role':
            row=next(r for r in bad if r['id']=='IPM-AUTH-004')
            row['roles'].pop('UNIT_TEST_GENERATOR');row['destinations'].pop('UNIT_TEST_GENERATOR')
            doc[row['id']][5]='; '.join(k+': '+v for k,v in row['destinations'].items())
        elif mutation=='documented-destination':doc['IPM-AUTH-001'][5]='NOBODY: no destination'
        else:
            bad[0]['destinations']['SCENARIO_AUTHOR']='NONEXISTENT.txt' if mutation=='invalid-path' else 'Main_Agent_Prompt.txt: Section 999'
            doc['IPM-AUTH-001'][5]='SCENARIO_AUTHOR: '+bad[0]['destinations']['SCENARIO_AUTHOR']
        try:matrix(bad,doc)
        except AssertionError:pass
        else:raise AssertionError('reverse audit mutation accepted '+mutation)


def docs():
    names=DOCS+(['docs/execution/design/S5-acceptance-report.md'] if (ROOT/'docs/execution/design/S5-acceptance-report.md').exists() else [])
    for name in names:
        path=ROOT/name;text=path.read_text()
        assert all(line.rstrip()==line for line in text.splitlines()),name
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r'[a-z]+:',link) or link.startswith('#'):continue
            assert not link.startswith('/') and (path.parent/link.split('#')[0]).exists(),(name,link)
    continuity=(ROOT/DOCS[0]).read_text();plan=(ROOT/DOCS[2]).read_text()
    nexts=[re.findall(r'^#{2,4} Exact [Nn]ext [Aa]ction\s*\n\s*([^\n]+)',s,re.M) for s in [continuity,plan]]
    assert len(nexts[0])==len(nexts[1])==1 and nexts[0]==nexts[1]
    assert '[S5-integration-legacy-cleanup.md](plans/S5-integration-legacy-cleanup.md)' in continuity
    return len(names)


def artifacts(design_only):
    expected=builder.expected();proposed={name:expected.get(name,builder.baseline(name)) for name in builder.EFFECTIVE}
    builder.verify(proposed)
    deltas=json.loads((ROOT/'fixtures/s5/product-deltas.json').read_text())
    assert len(deltas['replacements'])==9
    main=proposed['Main_Agent_Prompt.txt']
    assert b'Missing, additional, wrongly cased' not in main and b'fields are exactly `Success`' not in main
    assert main.count(b'Ignore additional platform metadata')==2
    assert deltas['appendix']['path']=='Main_Agent_Prompt.txt' and deltas['appendix']['schema']=='docs/contracts/GENERATOR_RUN_REPORT_V1.schema.json'
    for delta in deltas['replacements']:assert delta['rows'] and all(row in table('docs/execution/plans/S0-baseline-contracts.md') for row in delta['rows'])
    if design_only:
        for name in builder.EFFECTIVE:assert (ROOT/name).read_bytes()==builder.baseline(name),'product changed before design PASS'
    else:
        builder.verify()
        manifest=json.loads((ROOT/'fixtures/s5/artifact-manifest.json').read_text())
        assert set(manifest)==set(builder.EFFECTIVE)
        for name,h in manifest.items():assert builder.digest((ROOT/name).read_bytes())==h,name
    for name,needle,replacement in [
        ('Main_Agent_Prompt.txt',b'Ignore additional platform metadata',b'Reject additional platform metadata'),
        ('Main_Agent_Prompt.txt',b'required fields are `Success`',b'fields are exactly `Success`'),
        ('Main_Agent_Prompt.txt',b'legacy transient-memory transport',b'MemoryTemp'),
        ('Main_Agent_Prompt.txt',b'## 15. Generator terminal report contract',b'## 15. Missing report contract'),
        ('UnitTestGenerator_Prompt.txt',b'Validator preserves the same full grammar',b'Validator may omit sig and params'),
        ('UnitTestGenerator.txt',b'<pyModelName>Claude-Sonnet-4-6</pyModelName>',b'<pyModelName>Changed</pyModelName>'),
        ('JsonValidator_tool.txt',b'<pyPurpose>GetMemory</pyPurpose>',b'<pyPurpose>WriteMemory</pyPurpose>'),
        ('Validator_Prompt.txt',b'UnitTestCandidateUUID',b'LatestCandidate')]:
        bad=deepcopy(proposed);assert needle in bad[name];bad[name]=bad[name].replace(needle,replacement,1)
        try:builder.verify(bad)
        except AssertionError:pass
        else:raise AssertionError('artifact mutation accepted '+name)


def historical():
    with TemporaryDirectory(prefix='ruleiq-s5-baseline-') as temp:
        checkout=Path(temp)/'checkout'
        subprocess.run(['git','clone','--quiet','--shared','--no-checkout',str(ROOT),str(checkout)],check=True,capture_output=True)
        subprocess.run(['git','-C',str(checkout),'checkout','--quiet','--detach',BASE],check=True,capture_output=True)
        assert subprocess.check_output(['git','-C',str(checkout),'rev-parse','HEAD']).decode().strip()==BASE
        result=subprocess.run([sys.executable,'-B','scripts/validate_s4_design.py'],cwd=checkout,text=True,capture_output=True)
        assert result.returncode==0,result.stdout+result.stderr
        assert subprocess.check_output(['git','-C',str(checkout),'status','--porcelain'])==b''
        print(result.stdout,end='')
        print('PASS: unchanged complete historical gate on isolated fixed S4 checkout; current repository untouched')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--design-only',action='store_true');parser.add_argument('--skip-historical',action='store_true');args=parser.parse_args()
    protected=preservation();rows=matrix();matrix_mutations();document_count=docs();artifacts(args.design_only)
    flows.main()
    if not args.skip_historical:historical()
    for command in [['git','diff','--check'],['git','diff','--cached','--check']]:subprocess.run(command,cwd=ROOT,check=True)
    for base in ['scripts','fixtures/s5']:
        assert not list((ROOT/base).rglob('__pycache__'))
    for name in builder.git('ls-files','--others','--exclude-standard','scripts','fixtures/s5').decode().splitlines():
        assert all(line.rstrip()==line for line in (ROOT/name).read_text().splitlines()),name
    print(f'PASS: S5 {"design" if args.design_only else "artifact"} gate; rows={rows}; protected={protected}; docs={document_count}; historical={"not rerun" if args.skip_historical else "fixed S4 PASS"}; independent review recorded separately')


if __name__=='__main__':main()
