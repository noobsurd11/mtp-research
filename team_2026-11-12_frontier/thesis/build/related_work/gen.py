import hashlib, os, re, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rw_data import F, WEB, ROWS, PAPERS, ABS, OUT, NOACCESS, SRC, KNOWN_MD5

OUTDIR = sys.argv[1]
md5 = {}
for k, p in F.items():
    if os.path.exists(p):
        md5[k] = hashlib.md5(open(p, 'rb').read()).hexdigest()
        if md5[k] != KNOWN_MD5[k]:
            print('WARNING: source changed since 22 Nov:', k, p)
    else:
        md5[k] = KNOWN_MD5[k]
        print('note: source file gone, recorded md5 used:', k)
for r in ROWS + ABS:
    for v in r.values():
        assert '|' not in str(v), r['id']

# ---------- counts (per paper, full-text set) ----------
P = PAPERS
n = len(P)
def names(pred):
    return [v['name'] for v in P.values() if pred(v)]
c_int_none = names(lambda v: v['interval'] == 'none')
c_int_part = names(lambda v: v['interval'] == 'partial')
c_split_no = names(lambda v: v['split'] == 'no')
c_split_contra = names(lambda v: v['split'] == 'contradictory')
c_rel_bad = names(lambda v: v['release'] in ('not stated', 'mismatch'))
c_rel_unv = names(lambda v: v['release'] == 'unverified')
c_ovl_yes = names(lambda v: v['overlap'] == 'yes')
c_ovl_unc = names(lambda v: v['overlap'] == 'unclear')
c_undef = names(lambda v: v['undef'])
c_bg = names(lambda v: v['bg'] is True)
c_all4 = names(lambda v: v['release'] == 'stated' and v['split'] == 'yes' and not v['undef'])
assert len(c_int_none) + len(c_int_part) == n

def L(x):
    return ', '.join(x)

# ---------- markdown ----------
md = []
A = md.append
A('# Related work: published pixel-level EL segmentation numbers, and why they cannot be compared')
A('')
A('related_work, 22 Nov 2026, for the lead (gap G-N10; PROTOCOL v0.2 Open 9 and §6.6 item 4). Written from papers and team files only: no GPU job, no server, no sealed label or prediction read.')
A('')
A('**Tags.** E = stated in the cited source (paper, or a team file for our own measurements). S = judgement of this file. "inferred" = a convention not stated by the paper, with what it was inferred from. "PDF p." = page of the PDF file read; journal page numbers are given where printed. A number is never computed here; arithmetic checks are marked as such.')
A('')
A('**Sources.** Local full texts (md5 in `RW_SOURCES.tsv`): `/home/yugma/papers/`, `~/mtp/research/papers/`, `~/mtp/research/literature/pdfs_inst/`, `/home/noob/work/docs/papers/`. Open-access PDFs fetched today (SIGAN, Mayr, Yi, Hijjawi) stay in the session tool-results folder. Team files: `harness/final/PUBLIC_BENCH.md` (public_scout, 19 Nov), `results/final_opening_read/verdict.txt` l88 to l94, `thesis/THESIS_TABLES.md` T13a, handbook doc 05, literature notes A01 to A10, F04, F06, paper cards `cards/in2/`. The Research MCP was not available in this session (authentication only), so discovery used the ledgers, notes, local libraries and web search.')
A('')
A('**Scope.** Pixel-level segmentation (or pixel-level anomaly maps) of EL images of solar cells, 2018 to 2026. Image-level and box-only work is in table 3. Rows R are read in full text (22 papers); rows A are abstract-level or second-hand (7 papers) and are not counted in section 4.')
A('')
A('**Our protocol, for the last column** (PROTOCOL_v0.2 §0): BenchmarkEL `dataset_20211104`, label set v1.1, CV5-G module-grouped folds, sealed test50 and E1 (unseen modules); headline crack relF1@2 (tolerance 2 px) with relP@2 / relR@2, strict crack IoU, inactive IoU, mIoU-R13; operating point OP-A (argmax); 5 seeds per table row, group-bootstrap intervals. "yes" would need the same cells, labels, metric and a seed count; "partly" means the published metric can be recomputed on our per-cell records for the same cells (T13b), but not our card; "no" means another test set or an incompatible metric.')
A('')
A('## 1. Main table: pixel-level numbers, full text read (R rows)')
A('')
A('| # | Paper (year, venue, id) | Dataset and release | Split; module-disjoint? | Classes scored | Metric and averaging | Number(s) [where] | Interval, seeds, repeats | Code / weights | Comparable with v0.2 (S) |')
A('|---|---|---|---|---|---|---|---|---|---|')
for r in ROWS:
    A('| {id} | {paper} | {data} | {split} | {classes} | {metric} | {numbers} | {interval} | {code} | **{comp}**: {why} |'.format(**r))
