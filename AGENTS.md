# Slides for COMS E6998-019

The visual grammar below was read off the deck itself, not chosen. Follow it when you add slides to
any lecture deck in this folder. When the deck and this file disagree, the deck wins: re-derive the
rules with the tool at the foot of this file and correct what is written here.

Current deck: `lecture-2--2026-09-18/lecture2-1.pptx`, 7.5 by 5.625 in (6858000 by 5143500 EMU).
Slides 1 to 10 are Rahul's own. Slides 11 onward were drafted by Codex and edited by Rahul.

## Canvas and layout

- Put every body shape on one column: left 319251 EMU, width 6014545 EMU, right edge 6333796 EMU.
- Centre on the column axis (3326524 EMU), not the slide axis (3429000 EMU).
- Leave the title placeholder where the layout puts it (14251, 19250, 6815475 by 610800) and never
  move or resize it.
- Build a content slide as three bands: title down to 630050, body from 630050 to about 4400000, and
  a closing line ending no lower than 4800000.
- Start the first body object between 630050 and 860000 EMU. Use 700000 as the default.
- Keep the lowest edge at or above 4790000 EMU, where the master's corner mark and the slide number
  begin.
- Leave at least 186667 EMU between stacked blocks, and aim for 230000 to 420000.
- Never let two declared boxes overlap, even when autofit makes the text look clear.
- Use three layouts: TITLE for slide 1, Custom Layout for content, 1_Custom Layout for section
  dividers. Never use 2_Custom Layout.
- Give every box on the body column a MIDDLE vertical anchor.
- Keep the body to two or three objects, five at most, ordered loud to quiet from the top: list or
  table, then navy panel, then the closing line.
- Size a full-width image to left 250147 and width 6152752, a 69104 EMU bleed each side, and let the
  height follow the aspect ratio. Provisional, from two slides.

## Typography

- Use only the ten sizes already in the deck: 40, 24, 16, 15, 14, 13, 12, 11, 10.5, 10.
- Leave a content-slide title run bare, with no size, colour or weight, so the layout supplies 24 pt
  bold #2D2A62.
- Set bullets and panel prose at 14 pt. Use 15 pt only when the panel carries the slide's closing
  claim.
- Use 13 pt for the one-line verdict box, 12 pt for a closing box and a code caption, and 11 pt for
  code and the accent strip.
- Size a table by the job it does on the slide, not by its column count: 14 pt when the table *is*
  the slide and carries six or seven short rows, 12 pt when it sits under a definition, 11 pt when it
  shares the slide with a verdict box.
- Drop to 10 pt only when a table runs five columns wide or six rows of prose.
- Set a source citation at 10.5 pt italic. Use italic nowhere else, and never with bold.
- Take the typeface from the theme (`+mn-lt` or `+mj-lt`, both Fira Sans) or leave the run's font
  unset. Never type "Fira Sans" into a run.
- Set monospace in **Maple Mono NF**, never Menlo or Courier. The deck embeds Fira Sans, Fira Sans
  Light and Maple Mono NF, so any other face falls back on another machine.
- Name Fira Sans Light only on the accent strip.
- State the point size on every run inside a plain shape or text box. The fallback there is 14 pt
  Arial from presentation.xml, not the theme face.

## Colour

