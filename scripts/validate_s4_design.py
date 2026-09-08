#!/usr/bin/env python3
"""S4 design/artifact gate; original census, pinned owners, full regressions and parity."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys

import validate_s3_design as s3
import validate_s4_protocol as tests
from validate_s2_design import ContractError,require

ROOT=Path(__file__).resolve().parents[1]
BASE='4393c680633d176129676f7b91179262cc25391f'
PRODUCTS={'Validator_Prompt.txt','JsonValidator_tool.txt'}


def digest(raw):return hashlib.sha256(raw).hexdigest()


def protected_owner_artifacts():
    manifest=json.loads((ROOT/'fixtures/s4/preservation-manifest.json').read_text())
    require(manifest['baseline']==BASE,'fixed S3 baseline')
    names=s3.git('ls-tree','-r','--name-only',BASE).decode().splitlines()
    expected={name for name in names if (name.endswith('.txt') and name not in PRODUCTS) or name.startswith(('docs/contracts/','fixtures/s3/')) or (name.startswith('scripts/') and name.endswith('.py') and name!='scripts/validate_s3_design.py') or name=='docs/execution/plans/S0-baseline-contracts.md'}
    require(set(manifest['protected'])==expected,'complete fixed owner census')
    for name,expected_hash in manifest['protected'].items():
        require(digest(s3.git('show',BASE+':'+name))==expected_hash,'manifest matches fixed baseline '+name)
        require(digest((ROOT/name).read_bytes())==expected_hash,'protected owner artifact '+name)
    require(set(manifest['validatorBaseline'])==PRODUCTS,'selected pair census')
    for name,h in manifest['validatorBaseline'].items():require(digest(s3.git('show',BASE+':'+name))==h,'Validator source fixed')
    # The historical regression exception is exactly two selected products, not others.
    s3.scope(s4_regression=True);s3.future_tracking(True)
    original=s3.git
    def corrupt_unrelated(*args):
        raw=original(*args)
        if args==('show',BASE+':Main_Agent.txt'):return raw+b'changed'
        return raw
    try:
        s3.git=corrupt_unrelated
        try:s3.scope(s4_regression=True)
        except ContractError:pass
        else:raise ContractError('S3 scope exception leaked to unrelated product')
    finally:s3.git=original
    return len(expected)


def matrix():
    source={}
    for line in (ROOT/'docs/execution/plans/S0-baseline-contracts.md').read_text().splitlines():
        if line.startswith(('| IPM-AUTH-','| IPM-VAL-')):
            c=[x.strip() for x in line.strip('|').split('|')];source[c[0]]=c
    rows={}
    for line in (ROOT/'docs/execution/design/S4-instruction-implementation-slice.md').read_text().splitlines():
        if line.startswith(('| IPM-AUTH-','| IPM-VAL-')):
            c=[x.strip() for x in line.strip('|').split('|')];require(c[0] not in rows,'duplicate row');rows[c[0]]=c
    catalog=json.loads((ROOT/'fixtures/s4/row-regressions.json').read_text())
    require(len(source)==len(rows)==len(catalog)==150 and set(rows)==set(source),'complete original source census')
    contract=(ROOT/'docs/contracts/UNIT_TEST_VALIDATOR_V1.md').read_text()
    effective=0
    for ident,c in source.items():
        row=rows[ident];reg='S4-'+ident.replace('IPM-','');case=catalog[reg]
        require(len(row)==9 and row[1]==c[1] and row[2]==c[4] and row[5]==c[2],'exact original clause/owner '+ident)
        require(case['row']==ident and case['source']==c[1] and case['obligation']==c[2] and case['owner']==c[4] and case['disposition']==row[3],'row regression binding')
        require(case['checks'] and all(name in tests.CASES or name=='protected_owner_artifacts' for name in case['checks']),'executable check binding')
        require(reg==row[7] and 'DEC-011' in row[6] and 'DEC-030' in row[6],'row decision/evidence')
        if row[3] in {'IMPLEMENT','CONSUME_SHARED'}:
            effective+=1;require('## '+case['section']+'.' in contract and 'Validator contract '+case['section']==row[4],'effective destination')
        else:require(row[3] in {'REMOVED_LEGACY','PRESERVED_OTHER_OWNER'},'explicit excluded owner')
    require(sum(i.startswith('IPM-VAL-') for i in source)==44 and effective==73,'44 Validator/30 Author disposition census')
    return effective


def docs():
    names=['docs/execution/CONTINUITY.md','docs/execution/ROADMAP.md','docs/execution/plans/S4-validator-refactor.md','docs/contracts/UNIT_TEST_VALIDATOR_V1.md','docs/execution/design/S4-instruction-implementation-slice.md','docs/execution/design/S4-export-boundary.md','docs/execution/design/S4-acceptance-report.md']
    for name in names:
        p=ROOT/name;text=p.read_text()
        for link in re.findall(r'\]\(([^)]+)\)',text):
            if re.match(r'[a-z]+:',link) or link.startswith('#'):continue
            require(not link.startswith('/') and (p.parent/link.split('#',1)[0]).exists(),'local doc link '+link)
    s3.docs()
    for name in names+['scripts/validator_protocol.py','scripts/validate_s4_protocol.py','scripts/validate_s4_design.py']:
        raw=(ROOT/name).read_text();require(not any(line.rstrip()!=line for line in raw.splitlines()),'untracked whitespace '+name)
    return len(names)


def examples():
    examples=json.loads((ROOT/'fixtures/s4/report-examples.json').read_text())
    require(set(examples)=={'OK','SCHEMA_INVALID','SCHEMA_MASS','SCHEMA_TOOL','MEMORY_TOOL','PROJECTION','SEMANTIC','HUMAN','MIXED','WARNING_ONLY'},'report examples')
    for report in examples.values():tests.check_report(report)
    s3.reports()
    return len(examples)


def artifacts(design_only):
    if design_only:
        for name in PRODUCTS:require((ROOT/name).read_bytes()==s3.git('show',BASE+':'+name),'product changed before design freeze')
        return
    import build_s4_artifacts as builder
    builder.verify()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--design-only',action='store_true');args=parser.parse_args()
    owners=protected_owner_artifacts();effective=matrix();doc_count=docs();example_count=examples();artifacts(args.design_only)
    tests.main()
    r=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/validate_s3_design.py'),'--s4-regression'],cwd=ROOT,text=True,capture_output=True)
    require(r.returncode==0,r.stdout+r.stderr);print(r.stdout,end='')
    for command in [['git','diff','--check'],['git','diff','--cached','--check']]:subprocess.run(command,cwd=ROOT,check=True)
    require(not list((ROOT/'scripts').glob('__pycache__')),'cache hygiene')
    print(f'PASS: S4 {"design" if args.design_only else "artifact"} gate; 150 rows/{effective} effective; protected={owners}; examples={example_count}; docs={doc_count}; independent review required separately')


if __name__=='__main__':
    try:main()
    except (ContractError,KeyError,TypeError,ValueError,AssertionError) as error:raise SystemExit('FAIL: '+str(error))
