"""Check compact management state; no dependency on product or Pega test tooling."""
from pathlib import Path
import argparse
import hashlib
import json
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
STATE = 'docs/execution/CONTINUITY.md'
ARCHIVE = 'docs/archive/workflow-2026-09-09'
FIELDS = ('Objective', 'Stage', 'Active plan', 'State', 'Baseline', 'Verified evidence',
          'Pending', 'Blockers', 'Context and reviews')
STATES = {'NOT_STARTED', 'IMPLEMENTED_NOT_VERIFIED', 'VERIFIED', 'PARTIAL',
          'FAILED', 'BLOCKED', 'UNKNOWN'}
LINK = re.compile(r'\[[^\]\n]+\]\(([^)\n]+)\)')
NEXT = re.compile(r'(?im)^(?:#{1,6}\s+|[-*]\s+(?:\*\*)?)exact next action\b')
EXECUTION_STATE = re.compile(
    r'(?im)^(?:[-*]\s+(?:\*\*)?(?:State|Status|Stage|Pending|Blockers):|'
    r'#{1,6}[ \t]+(?:Current[ \t]+)?(?:State|Status|Stage|Pending|Blockers|Progress)[ \t]*#*[ \t]*\r?$)')


class InvalidState(Exception):
    pass


def require(condition, message):
    if not condition:
        raise InvalidState(message)


def read(path, overrides):
    name = path.relative_to(ROOT).as_posix()
    if name in overrides:
        return overrides[name]
    require(path.is_file(), 'Missing file: ' + name)
    return path.read_bytes().decode('utf-8')


def target(source, value):
    value = value.strip().removeprefix('<').removesuffix('>')
    require(not re.match(r'^[A-Za-z]:|^[/\\]', value), 'Use repository-relative links: ' + value)
    location, _, anchor = unquote(value).partition('#')
    path = (source.parent / location).resolve() if location else source
    require(path.is_relative_to(ROOT), 'Link escapes repository: ' + value)
    return path, anchor


def anchors(text):
    found = set()
    counts = {}
    for heading in re.findall(r'^#{1,6}\s+(.+)$', text, re.M):
        slug = re.sub(r'[^\w\- ]', '', heading.strip().lower()).replace(' ', '-')
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        found.add(slug + ('-' + str(count) if count else ''))
    return found


def links(source, text, overrides):
    for value in LINK.findall(text):
        if re.match(r'^(?:https?://|mailto:)', value):
            continue  # Network availability is not a management-file invariant.
        path, anchor = target(source, value)
        content = read(path, overrides)
        require(not anchor or anchor in anchors(content),
                'Missing anchor: ' + source.relative_to(ROOT).as_posix() + ' -> ' + value)


