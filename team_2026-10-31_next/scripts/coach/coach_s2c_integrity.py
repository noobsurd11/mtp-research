"""coach (14 Nov 2026): integrity checks for the SKR2C opening (protocol_SKR2C v1, E1 opening #7), own commands, run ON gaint.
Reads only; writes nothing but stdout. No metric value of the sealed sets is printed: md5s, counts, names, booleans.
Training stdouts are only counted (number of matching lines), never printed.
  1 FROZEN.md5 on gaint and in the project (md5, md5sum -c, set membership, read-only, no __pycache__)
  2 MANIFESTs of post/ and d_out/ at source and at the project copy (md5, md5sum -c, file lists, coverage)
  3 end lines of opening.log / post.log / d_run.log; no HOLD
  4 decision_rc.txt / extra_rc.txt
  5 real splits: (a) the opening's own assert logs; (b) my own check of every per-cell file against the real lists
    (el_f3 data/splits/test.txt a31fad14, val.txt 9dcccf00, ext117 stems_eval.txt 5266806b) and against the training root's
    test.txt (= val copy): m0 default / tau0 / tau1, scuffign, B5 records (rec, rec_w), LA per_cell, rescore n, D files
  6 exactly the 10 fresh runs scored (file lists, run names inside the JSONs, D members, latest.pth md5s three ways)
  7 scorer md5s against the expected list (md5sum -c now) and against the md5s named in review_s2c_stage2.md
  8 tau 0 == default cells for the 10 runs; step 20000; code_revision per arm
  9 worktrees, launch.log, training completeness (counts), config diffs vs pf2_SUPPF_100pct_s5
 10 the gaint readout script: diff vs the frozen script changes no scoring command
Runs 1 to 3 (04:45 to 04:47 IST, 14 Nov) flagged 4 lines or stopped on a KeyError; all were wrong expectations in this file, none a
fault of the opening: 13 real-splits calls expected (the driver makes 11); the B5 records' 'runs' field expected as a bare name (it is
the run dir path); the LA JSON expected with 20 keys (it has 40: each tau also with _maskabsent) and with 'check_max_abs_diff' in
every entry (not all have it); and a line-picking heuristic for the scoring commands (replaced by the whole-tail comparison).
Corrected and rerun; integrity.txt is a later run with every line ok.
Usage: python -B coach_s2c_integrity.py"""
import hashlib, json, os, re, subprocess, sys
from pathlib import Path

W = Path('/home/noob/work'); G = W / 's2c'; T = Path('/home/yugma/mtp/research/team_2026-10-31_next'); R = T.parent
RR, RD = T / 'results/s2c/raw_r', T / 'results/s2c/raw_d'
FZ = '836be7e50c509339266097f4ba712f67'; MAN = {'post': 'bb6dffeafbdf68764b08400cc22441bb', 'd_out': '648ff42b00b11d0535d5a6aaed59214e'}
ARMS = {'SKR01': ('el_thin', 'c9bbb02'), 'SUPPF': ('el_f3', 'e544133')}
RUNS = {a: [f's2c_{a}_100pct_s{k}' for k in range(10, 15)] for a in ARMS}
BAD = []


def md5f(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 22), b''):
            h.update(b)
    return h.hexdigest()


def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
    return r.returncode, (r.stdout + r.stderr).strip()


def say(lab, ok, extra=''):
    if not ok:
        BAD.append(lab)
    print(f'  [{"ok" if ok else "PROBLEM"}] {lab}' + (f' | {extra}' if extra else ''), flush=True)


def lines(p):
    return [l.rstrip('\n') for l in open(p)]


def count(p, pat):
    rx = re.compile(pat); return sum(1 for l in open(p, errors='replace') if rx.search(l))


