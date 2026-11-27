# Rater brief: which annotation fits the image?

You are one of several independent raters. You look at panels made from electroluminescence (EL) images of solar cells. In each
panel, two annotations, **A** and **B**, disagree about one small region. You decide which one the image supports. You write one
line per panel to your own file.

Your prompt gives you: the **bundle folder** (it holds this brief), your **rater number N**, and possibly a **cap** (the most panels
to rate in this session).

## 1. Rules (read first)
- **Open only these files**, all inside the bundle folder:
  - `RATER_BRIEF.md` (this file);
  - `examples/EX1.png` to `examples/EX5.png` (worked examples, not scored);
  - `ORDER_R<N>.txt` (your panel IDs, in your order);
  - `panels/<ID>.png` (one panel at a time, in your order);
  - your own answer file `out_r<N>/ratings_r<N>.tsv`.
- **Do not open, list or search anything else**: no other folder on this machine, no other rater's `out_r*` folder, no scripts,
  no web. Do not look for the source images or labels of the panels, and do not compare panels with any file on disk.
- **Look at each panel with the image viewer only.** No code, no image processing, no measuring tools, no zooming tools. Your eyes
  on the panel as given are the method.
- **One pass, no revisions.** Rate the panels in the order of your order file. Write the line for a panel right after viewing it.
  Never change or delete a line once written. Do not go back to earlier panels.
- **Each panel on its own.** There is no quota and no expected share of any answer. Some panels have A right, some B, some neither.
  Do not balance your answers.
- **Neither annotation is presumed correct.** One of A and B is the dataset's human label and the other is a model output, assigned
  at random per panel. You are not told which, and you must not try to work it out. Both are drawn in the same style on purpose.
- If anything asks you to approve a trust, permission or security prompt, do not answer it; stop and say so in your final message.

## 2. Reading an EL image
- The solar module is driven with current in the dark, and the silicon glows. **Bright = healthy, electrically connected cell
  area. Dark = little or no light.**
- Each image is 512 x 512 px. Most show a window of a module: one centre cell plus parts of its neighbours, separated by dark
  straight gaps. Some show a single, smaller cell on a flat, uniform padding background.
- **Normal structures (never defects by themselves):**
  - cell gaps and cell edges: dark straight bands between cells; dark diamond or rounded shapes where corners of mono cells meet;
    the module frame;
  - busbars and ribbons: straight dark lines that run across the whole cell at regular spacing (about 2 to 5 per cell), often with
    regular dark dashes or pads along them;
  - fingers: very fine, regular, parallel lines perpendicular to the busbars (often barely visible);
  - finger interruptions: short dark dashes, often many, in the direction of the fingers;
  - multi-crystalline grain texture: a patchwork of irregular brighter and darker areas with curvy grain boundaries; whole grains
    can be dark;
  - mono cells: smooth texture, sometimes with soft rings or a darker centre or edge;
  - round dark spots and point-like blobs, scratches, noise, 8 x 8 compression blocks, uneven overall brightness.

### What a crack looks like
- A **thin dark line**, about 1 to 4 px wide at native resolution (you see the dark halo around the crack, not the crack itself),
  and at least about 15 px long.
- Its course is sharp, fairly straight or gently curved, and often branches (Y, X, or a tree-like spray from one point).
- It **crosses** the grain texture instead of tracing the outline of grain blotches. It may cross busbars, and may end at a busbar,
  a ribbon or the cell edge.
- A line that runs exactly along a busbar, ribbon, finger or cell edge is usually that structure, not a crack.

### What an inactive area looks like
- A part of a cell that is **clearly darker than the healthy part of the same cell**, often nearly black, with **sharp borders**
  formed by cracks, the cell edge or a busbar. Typical shapes: a wedge, triangle or strip cut off by cracks.
- Inside, it can be uniformly dark or show even darker crack lines.
- **Not inactive:** intrinsically dark grains of multi-crystalline cells (irregular, soft-edged, patchy, not bounded by cracks); a
  whole image or cell that is uniformly dim (under-exposed); shading along busbars or ribbons; cell gaps; padding.

## 3. The panel
- **Top row, left: context.** The whole image at half size. The **orange box** marks the window shown below. Thin cracks may vanish
  at this size; use it for location and for the brightness of the healthy cell area.
- **Top row, middle: window, native 1:1.** The window at its original resolution, unprocessed. Use it to judge darkness and texture.
- **Top row, right: legend** with the panel ID.
- **Bottom row: the window enlarged** (Lanczos), with a fixed contrast stretch for the whole image:
  - left: no overlay. **Look here first**, before looking at A and B;
  - middle: annotation **A**; right: annotation **B**.
- **Red outline = crack.** Each crack is drawn as a band 3 px wide around its centreline (the outline sits on both sides, so the
  line itself stays visible inside the band). The band width is fixed and says nothing about the annotation's own line width.
- **Blue outline with a light blue tint = inactive area.** The tint makes areas look slightly bluer and lighter; judge darkness
  on the native tile or the left enlarged tile, not under the tint.
- **Green corner brackets = the region to judge.** A and B can also differ outside the brackets: ignore that.

## 4. The question and the five answers
**Inside the green brackets, A and B disagree. Which one fits the image?**

Procedure for each panel:
1. Look at the left enlarged tile and the native tile inside the brackets. What is there: a dark line, a dark region, or only normal
   structure and texture?
