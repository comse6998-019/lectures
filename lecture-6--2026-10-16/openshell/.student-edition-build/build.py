"""Build openshell-student-edition.html, the student edition of the course's OpenShell guide.

A reduced copy of ../.openshell-guide-build/build.py: the same template, the same figure embedding
(an SVG data URI plus a self-contained TikZ download under every figure) and the same source links
(data-source="path:line" resolved to the OpenShell commit be7af99, each line checked against a local
checkout). It adds data-cyberbird="path:line" links to Cyberbird at ead3421, a contents plan read
from contents.html, and three checks the guide's build did not make: chapter length, sentence
length, and that no defined term (each <dfn>) appears before the paragraph that defines it.

Run:
  uv run --no-project --python 3.12 python build.py
Environment (optional):
  OPENSHELL_REPO   a checkout of NVIDIA/OpenShell at be7af99 (default ~/workspace/imputed/openshell)
  CYBERBIRD_REPO   a checkout of comse6998-019/cyberbird (default ../../../../cyberbird)
"""
from pathlib import Path
from html.parser import HTMLParser
from html import escape, unescape
import base64
import json
import math
import os
import re
import subprocess
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / 'openshell-student-edition.html'
GUIDE_FIGURES = HERE.parent / 'openshell-figures'
STUDENT_FIGURES = HERE / 'figures'

SHA = 'be7af99ff2eacba807d82b69adb0c3d4eaa32158'
BASE = f'https://github.com/NVIDIA/OpenShell/blob/{SHA}/'
REPO = Path(os.environ.get('OPENSHELL_REPO', Path.home() / 'workspace/imputed/openshell'))

CB_SHA = 'ead3421938e71c1ca42173899e2ee7e8eab8623f'
CB_BASE = f'https://github.com/comse6998-019/cyberbird/blob/{CB_SHA}/'
CYBERBIRD = Path(os.environ.get('CYBERBIRD_REPO', HERE.parents[3] / 'cyberbird'))

# The figures in the order the chapters' text numbers them ("Figure 1" is three-needs, and so on).
FIGURE_ORDER = ['three-needs', 'three-needs-cyberbird', 'architecture', 'architecture-cyberbird']
WORDS_PER_CHAPTER = (1200, 1800)
MAX_SENTENCE_WORDS = 25


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True, check=True).stdout.strip()


assert REPO.is_dir(), f'No OpenShell checkout at {REPO}; set OPENSHELL_REPO'
assert git(REPO, 'rev-parse', 'HEAD') == SHA, f'{REPO} is not at {SHA}'
assert CYBERBIRD.is_dir(), f'No Cyberbird checkout at {CYBERBIRD}; set CYBERBIRD_REPO'