print(f'# coach integrity, SKR2C opening (E1 #7); host {os.uname().nodename}, user {os.environ.get("USER")}, {sh("date +%F_%T_%Z")[1]}')
print('## 1. FROZEN')
a, b, c = md5f(G / 'open/FROZEN.md5'), md5f(T / 'scripts/s2c/opening/FROZEN.md5'), md5f(G / 'post/FROZEN_s2c.md5')
say(f'FROZEN.md5 md5: gaint open/ {a[:8]}, project {b[:8]}, copy in post/ {c[:8]} == registered {FZ[:8]}', a == b == c == FZ)
rc, o = sh('md5sum -c --quiet FROZEN.md5', G / 'open'); n = len(lines(G / 'open/FROZEN.md5')); say(f'gaint md5sum -c FROZEN.md5 ({n} files)', rc == 0 and n == 27, o)
rc, o = sh('md5sum -c --quiet FROZEN.md5', T / 'scripts/s2c/opening'); say('project md5sum -c FROZEN.md5', rc == 0, o)
rc, o = sh('md5sum -c --quiet s2c_copies.md5', G / 'open'); say(f'gaint md5sum -c s2c_copies.md5 ({len(lines(G / "open/s2c_copies.md5"))} files)', rc == 0, o)
listed = {l.split('  ', 1)[1].lstrip('./') for l in lines(G / 'open/FROZEN.md5')}
have = {str(p.relative_to(G / 'open')) for p in (G / 'open').rglob('*') if p.is_file()} - {'FROZEN.md5'}
say(f'files in open/ == FROZEN list ({len(have)} files)', have == listed, f'extra {sorted(have - listed)} missing {sorted(listed - have)}')
wr = [str(p) for p in (G / 'open').rglob('*') if p.is_file() and (p.stat().st_mode & 0o222)]
say('no writable file and no __pycache__ in open/', not wr and not list((G / 'open').rglob('__pycache__')), f'writable {wr}')
mt = max(p.stat().st_mtime for p in (G / 'open').rglob('*') if p.is_file())
print(f'  newest file mtime in open/: {sh(f"date -d @{int(mt)} +%F_%T")[1]} (opening start 2026-11-14 00:22:45)')

print('## 2. MANIFESTs')
for d, cp in (('post', RR), ('d_out', RD)):
    ms, mc = md5f(G / d / 'MANIFEST.md5'), md5f(cp / 'MANIFEST.md5')
    say(f'{d}/MANIFEST.md5 md5 source {ms} == copy == expected', ms == mc == MAN[d])
    for lab, p in (('source', G / d), ('copy', cp)):
        rc, o = sh('md5sum -c --quiet MANIFEST.md5', p); say(f'{d} {lab} md5sum -c', rc == 0, o)
    fs = sorted(str(p.relative_to(G / d)) for p in (G / d).rglob('*') if p.is_file()); fc = sorted(str(p.relative_to(cp)) for p in cp.rglob('*') if p.is_file())
    cov = {l.split('  ', 1)[1].lstrip('./') for l in lines(G / d / 'MANIFEST.md5')}
    say(f'{d}: {len(fs)} files at source == copy; MANIFEST covers all but itself ({len(cov)} lines)', fs == fc and set(fs) - {'MANIFEST.md5'} == cov)

print('## 3. end lines')
for f in ('opening.log', 'post.log', 'd_run.log'):
    for l in lines(G / f):
        print(f'  {f}: {l}')
say("opening.log last line ends 's2c opening done: R rc=0 D rc=0'", lines(G / 'opening.log')[-1].endswith('s2c opening done: R rc=0 D rc=0'))
say("post.log last line ends 's2c scoring done: post rc=0'", lines(G / 'post.log')[-1].endswith('s2c scoring done: post rc=0'))
say("d_run.log last line ends 's2c D full end rc=0'", lines(G / 'd_run.log')[-1].endswith('s2c D full end rc=0'))
say('no s2c/HOLD, no opening_refused.log, post_pre.log empty', not (G / 'HOLD').exists() and not (G / 'opening_refused.log').exists() and (G / 'post_pre.log').stat().st_size == 0)
say(f"opening.log FROZEN md5 in the start line == {FZ[:8]}", FZ in lines(G / 'opening.log')[0])