A('')
A('Notes (E unless marked):')
A('- R02 to R04, R06a: the T13a wording stands. Pratt 2023: "rule A inferred; Fig. 7 / 8". SEiPV-Net: "averaging not defined". PV-S3 CSB-S1: "split not stated, background rule not stated". T13a reading, as written (S): "Pratt\'s averaging rule is inferred, and PV-S3\'s split is not stated. These rows are context only, never a claim to beat a published model."')
A('- R02, R03: the 50 test cells overlap our training pool: "8 test cells are the same physical cell as a pool cell (SPLIT_INTEGRITY 5b). 7 of them are confirmed by pixels. 1 (CFVS_00063_r3_c1) rests on the cells.tsv link only" (T13a, errata item 3). They are also the cells Pratt hand-picked for defects.')
A('- R04, R05, R10a: the release test sets of `20220723` (66 cells) and `20221008` (72 cells) each hold 51 cells of our pool; a model trained on those release splits would have trained on 38 of the 50 test cells (E, PUBLIC_BENCH §3).')
A('- Our own published-convention rows on test50 are T13b (v0 labels) and T13c (v1.1, our card); they are context only and are not repeated here.')
A('')
A('## 2. Abstract-level or second-hand rows (A rows; not counted in section 4)')
A('')
A('| # | Paper | Dataset | Split | Number(s) [where] | Comparable with v0.2 (S) |')
A('|---|---|---|---|---|---|')
for r in ABS:
    A('| {id} | {paper} | {data} | {split} | {numbers} | **{comp}**: {why} |'.format(**r))
A('')
A('## 3. Out of scope: image-level, box-only, not EL, or no pixel score')
A('')
A('| Paper | Data | Why out of scope |')
A('|---|---|---|')
for a, b, c in OUT:
    A(f'| {a} | {b} | {c} |')
