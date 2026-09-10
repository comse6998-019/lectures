# Lecture 1 deck — design

COMS 6998-019, Design of Production Agentic Systems. Columbia, Fall 2026.
Written 2026-09-09 for delivery Friday 2026-09-11.

## 1. Purpose and constraints

Lecture 1 is the orientation lecture. It must establish the course's thesis, its
vocabulary, its four-unit structure, its assessment, and the application the
class carries all semester — in one 110-minute meeting, to a room that is not
assumed to have built an agent before.

Fixed constraints, all from the course site and `instructor-materials/course_structure.md`:

| Constraint | Value |
| --- | --- |
| Slot | Friday 2026-09-11, 2:10–4:00pm, Hamilton 303 |
| Length | 110 minutes |
| Instructor | Rahul Krishna; TA to be announced |
| Assigned reading | Building effective agents; Poole & Mackworth §§2.1–2.3; CoALA §4 |
| Week-1 deliverable | Teams and repositories set up |
| Not yet assigned | HW1. It is released after week 2 |
| Not supplied | Any working agent. Students have no code on day one |
| Template | `lectures/template.pptx` |

The last two constraints are load-bearing. The lecture cannot end at an
assignment the way Stanford CS336's first lecture ends at Assignment 1, and it
cannot demonstrate student-owned code, because neither exists in week 1. It ends
instead at the week-1 obligation: form teams, create repositories, and locate an
alert in the pinned source.

### Structural model