print('## 4. rc files')
dr, er = lines(G / 'post/decision_rc.txt'), lines(G / 'post/extra_rc.txt')
say(f'decision_rc.txt: {"; ".join(dr)}', dr == ['e1_coprim rc=0', 'b5w rc=0', 'realsplits_b5 rc=0', 'guards rc=0', 'named_boot rc=0'])
say(f'extra_rc.txt: {"; ".join(er)}', er == ['enc_cosine rc=0', 'cellgate rc=0', 'scuffign rc=0', 'realsplits_scuffign rc=0'])

print('## 5a. the opening\'s own real-splits asserts')
rs = lines(G / 'post/realsplits.txt')
calls = [l for l in rs if l.startswith('== ')]; passes = [l for l in rs if l.startswith('REALSPLITS')]
say(f'realsplits.txt: {len(calls)} calls, {len(passes)} PASS lines, {sum("-> True" in l for l in rs)} "-> True", {sum(("False" in l) or ("FAIL" in l) for l in rs)} False / FAIL',
    len(calls) == len(passes) == 11 and all(l.endswith(' PASS') for l in passes) and not any(('False' in l) or ('FAIL' in l) for l in rs))
print('   modes: ' + ', '.join(f'{m} x{sum(1 for l in passes if l.split()[1] == m)}' for m in dict.fromkeys(l.split()[1] for l in passes)))
ds = lines(G / 'd_realsplits.txt'); say(f'd_realsplits.txt: {[l for l in ds if l.startswith("REALSPLITS")]}; 3 E-*.b*.json files', ds[-1] == 'REALSPLITS d PASS' and not any('False' in l for l in ds))

print('## 5b. my own real-splits check (stems of every per-cell file vs the real lists)')
rd = lambda p: sorted(l.strip() for l in open(p) if l.strip())
TEST, VAL, EXT = rd(W / 'el_f3/data/splits/test.txt'), rd(W / 'el_f3/data/splits/val.txt'), rd(W / 'el_f1/reports/f1/ext117/stems_eval.txt')
ROOT_TEST = rd(W / 's2c_root/splits/test.txt')
m = {p: md5f(W / p)[:8] for p in ('el_f3/data/splits/test.txt', 'el_f3/data/splits/val.txt', 'el_thin/data/splits/test.txt', 'el_thin/data/splits/val.txt',
                                    'el_f1/reports/f1/ext117/stems_eval.txt', 's2c_root/splits/test.txt', 's2c_root/splits/val.txt', 's2c_root/SPLITS.md5')}
say(f'real lists: el_f3 test {m["el_f3/data/splits/test.txt"]} ({len(TEST)}), val {m["el_f3/data/splits/val.txt"]} ({len(VAL)}); el_thin test {m["el_thin/data/splits/test.txt"]}, val '
    f'{m["el_thin/data/splits/val.txt"]}; ext117 stems_eval {m["el_f1/reports/f1/ext117/stems_eval.txt"]} ({len(EXT)})',
    m['el_f3/data/splits/test.txt'] == m['el_thin/data/splits/test.txt'] == 'a31fad14' and m['el_f3/data/splits/val.txt'] == m['el_thin/data/splits/val.txt'] == '9dcccf00'
    and m['el_f1/reports/f1/ext117/stems_eval.txt'] == '5266806b' and (len(TEST), len(VAL), len(EXT)) == (50, 54, 106))
say(f'training root: test.txt {m["s2c_root/splits/test.txt"]} == val.txt {m["s2c_root/splits/val.txt"]} (the val copy); SPLITS.md5 {m["s2c_root/SPLITS.md5"]}; real test and val lists share '
    f'{len(set(TEST) & set(VAL))} stems; test and E1 share {len(set(TEST) & set(EXT))}', ROOT_TEST == VAL and m['s2c_root/SPLITS.md5'] == '24568cdb' and not set(TEST) & set(VAL) and not set(TEST) & set(EXT))