- Most pages are white, but **any content slide may go dark** by setting its own `<p:bg>` to
  `scheme:bg2` (#28285E) while staying on Custom Layout. The layout's name therefore tells you
  nothing: read the slide's own background before choosing any ink.
- **On a dark page, invert deliberately and check every shape.** The title run takes `scheme:tx2`;
  the panel keeps its #28285E fill and gains a `scheme:bg1` outline so it still reads as a box;
  table text and table rules both become `scheme:tx2`. Anything still carrying `tx1`, `accent1` or
  `bg2` ink disappears into the page, and an uncoloured run falls back to black, which on navy is
  the same as invisible. State the colour on every run.
- **One navy, #28285E.** Write that literal for every fill, outline, bullet glyph and piece of
  emphasised ink you author (ruled 2026-09-17; the deck was converted off #2A2A63 that day). It is
  also theme dk2, which this deck's colour map reaches as `scheme:bg2`, so either spelling lands on
  the same ink. The layout's own #2D2A62 on a title belongs to the layout: never author it, never
  override it.
- Put `scheme:tx2` (#E8E8E8) on every run that sits on navy, and nothing else.
- Keep ordinary prose on white black, written as `scheme:tx1` rather than #000000.
- **Navy marks the lead, not the whole box.** In a list, only the lead-in line is navy; every item is
  `scheme:tx1`, its bold label included. In a table, only the label column is navy; the header row
  and the data cells are `scheme:tx1`. A text box set entirely in navy will be corrected.
- Mark emphasis by weight in the run's own colour: bold black inside black body text, bold navy
  inside a navy lead-in, bold `scheme:tx2` on a navy fill. Never mark emphasis by changing colour.
  Underline only on navy, and never on white.
- Use #348EDC for the verdict box: its bold lead phrase and its 1.5 pt rule. Nowhere else.
- Use magenta, `scheme:accent4` (#C73561), for the defect token in code, for a forward-reference
  aside, and as the accent strip's fill. Call it magenta, never pink, in any sentence that names it,
  and set the colour word itself in `scheme:accent4` so the name is shown in the colour it names.
- Use #099191 for the fixed token in code, and #8A8A9A for code line numbers.
- Set text on the accent strip in `scheme:tx2`, the same light ink that sits on navy.

## Components

- **Navy statement panel.** Rectangle filled #28285E with a #28285E line, anchor MIDDLE, insets
  182880 (137160 for a one-line claim), one 14 pt `scheme:tx2` paragraph, height 610801. One per
  slide, for the single sentence the slide exists to assert.
- **Closing box.** The last thing on a content slide, in one of two forms. Under a list that already
  has a navy panel, outline it: no fill, #28285E line, anchor MIDDLE, centred 12 pt bold #28285E,
  height 430000, at the body column. Under a table, fill it instead: #28285E fill, centred 12 pt
  `scheme:tx2`, bold on the one word that matters, narrower than the column (4445035) and
  right-aligned to its edge at 6333796. Two at most.
- **Verdict box.** Rectangle filled white with a 1.5 pt #348EDC line, anchor MIDDLE, insets 137160, at
  319251/3560000/6014545/820000. One 13 pt line whose opening phrase is bold #348EDC and whose
  remainder is #28285E. Use it only under a two-option comparison table, and never with a navy panel.
- **Accent strip.** The closing line, usually a borrowed sentence compressed to one line: fill and
  line `scheme:accent4`, one justified 11 pt Fira Sans run in `scheme:tx2`, wrap off, at
  250199/3835634/6152646/261610 — the full-bleed figure width, centred on the column axis. Set it in
  regular weight and bold only the clause that has to land ("… **lacks autonomy.**"). The citation
  goes in its own box *below* the strip, right-aligned, not above it.
- **Code panel.** Rounded rectangle (adjustment 0.04) filled #F2F2F6, no line, anchor MIDDLE, wrap
  off, insets 150000 left and 60000 top and bottom, height 520000 for two lines. Left align every
  paragraph: a shape's text centres by default.
- **Code caption.** A bare text box, no fill and no line, height 200000, one 12 pt bold #28285E line,
  its top 260000 EMU above the panel.
- **Bulleted list.** The layout's content placeholder (idx 1) moved to the column. The lead-in is
  bullet-free (marL 0, indent 0, buNone) and bold #28285E, with no extra space after it. Items sit at
  marL 400050, indent -285750, bullet ●, bullet colour #28285E, 14 pt `scheme:tx1`, spaced 6 pt
  before and 6 pt after so the gaps are even rather than trailing. Bold the item's lead-in label, in
  the same black. Three or four items, one list per slide, followed by the panel that says what the
  list adds up to.
- **Source citation.** Its own top-anchored text box, 10.5 pt italic `scheme:bg2`, right edge flush to
  6333796, top about 31000 EMU below the panel it supports.
- **Section divider.** On 1_Custom Layout, one text box at top 2217807, height 707886, holding a
  single 40 pt bold `+mj-lt` run in `scheme:tx2`, and nothing else on the slide. Size the box to its
  text and centre it on the slide axis, 3429000, not the column axis.
- **Dark content slide.** The whole page filled `scheme:bg2`, used where a slide is a signpost
  rather than an argument, such as the route through the lecture. Title in `scheme:tx2`, panel
  outlined in `scheme:bg1`, everything else in `scheme:tx2`. The closing sentence folds into the
  panel as a second paragraph instead of taking its own box.
- **Route list.** On a dark slide, one text box per step at 14 pt with `wrap="none"` and
  `spAutoFit`, a bold label, a colon, then the description in italic, all `scheme:tx2`. A vertical
  connector runs down the left with one small circle per step. Give the connector and the circles a
  light outline: navy on navy is not a style, it is a disappearance.
- **Build pair.** When a table or a list ends in a claim, make two slides, not one: the artifact
  alone, then the identical slide with the closing box added. Same title, same geometry, so only the
  new box appears when you advance. Slides 27 and 28, 29 and 30.
- Finish every content slide with one short closing line across the column, centred and bold, height
  260000 to 440000.

## Tables

- Span the column (width 6014545) on table style `{2D5ABB26-0587-4C30-8999-92F81FD0307C}`, with no
  cell fills, no vertical rules, and cell margins 95250 side, 47625 top and bottom.
- Draw the rules per cell: 1.5 pt (w=19050) `scheme:tx1` above the header row, 1.0 pt (w=12700) under
  every row.
- Bold the header row and the label column. Leave data cells regular.
- Colour the label column bold #28285E and every other cell `scheme:tx1`. Never set a whole table in
  navy.
- Set every body row to height 0 so it shrinks to its content, and keep a nominal height only on the
  header (300000). Even heights leave a gap under the header.
- Make the label column narrower than its text seems to need and give the width to the body column
  (1239525 plus 4775020 = 6014545). A three-column decision table is the exception: the label column
  takes the width it needs and the rest is split unevenly (3218428, 1648918, 1147199).
- Start a table that is the whole slide at 1491615, not at the top of the column: the band of white
  under the title is deliberate.
- Draw a 1.5 pt rule above the row where the table's sense changes, the way a `\midrule` does in the
  notes, not only above the header.
- Lay a two-option comparison table at 319251/700000/6014545/2450000 with columns 1150000, 2432272,
  2432273, and put the verdict box 410000 EMU below it.

## Writing on slides

- Put one sentence in the navy panel: the definition, the framing question, the demo's premise, or the
  claim that closes a list.
- Compress a borrowed sentence into a takeaway rather than reproducing it word for word, and drop the
  quotation marks when you do. If you keep the words, keep them exactly and keep the quotation marks.
- Keep the citation beside the definition it supports, not beside the takeaway.
- When you introduce an acronym, bold the cue letter in parentheses after each expanded term, as in
  (P), (E), (A), (S). Leave the acronym itself plain, and put the space before each parenthesis in its
  own unbolded run.
- Bold the lead-in phrase of a bullet or a cell and leave the rest regular.
- Close a forward-pointing bullet with a bold #C73561 parenthetical saying when the point starts to
  matter, and give every sibling bullet the same treatment.
- Write each failure bullet as one unit: the losing behaviour, its consequence, then the better
  behaviour. Cut words rather than add them when it reads long.
- Set a fixture, repository or corpus name in Maple Mono NF as its own run at the surrounding size,
  not bold and not recoloured.

## What Rahul corrects

These came from diffing his edits against the slides Codex handed him. They are corrections, so they
outrank anything inferred from Codex's own slides.

- Prefer his slides (3 to 8, and his edited 15 and 16) over Codex's unreviewed slides wherever the
  two disagree.
- Never park a quotation and its source inside the navy panel. Keep the definition there and move the
  rest out: the citation to its own box, the quoted sentence to the foot of the slide.
- Size a panel to 610801 and start it at the top of the column, rather than sizing it to the text you
  poured in.
- Pull the stack upward and tighten the gaps so the closing line fits, rather than letting the body
  run to the foot of the slide.
- Apply a note left on one bullet to every sibling in the list.
- Set row heights to auto rather than dividing the table height evenly.
- Send the room to the notes by number when a slide carries a figure or table the notes also carry:
  "names a row of the vocabulary table (Table 2) in the lecture notes."
- Let a box grow to hold a second line (430000 became 544308 on slide 24) rather than cutting words
  or shrinking the type.
- Split a slide that ends in a claim into a build pair rather than showing the claim with the
  evidence.
- Write "Us" in a table cell, not "We do".
- Cut a cell's qualifier rather than carry it: "The model", not "The model, within our schema".
- A panel may run to two sentences when the second one denies something: "It is a property of the
  program we have designed. It is not a prediction about what the model will do."
- Aim the closing line at what the students are about to build, not at the lecture's own structure:
  "When we build autonomous agents, we'll have to incorporate these into them. They don't come for
  free" replaced "Every later version spends one of the three".
- Prefer "the program we have designed" to "the program text".
- Write **ReACT** for the reactive loop when the slide names it, not ReAct.
- Prefer "acceptance is decoupled from the controller" to "acceptance moves off the thing that
  proposed".
- **Never use the "A, not B" contrast.** "The loop records observations, not intent", "more often,
  not less", "settled by the graph you compile, not by the prompt you write", "it arrives as input,
  not as the model's own reply" all got cut (ruled 2026-09-18). State the positive claim, or split
  it into two sentences where the second one denies something: "The graph you compile settles
  whether the judge is the proposer. No prompt can." This covers the whole family, including
  "A, and never B", "not X, but Y", and "not just". An ordinary comparative with "rather than"
  inside a sentence is fine; the banned shape is the trailing negated clause.
- **Write a descriptive title, not a riddle.** A title says what the slide is about, so that
  someone reading the deck afterwards can find it: "The edge from tools now has two destinations",
  not "The one edge that changed"; "Self-review, measured: accuracy and cost", not "What happens
  when a model grades itself"; "Where the accepting decision sits", not "Where acceptance lives".
  Describe the subject rather than the verdict, because the closing box carries the verdict. Keep
  it to roughly 45 characters so it stays on one line at 24 pt (ruled 2026-09-18; section 4's
  titles were rewritten in a single pass). Section 3's titles (slides 38 to 52) predate this and
  are still in the older teasing style.
- Turn a slide dark when it signposts rather than argues, and fold its closing sentence into the
  panel instead of giving it a box.

## Keeping this file current

Every edit Rahul makes is a correction to the house style, so fold it in here before making the next
slides. Run from the lecture folder:

1. Snapshot the deck as you hand it over:

       python3 slides/slidegrammar.py snapshot lecture2-1.pptx slides/snapshots/lecture2-1.latest.json

2. When it comes back edited, diff before you touch it:

       python3 slides/slidegrammar.py snapshot lecture2-1.pptx /tmp/now.json
       python3 slides/slidegrammar.py diff slides/snapshots/lecture2-1.latest.json /tmp/now.json

3. Read the diff as grammar. Each line names a slide, a shape and a property. Ask of every change: is
   this a fix to one slide, or a rule? A colour, a size, a margin, a row height, a new kind of box, or
   a wording pattern repeated twice is a rule.
4. Write the new rule into the list above with its value in parentheses, and delete any rule it
   replaces.
5. Re-snapshot, so the next diff starts clean.
6. Then make the slides, and check them before handing the deck back.

`python3 slides/slidegrammar.py summary <deck>.pptx` prints the deck's colours, sizes, fonts, column
positions and box idioms with counts. Read it when a rule here looks wrong, or when starting a deck
for a new lecture. The counts say what the deck does, which beats what this file remembers.

## Working on a deck

- Once Rahul has edited a deck, add slides to the real file. Never rebuild it from a script: a rebuild
  from a clean copy discards his edits and his comments.
- Check the package after every write. `zipfile` must report no duplicate part names. python-pptx
  assigns part names from the parts loaded in the session, so deleting and adding slides in one run
  can reuse a name a surviving slide still holds and overwrite it.
- Render before handing over. The previewer draws each slide with real font metrics and reports text
  that overflows its box or a table that grows past it. Fix what it reports. It reads the slide's own
  background, honours `wrap="none"`, draws connectors and ovals, and falls back to the deck's real
  defaults of 14 pt and black. Before trusting a render, check that it draws every shape the slide
  holds: a shape it silently skips is a shape you cannot see a fault in.
- **Never write a deck while PowerPoint has it open.** Check for a `~$<deck>.pptx` lock file first,
  and stop if one exists. On 2026-09-17 PowerPoint held `lecture2-1.pptx` open while it was rewritten
  underneath, then saved, and wrote all five image streams from stale offsets. The slide XML survived
  because it lives in memory; every picture in the deck became garbage that was not even a PNG.
  Recovery needed a donor copy of the media.
- Keep a dated copy of the deck in `slides/snapshots/` or the scratch directory before each write, so
  a donor exists. `unzip -t <deck>.pptx` must report no errors after every write; python-pptx's own
  reader will open a file whose images are already ruined.
