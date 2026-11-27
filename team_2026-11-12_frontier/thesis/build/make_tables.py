#!/usr/bin/env python3
"""Build THESIS_TABLES.md, thesis_tables.tex and SOURCES.tsv from tables_data.py (thesis_tables, 21 Nov 2026).

Checks, and stops on the first failure:
  1. every anchor matches exactly one line of its source file;
  2. every value is a substring of that line (the number is copied, not recomputed);
  3. every value is a substring of the row's own cells (the table shows the copied string).
Run:  python3 -I make_tables.py   (from T/thesis/build/). Reads only result text files; writes only T/thesis/.
"""
import hashlib
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
T = os.path.abspath(os.path.join(HERE, '..', '..'))
OUT = os.path.abspath(os.path.join(HERE, '..'))
sys.path.insert(0, HERE)
from tables_data import P, TABLES  # noqa: E402
import intro_text  # noqa: E402

_cache = {}


def src_path(key):
    p = P[key]
    return p if os.path.isabs(p) else os.path.join(T, p)


def show_path(key):
    p = P[key]
    return p if os.path.isabs(p) else 'T/' + p


def load(key):
    if key not in _cache:
        path = src_path(key)
        data = open(path, 'rb').read()
        _cache[key] = (data.decode('utf-8').split('\n'), hashlib.md5(data).hexdigest())
    return _cache[key]


def resolve(key, anchor):
    lines, md5 = load(key)
    k = 0
    m = re.match(r'#(\d+):(.*)$', anchor, re.S)
    if m:  # '#k:' = the k-th line holding the string (record traces where the value recurs; context checked by hand)
        k, anchor = int(m.group(1)), m.group(2)
    hits = [i for i, ln in enumerate(lines) if anchor in ln]
    if k:
        if len(hits) < k:
            raise SystemExit('ANCHOR %s in %s has %d < %d hits: %r' % (key, P[key], len(hits), k, anchor))
        hits = [hits[k - 1]]
    if len(hits) != 1:
        raise SystemExit('ANCHOR %s in %s matched %d lines: %r' % (key, P[key], len(hits), anchor))
    return hits[0] + 1, lines[hits[0]], md5


def check_and_collect():
    rows_out = []
    n_values = 0
    for t in TABLES:
        groups = [(r['cells'], r['src'], r['cells'][0]) for r in t['rows']]
        for k, (text, src) in enumerate(t.get('notes', [])):
            groups.append(([text], src, 'note %d' % (k + 1)))
        for cells, src, label in groups:
            assert len(cells) == len(t['header']) or label.startswith('note'), (t['id'], label, len(cells))
            rowtext = ' | '.join(cells)
            for tup in src:
                if tup[0] == '=':  # derived value: ('=', expression, printed value, format)
                    _, expr, val, fmt = tup
                    got = fmt % eval(expr, {'__builtins__': {}})
                    if got != val:
                        raise SystemExit('DERIVED mismatch %s %s: %s gives %s, printed %s' % (t['id'], label, expr, got, val))
                    if val not in rowtext:
                        raise SystemExit('DERIVED value not in row: %s %s %r' % (t['id'], label, val))
                    col = 'note' if label.startswith('note') else next(t['header'][i] for i, c in enumerate(cells) if val in c)
                    cmd = 'python3 -c "print(\'%s\' %% (%s))"' % (fmt, expr)
                    rows_out.append((t['id'], label, col, val, '(derived)', '', '', 'yes', cmd))
                    n_values += 1
                    continue
                key, anchor, values = tup
                line_no, line, md5 = resolve(key, anchor)
                for v in values:
                    if v not in line:
                        raise SystemExit('VALUE not on source line: %s %s %r\n  line %d: %s' % (t['id'], label, v, line_no, line))
                    if v not in rowtext:
                        raise SystemExit('VALUE not in table row: %s %s %r\n  row: %s' % (t['id'], label, v, rowtext))
                    if label.startswith('note'):
                        col = 'note'
                    else:
                        tok = re.compile(r'(?<![\d.])' + re.escape(v) + r'(?![\d])')
                        cand = [i for i, c in enumerate(cells) if tok.search(c)] or [i for i, c in enumerate(cells) if v in c]
                        col = t['header'][cand[0]]
                    rows_out.append((t['id'], label, col, v, show_path(key), str(line_no), md5, 'no', ''))
                    n_values += 1
    return rows_out, n_values


def md_cell(s):
    assert '|' not in s, s
    return s