SM = {'val': VAL, 'val_tta': VAL, 'test': TEST, 'test_noscuff': TEST, 'ext': EXT}
nfile = 0; badf = []
M0 = {}
for arm, runs in RUNS.items():
    for r in runs:
        for suf in ('', '.tau0', '.tau1'):
            j = json.load(open(RR / f'm0/{arm}/{r}{suf}.json')); nfile += 1
            if suf == '':
                M0[r] = j
            ok = all(sorted(j['cells'][s]) == SM[s] for s in ('val', 'val_tta', 'test', 'ext')) and set(j['cells']) == {'val', 'val_tta', 'test', 'ext'} and sorted(j['cells']['test']) != ROOT_TEST
            if not ok:
                badf.append(f'm0/{arm}/{r}{suf}')
        j = json.load(open(RR / f'm0_scuffign/{arm}/{r}.scuffign.json')); nfile += 1
        if not all(sorted(j['cells'][s]) == SM[s] for s in ('val', 'val_tta', 'test', 'ext')):
            badf.append(f'm0_scuffign/{arm}/{r}')
        for d in ('rec', 'rec_w'):
            for s, ref in (('val', VAL), ('test', TEST), ('ext', EXT)):
                j = json.load(open(RR / f'b5/{arm}/{d}/{r}.{s}.json')); nfile += 1
                if not (sorted(j['cells']) == ref and j['set'] == s and j['runs'] == [str(W / ARMS[arm][0] / 'experiments' / r)]):
                    badf.append(f'b5/{arm}/{d}/{r}.{s}')
        j = json.load(open(RR / f'rescore/{arm}/{r}.json')); nfile += 1
        if not (j[f'test/{r}']['n'] == 50 and j[f'val/{r}']['n'] == 54 and j[f'test/{r}']['step'] == 20000):
            badf.append(f'rescore/{arm}/{r}')
    j = json.load(open(RR / f'la_{arm}.json')); nfile += 1
    exp = {f'{s}/{r}/tau{t}{m_}' for s in ('test', 'val') for r in runs for t in (0, 1) for m_ in ('', '_maskabsent')}
    ok = set(j) == exp and all(j[k]['n'] == (50 if k.startswith('test') else 54) and (not j[k].get('per_cell') or sorted(j[k]['per_cell']) == (TEST if k.startswith('test') else VAL)) for k in j)
    ok = ok and all(sorted(j[k]['per_cell']) == TEST for k in j if k.startswith('test')) and all(j[k]['step'] == 20000 and j[k].get('check_max_abs_diff', 0.0) == 0.0 for k in j)
    if not ok:
        badf.append(f'la_{arm}')
DF = sorted(p.name for p in RD.glob('E-*.json'))
for f in DF:
    j = json.load(open(RD / f)); nfile += 1
    if not (all(sorted(j['cells'][s]) == SM[s] for s in ('val', 'test', 'test_noscuff', 'ext')) and set(j['cells']) == {'val', 'test', 'test_noscuff', 'ext'}):
        badf.append(f)
say(f'{nfile} per-cell / per-run files: test stems == the real 50 (a31fad14 list), ext stems == the 106 E1 cells, val stems == the real 54; no file holds the training root\'s test list as "test"', not badf, f'bad {badf}')

for arm in RUNS:
    rc, o = sh(f'md5sum -c --quiet {G}/post/b5/{arm}/dump_md5_on_gaint.txt', G / f'post_work/b5/{arm}/dump')
    say(f'B5 dumps of {arm} in post_work (15 npz) == dump_md5_on_gaint.txt', rc == 0 and len(lines(G / f"post/b5/{arm}/dump_md5_on_gaint.txt")) == 15, o)
    for d in ('rec', 'rec_w', 'sum', 'sum_w'):
        same = all(md5f(q) == md5f(RR / f'b5/{arm}/{d}/{q.name}') for q in (G / f'post_work/b5/{arm}/{d}').glob('*') if q.is_file())
        say(f'B5 {arm}/{d}: files in post_work == copies in post/ ({len(list((G / f"post_work/b5/{arm}/{d}").glob("*")))} files)', same)