The lecture is modeled on CS336 Lecture 1 (Stanford, "Language Modeling from
Scratch"), analyzed from its 79-minute recording. The proportions that transfer:

| CS336 section | Share of lecture |
| --- | --- |
| Staff introductions | 3% |
| Why the course exists, ending in the thesis | 12% |
| Field history, ending in "the fundamentals have not changed" | 9% |
| Artifact meta-explanation | 1% |
| Logistics, syllabus, why *not* to take it, AI policy | 9% |
| Course map, each unit ending in "so in Assignment N you will…" | 48% |
| Synthesis: re-derive every unit from the thesis | 2% |
| Teach the first unit for real, ending at its assignment | 18% |

The devices adopted here:

- Motivation before mechanics, mechanics before logistics.
- The course map is the largest section, and the map and the assessment are the
  same list presented once.
- One recurring question, restated in every unit, and used at the end to
  re-derive the whole map.
- A named section on why a student should *not* take the course.
- Real measured numbers rather than assertions, throughout.
- Question pauses at section seams rather than a single Q&A at the end.

The devices deliberately not adopted: CS336's executable-Python lecture format
(see §8), its leaderboard, and its practice of releasing the first assignment in
the first lecture.

## 2. Thesis

**How do we place a probabilistic model inside a software system without
surrendering the guarantees expected of production software?**

Supporting claim: **the model is a component of an agentic system, not the
system itself.**

CS336's thesis recurs because it is compact and measurable —
`accuracy = efficiency × resources`. Two rules give this course the same
property, and both are already implied by its own rubric:

1. **Ownership rule.** Every guarantee the system makes is owned by a component
   that is not the model.
2. **Measurement rule.** Every claim about an agent is a pair of runs — normal
   against exhausted, sequential against concurrent, uninterrupted against
   restarted.

The measurement rule is not a slogan. It is what all three homeworks require,
and it is why the rubric reads "a sound experiment earns full credit without a
speedup, a token reduction, or a confirmed hypothesis." Two slides from the
reference system prove it: a run that reports success having done nothing
(§4.9, candidate D), and three runs that cannot be compared to each other
because nothing was pinned across them (§4.6, unit 2).

The recurring question, asked at the close of every unit: **which component owns
this guarantee?**

## 3. Scope of the application

The course application is security-alert triage: an agent inspects a pinned
repository and returns structured, evidence-backed findings. Its role in
Lecture 1 is to be a workload large enough to exercise every systems concept —
many independent bounded investigations, each needing tool access, accumulated
evidence, and a verdict. It is a chassis, not a subject.

This has a concrete editorial consequence. Facts about security triage as a
discipline are out of scope: the distribution of true and false positives, the
uninformativeness of scanner severity, the composition of exploitability from
reachability and exposure and impact. That material argues that security triage
is hard, which is not what this course teaches. It is available in
`juice-shop-eval/` and is deliberately excluded.

Facts about *system behavior* measured on that workload are in scope, and carry
the lecture: turn counts, tool-call counts, wall-clock, terminal status, token
accounting, truncation, and missing terminal events.

The application is introduced at minute 84, after the architecture it
instantiates, and not before.

## 4. Structure

| Minutes | Section | Length |
| --- | --- | --- |
| 0–3 | Welcome | 3 |
| 3–13 | Why this course exists | 10 |
| 13–19 | How we got here | 6 |
| 19–26 | Logistics, and why not to take this course | 7 |
| 26–45 | Anatomy of an agentic system | 19 |
| 45–63 | Course map, units 1–2 | 18 |
| 63–66 | Break | 3 |
| 66–84 | Course map, units 3–4 | 18 |
| 84–90 | The job | 6 |
| 90–97 | Homeworks | 7 |
| 97–108 | Inspect one trace | 11 |
| 108–110 | Next week | 2 |

The break falls at minute 63 because that is the midterm/final seam: the midterm
covers units 1–2, the final emphasizes units 3–4. The map splits along the same
line, so the break separates the two halves of the assessment as well as the two
halves of the room's attention.

Question pauses: minute 19 (after history), minute 45 (after anatomy), minute 84
(after the map), minute 97 (after homeworks). Each is 30–45 seconds and is
absorbed by the following section's slack.

### 4.1 Welcome — 0:00–3:00

Instructor and TA. The room, the slot, the site. The promise in one sentence:
by December you will be able to design a production agentic system, not an agent
demo. No agenda slide.

### 4.2 Why this course exists — 3:00–13:00

The abstraction ladder, and where each rung leaks:

1. A single model call. Leaks when the answer needs facts the model does not have.
2. A tool-using loop. Leaks when it will not stop, or stops in the wrong place.
3. An agent runtime or framework. Leaks when the guarantee you need is not one
   the framework owns.
4. A production service. Leaks when a process restarts and accepted work is lost.

Then the reference system, as CS336 uses frontier language models: production
agentic systems already exist and are large. OSPREY, the instructor's triage
system, is eight coordinated agents over a code knowledge graph. Its measured
scale is on screen — 28,972 model turns and 32,010 tool calls in one 9.1-hour
run; four of twenty-two recorded runs cannot say how they ended.

What is out of reach in one semester: that system, that scale, that graph. What
transfers unchanged: the five component roles, the ownership question, and the
measurement discipline. This mirrors CS336's distinction between mechanics and
mindset, which transfer, and intuitions, which do not.

### 4.3 How we got here — 13:00–19:00

Poole & Mackworth chapter 2 supplies controller, environment, and belief state,
and predates large language models by decades. The systems problems in this
course — bounded execution, partial failure, durable state, recovery — are old
problems with mature vocabulary. What is new is that one component now *proposes*
the work, probabilistically.

Closing beat, matching CS336's "the fundamentals have not changed": the
engineering problems did not change when the model arrived. The authority
boundary did.

Pause for questions.

### 4.4 Logistics, and why not to take this course — 19:00–26:00

Site, CourseWorks discussions, office hours Fridays 12:00–1:30pm, email for
personal matters. Midterm Friday October 23, in class, one hour, individual,
closed book, units 1–2. Final Thursday December 17, individual, closed book,
emphasizing units 3–4 while connecting earlier units. Weights: three homeworks
and two exams at 20% each. Neither exam tests framework API memorization; both
ask for reasoning about scenarios.

The rubric gets its own slide, because it defines what the course rewards. Each
homework is marked out of 20 on four criteria worth five points each: systems
design and claim; experimental design; evidence and reproducibility;
interpretation and limitations. A sound experiment earns full credit without a
speedup, a token reduction, or a confirmed hypothesis. A missing required
mechanism does not.

Teams, one codebase all semester, submissions carrying configuration, pinned
dependencies, snapshots, raw logs, and a contribution statement. Six late days
per student, at most three on any one assignment. LangGraph is the supported
stack; another framework is acceptable if it meets the same behavioral
expectations. Prerequisites: Python, prior use of an LLM API with tool
definitions, and undergraduate systems background. Kubernetes is taught.

AI policy, stated as the course site states it: using an assistant to learn — to
explain a concept, debug your own code, review a design — is permitted, and so is
scoped autocomplete. Handing an assignment to an agent and submitting what it
produces is not, because it removes the practice this course is built on. Teams
must be able to explain every part of what they submit, and the individual exams
test that.

Why not to take this course, following CS336's example of naming the exclusions
plainly:

- It is not a prompting course, and not a prompt-engineering course.
- It is not a survey of agent frameworks.
- It is not about model training, fine-tuning, or evaluation of model quality.
- It is not a security course. Security appears as a workload and at the tool
  boundary in week 6.
- If your goal is results on your own application this semester, prompt a model
  first. Come back when the thing you need is a guarantee.
- It is implementation-heavy and teams own one codebase for fourteen weeks.

### 4.5 Anatomy of an agentic system — 26:00–45:00

The main technical section. Four beats.

**Beat 1, four minutes. Agent against agentic system.** The vocabulary ladder,
each rung adding a party that can fail: a model call, a fixed workflow, an
autonomous agent, a production agentic system. Precision here is the point;
these four terms are used exactly for the rest of the semester.

**Beat 2, eight minutes. The five roles.** One slide per row, then the assembled
table.

| Component | Owns | Does not own |
| --- | --- | --- |
| Model | Interpretation and proposed actions | Permission, durability, or execution guarantees |
| Controller | Control flow, validation, scheduling, termination | External facts |
| Tools | Narrow, typed interactions with external systems | Goals or global policy |
| State | Progress, evidence, context, and recoverability | Decision-making by itself |
| Environment | External truth, resources, effects, and failures | Internal orchestration |

Then the cross-cutting production concerns, drawn around the five boxes rather
than inside any one of them: bounded execution, partial failure, observability,
security and permissions, reproducibility, recovery. Each is a guarantee, and
each must be owned. The question that follows every unit for the rest of the
semester: which component owns this guarantee?

**Beat 3, five minutes. The tensions, as boundary disputes.** The five production
tensions are presented as arguments between two roles over one guarantee, not as
a list of themes:

| Tension | The dispute |
| --- | --- |
| Autonomy against control | The model proposes; the controller admits |
| Context against durable state | State inside the run against state that outlives it |
| Concurrency against coordination | The controller schedules; tools have real effects |
| Retries against side effects | The controller retries; the environment already happened |
| Capability against boundedness | The model's reach against the tool surface it is given |

**Beat 4, two minutes.** Why the model can own none of them, closing on the
supporting claim: the model is a component, not the system.

Pause for questions.

### 4.6 Course map — 45:00–63:00 and 66:00–84:00

Four units, roughly nine minutes each. Every unit follows one shape:

1. The driving question.
2. The named concepts, from `course_structure.md`.
3. The constraint the unit introduces that forces a redesign of what students
   already have.
4. Measured evidence from the reference system that the problem is real.
5. The closing slide: which component owns this guarantee?

| Unit | Weeks | Driving question | Role made real |
| --- | --- | --- | --- |
| 1. Agent architectures and dynamic workflows | 1–3 | Who chooses the next operation, and who decides when execution stops? | Model and controller |
| 2. Tool interfaces and concurrent agent execution | 4–6 | How does a requested action become a real effect, safely, and which effects may overlap? | Tools |
| 3. Context management, state, and persistence | 8–9 | What information is available now, and what survives the process? | State |
| 4. Deployment, fault recovery, and observability | 10–12 | How do we run it, and recover accepted work rather than merely restarting? | Environment |

Evidence assigned to each unit, all figures verified against
`sawmill/osprey/experiments/*/trajectory/events.jsonl` on 2026-09-09:

- **Unit 1.** `run-juice-10155d5b`: 50 steps, 236 model turns, 192 tool calls,
  terminal status `error` after 460 seconds. `run-juice-10155d5b-crash1`: dead at
  turn 31 after 285 seconds, having completed 2 steps. Termination is a design
  decision, and these runs did not own it.
- **Unit 2.** Three runs of the same application at increasing concurrency,
  presented as a cautionary slide rather than a speedup:

  | Run | Concurrency | Steps | Wall-clock | Status | `config_digest` |
  | --- | --- | --- | --- | --- | --- |
  | `run-odoo-fixed-c16` | 16 | 2,673 | 32,738 s | `ok` | `018c2a113c5e` |
  | `run-odoo-c32` | 32 | 2,993 | 22,430 s | `ok` | `5832dd922cc6` |
  | `run-odoo-fixed-c48` | 48 | 547 | 1,369 s | `error` | `b31602234173` |

  Read the wall-clock column alone and concurrency 48 looks 24 times faster. It
  is not: it errored after 547 of 2,673 steps. And the comparison is invalid
  anyway, because all three configuration digests differ — even the two runs
  loading the same TOML file. Nothing was pinned across them, so there is no
  variable being varied. Three anecdotes, not an experiment.

  This is why HW2 asks for "the same fixed work run sequentially and
  concurrently," and why `config_digest` is in the trace format at all: so that a
  run can tell you whether it is comparable to another one.
- **Unit 3.** `run-odoo-fixed-c16` token accounting:

  ```
  input          57,944
  output     29,516,316
  cache_read 883,599,352
  cache_create 69,559,000
  ```

  Count only `input` and you report 57,944 tokens for a run that moved roughly
  983 million. Also from the same run: 266 truncated tool results, a 4.7 MB
  `checkpoints.sqlite`, and a `large_tool_results/` directory — three separate
  admissions that context is a bounded resource.
- **Unit 4.** Of 22 recorded runs, 15 report `ok`, 3 report `error`, and 4 wrote
  no terminal event at all — `run-a2-1000`, `run-a2-1000-c16`,
  `run-juice-10155d5b-c4-aborted`, `run-odoo-fixed-c16-killed`. A process that
  dies does not get to write its own ending. Recovering accepted work is
  therefore not the same problem as restarting a process.

Four units against three homeworks is stated plainly rather than smoothed over:
HW3 spans units 3 and 4.

Pause for questions at minute 84.

### 4.7 The job — 84:00–90:00

The application, arriving after the architecture it instantiates. One real alert
on screen, reduced to the fields that matter:

```
severity      Medium
kind          CODE_FINDING
description   Untrusted user input in findOne() function can result in NoSQL Injection.
tool          Semgrep OSS
location      routes/delivery.ts:34
```

An alert is a hypothesis. A finding is a verdict plus evidence references, and
an unverifiable verdict is worth nothing. That is the entire domain content
required; the interesting part is the workload shape. Many independent bounded
investigations, each requiring code reading, accumulated evidence, and a
terminating decision. One run of the reference system staged 155 of them.

Then the four units re-read through the application, which is this lecture's
synthesis beat:

```
Architecture  controls how a triage proceeds
Tools         expose repository evidence
State         preserves investigation progress
Production    keeps the service observable and recoverable
```

This is the same alert that the trace section walks at minute 97.

### 4.8 Homeworks — 90:00–97:00

Three team assignments building one agent incrementally, each graded once.

**HW1, bounded agent execution.** A sequential reactive agent takes one JSON
alert and a repository path, uses source search and read tools, and returns a
structured TP/FP/Other finding with evidence references. Add a configurable
per-run token budget: pre-call admission with an output allowance, post-call
reconciliation of reported usage, and an explicit exhaustion outcome. Experiment:
one normal run and one scripted exhaustion run, showing the runtime refuses an
unaffordable invocation. Released after week 2.

**HW2, tool interfaces and coordinated execution.** Wrap CLDK as an MCP server
exposing its analysis surface as tools. Compare that structured-tool interface
against a CodeAct-style code-action interface over the same analyses. Organize
the application into explicit stages with conditional routing, and parallelize
one independent read-only section under a bounded concurrency limit. Guard the
tool boundary against prompt injection. Experiment: the same fixed work run
sequentially and concurrently.

**HW3, recoverable integrated prototype.** One context-compaction mechanism that
keeps artifact references and source identity; persisted run, progress, and
accounting state; one checkpointed stage. Deploy the agent and MCP server on a
local KIND cluster. Experiment: one uninterrupted run and one interrupted by a
Pod restart at a committed checkpoint, resumed as the same job. Repeat on a
larger application. Its report is the final project report.

Each brief's experiment is a pair of runs. Say so out loud, and point back to the
measurement rule.

This week: form teams, create repositories, establish the specification workflow,
configure dependencies, and inspect the pinned source and the JSON alerts. No
agent is required and none is supplied.

Pause for questions.

### 4.9 Inspect one trace — 97:00–108:00

Every component and the workload are now known, so the trace is readable. The
section opens by showing that the trace format *is* the anatomy:

```
run_start    argv, config_digest, run_id, schema_version   environment, reproducibility
step_start   ─┐                                            controller stages
turn_start    │  tokens{input, output,                      model calls
tool_call     │         cache_read, cache_create}           accounting
tool_result   │  ok, error, duration_ms,                    tools, partial failure
turn_end     ─┘  result_bytes, result_truncated             context pressure
step_end
run_end      status, elapsed_ms                             termination
```

Then the landscape: a filtered eight-row view of the 22 recorded runs for the
room, with the full table in the appendix.

Five candidate walkthroughs ship in the deck so the instructor selects at
delivery. Each candidate is a self-contained three-to-four slide block.

| | Run | Size | Why it is in the deck |
| --- | --- | --- | --- |
| A | `run-juice-10155d5b` | 954 events, 50 steps, 236 turns, status `error` | The honest spine: a complete run that fails |
| B | `run-juice-10155d5b-crash1` | 134 events, dies at turn 31 | Shortest. Failure first |
| C | `osprey-run-terra` `.traj` | 15 rendered turns with per-turn token tables | Most readable on a projector |
| D | `run-smoke-10155d5b` | 2 events, 526 ms, status `ok`, zero work | Sixty seconds. `ok` means nothing without a claim about work done |
| E | `run-odoo-fixed-c16` | 127,312 events, 28,972 turns, 9.1 hours | Scale |

Recommended delivery: D as a one-minute opener, A as the spine, B substituted if
running behind. C is the fallback if projector legibility is worse than expected.

The section closes on the alert from §4.7 and what a finding must carry.

### 4.10 Next week — 108:00–110:00

Week 2: agent architectures, state, and dynamic control flow. The question:
who chooses the next operation? Reading: ReAct §2 and one trajectory; LangGraph
workflows and agents; Reflexion §3. Due: teams and repositories.

## 5. Template and slide budget

`lectures/template.pptx` inspected 2026-09-09.

- Slide size 6,858,000 × 5,143,500 EMU — 7.5 × 5.625 inches, 4:3.
- Major and minor fonts both Fira Sans, set in `ppt/theme/theme1.xml` and
  `theme2.xml`. Fira Sans Regular measures 0.484 em average advance against
  Arial's 0.485, so the proportional fit budgets carry over unchanged.
- Monospace runs (event kinds, JSON keys, tool names) are Fira Code, applied
  per-run by the renderer rather than through the theme, which carries only a
  major and a minor face. Fira Code is fixed-pitch at 0.6154 em, wider than
  Menlo's 0.6021, so `MONO_ADVANCE` is 0.62 — the mono budget is pessimistic
  in the same direction as the proportional one.
- Palette: `dk1 #000000`, `lt1 #FFFFFF`, `dk2 #595959`, `lt2 #EEEEEE`,
  `accent1 #4285F4`, `accent2 #212121`, `accent3 #78909C`, `accent4 #FFAB40`,
  `accent5 #0097A7`, `accent6 #EEFF41`, hyperlinks `#0097A7`.
- Master text sizes present: 7.5, 10.5, 11.93, 16.2, 24 pt.

Ten layouts. Placeholder geometry is in inches, measured from the template, and
determines what each layout can actually hold:

| Layout | Placeholders (idx, pt, w × h in) | Use here |
| --- | --- | --- |
| `TITLE` | 0 title 31.5pt 6.99 × 2.24 · 1 subtitle 18pt 6.99 × 0.87 | Opening slide |
| `SECTION_HEADER` | 0 title 27pt 6.99 × 0.92 | Section breaks |
| `SECTION_HEADER_1` | 0 title 27pt 6.99 × 0.92 | Break slide |
| `TITLE_ONLY` | 0 title inherited 6.99 × 0.63 at top | Workhorse: heading plus 4.5 × 7.0 in of free canvas for drawn content |
| `ONE_COLUMN_TEXT` | 0 title 18pt 2.3 × 0.83 · 1 body 9pt 2.3 × 3.48 | Narrow left column only. Rarely useful |
| `MAIN_POINT` | 0 title 36pt 5.22 × 4.47 | Thesis, ownership rule, measurement rule |
| `SECTION_TITLE_AND_DESCRIPTION` | 0 title 31.5pt 3.32 × 1.62 · 1 subtitle 15.75pt 3.32 × 1.35 · 2 body 3.15 × 4.04 | Genuine two-column. Unit openers: name and driving question left, concepts right |
| `CAPTION_ONLY` | 1 body 4.92 × 0.66 at bottom | Captions under drawn figures |
| `BIG_NUMBER` | 0 title 90pt 6.99 × 2.15 · 1 body 6.99 × 1.42 | Measured figures, number above label. Heavily used |
| `BLANK` | — | Tables, diagrams, code |

Four consequences for the build:

- `BIG_NUMBER` is the right layout for measured figures and is used often, matching
  CS336's practice of one number on screen at a time. At 90pt in a 6.99-inch box
  it holds roughly ten characters, so `883,599,352` needs a size override or an
  abbreviated form. The fit check catches this rather than the projector.
- `SECTION_TITLE_AND_DESCRIPTION` is a real two-column layout and is the unit
  opener. There is still no picture or table layout, so every table, diagram, and
  code block is hand-placed on `TITLE_ONLY` or `BLANK`. That placement is real
  work and is budgeted for.
- `TITLE_ONLY`, `CAPTION_ONLY`, `BIG_NUMBER`'s label, and
  `SECTION_TITLE_AND_DESCRIPTION`'s body carry no explicit size and inherit
  10.5pt from the master, which is too small for a heading. The renderer sets
  sizes for these explicitly.
- The slide-number placeholder sits at 7.05, 5.19, so drawn content stays clear of
  the bottom-right corner. Usable canvas below a `TITLE_ONLY` heading is
  x 0.26–7.24, y 0.65–5.10.

The template is not empty: it ships with two seeded slides, a `TITLE` slide
reading "Designing Production Agentic Systems / Fall 2026" and an empty
`SECTION_HEADER_1`. The build removes both before adding its own.

Slide budget, approximately 97 delivered plus 16 appendix:

| Section | Slides |
| --- | --- |
| Welcome | 3 |
| Why this course exists | 9 |
| How we got here | 5 |
| Logistics and why not | 7 |
| Anatomy | 16 |
| Map units 1–2 | 14 |
| Break | 1 |
| Map units 3–4 | 14 |
| The job | 6 |
| Homeworks | 6 |
| Inspect one trace | 14 |
| Next week | 2 |
| Appendix: trace candidates B–E, full run table | 16 |

Every slide carries speaker notes with three things: seconds allotted, the claim
to make, and any question to ask.

## 6. Data sources

All figures verified 2026-09-09. No number reaches a slide unless it was read
from one of these sources by `extract.py`.

| Source | What it provides |
| --- | --- |
| `sawmill/osprey/experiments/*/trajectory/events.jsonl` | 22 runs. Schema version 1. Event kinds `run_start`, `step_start`, `turn_start`, `tool_call`, `tool_result`, `turn_end`, `step_end`, `run_end` |
| `juice-shop-osprey-runs/osprey-run-{terra,luna,sonnet5}/out/.traj/` | Rendered per-turn markdown with token tables. 15, 32, and 66 turns |
| `coms6998-E019.github.io/index.html` | Logistics, weights, rubric, AI policy, schedule, readings |
| `teaching/COMS6998-E019/instructor-materials/course_structure.md` | Unit definitions, week rows, homework briefs, week-1 obligations |
| `lectures/template.pptx` | Layouts, theme, dimensions |

Token accounting must report `input`, `output`, `cache_read`, and `cache_create`
as four separate quantities. Summing only `input` understates
`run-odoo-fixed-c16` by roughly four orders of magnitude. A course that grades
token accounting cannot get this wrong on its own slides.

### Redaction

Removed before any figure reaches a slide, enforced by a check in the build:

- The internal inference endpoint hostname and any API key or key-environment value.
- `NEO4J_PASSWORD` and all Neo4j connection details.
- `concert_assessment_id` UUIDs and the `concert-*` application name.
- References to the internal alert-producing product by name.
- EKS cluster, namespace, Pod, node, and instance identifiers.
- Absolute paths under `/Users/rkrsn`, rewritten to repository-relative form.

## 7. Build

```
lectures/week1/
  build.py            entry point: python3 build.py
  extract.py          reads events.jsonl and .traj, emits redacted data/*.json
  content/            one module per section, each returning slide descriptors
  data/               extracted, redacted figures. Committed
  out/lecture-01.pptx
  render/             PNG proofs
```

`python-pptx` against `template.pptx`. Content is data, not code: each section
module returns a list of slide descriptors naming a layout, placeholder text,
drawn shapes, and speaker notes. One renderer walks descriptors and emits the
deck. No new build framework.

Checks, per the repository's convention that non-trivial logic leaves one
runnable check behind:

- `extract.py` has an assert-based self-check pinning the verified figures for
  `run-juice-10155d5b`, `run-odoo-fixed-c16`, `run-smoke-10155d5b`, and the
  22-run status tally. If the source data or the extraction changes, it fails.
- The same self-check asserts the three odoo `config_digest` values are distinct,
  since unit 2's slide makes a claim about that fact.
- The build asserts every slide's text fits its placeholder's character budget,
  and that no redacted string appears anywhere in the output XML.
- `render/` is produced by exporting the deck to PDF through Microsoft PowerPoint
  via AppleScript, then rasterising with `pdftoppm`, and is inspected once before
  delivery. PowerPoint is the delivery target, so its own layout engine is the
  right one to proof against; LibreOffice is not installed and is not needed.

Available tooling, verified on this machine: Python 3.14.0, `python-pptx` 1.0.2,
`pytest` 9.1.1, Microsoft PowerPoint, `pdftoppm`.

## 8. Out of scope

- An executable-lecture renderer in the CS336 style. There is no agent codebase
  in week 1 to execute, and two days to deliver. Revisit from week 2, when
  student code exists.
- A live coded demo. High risk in a first lecture, and it would hand students
  HW1's answer.
- Security-triage domain content beyond one alert and one finding contract; see §3.
- Any build framework beyond a single script.
- Committing raw trace data. Only extracted, redacted figures are committed.

## 9. Risks

1. **The 36-minute map is the easiest section to overrun.** Mitigated by a hard
   slide cap per unit and per-slide seconds in the speaker notes.
2. **4:3 at 7.5 inches wide, in Fira Sans, is a small canvas for tables.** The 22-run
   table is filtered to eight rows for the room and kept whole in the appendix.
   Legibility is checked against rendered PNGs, not in the editor.
3. **Token figures are easy to get wrong**, as the first extraction pass here
   did. Four counters, always, and an assert-based check pinning them.
4. **Hand-placed diagrams cost time** because no picture layout exists and every
   figure is positioned explicitly. Tables are cheap — `python-pptx` provides a
   native table shape — but box-and-arrow diagrams are not. Diagram-heavy slides
   are built first, not last.
5. **The concurrency comparison is not a speedup and must not be drawn as one.**
   c48 is faster because it failed, and the three runs have three different
   configuration digests, so they are not comparable at all. Drawing this as a
   scaling curve would be wrong and would teach the opposite of the measurement
   rule. The slide must state both defects explicitly.
6. **Every remaining cross-run comparison in the deck needs the same check.**
   `config_digest` and terminal status are verified for any two runs shown
   together, and a run pair that fails the check is either dropped or presented,
   like unit 2's, as a negative example.

## 10. Definition of done

- `out/lecture-01.pptx` opens in PowerPoint and Keynote with no missing fonts
  and no overflowing placeholders.
- Every measured figure on a slide traces to `data/*.json`, and `extract.py`'s
  self-check passes.
- Every slide comparing two or more runs states their terminal status, and the
  runs' `config_digest` values have been checked.
- No redacted string appears in the output.
- Speaker notes on every slide, carrying seconds, claim, and question.
- Section minute marks sum to 110, and the notes' per-slide seconds sum to each
  section's budget.
- All five trace-walkthrough candidates are present and selectable at delivery.
- A full PDF export from PowerPoint has been rasterised and reviewed once end to
  end, with no clipped text and no content under the slide-number placeholder.
- The four-units-against-three-homeworks mismatch and the HW1 release timing are
  stated on slides, not left implicit.