A('')
A(f'## 4. What this shows (counts over the {n} full-text papers of table 1; R12 counts as two papers)')
A('')
A('| Problem | Papers | Which |')
A('|---|---|---|')
A(f'| No interval, seed count or repeat on any reported number | {len(c_int_none)} of {n} | all except the four below |')
A(f'| Interval only on a side quantity or a subset (none on the headline test number) | {len(c_int_part)} of {n} | {L(c_int_part)} |')
A(f'| Split not stated | {len(c_split_no)} of {n} | {L(c_split_no)} |')
A(f'| Split stated two ways that conflict | {len(c_split_contra)} of {n} | {L(c_split_contra)} |')
A(f'| Split stated to be module- or panel-disjoint | 0 of {n} | none (in the sections read) |')
A(f'| Release not stated, or paper data not the public release | {len(c_rel_bad)} of {n} | {L(c_rel_bad)} |')
A(f'| Release not verifiable today | {len(c_rel_unv)} of {n} | {L(c_rel_unv)} |')
A(f'| Test overlaps training, or the test set selects the model (stated, measured by us, or implied by the paper\'s own wording) | {len(c_ovl_yes)} of {n} | {L(c_ovl_yes)} |')
A(f'| Overlap not checkable from the paper (no grouping, no list, or selection set not stated) | {len(c_ovl_unc)} of {n} | {L(c_ovl_unc)} |')
A(f'| Metric undefined (averaging, absent-class rule, class set or background not stated) or numbers internally inconsistent | {len(c_undef)} of {n} | {L(c_undef)} |')
A(f'| Background (or no-defect class) inside the headline mean | {len(c_bg)} of {n} | {L(c_bg)} |')
A(f'| Distance-tolerant metric for 1 to 2 px crack labels | 0 of {n} | none; the only tolerance metric found is RERN\'s ODS-F at maxDist (A6, abstract, edge task) |')
A(f'| Number on unseen modules or a module-held-out set | 0 of {n} | none (PUBLIC_BENCH §0 item 3: no paper reports on E1) |')
A(f'| Release, split and metric all stated | {len(c_all4)} of {n} | {L(c_all4)} (Duan evaluates on its validation set) |')
A('')
A('Readings (S unless marked):')
A('1. **One data family, many test sets.** Only three papers score on test50 (Pratt 2023, SEiPV-Net, PV-S3 CSB-S1, the last with its split unstated). Torpey uses release `20220723`; Mazen, Ramadan and Hanifi use `20221008` (Hanifi re-split it and did not release the split). Mazen Tables 1 to 3, Ramadan Table 11 and PV-S3 Table 6 still rank their numbers against test50 rows (E). The same holds for UCF-EL (official release, own 80/10/10 splits, and the unreleased paper data) and PVEL-S.')
A('2. **No published split is module-disjoint, and where we could check, test overlaps training.** test50 has 8 physical-cell duplicates of pool cells (E, T13a); PV-S3\'s released lists put 1,769 of 2,289 UCF-EL test images in train lists (E, handbook 05 §4.2); Fioresi validates on the test set each epoch (E, PDF p. 5); Duan evaluates on its validation set (E); MultiSolSegment and Saleh describe augmenting before the split (E wording, S consequence).')
A(f'3. **Almost no uncertainty.** {len(c_int_none)} of {n} papers report no interval, seed count or repeat at all; the four others give intervals on a side quantity (Torpey: Tukey CIs for crack and five runs per regime, with R7 and R8 run once; PV-S3: SD over three samplings at 20% labels; Ramadan: 3-fold CV on training data; MultiSolSegment: CV accuracy). None gives an interval on the headline test number.')
A('4. **Convention moves the number as much as the method.** Same models, same 50 cells, our own test50 read on v0 labels (E, `verdict.txt` l100 to l116, C1, mean over seeds): Pratt mean of 3 defect medians 0.405 under rule A, 0.202 under rule B, 0.541 under rule C; SEiPV-style per-image mIoU 0.855 with absent-and-unpredicted = 1 and 0.545 with absent skipped; pooled micro IoU 0.891. Across papers on test50 (PV-S3 split assumed): crack 0.25 as Pratt\'s per-image median and 0.58 as PV-S3\'s pooled IoU (E). SEiPV-Net\'s "IoU" 0.7447 is a pooled pixel quantity with background (IoU = Dice / (2 - Dice) of its Dice 0.8531 within 0.001, E arithmetic); its headline "mIoU" 0.8604 has no stated averaging, and Ramadan prints it as wIoU (E). On PVEL-S, STC-Net prints MIoU 95.98 on "validation" and 72.52 on the 360 test images (E, Tables I, II): the 0.95 to 0.97 PVEL-S numbers of Duan, Ramadan and STC-Net are validation-set numbers with background in a binary mean.')
A('5. **Nothing published measures what our protocol measures.** No paper uses a distance tolerance for the 1 to 2 px crack labels, only Torpey repeats training runs behind its headline table, none reports on unseen modules. So no published row is comparable with relF1@2, OP-A or E1; three rows (R02, R03, R06a) are "partly" comparable on test50 by re-scoring our models in their convention (T13b), as context only.')
A('')
A('## 5. Papers I could not access (no number taken from them unless shown in table 2)')
A('')
for a, b in NOACCESS:
    A(f'- {a}: {b}.')