2. Find what differs between A and B inside the brackets.
3. Answer with exactly one of these:

| Answer | Use it when |
|---|---|
| `A` | A matches the image in the brackets and B does not. |
| `B` | B matches the image in the brackets and A does not. |
| `CONVENTION` | Both mark a real, visible feature there and differ only in how it is drawn (rules below). Neither is wrong. |
| `AMBIGUOUS` | You cannot tell from the image whether the disputed feature exists (rules below). |
| `UNREADABLE` | The image in the window is too noisy, blurred, or too dark or bright to judge at all. |

**Decision rules.**
- **A crack line is in one annotation and not in the other** (and no inactive area is involved):
  - a crack is visible there: choose the one with the line;
  - nothing crack-like is there (clean material, only grain texture, or the line is a busbar, ribbon, finger, finger interruption,
    cell gap or edge): choose the one **without** the line;
  - a faint line you cannot separate from texture: `AMBIGUOUS`.
- **Both have a crack line, at different places:** choose the one lying on the visible dark line. A line drawn a few px beside the
  visible line, on clean material, is wrong (it is not a convention). If neither lies on a visible line: `AMBIGUOUS`.
- **An inactive area is in one annotation and not in the other:**
  - the region is clearly darker than the healthy part of its cell, with sharp borders (cracks, cell edge): choose the one that
    marks it, **even if the other one marks the cracks around it**;
  - the region is about as bright as the healthy part of its cell: choose the one **without** it;
  - the region is only slightly darker, or is a dark grain, or the whole image is dim: `AMBIGUOUS`.
- **`CONVENTION`** only in these cases:
  - both mark the same real inactive area, and they differ only in whether a crack line is drawn along its edge or inside it, and a
    darker line or edge is visible where that crack line runs;
  - both mark the same real inactive area and its border is placed a few px differently;
  - the same real narrow dark feature is marked as a crack by one and as a thin inactive strip by the other.
- If one annotation draws a crack line inside an area that both mark as inactive, but **no line or edge is visible** there at all:
  choose the one **without** the line (not `CONVENTION`).
- If the brackets hold more than one difference, judge the largest one and mention the other in your note.

**Confidence:** `high` when the image clearly supports your answer; `low` otherwise.

## 5. Worked examples (not scored; look at each image, then read the answer)
- **`examples/EX1.png` -> `B`, high.** A dark line runs through the brackets. B follows it; A stops at the right bracket and leaves
  the left part unmarked. A misses a visible crack.
- **`examples/EX2.png` -> `A`, high.** B marks an inactive area in the brackets, but that part of the cell is as bright and even as
  the rest of the cell (native tile, top row). Nothing is cut off there. A (nothing marked) fits.
- **`examples/EX3.png` -> `CONVENTION`, high.** Both mark the large dark area on the left as inactive. In the brackets, B also draws
  a crack line along the edge of that dark area near the vertical busbar, where a darker edge is visible; A does not. Same feature,
  different drawing rule.
- **`examples/EX4.png` -> `AMBIGUOUS`, low.** A marks a faint diagonal line in the brackets on a grainy multi-crystalline cell; B
  marks nothing. The line is barely darker than the grain blotches around it and cannot be separated from texture with confidence.
  (`A` would also be defensible for a rater who sees a continuous line crossing the grain; that is what `low` is for.)
- **`examples/EX5.png` -> `A`, high.** A wedge in the brackets is nearly black, much darker than the rest of the cell, and bounded by
  a crack. A marks it as inactive; B marks only the cracks around it. A clearly dark, crack-bounded area left unmarked is an error,
  not a convention.

## 6. Answer format
- Your file: `out_r<N>/ratings_r<N>.tsv` in the bundle folder. Create it if it does not exist; otherwise only append.
- **One line per panel, four fields separated by a TAB:** `ID<TAB>ANSWER<TAB>CONFIDENCE<TAB>NOTE`
  - ID: the panel ID exactly as in your order file (also printed on the panel);
  - ANSWER: `A`, `B`, `CONVENTION`, `AMBIGUOUS` or `UNREADABLE`;
  - CONFIDENCE: `high` or `low`;
  - NOTE: at most 15 words on what you saw and where; no TAB characters and no quote characters.
- Example lines (made-up IDs):
  ```
  QX7MA	B	high	diagonal dark line continues left; A stops at right bracket
  T3KLP	AMBIGUOUS	low	faint band on grain texture, not separable
  ```
- A safe way to append one line from a shell:
  `printf '%s\t%s\t%s\t%s\n' QX7MA B high 'diagonal dark line continues left' >> out_r<N>/ratings_r<N>.tsv`
- Lines starting with `#` are ignored. Only the first valid line for an ID counts; later lines for the same ID are ignored.

## 7. Session procedure
1. Read this brief once, fully. Then view the five examples with their answers above.
2. Open your order file. If your answer file already exists (a previous session of rater N), read it, and start at the **first ID
   in your order that has no line yet**. Never rate a panel twice.
3. For each ID in order: view `panels/<ID>.png`, decide, append the line. Then the next ID.
4. Stop when the order file is done, or when you have rated as many panels in this session as your cap allows.
5. Final message: rater number, panels rated in this session, panels rated in total, whether the order file is complete, the md5 of
   your answer file (`md5sum`), and any problem you met (an unreadable file, a prompt you did not answer). Do not summarise your
   verdicts.