print('## 6. exactly the 10 fresh runs')
for arm, runs in RUNS.items():
    got = sorted(p.name for p in (RR / f'm0/{arm}').glob('*.json'))
    exp = sorted(f'{r}{s}.json' for r in runs for s in ('', '.tau0', '.tau1'))
    say(f'm0/{arm}: {len(got)} JSONs = s10..s14 x (default, tau0, tau1); run names inside == file names', got == exp and all(M0[r]['run'] == r for r in runs))
    say(f'{arm}: scuffign / rescore / rec / rec_w hold exactly the 5 runs',
        sorted(p.name for p in (RR / f'm0_scuffign/{arm}').glob('*.json')) == sorted(f'{r}.scuffign.json' for r in runs)
        and sorted(p.name for p in (RR / f'rescore/{arm}').glob('*.json')) == sorted(f'{r}.json' for r in runs)
        and all(sorted(p.name for p in (RR / f'b5/{arm}/{d}').glob('*.json')) == sorted(f'{r}.{s}.json' for r in runs for s in ('val', 'test', 'ext')) for d in ('rec', 'rec_w')))
say(f'D per-cell files: {DF}', DF == ['E-SKR2.b-0.45.json', 'E-SKR2.b0.json', 'E-SUPPF.b0.json'])
DJ = {f: json.load(open(RD / f)) for f in DF}
for f, j in DJ.items():
    arm = 'SKR01' if 'SKR2' in f else 'SUPPF'
    say(f'{f}: members {[Path(x).name if "/" in x else x for x in j["members"]]}; step {j["step"]}; code_revision {j["code_revision"]}; model code {j["model_code_revision"]}; bias {j["bias"]}',
        [re.search(r's2c_\w+_100pct_s\d+', x).group(0) for x in j['members']] == RUNS[arm] and j['step'] == 20000 and j['code_revision'] == ARMS[arm][1] and j['model_code_revision'] == 'e544133'
        and j['bias'] == (-0.45 if 'b-0.45' in f else 0.0))
ic = {l.split()[0]: l.split(';')[-1].split()[0] for l in lines(G / 'post/init_check.txt')}
ml = lines(RD / 'member_latest_md5.txt'); mlm = {}
for l in ml:
    q = re.search(r'(s2c_\w+_100pct_s\d+)', l); h = re.search(r'\b([0-9a-f]{32})\b', l)
    if q and h:
        mlm[q.group(1)] = h.group(1)
act = {r: md5f(W / ARMS[arm][0] / 'experiments' / r / 'checkpoints/latest.pth') for arm, runs in RUNS.items() for r in runs}
say(f'latest.pth md5 of the 10 runs: R init_check.txt == D member_latest_md5.txt == the files now ({len(act)} runs)', ic == act and mlm == act, f'init {len(ic)} member {len(mlm)}')
for r in sorted(act):
    print(f'    {r} {act[r]}')
for arm, (wt, _) in ARMS.items():
    others = sorted(p.name for p in (W / wt / 'experiments').glob('s2c_*') if p.is_dir() and p.name not in RUNS[arm])
    say(f'{wt}/experiments: no other s2c_* run dir, no *_STOPPED_*', not others and not list((W / wt / 'experiments').glob('*STOPPED*')), f'{others}')