A('')
A('## 6. Method and limits (S)')
A('- Discovery: ledger `cards/ledger/MASTER.tsv` (645 rows), notes A01 to A10, F04, F06, PUBLIC_BENCH §1 forward-citation walk of 19 Nov, `/home/yugma/papers` (360 files), web search. Not done: a fresh forward-citation walk (Research MCP not available here). Conference-only and non-English work is under-covered (as F06 says).')
A('- Every table value in R rows was read today in the cited file, except SEiPV-Net (reprint in Mazen Table 1, read on the page image) and the P19 reproduction note in R08. Figure values (Pratt Fig. 7, Hanifi Fig. 3) were read from page images or their printed reprint.')
A('- Counts in section 4 are per paper (the "Which" column names them); a paper with several rows (PV-S3, Ramadan, EFSegNet) counts once, and a problem counts if any of its rows has it. "unclear" is not counted as overlap.')
A('')
A('## 7. Verified references for the thesis (added 22 Nov on the lead\'s request)')
A('')
A('Checked today (E) against: the arXiv API (`export.arxiv.org`: id, title, authors, first-version date); the Crossref REST API (publisher-deposited metadata: DOI, venue, volume, issue, pages, year); and `doi.org` resolution to the publisher page. LNCS volume numbers are **not checked**: Springer and DBLP returned bot checks, and Crossref has no volume field for these chapters, so the entries give the proceedings part and pages instead. BibTeX: `thesis/refs_extra.bib`.')
A('')
A('| Ref | Full citation | DOI (resolves to) | arXiv | Check |')
A('|---|---|---|---|---|')
A('| HRNet | Wang J., Sun K., Cheng T., Jiang B., Deng C., Zhao Y., Liu D., Mu Y., Tan M., Wang X., Liu W., Xiao B. Deep High-Resolution Representation Learning for Visual Recognition. IEEE Trans. Pattern Anal. Mach. Intell. 43(10):3349-3364, 2021. | 10.1109/TPAMI.2020.2983686 (IEEE Xplore document 9052469) | 1908.07919 (v1 20 Aug 2019) | Crossref and arXiv titles and 12 authors agree |')
A('| U-Net++ | Zhou Z., Rahman Siddiquee M. M., Tajbakhsh N., Liang J. UNet++: A Nested U-Net Architecture for Medical Image Segmentation. In: Deep Learning in Medical Image Analysis and Multimodal Learning for Clinical Decision Support (DLMIA 2018, ML-CDS 2018, held with MICCAI 2018), Lecture Notes in Computer Science, Springer, Cham, pp. 3-11, 2018. | 10.1007/978-3-030-00889-5_1 (link.springer.com) | 1807.10165 (v1 18 Jul 2018) | agree. This is the paper the U-Net++ decoder is usually cited by (S) |')
A('| U-Net++ (journal version, optional) | Zhou Z., Siddiquee M. M. R., Tajbakhsh N., Liang J. UNet++: Redesigning Skip Connections to Exploit Multiscale Features in Image Segmentation. IEEE Trans. Med. Imaging 39(6):1856-1867, 2020. | 10.1109/TMI.2019.2959609 (IEEE Xplore document 8932614) | 1912.05074 (v1 11 Dec 2019) | agree |')
A('| Skeleton Recall loss | Kirchhoff Y., Rokuss M. R., Roy S., Kovacs B., Ulrich C., Wald T., Zenk M., Vollmuth P., Kleesiek J., Isensee F., Maier-Hein K. Skeleton Recall Loss for Connectivity Conserving and Resource Efficient Segmentation of Thin Tubular Structures. In: Computer Vision - ECCV 2024, Part LXXVII, Lecture Notes in Computer Science, Springer, Cham, pp. 218-234, 2024. | 10.1007/978-3-031-72980-5_13 (link.springer.com) | 2404.03010 (v1 3 Apr 2024) | agree; found by Crossref title search. Not to be confused with the one-page BVM 2025 abstract, doi:10.1007/978-3-658-47422-5_52 |')
A('| DeepLabV3+ | Chen L.-C., Zhu Y., Papandreou G., Schroff F., Adam H. Encoder-Decoder with Atrous Separable Convolution for Semantic Image Segmentation. In: Computer Vision - ECCV 2018, Part VII, Lecture Notes in Computer Science, Springer, Cham, pp. 833-851, 2018. | 10.1007/978-3-030-01234-2_49 (link.springer.com) | 1802.02611 (v1 7 Feb 2018) | agree |')
A('| D4 (flip / rot90) TTA | **None.** Our D4 step cites no paper: it entered as Track M R1 (24 Oct, handbook 18 §M1), and `results/stageB/B5_tta_module.md` checks it against a code reference (`dihedral`), not a publication. The T7 `msc_tta` arm, which added scale views on top of D4, was built from ledger P231: Huang R. When Online Adaptation Hurts: Parameter-Frozen Test-Time Ensembling for Continual Medical Image Segmentation. arXiv preprint, 2026. That paper motivates the scale views, not D4. The ledger records an abstract-level read only. | none | 2609.21412 (v1 18 Sep 2026; single author per arXiv) | id, title and author agree (E); content not re-read (S) |')
A('')
with open(os.path.join(OUTDIR, 'RELATED_WORK.md'), 'w') as f:
    f.write('\n'.join(md))