class Text(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts = []
    def handle_data(self, value):
        self.parts.append(value)


def plain(value):
    parser = Text(); parser.feed(value); return ' '.join(parser.parts)


def words(value):
    return len(re.findall(r"[\w][\w'/-]*", plain(value)))


# ---- the pieces --------------------------------------------------------------------------------
chapter_files = sorted(HERE.glob('[0-9][0-9]-*.html'))
assert chapter_files, 'No chapter files'
content = '\n'.join(p.read_text() for p in chapter_files)
contents = (HERE / 'contents.html').read_text()
template = (HERE / 'template.html').read_text()
figure_specs = json.loads((HERE / 'figures.json').read_text())

# ---- checks on the authored text, before figures are embedded ----------------------------------
BLOCKS = {'p', 'li', 'h2', 'h3', 'figcaption', 'summary', 'pre', 'strong-head', 'header'}


class Blocks(HTMLParser):
    """Visible text split into blocks (paragraph, list item, heading, caption), with dfn positions."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.blocks = []          # [kind, text, section_id]
        self.dfns = []            # (term, block_index)
        self.stack = []
        self.section = None
        self.in_dfn = False
        self.skip = 0             # inside <pre>, or the sources line

    def start_block(self, kind):
        self.blocks.append([kind, '', self.section])

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'section':
            self.section = a.get('id')
        if tag in ('p', 'li', 'h2', 'h3', 'figcaption', 'summary', 'pre', 'div'):
            kind = 'sources' if (tag == 'p' and 'sources' in (a.get('class') or '')) else tag
            self.start_block(kind)
        if tag == 'dfn':
            self.in_dfn = True
            self.dfns.append(['', len(self.blocks) - 1])
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag == 'dfn':
            self.in_dfn = False
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()

    def handle_data(self, data):
        if not self.blocks:
            self.start_block('text')
        self.blocks[-1][1] += data
        if self.in_dfn:
            self.dfns[-1][0] += data


def captions_inline(html):
    return re.sub(r'<figure data-tikz="([^"<>]+)"></figure>',
                  lambda m: '<figcaption>' + escape(figure_specs[m.group(1)]['caption']) + '</figcaption>', html)


intro = re.search(r'<div class="intro">(.*?)</div>', template, re.S).group(1)
reader = Blocks()
reader.feed('<section id="intro">' + intro + '</section>' + captions_inline(content))

# 1. No defined term before the paragraph that defines it. Navigation (the contents plan) is not prose and is
#    not read here. A term matches as a whole word, with an optional plural "s"; "sandbox runtime" is checked
#    on "runtime", "compute driver" on "driver", and the control session on its last two words.
ALIASES = {'sandbox runtime': r'runtime', 'compute driver': r'drivers?',
           'supervisor-initiated control session': r'control sessions?'}
term_report = []
problems = []
for term, index in reader.dfns:
    key = term.lower().strip()
    pattern = ALIASES.get(key, re.escape(key).replace(r'\ ', r'\s+') + r's?')
    regex = re.compile(r'(?<![\w-])' + pattern + r'(?![\w-])', re.I)
    first = next((i for i, (kind, text, _) in enumerate(reader.blocks) if regex.search(text)), None)
    snippet = ' '.join(reader.blocks[first][1].split())[:90] if first is not None else ''
    term_report.append({'term': term, 'defined_in_block': index, 'first_used_in_block': first, 'first_use': snippet})
    if first is None or first < index:
        problems.append(f'term "{term}" is used in block {first} before its definition in block {index}: {snippet}')
assert len({t.lower() for t, _ in reader.dfns}) == len(reader.dfns), 'A term is defined twice'

# 2. No sentence over MAX_SENTENCE_WORDS words in the prose (the sources lines and code blocks are not prose).
long_sentences = []
for kind, text, section in reader.blocks:
    if kind in ('sources', 'pre'):
        continue
    for sentence in re.split(r'(?<=[.!?])\s+(?=[A-Z"(])', ' '.join(text.split())):
        n = len(re.findall(r"[\w][\w'/-]*", sentence))
        if n > MAX_SENTENCE_WORDS:
            long_sentences.append(f'{section}: {n} words: {sentence}')
problems += long_sentences

# 3. Banned shapes from the course's language rules: a semicolon or a dash joining clauses.
for kind, text, section in reader.blocks:
    if kind in ('sources', 'pre'):
        continue
    flat = ' '.join(text.split())
    for bad, why in ((r';\s', 'semicolon joining clauses'), (r'\s[–—]\s|—', 'dash joining clauses')):
        for m in re.finditer(bad, flat):
            problems.append(f'{section}: {why}: ...{flat[max(0, m.start() - 50):m.end() + 50]}...')

assert not problems, '\n'.join(problems)

# ---- source links ------------------------------------------------------------------------------
def check_line(root, path, number):
    file = root / path
    assert file.is_file(), f'Missing source {root.name}/{path}'
    count = len(file.read_text(errors='replace').splitlines())
    assert 1 <= number <= count, f'Bad line {path}:{number}, file has {count}'


sources = []
for attr, root in (('data-source', REPO), ('data-cyberbird', CYBERBIRD)):
    for source in re.findall(attr + r'="([^"]+)"', content):
        path, number = source.rsplit(':', 1)
        check_line(root, path, int(number))
        if root == CYBERBIRD:
            # the cited file must be as committed at CB_SHA, or the link would show other code
            changed = subprocess.run(['git', '-C', str(CYBERBIRD), 'diff', '--quiet', CB_SHA, '--', path])
            assert changed.returncode == 0, f'cyberbird/{path} differs from {CB_SHA}'
        sources.append(source)


def resolve_openshell(match):
    source = unescape(match.group(1)); path, number = source.rsplit(':', 1)
    return (f'data-source="{escape(source)}" href="{BASE + escape(path)}#L{number}" target="_blank" '
            f'rel="noopener noreferrer" title="{escape(source)} · commit be7af99ff"')


def resolve_cyberbird(match):
    source = unescape(match.group(1)); path, number = source.rsplit(':', 1)
    return (f'data-cyberbird="{escape(source)}" href="{CB_BASE + escape(path)}#L{number}" target="_blank" '
            f'rel="noopener noreferrer" title="cyberbird/{escape(source)} · commit ead3421"')


content = re.sub(r'data-source="([^"]+)"', resolve_openshell, content)
content = re.sub(r'data-cyberbird="([^"]+)"', resolve_cyberbird, content)

# ---- figures -----------------------------------------------------------------------------------
found = re.findall(r'<figure data-tikz="([^"<>]+)"></figure>', content)
assert found == FIGURE_ORDER, f'Figures appear as {found}, the text numbers them as {FIGURE_ORDER}'
figure_number = 0


def figure(m):
    global figure_number
    figure_number += 1
    name = m.group(1); spec = figure_specs[name]
    root = GUIDE_FIGURES if spec['root'] == 'guide' else STUDENT_FIGURES
    svg = (root / (name + '.svg')).read_bytes()
    tree = ET.fromstring(svg)
    width = round(float(tree.attrib['width'].removesuffix('pt')) * 1.65)
    height = round(float(tree.attrib['height'].removesuffix('pt')) * 1.65)
    image_data = base64.b64encode(svg).decode()
    tex = ((GUIDE_FIGURES / 'standalone-style.tex').read_text() + '\n' + r'\begin{document}' + '\n'
           + (root / (name + '.tikz')).read_text() + r'\end{document}' + '\n')
    source_data = base64.b64encode(tex.encode()).decode()
    return (f'<figure class="tikz-figure" id="fig-{name}" data-figure="{name}"><div class="diagram-scroll" tabindex="0" '
            f'role="region" aria-label="Figure {figure_number}; scroll horizontally on narrow screens"><img '
            f'src="data:image/svg+xml;base64,{image_data}" alt="{escape(spec["alt"], quote=True)}" width="{width}" '
            f'height="{height}"></div><figcaption><strong>Figure {figure_number}.</strong> {escape(spec["caption"])}'
            f'</figcaption><p class="figure-source"><a href="data:text/plain;base64,{source_data}" '
            f'download="openshell-student-{name}.tex">TikZ source</a></p></figure>')


content = re.sub(r'<figure data-tikz="([^"<>]+)"></figure>', figure, content)

# ---- chapter numbering, subsection anchors, contents -------------------------------------------
chapter_matches = list(re.finditer(r'<section class="chapter" id="(ch\d+)" data-title="([^"]+)">', content))
assert len(chapter_matches) == len(chapter_files)
chapters = []
for index in range(len(chapter_matches) - 1, -1, -1):
    match = chapter_matches[index]
    end = chapter_matches[index + 1].start() if index + 1 < len(chapter_matches) else len(content)
    body = content[match.start():end]
    number = int(match.group(1)[2:])
    title = plain(re.search(r'<h2>(.*?)</h2>', body, re.S).group(1))
    total_words = words(body)
    prose = re.sub(r'<p class="sources">.*?</p>|<p class="figure-source">.*?</p>|<pre>.*?</pre>', '', body, flags=re.S)
    body = re.sub(r'<p class="eyebrow">.*?</p>', '', body, flags=re.S)
    body = body.replace('<header class="chapter-head">', '<header class="chapter-head"><hr>', 1)
    body = body.replace('<h2>', f'<h2><span class="section-number">{number}</span>', 1).replace('</h2>', '</h2><hr>', 1)
    sections = []

    def subsection(m):
        n = len(sections) + 1
        anchor = f'{match.group(1)}-s{n}'
        sections.append((anchor, plain(m.group(1))))
        return f'<h3 id="{anchor}"><span class="section-number">{number}.{n}</span>{m.group(1)}</h3>'

    body = re.sub(r'<h3>(.*?)</h3>', subsection, body, flags=re.S)
    closing = body.rfind('</section>')
    body = body[:closing] + '<p class="chapter-return"><a href="#contents">Contents</a></p>\n' + body[closing:]
    content = content[:match.start()] + body + content[end:]
    chapters.insert(0, {'id': match.group(1), 'title': title, 'words': total_words, 'prose_words': words(prose),
                        'minutes': max(1, math.ceil(total_words / 220)), 'subsections': sections})
    low, high = WORDS_PER_CHAPTER
    assert low <= total_words <= high, f'{match.group(1)} has {total_words} words, outside {low} to {high}'

plan = re.findall(r'<li data-chapter="(ch\d+)">(.*?)</li>', contents, re.S)
assert [c for c, _ in plan] == [f'ch{n:02d}' for n in range(1, 16)], 'The plan must list chapters 1 to 15 in order'
written = {c['id']: c for c in chapters}
for chapter_id, item in plan:
    has_link = f'href="#{chapter_id}"' in item
    to_come = '(to come)' in item
    assert 'class="question"' in item, f'{chapter_id} has no question'
    assert has_link == (chapter_id in written) and to_come == (chapter_id not in written), \
        f'{chapter_id}: link and "to come" must match whether the chapter is written'
for chapter in chapters:
    sub = '<ol>' + ''.join(f'<li><a href="#{a}">{chapter["id"][2:].lstrip("0")}.{n}&nbsp; {escape(t)}</a></li>'
                           for n, (a, t) in enumerate(chapter['subsections'], 1)) + '</ol>'
    contents = re.sub(rf'(<li data-chapter="{chapter["id"]}">.*?)(</li>)', lambda m: m.group(1) + sub + m.group(2),
                      contents, count=1, flags=re.S)

html = template.replace('{{CONTENTS}}', contents).replace('{{CONTENT}}', content)
assert not re.search(r'\{\{[A-Z_]+\}\}', html), 'Unresolved template marker'
OUT.write_text(html)


# ---- structural audit, as the guide's build makes it -------------------------------------------
class Audit(HTMLParser):
    def __init__(self):
        super().__init__(); self.ids = []; self.hrefs = []; self.resources = []; self.stack = []; self.errors = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        if 'href' in a: self.hrefs.append(a['href'])
        if 'src' in a: self.resources.append(a['src'])
        if tag not in {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source',
                       'track', 'wbr'}:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if not self.stack or self.stack[-1] != tag: self.errors.append((tag, self.stack[-5:]))
        else: self.stack.pop()


audit = Audit(); audit.feed(html)
dupes = sorted({x for x in audit.ids if audit.ids.count(x) > 1})
assert not dupes, dupes
bad = [h for h in audit.hrefs if h.startswith('#') and h[1:] not in audit.ids]
assert not bad, bad
assert len(audit.resources) == len(FIGURE_ORDER) and all(r.startswith('data:image/svg+xml;base64,') for r in audit.resources)
assert not audit.errors, audit.errors
assert not audit.stack, audit.stack

summary = {'file': str(OUT), 'bytes': OUT.stat().st_size, 'chapters': chapters, 'figures': FIGURE_ORDER,
           'sources': sources, 'exercises': len(re.findall('class="exercise"', content)),
           'defined_terms': term_report,
           'checks': 'passed: no term before its defining paragraph, no sentence over 25 words, no semicolon or dash '
                     'joining clauses, chapter length, figure order, source paths and lines at both commits, '
                     'contents plan, balanced markup, unique IDs, internal anchors, no external assets'}
(HERE / 'build-report.json').write_text(json.dumps(summary, indent=2) + '\n')
print(json.dumps({k: v for k, v in summary.items() if k != 'defined_terms'}, indent=2))
print('defined terms, in order of definition:')
for t in term_report:
    print(f"  {t['term']:<38} defined in block {t['defined_in_block']:>3}, first used in block {t['first_used_in_block']:>3}")