print('## 7. scorer md5s')
rc, o = sh(f'md5sum -c --quiet {G}/post/scorer_md5_expected.txt', '/'); exp = lines(G / 'post/scorer_md5_expected.txt')
say(f'md5sum -c scorer_md5_expected.txt now ({len(exp)} files)', rc == 0 and len(exp) == 22, o)
sm = lines(G / 'post/scorer_md5.txt'); say(f"the opening's scorer_md5.txt: {sum(l.endswith(': OK') for l in sm)} OK of {len(sm)}", len(sm) == 22 and all(l.endswith(': OK') for l in sm))
REV = {'el_f1/reports/f1/m0_audit.py': 'd36f7438', 'el_f1/reports/f1/m0_audit_tau.py': 'd77241bb', 'el_thin/scripts/b3/m0_audit_b3.py': '7aa7d6d8',
       'el_thin/scripts/rescore_label_versions.py': '1e41202b', 'el_f3/scripts/rescore_label_versions.py': '1e41202b', 'el_f3/scripts/rescore_logit_adjust.py': 'ec315d2e',
       'el_thin/scripts/rescore_logit_adjust.py': '419486b1', 'el_f3/reports/pf2/scripts/gpu_gate.sh': '00fabfdd', 'el_f3/reports/d/e1_context.tsv': '12bd1385',
       'el_f1/reports/f1/ext117/stems_eval.txt': '5266806b', 'el_f3/data/splits/val.txt': '9dcccf00', 'el_f3/data/splits/test.txt': 'a31fad14', 'el_thin/data/splits/val.txt': '9dcccf00',
       'el_thin/data/splits/test.txt': 'a31fad14', 's2c/exp_SKR01.txt': '1343cca2', 's2c/exp_SUPPF.txt': 'dc9c344a', 's2c_root/SPLITS.md5': '24568cdb', 's2c/launch.log': '5d2544a7'}
em = {l.split('  ', 1)[1].replace('/home/noob/work/', ''): l[:8] for l in exp}
say(f'expected list == the md5s named in review_s2c_stage2.md / build_s2c_stage2.md ({len(REV)} of {len(em)} named there)', all(em.get(k) == v for k, v in REV.items()), str({k: em.get(k) for k, v in REV.items() if em.get(k) != v}))
print('   not named in the review (md5 as pinned by the frozen driver): ' + ', '.join(f'{k} {v}' for k, v in em.items() if k not in REV))
fz = {l.split('  ', 1)[1].lstrip('./'): l[:8] for l in lines(G / 'open/FROZEN.md5')}
FRZ = {'s2c_settings.sh': '6766a6b0', 's2c_post.sh': '2111dbef', 's2c_e1_coprim.py': '7d40ba12', 's2c_guards.py': '95312e8f', 'post_extra/s2c_b5w.sh': 'b80ca030', 'post_extra/s2c_scuffign.sh': '2baf71e5',
       'd/s2c_d_infer.py': '6fccdbdf', 'd/s2c_d_run.sh': '6f1d305f', 'local/s2c_d_boot.py': '164ef377', 'local/s2c_post_local.sh': '1da9a692', 's2c_opening.sh': 'fc809364', 's2c_realsplits.py': '9af1af71',
       's2c_named_boot.py': 'f227d00a', 's2c_ckpt_check.py': 'fab969ce', 's2c_gates.sh': 'ad0122f8', 'selftest_ref/coach_s2_boot.txt': '7ce0faa0', 's2_b5w_check.py': '60423dde', 's2_cellgate.py': '0ed83bf5',
       'calib_w/el_metrics_w.py': '45b1df03', 'trackM/m0_analyze.py': 'd5adbe6b', 'thin/thin_e1_relf1.py': '98bcb979', 'post_extra/pf2_scuffign.py': 'e3615fdb', 'post_extra/calib/calib_dump.py': 'c172717e',
       'post_extra/calib/el_metrics.py': '6e73ff11', 'post_extra/calib/pf2_b5_hook.sh': 'e06dfc5f', 'post_extra/calib/pf2_b5_pooled.sh': '873591ff', 's2c_copies.md5': '1adcaeaa'}
say('FROZEN.md5 entries == the 27 md5s of build_s2c_stage2.md section 4', fz == FRZ, str({k: (fz.get(k), v) for k, v in FRZ.items() if fz.get(k) != v}))
say(f'D scripts copied into d_out == the frozen ones (s2c_d_infer.py {md5f(RD / "s2c_d_infer.py")[:8]}, s2c_d_run.sh {md5f(RD / "s2c_d_run.sh")[:8]}); settings used {md5f(RR / "s2c_settings_used.sh")[:8]}',
    md5f(RD / 's2c_d_infer.py')[:8] == '6fccdbdf' and md5f(RD / 's2c_d_run.sh')[:8] == '6f1d305f' and md5f(RR / 's2c_settings_used.sh')[:8] == '6766a6b0')
