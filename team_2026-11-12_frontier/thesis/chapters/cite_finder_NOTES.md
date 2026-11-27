# cite_finder notes (23 Nov 2026)

Entries are in `cite_finder.bib`, same folder. Neither key clashes with `references.bib`, `refs_extra.bib` or `chapters/*.bib`. bibtex is not installed on this machine, so the file was checked only by a brace-balance and field parse (balanced; 9 and 7 fields).

## 1. `kontges2014iea`: ch02_background.tex l14-16

Sentence: "A crystalline silicon module is a laminate of cells wired in series. Printed metal fingers on each cell collect the current, wider busbars gather it, and soldered interconnect ribbons carry it to the next cell \CITE{...}."
(The next sentence, on mono vs multi, already cites `pratt2023benchmark`. Half-cut cells are not mentioned anywhere in ch02, so no claim needs a source for them.)

**Source read:** the full report PDF from IEA-PVPS, https://iea-pvps.org/wp-content/uploads/2020/01/IEA-PVPS_T13-01_2014_Review_of_Failures_of_Photovoltaic_Modules_Final.pdf (140 PDF pages, md5 65d7338d..., downloaded to the scratchpad only, not kept in the project). Report page = PDF page - 6.

**Bibliographic data, from the title pages (PDF pp. 1-2):** "Review of Failures of Photovoltaic Modules", Report IEA-PVPS T13-01:2014, IEA PVPS Task 13, Subtask 3.2, "External final report IEA-PVPS", March 2014, ISBN 978-3-906042-16-9. There are nine primary authors, in this order: Marc Köntges, Sarah Kurtz, Corinne Packard, Ulrike Jahn, Karl A. Berger, Kazuhiko Kato, Thomas Friesen, Haitao Liu, Mike Van Iseghem. The contributing authors (Wohlgemuth, Miller, Kempe, Hacke, Reil, Bogdanski, Herrmann, Buerhop-Lutz, Razongles, G. Friesen) are left out of the entry. The report has no DOI. The same author list appears in references [29] of Pratt et al. 2021 and [3] of Hanifi et al. 2025, both on disk.

**Claim support, by part of the sentence:**

| Claim | Supported? | Where (report page) and what it says |
|---|---|---|
| module is a laminate | yes | p. 55, §6.1: "The most similar part of all different kinds of modules is the laminate"; §6.1.1: "adhesion between the glass, encapsulant, active layers, and back layers". p. 13, §4.3.2: "cells in the laminate". |
| cells wired in series | yes | p. 19, §4.6: a 'string' is "usually 10 or 12 cells in a wafer-based module ... electrically connected in series"; "Cells wired in series are connected to form a string by the 'cell interconnect ribbon'". p. 82, §6.2.6: cells "interconnected in series with cell interconnect ribbons to obtain higher voltage". Note: the report adds that strings are "typically interconnected in series or sometimes in parallel" and that bypass diodes form sub-modules. "Cells wired in series" is a fair simplification. |
| fingers on each cell collect the current | yes | p. 19, §4.6: "'Gridlines' (interchangeably referred to as 'fingers') make up the finest level of metallisation directly on the cells and consist of an array of lines <0.4 mm thick." |
| busbars gather it | yes | p. 19, §4.6: "Current from the gridlines is collected in the 'busbars', which are also directly on the cell." Fig. 4.6.1: "Metallisation on a silicon cell consists of gridlines and busbars." |
| ribbons carry it to the next cell | yes | p. 19, §4.6 (quote above). p. 82, §6.2.6: ribbons "are connected from the front side to the rear side of the solar cells". p. 19: the ribbon "directly overlaps" the busbars. |
| **"printed"** (fingers) | **not stated** | The report says "metallisation", never "printed" or "screen-printed". |
| **"wider"** (busbars) | **not stated in text** | The text gives finger width (<0.4 mm) but no busbar width. Fig. 4.6.1 is a schematic; I read only the extracted text, not the figure. |
| "soldered" (ribbons) | indirectly | p. 82, §6.2.6: "Poor soldering ... of the connection between cell interconnect ribbon and string interconnect"; p. 8: the TCT200 test stresses "the solder connection of wafer-based PV modules"; p. 44, finger failure C: "gridfinger interruptions caused by soldering (GICS)". The report never says in one sentence that the ribbon is soldered to the busbar. |

**Suggestion for the lead:** to make every word traceable to this one source, drop "Printed" and "wider", e.g. "Metal fingers on each cell collect the current, busbars on the cell gather it, and soldered interconnect ribbons carry it to the next cell \citep[§4.6]{kontges2014iea}." Or keep the sentence as is; "printed" and "wider" are textbook-standard but not in this report.

## 2. `lei2025alhvr`: ch05_legacy.tex l69

Sentence: "an adapted region-routing SSL method \CITE{ALHVR, Lei et al., ICCV 2025} was WORSE on all three primaries in all four cell sets (AL1)."

**What ALHVR is in the project notes:** `/home/yugma/mtp/research/literature/notes/B01_alhvr2025.md` l1-2 gives the title "Adaptive Learning of High-Value Regions for Semi-Supervised Medical Image Segmentation" (ICCV 2025), the mlanthology and CVF supplement URLs, and the code https://github.com/ziziyao/ALHVR. The AL1 experiment is `/home/yugma/mtp/research/team_2026-10-21/alhvr/results.md` ("ALHVR adapted to EL, 5% labels"). `ch05_legacy_NOTES.md` l123 noted that no DOI or arXiv id was on disk.

**Verified on three independent sites (all agree):**
- **CVF open access** (fetched with curl; WebFetch got HTTP 403): https://openaccess.thecvf.com/content/ICCV2025/html/Lei_Adaptive_Learning_of_High-Value_Regions_for_Semi-Supervised_Medical_Image_Segmentation_ICCV_2025_paper.html. The page's BibTeX gives the authors "Lei, Tao and Yang, Ziyao and Wang, Xingwu and Wang, Yi and Wang, Xuan and Sun, Feiman and Nandi, Asoke K.", the same title, "Proceedings of the IEEE/CVF International Conference on Computer Vision (ICCV)", October 2025, pages 21450-21459. The abstract names the method "adaptive learning of high-value regions (ALHVR)": dual-branch predictions split regions into reliable stable, reliable unstable and unreliable stable; CG-CPCL handles the reliable unstable region and DTCT the unreliable stable region. It ends "Code is available at https://github.com/ziziyao/ALHVR". This matches B01 and fits the thesis phrase "region-routing SSL method".
- **Crossref**, https://api.crossref.org/works/10.1109/ICCV51701.2025.01992: proceedings-article, same title, the same 7 authors in order, container "2025 IEEE/CVF International Conference on Computer Vision (ICCV)", pages 21450-21459, publisher IEEE, event Honolulu, 19-25 Oct 2025.
- **mlanthology**, https://mlanthology.org/iccv/2025/lei2025iccv-adaptive/: same title, authors and pages; DOI 10.1109/ICCV51701.2025.01992.

**arXiv:** an arXiv API title search (`ti:"High-Value Regions" AND ti:"Semi-Supervised"`) returned 0 results. No arXiv id was found; the DOI is the identifier.

**Style:** the booktitle, publisher and `--` page range follow the house style of `hoyer2022daformer` (CVPR) in references.bib.

## Not verified / caveats
- "Printed" fingers and "wider" busbars (ch02 l14-15) are not in the IEA report text (see table above).
- The report's Fig. 4.6.1 and 4.6.2 were not viewed as images; only the extracted text was read.
- I did not compile the bib with bibtex, because it is not installed here.