def check(overrides=None):
    overrides = overrides or {}
    state = read(ROOT / STATE, overrides)
    fields = {}
    for key in FIELDS:
        matches = re.findall(r'^- ' + re.escape(key) + r': (.+)$', state, re.M)
        require(len(matches) == 1 and matches[0].strip(), 'Required unique field: ' + key)
        fields[key] = matches[0].strip()
    require(fields['State'] in STATES, 'Unknown evidence state')
    require(fields['Stage'].lower() != 'none' and 'no active stage' not in state.lower(),
            'Continuity must identify the selected task/stage')
    plan_links = LINK.findall(fields['Active plan'])
    require(len(plan_links) == 1, 'Active plan requires one local link')
    plan, anchor = target(ROOT / STATE, plan_links[0])
    require(not anchor and plan.suffix == '.md' and
            plan.is_relative_to(ROOT / 'docs/execution/plans'), 'Active plan must be a local ExecPlan')
    evidence_links = LINK.findall(fields['Verified evidence'])
    require(evidence_links and all(not re.match(r'^\w+://', link) for link in evidence_links),
            'Verified evidence requires local evidence links')
    require(len(NEXT.findall(state)) == 1, 'Continuity needs exactly one next action')
    action = re.search(r'(?m)^## Exact next action\r?\n(.*?)(?=^#{1,6} |\Z)', state, re.S)
    block = action.group(1).strip() if action else ''
    require(block and len(block.splitlines()) == 1 and
            not re.match(r'(?:\d+[.)]|[-*+#])\s', block),
            'Next action must be one plain-text line, not a list or multiple paragraphs')
    sizes = {}
    for path, limit in [(ROOT / 'AGENTS.md', 2000), (ROOT / STATE, 3500), (plan, 6500)]:
        content = read(path, overrides)
        name = path.relative_to(ROOT).as_posix()
        sizes[name] = len(content)
        require(len(content) <= limit, f'{name}: {len(content)} characters exceeds {limit}')
        if path != ROOT / STATE:
            require(not NEXT.search(content), name + ': duplicated next action')
            require(not EXECUTION_STATE.search(content), name + ': duplicates current execution state')
        links(path, content, overrides)
    require(sum(sizes.values()) <= 12000, 'Combined startup exceeds 12000 characters')
    for name in ['docs/execution/WORKFLOW.md', 'docs/execution/ROADMAP.md', 'docs/decisions/DECISIONS.md']:
        content = read(ROOT / name, overrides)
        require(not NEXT.search(content), name + ': duplicated next action')
        require(not EXECUTION_STATE.search(content), name + ': duplicates current execution state')
        links(ROOT / name, content, overrides)
    # Validate linked evidence and individual decisions without loading them into agent context.
    for value in evidence_links:
        path, _ = target(ROOT / STATE, value)
        links(path, read(path, overrides), overrides)
    for path in (ROOT / 'docs/decisions').glob('DEC-*.md'):
        links(path, read(path, overrides), overrides)
    return sizes


def migration():
    archive = ROOT / ARCHIVE
    manifest = json.loads((archive / 'manifest.json').read_text(encoding='utf-8'))
    for original, fact in manifest['snapshots'].items():
        raw = (archive / original).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == fact['sha256'], 'Archive drift: ' + original)
        require(len(raw.decode('utf-8')) == fact['characters'], 'Archive size drift: ' + original)
        snapshot = ARCHIVE + '/' + original
        attributes = subprocess.check_output(['git', 'check-attr', 'text', '--', snapshot], cwd=ROOT).decode().strip()
        require(attributes.endswith(': text: unset'), 'Archive must disable Git text conversion: ' + original)
        stored = subprocess.check_output(['git', 'hash-object', '--path=' + snapshot, '--stdin'],
                                         input=raw, cwd=ROOT).decode().strip()
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(stored == blob, 'Git would transform archive bytes: ' + original)
    for original, digest in manifest['protected'].items():
        require((ROOT / original).is_file() and hashlib.sha256((ROOT / original).read_bytes()).hexdigest() == digest,
                'Unrelated pre-migration file changed: ' + original)
    old = (archive / 'docs/decisions/DECISIONS.md').read_text(encoding='utf-8')
    entries = list(re.finditer(r'^## (DEC-\d{3})[^\n]*', old, re.M))
    index = (ROOT / 'docs/decisions/DECISIONS.md').read_text(encoding='utf-8')
    for i, match in enumerate(entries):
        name = match.group(1)
        expected = old[match.start():entries[i+1].start() if i+1 < len(entries) else len(old)].strip()
        if name == 'DEC-033':
            expected = expected.replace('S6 design/activation IMPLEMENTED_NOT_VERIFIED pending independent review.',
                'S6 design independently reviewed PASS. See [review evidence](../execution/evidence/S6-design-review.md); [continuity](../execution/CONTINUITY.md) owns current implementation state.')
        require((ROOT / ('docs/decisions/' + name + '.md')).read_text(encoding='utf-8').strip() == expected,
                'Decision extraction drift: ' + name)
        require(f']({name}.md)' in index and match.group(0) in index, 'Missing indexed decision: ' + name)
    require(len(entries) == 33, 'Original decision census changed')
    old_startup = sum(manifest['snapshots'][p]['characters'] for p in
                      ['AGENTS.md', STATE, 'docs/execution/ROADMAP.md', 'docs/execution/plans/S6-data-page-parameters.md'])
    return len(manifest['protected']), old_startup