cc = lines(G / 'post/comparator_check.txt')
say('comparator_check.txt: PF2 3827f7c0, HC d5c39e0d, THIN 5d3f5b31, S2 bd671e26, SKR2E 9b43e636 unchanged', all(x in cc[0] for x in ('3827f7c0', 'd5c39e0d', '5d3f5b31', 'bd671e26', '9b43e636')))

print('## 8. tau 0 == default; step; code revision')
for arm, runs in RUNS.items():
    same = all(M0[r]['cells'] == json.load(open(RR / f'm0/{arm}/{r}.tau0.json'))['cells'] for r in runs)
    diff1 = sum(M0[r]['cells'] != json.load(open(RR / f'm0/{arm}/{r}.tau1.json'))['cells'] for r in runs)
    say(f'{arm}: tau0 cells == default cells for all 5 (my comparison); tau1 differs from default in {diff1} of 5; step 20000; code_revision {ARMS[arm][1]}; conf 24x24',
        same and all(M0[r]['step'] == 20000 and M0[r]['code_revision'] == ARMS[arm][1] for r in runs) and all(len(c['conf']) == 576 for r in runs for s in ('val', 'test', 'ext') for c in M0[r]['cells'][s].values()))
    print(f'   the opening\'s tau0_check_{arm}.txt: {lines(G / f"post/tau0_check_{arm}.txt")[0]}')

print('## 9. worktrees, queue log, training completeness (counts only), config diffs')
for arm, (wt, dep) in ARMS.items():
    h = sh('git rev-parse --short=7 HEAD', W / wt)[1]; rv = open(W / wt / 'REVISION').read().strip()[:7]; ch = sh('git status --short --untracked-files=no', W / wt)[1]
    say(f'{wt}: HEAD {h} REVISION {rv} tracked changes {len(ch.splitlines())} (expect {dep}, 0)', h == rv == dep and not ch)
LL = G / 'launch.log'
say(f'launch.log md5 {md5f(LL)[:8]} (5d2544a7); "S2C ALL TRAINED (10 rc 0 of 10" x{count(LL, r"S2C ALL TRAINED \(10 rc 0 of 10")}; HOLD / FAIL / MISMATCH lines {count(LL, r"HOLD|FAIL|MISMATCH")}',
    md5f(LL)[:8] == '5d2544a7' and count(LL, r'S2C ALL TRAINED \(10 rc 0 of 10') == 1 and count(LL, r'HOLD|FAIL|MISMATCH') == 0)
say(f'autostop.log md5 {md5f(G / "autostop.log")[:8]}: trigger / SIGTERM / SIGKILL lines {count(G / "autostop.log", r"(?i)trigger|SIGTERM|SIGKILL")}', count(G / 'autostop.log', r'(?i)trigger|SIGTERM|SIGKILL') == 0)
REF = lines(W / 'el_f3/experiments/pf2_SUPPF_100pct_s5/config_used.yaml')
for arm, (wt, dep) in ARMS.items():
    expf = sorted(l for l in lines(G / f'exp_{arm}.txt') if l.strip())
    for r in RUNS[arm]:
        k = r.rsplit('_s', 1)[1]; so = W / wt / 'experiments' / f'{r}.stdout'; cfg = lines(W / wt / 'experiments' / r / 'config_used.yaml')
        d = sorted({('< ' + l).rstrip() for l in cfg if l not in REF} | {('> ' + l).rstrip() for l in REF if l not in cfg})
        dd = [l for l in d if not re.match(r'^[<>] (run_name|seed):|^[<>]   experiments_dir:', l)]
        n = (count(so, 'INFO train — Run: '), count(so, 'step 20000/20000'), count(so, 'Traceback'), count(so, 'val: 54  test: 54'))
        ok = n == (1, 1, 0, 1) and count(LL, rf'\] config OK {r} vs pf2_SUPPF_100pct_s5: ') == 1 and count(LL, rf'\] trained {r} rc=0$') == 1 and f'seed: {k}' in cfg and dd == expf \
            and open(G / f'pids/{r}.rc').read().strip() == '0'
        say(f'{r}: stdout header x{n[0]}, "step 20000/20000" x{n[1]}, Traceback x{n[2]}, "val: 54  test: 54" x{n[3]}; launch.log config OK x1, trained rc=0 x1; rc file 0; seed {k}; '
            f'config diff vs pf2_SUPPF_100pct_s5 beyond run_name / seed / experiments_dir = {[x[2:].strip() for x in dd]}', ok, f'exp file {expf}')
    print(f'   exp_{arm}.txt md5 {md5f(G / f"exp_{arm}.txt")[:8]}')

