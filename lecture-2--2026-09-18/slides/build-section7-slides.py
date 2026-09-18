"""Section 7 of the notes (Routing, feedback loops, and termination) as slides.

    DECK=../lecture2-1.pptx OUT=/tmp/built.pptx python3 build-section7-slides.py

Appends eleven content slides. Table heights are rendered totals measured with preview.py: body
rows are height 0 by the house rule, so a table's declared box says nothing about what it fills.
"""
import os
import sys

from pptx import Presentation
from pptx.dml.color import RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from partb_grammar import (GREY, bullets, check, citation, closing_filled, closing_line,
                           code_caption, code_panel, content_slide, notes, panel, table)

DECK = os.environ.get("DECK", "../lecture2-1.pptx")
OUT = os.environ["OUT"]
FIGS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
MAGENTA = RGBColor(0xC7, 0x35, 0x61)

prs = Presentation(DECK)
start = len(prs.slides)

# ---------------------------------------------------------------- 1. the three responsibilities
s = content_slide(prs, "Where the next node is chosen", keep_body=True)
bullets(s, "Three responsibilities, on three different components.", [
    [("The model proposes. ", 'b'), ("A tool call, a plan, a candidate, a judgement. Every one of "
                                     "those is a value.", '')],
    [("The runtime records. ", 'b'), ("It merges the proposal through the reducers and writes what "
                                      "happened to the trace.", '')],
    [("The router decides. ", 'b'), ("It reads named fields and returns a node name.", '')],
], 700000, 1970000)
panel(prs, s, [("A conditional edge is a function that receives the current state and returns the "
                "name of the next node.", '')], 2820000)
citation(s, "LangGraph, Graph API", 3461801)
closing_line(s, [("It runs in the runtime's process, and its return value is the transition.",
                  '')], 3690000)
notes(s, "Both things are true at once, and that is what makes the arrangement worth describing "
         "carefully. The model's output decides which way the comparison comes out. The comparison "
         "decides where the run goes. A router that reads the model's prose has handed the control "
         "decision back to the model.")

# ---------------------------------------------------------------- 2. the graph
s = content_slide(prs, "The complete graph, with both back edges")
s.shapes.add_picture(f"{FIGS}/graph-v4-deck.png", 250147, 800000, width=6152752)
closing_line(s, [("Every edge is a line of wiring code, and every label is a predicate over state.",
                  '')], 3250000)
notes(s, "The upper back edge revises a plan inside an attempt. The lower path runs the reflection "
         "step and begins a new attempt. Compilation fixes this object; what differs between two runs "
         "on the same alert is the sequence of states, and therefore the sequence of edges the routers "
         "select.")

# ---------------------------------------------------------------- 3. what the router reads
s = content_slide(prs, "What the router actually reads")
code_caption(s, "after_controller, the loop's only branch", 800000)
code_panel(s, [
    [("def after_controller(self, state) -> str:", None)],
    [("    if state[\"status\"] != RUNNING:", None)],
    [("        return END", None)],
    [("    if state[\"messages\"][-1].tool_calls:", None)],
    [("        return \"tools\"", None)],
    [("    return \"submit\"", None)],
], 1060000, 1250000)
panel(prs, s, [("A model that writes “I am confident, submit it” moves the run exactly as "
                "far as a model that writes nothing.", '')], 2600000)
closing_line(s, [("The branch is taken on the presence of a tool call.", '')], 3450000)
notes(s, "Two fields, and there is no third condition. It never reads the model's prose. after_submit "
         "is one line: END when the submission was accepted, the controller otherwise.")

# ---------------------------------------------------------------- 4. who decided
s = content_slide(prs, "Reading who decided from the trace", keep_body=True)
bullets(s, "A routing event names who supplied the value the predicate tested.", [
    [("by=\"runtime\" ", 'code'), ("when a limit fired before any call was issued.", '')],
    [("by=\"model\" ", 'code'), ("when the model's output selected the branch.", '')],
    [("Neither means the model chose the edge. ", 'b'),
     ("The edge was chosen when we wrote the predicate.", '')],
], 700000, 1780000)
panel(prs, s, [("The routing event names the origin of the value, and the predicate stays ours.",
                '')], 2700000)