# ---------- TSV ----------
tsv = ['row\tpaper_key\tmetric\tvalue\tlocation\tquote\tsource_file\tmd5']
warn = []
for rid, pk, fk, loc, quote, vals in SRC:
    if len(quote.split()) > 20:
        warn.append((rid, len(quote.split())))
    if fk in F:
        path, m = F[fk], md5[fk]
    else:
        path, m = 'web: ' + WEB[fk], 'n/a (not saved)'
    for metric, value in vals:
        tsv.append('\t'.join([rid, pk, metric, value, loc, quote, path, m]))
with open(os.path.join(OUTDIR, 'RW_SOURCES.tsv'), 'w') as f:
    f.write('\n'.join(tsv) + '\n')

# ---------- TeX ----------
def tex(s):
    s = s.replace('\\', '/')
    s = re.sub(r'"([^"]*)"', r"``\1''", s)
    for a, b in [('&', r'\&'), ('%', r'\%'), ('$', r'\$'), ('#', r'\#'), ('_', r'\_'), ('{', r'\{'), ('}', r'\}'), ('~', r'\textasciitilde{}'), ('^', r'\textasciicircum{}')]:
        s = s.replace(a, b)
    s = s.replace('+-', r'$\pm$').replace(' x ', r' $\times$ ').replace('§', r'\S{}')
    return re.sub(r'\S{10,}', brk, s)
def brk(m):
    # layout only (layout_fix, 23 Nov 2026): a DOI, URL or repository path (a long token holding '/') may break after / . _ :
    tok = m.group(0)
    if '/' not in tok:
        return tok
    return re.sub(r'([/.:]|\\_)(?=[^\s]*[A-Za-z0-9])', lambda k: k.group(1) + r'\allowbreak{}', tok)
t = []
B = t.append
B('% related_work.tex: related-work tables for the thesis (G-N10). Generated 22 Nov 2026 by related_work; not compiled (gaint has no TeX).')
B('% Needs: \\usepackage{booktabs,longtable,pdflscape,array}. Source of every value: RELATED_WORK.md and RW_SOURCES.tsv.')
B('\\begin{landscape}')
B('\\scriptsize')
B('\\setlength{\\tabcolsep}{3pt}')
B('\\begin{longtable}{>{\\raggedright\\hspace{0pt}}p{3.0cm} >{\\raggedright\\hspace{0pt}}p{4.0cm} >{\\raggedright\\hspace{0pt}}p{3.4cm} >{\\raggedright\\hspace{0pt}}p{5.0cm} >{\\raggedright\\hspace{0pt}}p{2.2cm} >{\\raggedright\\hspace{0pt}}p{3.0cm} >{\\raggedright\\arraybackslash\\hspace{0pt}}p{2.3cm}}')
B('\\caption{Published pixel-level EL segmentation numbers (full text read). Locations as in RW\\_SOURCES.tsv. Comparable: with protocol v0.2 (relF1@2, OP-A, test50 / E1); S = judgement.}\\label{tab:rw_main}\\\\')
hdr = 'Paper & Data, release, split & Metric and averaging & Number(s) [where] & Interval & Code & Comparable (S) \\\\'
B('\\toprule'); B(hdr); B('\\midrule'); B('\\endfirsthead')
B('\\toprule'); B(hdr); B('\\midrule'); B('\\endhead')
B('\\bottomrule'); B('\\endfoot')
for r in ROWS:
    cells = [r['id'] + ' ' + r['paper'], r['data'] + '. Split: ' + r['split'] + '. Classes: ' + r['classes'], r['metric'], r['numbers'], r['interval'], r['code'], r['comp'] + ': ' + r['why']]
    B(' & '.join(tex(c) for c in cells) + ' \\\\')
    B('\\addlinespace')