def self_test():
    state = (ROOT / STATE).read_text(encoding='utf-8')
    path, _ = target(ROOT / STATE, LINK.findall(re.search(r'^- Active plan: (.+)$', state, re.M).group(1))[0])
    plan_name = path.relative_to(ROOT).as_posix()
    plan = path.read_text(encoding='utf-8')
    cases = [
        {STATE: re.sub(r'^- Verified evidence:.*$', '- Verified evidence: No reference', state, flags=re.M)},
        {STATE: state + '\n## Exact next action\nDuplicate\n'},
        {plan_name: plan + '\n## Exact next action\nDuplicate\n'},
        {STATE: re.sub(r'^- Objective:.*\n', '', state, flags=re.M)},
        {STATE: state + '\n- State: VERIFIED\n'},
        {STATE: re.sub(r'^- State:.*$', '- State: CLAIMED', state, flags=re.M)},
        {STATE: state + '\nNo active stage.\n'},
        {STATE: re.sub(r'^- Active plan:.*$', '- Active plan: [Absent](plans/missing-plan.md)', state, flags=re.M)},
        {STATE: state.replace('## Exact next action', '## Action')},
        {STATE: re.sub(r'(## Exact next action\n)\n[^\n]+', r'\1', state)},
        {STATE: state + '\n[Missing](missing-evidence.md)\n'},
        {STATE: state + '\n[Missing anchor](WORKFLOW.md#not-an-anchor)\n'},
        {STATE: state + '\n[Escape](../../../../outside.md)\n'},
        {STATE: state + 'x' * 3501},
        {'AGENTS.md': 'x' * 2001},
        {plan_name: plan + 'x' * 6501},
        {plan_name: plan + '\n- State: VERIFIED\n'},
        {STATE: re.sub(r'(## Exact next action\n)\n[^\n]+', r'\1\n1. First action\n2. Second action', state)},
        {STATE: re.sub(r'(## Exact next action\n)\n[^\n]+', r'\1\nFirst action\n\nSecond action', state)},
        {plan_name: plan + '\n## State\n\nVERIFIED\n'},
        {plan_name: plan.replace('\n', '\r\n') + '\r\n## State\r\nVERIFIED\r\n'},
        {'docs/execution/ROADMAP.md': (ROOT / 'docs/execution/ROADMAP.md').read_text(encoding='utf-8') + '\n- State: VERIFIED\n'},
        {'docs/execution/WORKFLOW.md': (ROOT / 'docs/execution/WORKFLOW.md').read_text(encoding='utf-8') + '\n## Current Status\n\nVERIFIED\n'},
    ]
    for number, overrides in enumerate(cases, 1):
        try:
            check(overrides)
        except InvalidState:
            continue
        raise InvalidState('Negative self-test accepted: ' + str(number))
    # A valid on-budget change still passes; checks must not reject all overrides.
    check({STATE: state.replace('- Objective:', '- Objective:', 1)})
    check({STATE: state.replace('\n', '\r\n'), plan_name: plan.replace('\n', '\r\n')})
    return len(cases)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--self-test', action='store_true')
    parser.add_argument('--migration', action='store_true', help='Verify this migration snapshot; not a future product gate')
    args = parser.parse_args()
    try:
        sizes = check()
        result = {'startupCharacters': sum(sizes.values()), 'files': sizes}
        if args.self_test:
            result['negativeTests'] = self_test()
        if args.migration:
            count, previous = migration()
            result.update(protectedFiles=count, previousStartupCharacters=previous,
                          startupReductionPercent=round(100 * (1 - sum(sizes.values()) / previous), 1))
        print('PASS ' + json.dumps(result))
    except (InvalidState, OSError, UnicodeError, ValueError) as error:
        print('FAIL ' + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