closing_line(s, [("This is the field to read when a run surprises us.", '')], 3550000)
notes(s, "When a run does something unexpected, this is the first thing to open. The decision field "
         "tells you which branch was taken; the by field tells you whether a limit fired or a model "
         "output selected it.")

# ---------------------------------------------------------------- 5. one graph, many paths
s = content_slide(prs, "One compiled graph, different paths")
code_caption(s, "compile() wires it once, and the object is the same on every run", 800000)
code_panel(s, [
    [("graph.add_edge(START, \"controller\")", None)],
    [("graph.add_conditional_edges(\"controller\", self.after_controller, ...)", None)],
    [("graph.add_edge(\"tools\", \"controller\")", None), ("   # the loop's one back edge", GREY)],
    [("graph.add_conditional_edges(\"submit\", self.after_submit, ...)", None)],
], 1060000, 1000000)
panel(prs, s, [("Delete that one line and the same three nodes become a chain.", '')], 2350000)
closing_line(s, [("The recorded run enters the controller four times, and the graph never changes.",
                  '')], 3200000)
notes(s, "Three nodes, two conditional edge sets, one unconditional edge. The conditional edges are "
         "what give one compiled graph its different shapes at run time. A dynamic path does not "
         "require a dynamic graph.")

# ---------------------------------------------------------------- 6. two back edges
s = content_slide(prs, "Two returns to the planner")
table(s,
      [[("Back edge", '')], [("Trigger", '')], [("Retained", '')], [("Reset", '')]],
      [
          [[("In-run plan revision", 'm')],
           [("A planned step still fails after the runtime's free retry", '')],
           [("The attempt's observations and its accounting", '')],
           [("The remaining subgoals, which the planner rewrites", '')]],
          [[("New attempt after reflection", 'm')],
           [("The validator rejects and the attempt limit permits another try", '')],
           [("Reflections, identity, the counters, the usage ledger", '')],
           [("Observations, plan, candidate patch, validation", '')]],
      ],
      1400000, [1250000, 1650000, 1557272, 1557273], size=10, height=1500000)
closing_filled(s, [("Collapse them and the system rewrites its plan over every ", ''),
                   ("transient tool error", 'b'), (".", '')], 3250000)
notes(s, "One asks what to do about a step that did not work. The other asks what to do about an "
         "attempt that did not work. Both edges arrive with the planner and the reflection step, which "
         "is what the colour on the labels marks.")

# ---------------------------------------------------------------- 7. ownership
s = content_slide(prs, "Who owns each return", keep_body=True)
bullets(s, "Ownership divides on the same line as the two edges.", [
    [("The free retry is ours. ", 'b'), ("The runtime reissues a failed tool call once, because a "
                                         "transient failure is not evidence about the plan.", '')],
    [("The revision is the model's proposal. ", 'b'), ("The runtime records it and merges it into ",
                                                       ''), ("plan", 'code'), (".", '')],
    [("The new attempt is ours. ", 'b'), ("It is a comparison on the attempt counter.", '')],
], 700000, 1990000)
panel(prs, s, [("A limit that the model can talk its way past is not a limit.", '')], 2850000)
closing_line(s, [("The retry before the upper edge costs no model call.", '')], 3700000)
notes(s, "That last point is what makes the retry the runtime's decision rather than the model's: "
         "nobody is consulted, and nothing is paid for.")

# ---------------------------------------------------------------- 8. what stops a loop
s = content_slide(prs, "Three limits the runtime checks", keep_body=True)
bullets(s, "An acceptance condition says when a loop may stop. It does not establish that it will.", [
    [("The model-call budget. ", 'b'), ("Forty per run, checked before the call is issued rather "
                                        "than after.", '')],
    [("The stall check. ", 'b'), ("Three consecutive observations with identical results end the "
                                  "run.", '')],
    [("The attempt limit. ", 'b'), ("Two attempts, counted in a field that survives the reflection "
                                    "reset.", '')],
], 700000, 2200000)
panel(prs, s, [("All three are comparisons the runtime performs on fields it owns.", '')], 3010000)
closing_line(s, [("The framework's recursion limit sits underneath, as a failsafe on wiring.",
                  '')], 3860000)