B('\\end{longtable}')
B('\\end{landscape}')
B('')
B('\\begin{table}[ht]\\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}')
B('\\caption{Abstract-level or second-hand rows (not counted in the problem counts).}\\label{tab:rw_abs}')
B('\\begin{tabular}{>{\\raggedright\\hspace{0pt}}p{3.6cm} >{\\raggedright\\hspace{0pt}}p{3.2cm} >{\\raggedright\\hspace{0pt}}p{5.6cm} >{\\raggedright\\arraybackslash\\hspace{0pt}}p{2.6cm}}')
B('\\toprule'); B('Paper & Data, split & Number(s) [where] & Comparable (S) \\\\'); B('\\midrule')
for r in ABS:
    B(' & '.join(tex(c) for c in [r['id'] + ' ' + r['paper'], r['data'] + '; split: ' + r['split'], r['numbers'], r['comp'] + ': ' + r['why']]) + ' \\\\')
B('\\bottomrule'); B('\\end{tabular}'); B('\\end{table}')
B('')
B('\\begin{table}[ht]\\centering\\scriptsize\\setlength{\\tabcolsep}{3pt}')
B('\\caption{Out of scope: image-level, box-only, not EL, or no pixel score.}\\label{tab:rw_out}')
B('\\begin{tabular}{>{\\raggedright\\hspace{0pt}}p{5.2cm} >{\\raggedright\\hspace{0pt}}p{4.2cm} >{\\raggedright\\arraybackslash\\hspace{0pt}}p{5.4cm}}')
B('\\toprule'); B('Paper & Data & Why out of scope \\\\'); B('\\midrule')
for a, b, c in OUT:
    B(' & '.join(tex(x) for x in (a, b, c)) + ' \\\\')
B('\\bottomrule'); B('\\end{tabular}'); B('\\end{table}')
B('')
B('\\begin{table}[ht]\\centering\\small')
B(f'\\caption{{What the published record shows: counts over the {n} full-text papers.}}\\label{{tab:rw_counts}}')
B('\\begin{tabular}{lr}')
B('\\toprule'); B('Problem & Papers \\\\'); B('\\midrule')
for lab, k in [('No interval, seeds or repeats on any number', len(c_int_none)),
               ('Interval only on a side quantity', len(c_int_part)),
               ('Split not stated', len(c_split_no)),
               ('Split stated two ways that conflict', len(c_split_contra)),
               ('Split stated to be module-disjoint', 0),
               ('Release not stated or not the public data', len(c_rel_bad)),
               ('Test overlaps training or selects the model', len(c_ovl_yes)),
               ('Overlap not checkable', len(c_ovl_unc)),
               ('Metric undefined or inconsistent', len(c_undef)),
               ('Background inside the headline mean', len(c_bg)),
               ('Distance-tolerant crack metric', 0),
               ('Result on unseen modules', 0)]:
    B(f'{tex(lab)} & {k} of {n} \\\\')
B('\\bottomrule'); B('\\end{tabular}'); B('\\end{table}')
with open(os.path.join(OUTDIR, 'related_work.tex'), 'w') as f:
    f.write('\n'.join(t) + '\n')

print('papers full text', n, 'abstract rows', len(ABS), 'out', len(OUT), 'noaccess', len(NOACCESS))
print('tsv rows', len(tsv) - 1, 'quote>20 words', warn)
print('counts', dict(int_none=len(c_int_none), int_part=len(c_int_part), split_no=len(c_split_no), contra=len(c_split_contra),
      rel_bad=len(c_rel_bad), rel_unv=len(c_rel_unv), ovl=len(c_ovl_yes), unc=len(c_ovl_unc), undef=len(c_undef), bg=len(c_bg), all4=c_all4))
