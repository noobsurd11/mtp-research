# Audit brief for the project-record appendices (27 Nov 2026)

A writer drafted one appendix of the MTP thesis under `RECORD_BRIEF.md` (same folder; read it, its hard rules are yours too). You are the independent checker. The user's requirement is **no mistakes**.

Working copy: `/tmp/claude-1000/-home-yugma-mtp-research/2702d0bd-61fc-421d-8eb2-2bf4956d23c8/scratchpad/thesis_w3/`. Server (read only, same rules as the writer): `ssh -o BatchMode=yes noob@172.18.22.20`, root `/home/yugma/mtp/research/`. Local repo `/home/yugma/mtp/research/`.

## Do
1. For every number, count, date and named result in the appendix: open the source named in its `_NOTES.md` entry **yourself** (do not trust the quote), confirm the value, the rounding, the unit or scale, and that the sentence says what the source says (same arm, same set, same metric, same direction of the contrast).
2. Check claim strength: verdict vs robustness check vs reading kept apart; n.d. never worded as worse/no effect/equals; old-era numbers labelled as history; no selection-biased value called a test result; nothing stronger than the source.
3. Check consistency with the main thesis (`chapters/ch0*.tex`, `ch1*.tex`, `THESIS_TABLES.md`): the same quantity must have the same value; if the appendix and the main text disagree, find out which is right from the primary record.
4. Check the conventions of RECORD_BRIEF rule 6 (no dashes as punctuation, no host/user/path names, the industry partner unnamed, people other than the two students and published authors unnamed) and LaTeX validity (escapes, balanced environments, labels unique across `chapters/*.tex`, every `\ref` target exists in the thesis, every `\citep`/`\citet` key exists in `references.bib`).
5. Fix verified errors directly in the appendix .tex (smallest edit) and update its NOTES entry. Anything you cannot settle from the files: remove the claim if it is unsupported, or list it.

## Do not
- Rewrite style or structure. Touch any file other than your appendix's .tex and NOTES. Compile.

## Report (write to `AUDIT_REC_<id>.md` in the working copy)
CHANGES (file:line | old | new | evidence path:line quoted), REMOVED (unsupported claims taken out), CONFLICTS, OPEN, and one line: numbers checked against the primary file vs only against NOTES.