notes(s, "A limit checked afterwards is a post-mortem: the call has already been paid for. The stall "
         "check compares results rather than requests, because that also catches six distinct searches "
         "that all return nothing, which is the repeated-action failure ReAct reports for its own "
         "trajectories. And an attempt counter that reset with the attempt would bound nothing.")

# ---------------------------------------------------------------- 9. the status vocabulary
s = content_slide(prs, "The five terminal statuses", keep_body=True)
bullets(s, "The vocabulary is closed on purpose.", [
    [("Set by the loop. ", 'b'), ("accepted", 'code'), (", ", ''), ("budget_exhausted", 'code'),
     (", ", ''), ("no_progress", 'code'), (" and ", ''), ("error", 'code'), (".", '')],
    [("Arrives with the attempt limit. ", 'b'), ("unresolved", 'm'), (".", '')],
    [("The trace writer refuses both mistakes. ", 'b'), ("A status outside the set, and a trace "
                                                         "closed with no terminal event.", '')],
], 700000, 1780000)
panel(prs, s, [("A run that never said how it ended is a defect in our instrumentation rather than "
                "an outcome we can report.", '')], 2700000)
closing_line(s, [("Reaching END establishes only that the graph stopped.", '')], 3550000)
notes(s, "Errors and outcomes are not the same thing: a refused tool call is an observation inside a "
         "run that can still end accepted, and a process killed between two events leaves a run with "
         "no status at all. The reason lives in status, which we set.")

# ---------------------------------------------------------------- 10. three readings
s = content_slide(prs, "What a trace lets you conclude")
table(s,
      [[("What the trace records", '')], [("What it supports", '')]],
      [
          [[("A verdict, then a terminal event with status accepted", '')],
           [("A completed assessment under the runtime's acceptance rules, whose quality is a "
             "separate question", '')]],
          [[("A terminal event with a stop status and its reason", '')],
           [("A declared end to execution, with whatever partial evidence the run had gathered",
             '')]],
          [[("No terminal event", '')],
           [("Completion has not been established by this record", '')]],
      ],
      1491615, [2400000, 3614545], size=12, height=1860000)
closing_filled(s, [("The third is a statement about the evidence. Treating it as an ", ''),
                   ("error", 'b'), (" attributes a cause the record does not carry.", '')],
               3600000, height=540000)
notes(s, "Five statuses, three readings. The run in the third row may still be active, may have been "
         "interrupted, or may have written an incomplete trace, and the record does not say which.")

# ---------------------------------------------------------------- 11. three endings
s = content_slide(prs, "Three endings, in the recorded runs", keep_body=True)
bullets(s, "The difference between them is where the last event sits.", [
    [("Accepted. ", 'b'), ("Event seventeen is a terminal record with the usage totals, written "
                           "after submit reported three passing checks.", '')],
    [("Budget exhausted. ", 'b'), ("The check fires before the call, so no fifth model call sits "
                                   "between the routing event and the terminal one.", '')],
    [("No ending observed. ", 'b'), ("Interrupt between a tool result and the next model call: "
                                     "every event is valid and no terminal record arrives.", '')],
], 700000, 2010000)
panel(prs, s, [("What we may not say is which ending would have arrived.", '')], 2870000)
closing_line(s, [("An excerpt used in teaching is worth marking with how it was produced.",
                  '')], 3720000)
notes(s, "The first ending is the recorded run, runs/v1-bc284c6b.jsonl. The routing event just before "
         "the terminal one carries by=runtime: nothing in that trace is a model's opinion about "
         "whether the work was done. In the second, the evidence the run gathered is still in "
         "observations, and the absence of a finding is not the absence of work.")

# ----------------------------------------------------------------
bad = check(prs, start)
if bad:
    print("GEOMETRY FAILURES")
    for b in bad:
        print("  " + b)
    sys.exit(1)
prs.save(OUT)
print(f"{len(prs.slides) - start} slides appended, {start + 1} to {len(prs.slides)} -> {OUT}")