def write_md(path, stats=''):
    o = [intro_text.HEAD.strip(), '', 'Last check run: ' + stats, '']
    o.append('## 1. Outline and proposed placement')
    o.append('')
    o.append('| Id | Title | Rows | Placement | Sources |')
    o.append('|---|---|---|---|---|')
    for t in TABLES:
        keys = []
        for r in t['rows']:
            for s in r['src']:
                if s[0] != '=' and s[0] not in keys:
                    keys.append(s[0])
        srcs = ', '.join(os.path.basename(P[k]) if k not in ('FOV', 'E1R', 'FTV') else P[k].split('results/')[-1] for k in keys)
        o.append('| %s | %s | %d | %s | %s |' % (t['id'], t['title'], len(t['rows']), t['place'], srcs))
    o.append('')
    o.append(intro_text.PLACEMENT.strip())
    o.append('')
    o.append('## 2. Tables')
    o.append('')
    for t in TABLES:
        o.append('### %s. %s' % (t['id'], t['title']))
        o.append('')
        o.append('Placement: %s. Tags: %s.' % (t['place'], t['tag']))
        o.append('')
        o.append(t['caption'])
        o.append('')
        o.append('| ' + ' | '.join(t['header']) + ' |')
        o.append('|' + '---|' * len(t['header']))
        for r in t['rows']:
            o.append('| ' + ' | '.join(md_cell(c) for c in r['cells']) + ' |')
        if t.get('notes'):
            o.append('')
            for text, _ in t['notes']:
                o.append('- ' + text)
        extra = intro_text.EXTRA.get(t['id'])
        if extra:
            o.append('')
            o.append(extra.strip())
        o.append('')
    o.append(intro_text.TAIL.strip())
    o.append('')
    open(path, 'w').write('\n'.join(o))


def tex(s):
    s = s.replace('\\', r'\textbackslash{}')
    for ch in '&%$#_{}':
        s = s.replace(ch, '\\' + ch)
    s = s.replace('~', r'\textasciitilde{}').replace('^', r'\textasciicircum{}')
    s = re.sub(r"(?<![A-Za-z])'([A-Za-z0-9-]+)'", r"`\1'", s)
    s = re.sub(r'"([^"]*)"', r"``\1''", s)
    s = re.sub(r'\*\*(.+?)\*\*', r'\\textbf{\1}', s)
    s = s.replace('+-', r'$\pm$').replace('<=', r'$\leq$').replace('>=', r'$\geq$')
    s = s.replace('->', r'$\rightarrow$')
    s = s.replace('<', r'$<$').replace('>', r'$>$')
    s = s.replace('\u2212', '$-$').replace('\u0394', r'$\Delta$').replace('\u2192', r'$\rightarrow$')
    s = s.replace('\u00d7', r'$\times$').replace('\u2265', r'$\geq$').replace('\u2264', r'$\leq$')
    s = s.replace('\u00b7', r'$\cdot$').replace('\u221a', r'$\surd$').replace('\u00b2', r'$^2$')
    s = s.replace(' - ', ' $-$ ')
    s = re.sub(r'(?<![A-Za-z0-9$])-(?=\d)', '$-$', s)
    return s


# Layout only (layout_fix, 23 Nov 2026). Nothing below changes a value, a word or a cell of tables_data.py.
# Tables taller than one page as floats (LaTeX "Float too large" on the 23 Nov compile): set as longtable, which
# breaks across pages and repeats the header row.
LONG = {'T6', 'T7a', 'T16a', 'T20', 'T21'}
# Column widths (relative, as tables_data 'widths') for tables where one word did not fit its column.
WIDTHS = {
    'T7a': [0.08, 0.12, 0.12, 0.11, 0.12, 0.11, 0.14, 0.20],                       # 'HOUSE' in Item
    'T11a': [0.07, 0.08, 0.16, 0.08, 0.08, 0.1, 0.1, 0.1, 0.09, 0.1],              # 'models' in the header
    'T15': [0.21, 0.095, 0.06, 0.08, 0.085, 0.12, 0.08, 0.08, 0.08, 0.08],         # 'Machine,' and 'relF1@2' in the header
    'T22': [0.07, 0.095, 0.09, 0.145, 0.07, 0.145, 0.08, 0.145, 0.12],             # 'Forwards' and 'GFLOPs' in the header
}


def brk(s):
    r"""Allow a line break after '_' and inside a/b tokens (file names, run names, paths). Adds \allowbreak{} only."""
    s = s.replace(r'\_', r'\_\allowbreak{}')
    return re.sub(r'(?<=[A-Za-z0-9.)])/(?=[A-Za-z0-9(])', r'/\\allowbreak{}', s)