print('## 10. gaint readout script vs the frozen script')
fz_s, gt_s, df_s = T / 'scripts/s2c/opening/local/s2c_post_local.sh', T / 'scripts/s2c/readout_gaint/s2c_post_local_gaint.sh', T / 'scripts/s2c/readout_gaint/s2c_post_local_gaint.diff'
say(f'frozen s2c_post_local.sh {md5f(fz_s)[:8]} (FROZEN lists 1da9a692); gaint copy {md5f(gt_s)[:8]}; stored diff {md5f(df_s)[:8]}', md5f(fz_s)[:8] == '1da9a692')
mine = sh(f'diff -u {fz_s} {gt_s}')[1].split('\n')[2:]; stored = lines(df_s)[2:]
say('stored diff == my diff -u of the two files (below the 2 header lines)', mine == stored)
strip = lambda L: [re.sub(r'\s*2> ?\S+', '', l) for l in L]
t0 = next(i for i, l in enumerate(lines(fz_s)) if '$M2 --label SKR01_vs_SUPPF --a' in l); t1 = next(i for i, l in enumerate(lines(gt_s)) if '$M2 --label SKR01_vs_SUPPF --a' in l)
say('from the first m2_rung call to the end, the two files are equal after dropping the stderr redirect', strip(lines(fz_s)[t0:]) == strip(lines(gt_s)[t1:]))
chg = [l for l in mine if l.startswith(('+', '-')) and not l[1:].lstrip().startswith('#')]
print(f'   changed non-comment lines in the diff: {len(chg)}; of them with PY= / PYB= (interpreter): {sum(("PY=" in l or "PYB=" in l) for l in chg)}; ssh / rsync (transport): {sum(("ssh" in l or "rsync" in l) for l in chg)}')
TM = R / 'team_2026-10-24_go/trackM/scripts'
say(f'Track M: m2_rung {md5f(TM / "m2_rung.py")[:8]} m1_analyze {md5f(TM / "m1_analyze.py")[:8]} m0_analyze {md5f(TM / "m0_analyze.py")[:8]}; e1_context {md5f(R / "team_2026-10-29_features/scripts/e1_context.tsv")[:8]}; '
    f'frozen s2c_d_boot.py {md5f(T / "scripts/s2c/opening/local/s2c_d_boot.py")[:8]}',
    (md5f(TM / 'm2_rung.py')[:8], md5f(TM / 'm1_analyze.py')[:8], md5f(TM / 'm0_analyze.py')[:8]) == ('0ae9d505', '8e566254', 'd5adbe6b') and md5f(R / 'team_2026-10-29_features/scripts/e1_context.tsv')[:8] == '12bd1385'
    and md5f(T / 'scripts/s2c/opening/local/s2c_d_boot.py')[:8] == '164ef377')
print(f'\nINTEGRITY: {"NO PROBLEM FOUND" if not BAD else str(len(BAD)) + " PROBLEM(S): " + "; ".join(BAD)}')