def write_tex(path):
    o = [r'% thesis_tables.tex: results tables of the MTP thesis (thesis_tables, 21 Nov 2026).',
         r'% Generated by T/thesis/build/make_tables.py from tables_data.py; every value is traced in SOURCES.tsv.',
         r'% Preamble needs: \usepackage{booktabs}, \usepackage{array} and \usepackage{longtable} (tables in LONG of make_tables.py).',
         r'% Labels: tab:<id>, e.g. \ref{tab:T8}. Long tables are floats; move them to the appendix as THESIS_TABLES.md section 1 proposes.',
         '']
    for t in TABLES:
        n = len(t['header'])
        w = WIDTHS.get(t['id'], t['widths'])
        assert len(w) == n, t['id']
        scale = (0.995 - 0.014 * (n - 1)) / sum(w)
        # \hspace{0pt} lets TeX hyphenate the first word of a narrow cell
        spec = '@{}' + ''.join(r'>{\raggedright\arraybackslash\hspace{0pt}}p{%.3f\linewidth}' % (x * scale) for x in w) + '@{}'
        # full width of the table (columns plus the 2 x 3pt gaps between them), for a notes row spanning all columns
        full = r'\dimexpr %.3f\linewidth+%dpt\relax' % (sum(float('%.3f' % (x * scale)) for x in w), 6 * (n - 1))
        size = r'\footnotesize' if n <= 5 else r'\scriptsize'
        long = t['id'] in LONG
        caption = r'\caption[%s]{\textbf{%s.} %s Tags: %s.}' % (tex(t['title']), tex(t['title']), tex(t['caption']), tex(t['tag']))
        header = ' & '.join(r'\textbf{%s}' % brk(tex(h)) for h in t['header']) + r' \\'
        o.append('%% ---- %s (%s)' % (t['id'], t['place']))
        if long:
            o.append(r'\clearpage')  # earlier floats first, so table numbers stay in page order
            o.append(r'\begingroup')
            o.append(size)
            o.append(r'\setlength{\tabcolsep}{3pt}')
            o.append(r'\setlength{\LTcapwidth}{\linewidth}')
            o.append(r'\begin{longtable}{%s}' % spec)
            o.append(caption)
            o.append(r'\label{tab:%s}\\' % t['id'])
            o.append(r'\toprule')
            o.append(header)
            o.append(r'\midrule')
            o.append(r'\endfirsthead')
            o.append(r'\toprule')
            o.append(header)
            o.append(r'\midrule')
            o.append(r'\endhead')
            if not t.get('notes'):
                o.append(r'\bottomrule')
                o.append(r'\endlastfoot')
        else:
            o.append(r'\begin{table}[htbp]')
            o.append(r'\centering')
            o.append(size)
            o.append(r'\setlength{\tabcolsep}{3pt}')
            o.append(caption)
            o.append(r'\label{tab:%s}' % t['id'])
            o.append(r'\begin{tabular}{%s}' % spec)
            o.append(r'\toprule')
            o.append(header)
            o.append(r'\midrule')
        for r in t['rows']:
            cells = [brk(tex(c)) for c in r['cells']]
            if cells[0].startswith('['):
                cells[0] = '{}' + cells[0]
            o.append(' & '.join(cells) + r' \\')
        if long and t.get('notes'):
            # notes as a last row, with no page break allowed between it and the last table row
            o.append(r'\bottomrule')
            o.append(r'\noalign{\unskip\nobreak}')
            o.append(r'\multicolumn{%d}{@{}p{%s}@{}}{\scriptsize\raggedright\rule{0pt}{2.6ex}' % (n, full))
            for text, _ in t['notes']:
                o.append(brk(tex(text)) + r'\par')
            o.append(r'}\\')
        if long:
            o.append(r'\end{longtable}')
        else:
            o.append(r'\bottomrule')
            o.append(r'\end{tabular}')
        if t.get('notes') and not long:
            o.append(r'\par\smallskip')
            o.append(r'\begin{minipage}{\linewidth}\scriptsize\raggedright')
            for text, _ in t['notes']:
                o.append(brk(tex(text)) + r'\par')
            o.append(r'\end{minipage}')
        o.append(r'\endgroup' if long else r'\end{table}')
        o.append('')
    open(path, 'w').write('\n'.join(o))


def write_sources(path, rows):
    hdr = ('table_id', 'row', 'column', 'value', 'source_file', 'line', 'md5', 'derived', 'command')
    with open(path, 'w') as f:
        f.write('\t'.join(hdr) + '\n')
        for r in rows:
            f.write('\t'.join(x.replace('\t', ' ') for x in r) + '\n')


if __name__ == '__main__':
    rows, n = check_and_collect()
    write_sources(os.path.join(OUT, 'SOURCES.tsv'), rows)
    stats = 'OK: %d tables, %d rows, %d traced values, %d source files' % (
        len(TABLES), sum(len(t['rows']) for t in TABLES), n, len(_cache))
    write_md(os.path.join(OUT, 'THESIS_TABLES.md'), stats)
    write_tex(os.path.join(OUT, 'thesis_tables.tex'))
    print(stats)
