from pathlib import Path
from os.path import relpath
import argparse
import hashlib
import json
import re
import struct
import subprocess

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
BUILD = ROOT / "build"
SHARED = ROOT.parents[3] / "assets" / "standalone-style.tex"

STYLE = r"""
\tikzset{
  card/.style={gnode, draw=deckNavy, text=black, font=\sffamily\fontsize{11}{13}\selectfont,
    minimum height=9mm, text width=3.3cm, align=center},
  main/.style={card, fill=deckLilac!45},
  record/.style={card, fill=black!4, align=left},
  lost/.style={card, draw=deckRose, fill=deckRose!7},
  quiet/.style={card, draw=black!25, text=black!40, dashed},
  title/.style={font=\sffamily\fontsize{12}{14}\selectfont\bfseries, text=deckNavy, inner sep=1pt},
  caption/.style={font=\sffamily\fontsize{10.5}{12}\selectfont, text=deckGrey, align=center},
  edge/.style={-{Stealth[length=2.2mm]}, draw=deckNavy, line width=0.9pt},
  risk/.style={edge, draw=deckRose, line width=1.4pt},
  boundary/.style={draw=deckNavy, dashed, rounded corners=3pt, line width=0.9pt},
}
\newcommand{\stepedge}[3]{\atstage{#1}{%
  \ifnum\stage=#1\draw[edge,line width=1.4pt] (#2) -- (#3);%
  \else\draw[edge] (#2) -- (#3);\fi}}
"""

FIGURES = []


def add(name, topics, steps, body, height=5.4):
    FIGURES.append({"name": name, "topics": topics, "steps": steps, "body": body, "height": height})


add("context-input", ["5.1"], [
    "Add instructions and tool definitions.",
    "Add messages and observations.",
    "Add selected source material.",
    "Assemble the request and leave other records outside.",
], r"""
\node[main, text width=4.3cm, minimum height=27mm] (req) at (12.9,2.9) {\textbf{One model call}\\assembled context};
\node[caption] at (12.9,0.75) {Only selected material enters.};
\node[record, text width=5.5cm] (ins) at (3.6,4.5) {Instructions and tools};
\stepedge{1}{ins.east}{req.north west}
\atstage{2}{\node[record, text width=5.5cm] (hist) at (3.6,3.2) {Messages and observations};}
\stepedge{2}{hist.east}{req.west}
\atstage{3}{\node[record, text width=5.5cm] (ext) at (3.6,1.9) {Selected source material};}
\stepedge{3}{ext.east}{req.south west}
\atstage{4}{\node[quiet, text width=5.5cm] at (3.6,0.6) {Other records stay outside};}
""")

add("objectives", ["5.2"], [
    "Start with the next useful decision.",
    "Add the resource budget.",
    "Check whether the record preserves meaning.",
    "Keep access to the source record.",
], r"""
\node[main, text width=4.6cm, minimum height=16mm] (dec) at (8.25,2.7) {\textbf{Next decision}\\Order more SKU-A?};
\node[record, text width=3.7cm] (quality) at (2.6,4.3) {\textbf{Task quality}\\Correct next action};
\stepedge{1}{quality.south east}{dec.north west}
\atstage{2}{\node[record, text width=3.7cm] (budget) at (13.9,4.3) {\textbf{Efficiency}\\Tokens, time, charges};}
\stepedge{2}{budget.south west}{dec.north east}
\atstage{3}{\node[record, text width=3.7cm] (faith) at (2.6,1.0) {\textbf{Faithfulness}\\Paid order still recorded};}
\stepedge{3}{faith.north east}{dec.south west}
\atstage{4}{\node[record, text width=3.7cm] (source) at (13.9,1.0) {\textbf{Source access}\\Read the order ledger};}
\stepedge{4}{source.north west}{dec.south east}
""")

add("capacity-cost", ["5.3"], [
    "Show the capacity limit of one request.",
    "Repeat the history across three calls.",
    "Add the work of compression and retrieval.",
], r"""
\node[title] at (3.8,4.9) {One request};
\draw[boundary] (0.7,2.1) rectangle (6.9,4.4);
\node[main, text width=3.6cm] at (2.8,3.5) {Input tokens};
\node[card, text width=1.5cm] at (5.9,3.5) {Output\\room};
\node[caption] at (3.8,2.55) {A finite context window};
\atstage{2}{
  \node[title] at (11.65,4.9) {The complete run};
  \foreach \x/\n in {8.8/1,11.6/2,14.4/3}{
    \node[main, text width=1.9cm] at (\x,3.5) {Call \n\\history again};}
  \draw[edge] (9.95,3.5) -- (10.45,3.5);
  \draw[edge] (12.75,3.5) -- (13.25,3.5);
  \node[caption] at (11.6,2.45) {Count tokens across every call.};
}
\atstage{3}{
  \node[record, text width=13.7cm] at (8.25,0.9) {Also count summary calls, source reads, elapsed time, and charges.};
}
""")

add("evidence-position", ["6.1"], [
    "Place the relevant passage near the start.",
    "Move the same passage to the middle.",
    "Move it near the end and state the study limits.",
], r"""
\node[title] at (8.25,4.9) {The same relevant passage, three positions};
\foreach \i in {1,...,9}{
  \pgfmathsetmacro{\x}{0.9+(\i-1)*1.82}
  \node[quiet, text width=1.5cm, minimum height=13mm] at (\x,3.1) {doc \i};
}
\onlystage{1}{\node[main, text width=1.5cm, minimum height=13mm] at (0.9,3.1) {relevant};}
\onlystage{2}{\node[main, text width=1.5cm, minimum height=13mm] at (8.18,3.1) {relevant};}
\onlystage{3}{\node[main, text width=1.5cm, minimum height=13mm] at (15.46,3.1) {relevant};}
\node[caption] at (8.25,1.65) {Position schematic for Lost in the Middle. No scores appear here.};
\atstage{3}{\node[caption] at (8.25,0.65) {Apply the result to the models, prompts, and tasks in Liu et al. (2024).};}
""")

add("context-tasks", ["6.2"], [
    "Retrieve a specified fact.",
    "Trace a value through several assignments.",
    "Combine several facts into one answer.",
], r"""
\node[title, anchor=west] at (0.5,4.65) {Retrieve};
\node[record, text width=5.1cm] (r) at (6.2,4.5) {Record: SKU-A arrives on Day 4};
\node[main, text width=3.3cm] (ra) at (13.6,4.5) {Answer: Day 4};
\draw[edge] (r.east) -- (ra.west);
\atstage{2}{
  \node[title, anchor=west] at (0.5,2.95) {Trace};
  \node[record, text width=2.1cm] (a) at (4.7,2.8) {$a=4$};
  \node[record, text width=2.1cm] (b) at (8.9,2.8) {$b=a$};
  \node[main, text width=2.1cm] (c) at (13.6,2.8) {$c=b=4$};
  \draw[edge] (a.east) -- (b.west); \draw[edge] (b.east) -- (c.west);
}
\atstage{3}{
  \node[title, anchor=west] at (0.5,1.25) {Aggregate};
  \node[record, text width=5.1cm] (vals) at (6.2,1.1) {Two orders: 4 units and 6 units};
  \node[main, text width=3.3cm] (sum) at (13.6,1.1) {Total: 10 units};
  \draw[edge] (vals.east) -- (sum.west);
}
\node[caption] at (8.25,0.2) {Teaching examples of task types. These are not RULER scores.};
""")

add("context-choices", ["7.1"], [
    "Retain original material.",
    "Retrieve a record through a reference.",
    "Select tokens from the source.",
    "Rewrite the source as a summary.",
], r"""
\node[record, text width=3.0cm, minimum height=27mm] (src) at (2.2,2.8) {\textbf{Source history}\\messages\\tool results\\records};
\foreach \k/\y/\verb/\out in {1/4.6/Retain/{Original messages},2/3.4/Retrieve/{Fetched record},3/2.2/Extract/{Selected tokens},4/1.0/Rewrite/{Generated summary}}{
  \atstage{\k}{
    \node[main, text width=2.6cm] (op\k) at (7.9,\y) {\verb};
    \node[card, text width=3.5cm] (out\k) at (13.7,\y) {\out};
    \draw[edge] (src.east) -- (op\k.west); \draw[edge] (op\k.east) -- (out\k.west);
  }
}
""")

add("extractive", ["7.2", "7.4b"], [
    "Show a source passage from the teaching case.",
    "Classify each source token as keep or drop.",
    "Assemble the selected source words.",
    "Check whether deletion loses the paid order or due date.",
], r"""
\node[record, text width=14.0cm] (src) at (8.25,4.55) {\textbf{Source}\\SKU-A is empty. The order is paid and due on Day 4.};
\atstage{2}{
  \node[main, text width=6.2cm] (model) at (8.25,3.05) {Classifier: keep or drop each token};
  \draw[edge] (src.south) -- (model.north);
}
\atstage{3}{
  \node[record, text width=10.8cm] (kept) at (8.25,1.6) {\textbf{Selected source words}\\SKU-A empty. order paid due Day 4.};
  \draw[edge] (model.south) -- (kept.north);
}
\atstage{4}{\node[caption, text=deckRose] at (8.25,0.45) {Test the paid order and due date after deletion.};}
""")

add("abstractive", ["7.3", "7.4c"], [
    "Start from messages and source records.",
    "Generate a shorter account in new words.",
    "Assemble the next request from the summary and recent messages.",
    "Check for omissions and unsupported claims.",
], r"""
\node[record, text width=3.8cm, minimum height=22mm] (old) at (2.6,3.4) {\textbf{Earlier history}\\Day 1: 10 units ordered\\Payment complete\\Expected arrival: Day 4};
\atstage{2}{\node[main, text width=3.8cm, minimum height=22mm] (sum) at (8.25,3.4) {\textbf{Generated summary}\\A paid order for 10 units\\is due on Day 4.};}
\stepedge{2}{old.east}{sum.west}
\atstage{3}{\node[card, text width=3.8cm, minimum height=22mm] (req) at (13.9,3.4) {\textbf{Next request}\\Summary\\Recent messages};}
\stepedge{3}{sum.east}{req.west}
\atstage{4}{\node[lost, text width=12.8cm] at (8.25,1.0) {Check the order, payment, date, and source before the next action.};}
""")

add("recency", ["7.4a"], [
    "Show the old commitment among the recorded turns.",
    "Keep the recent turns and dim the older turns.",
    "Remove the older turns and expose the lost commitment.",
], r"""
\node[title] at (8.25,4.9) {History in time order};
\foreach \i/\x/\txt in {1/1.65/{Day 1\\Order paid},2/4.3/{Day 1\\Due Day 4},3/6.95/{Day 2\\Tool result},4/9.6/{Day 3\\Empty shelf},5/12.25/{Day 3\\No sales},6/14.9/{Day 3\\Next step}}{
  \ifnum\i<4
    \onlystage{1}{\node[record, text width=1.8cm, minimum height=16mm] at (\x,3.35) {\txt};}
    \onlystage{2}{\node[quiet, text width=1.8cm, minimum height=16mm] at (\x,3.35) {\txt};}
  \else
    \node[main, text width=1.8cm, minimum height=16mm] at (\x,3.35) {\txt};
  \fi
}
\atstage{2}{\draw[boundary] (8.35,2.1) rectangle (16.1,4.4); \node[caption] at (12.2,2.45) {Retained recent turns};}
\atstage{3}{\node[lost, text width=13.0cm] at (8.25,0.9) {The retained text loses the paid order and expected arrival.};}
""")

add("structured-notes", ["7.4d"], [
    "Write the goal in a state card.",
    "Add the paid order as an open commitment.",
    "Update its next check while the run advances.",
], r"""
\draw[boundary] (2.0,0.6) rectangle (14.5,4.9);
\node[title] at (8.25,4.5) {Task state card};
\node[record, text width=10.5cm] at (8.25,3.65) {\textbf{Goal:} keep SKU-A available};
\atstage{2}{\node[main, text width=10.5cm] at (8.25,2.45) {\textbf{Open order:} 10 units, paid, expected Day 4};}
\atstage{3}{\node[record, text width=10.5cm] at (8.25,1.25) {\textbf{Next check:} confirm delivery on Day 4};}
""")

add("delegation", ["7.4e"], [
    "Start a subtask in a separate context.",
    "Keep its large reads inside that context.",
    "Return a short result to the main agent.",
], r"""
\node[main, text width=3.8cm, minimum height=18mm] (main) at (2.7,3.25) {\textbf{Main context}\\Decide whether to order};
\draw[boundary] (7.0,0.9) rectangle (16.0,4.8);
\node[title] at (11.5,4.4) {Separate sub-agent context};
\node[card, text width=4.8cm] (task) at (11.5,3.25) {Check the pending order};
\draw[edge] (main.east) -- node[lab,above] {subtask} (task.west);
\atstage{2}{\node[record, text width=6.6cm] at (11.5,1.9) {Ledger and delivery notices stay here.};}
\atstage{3}{\draw[edge,dashed] (task.west) -- (6.3,2.0) -- node[lab,below] {Paid. Due Day 4.} (4.8,2.0) -- (main.south east);}
""")

add("retrieval", ["7.4f"], [
    "Keep a compact reference inside the request.",
    "Fetch the matching record from an external store.",
    "Return the evidence needed for the next decision.",
], r"""
\draw[boundary] (0.5,1.6) rectangle (6.9,4.8);
\node[title] at (3.7,4.4) {Current context};
\node[main, text width=4.5cm] (ref) at (3.7,3.25) {\textbf{Reference}\\\texttt{inventory-ledger}, Day 1};
\node[record, text width=5.6cm, minimum height=22mm] (store) at (12.5,3.25) {\textbf{External records}\\Day 1: 10 units, paid\\Expected Day 4};
\atstage{2}{\draw[edge] (ref.east) -- node[lab,above] {fetch by reference} (store.west);}
\atstage{3}{\draw[edge,dashed] (store.south) -- (12.5,1.2) -- node[lab,below] {return the source record} (3.7,1.2) -- (ref.south);}
\node[caption] at (8.25,0.4) {Check that the reference still reaches the needed evidence.};
""")

add("harness-branches", ["7.5"], [
    "Replace the older trajectory with a summary branch.",
    "Add an isolated sub-agent context.",
    "Retry a failed path from a recorded point.",
], r"""
\node[record, text width=2.3cm] (hist) at (1.8,3.25) {Earlier history};
\node[main, text width=2.8cm] (sum) at (6.8,3.25) {Summary branch};
\node[main, text width=2.8cm] (next) at (13.7,3.25) {Main run continues};
\draw[edge] (hist.east) -- (sum.west); \draw[edge] (sum.east) -- (next.west);
\atstage{2}{
  \draw[boundary] (8.8,0.6) rectangle (16.0,2.0);
  \node[card, text width=4.7cm] (sub) at (12.4,1.3) {Isolated sub-agent reads};
  \draw[edge] (sum.south) -- (sub.west); \draw[edge,dashed] (sub.north) -- (next.south);
}
\atstage{3}{
  \node[lost, text width=2.8cm] (fail) at (10.2,4.65) {Failed path};
  \draw[risk] (sum.north) -- (fail.west);
  \draw[edge,dashed] (fail.east) to[out=0,in=80] node[lab,right] {retry} (next.north);
}
\node[caption] at (4.0,0.6) {Schematic of the practice in QwenGyre.};
""")

add("pi-format", ["7.5a"], [
    "Show the fixed summary sections.",
    "Keep recent messages after the summary.",
    "Carry the cumulative file lists with the record.",
], r"""
\node[main, text width=7.3cm, minimum height=27mm] (sum) at (4.8,3.45) {\textbf{Pi summary}\\Goal \quad Constraints and Preferences\\Progress \quad Key Decisions\\Next Steps \quad Critical Context};
\atstage{2}{
  \node[card, text width=4.7cm, minimum height=27mm] (recent) at (13.0,3.45) {\textbf{Recent messages}\\\texttt{keepRecentTokens}\\Default: 20k tokens};
  \draw[edge] (sum.east) -- (recent.west);
}
\atstage{3}{\node[record, text width=13.4cm] at (8.25,1.05) {\textbf{Cumulative file lists}\\\texttt{readFiles} \qquad \texttt{modifiedFiles}};}
""")

add("claude-format", ["7.5b"], [
    "Replace conversation history with a structured summary.",
    "Read up to five recent files again.",
    "Add hook output and skill text again.",
], r"""
\node[main, text width=8.5cm] (sum) at (8.25,4.3) {\textbf{Claude Code}\\Structured conversation summary};
\atstage{2}{
  \foreach \i in {1,...,5}{
    \pgfmathsetmacro{\x}{1.7+(\i-1)*3.25}
    \node[record, text width=2.1cm] at (\x,2.7) {Recent file \i};
  }
  \draw[edge] (8.25,3.75) -- (8.25,3.25);
  \node[caption] at (8.25,1.75) {Over 5000 tokens: keep a path reference.};
}
\atstage{3}{\node[record, text width=12.7cm] at (8.25,0.65) {Add hook output and skill text again. Keep sub-agent reads separate.};}
""")

add("codex-format", ["7.5c"], [
    "Write the context-checkpoint handoff summary.",
    "Retain the state of the tools the previous model used.",
    "Keep cross-session memories separate from this compaction step.",
], r"""
\node[main, text width=6.4cm, minimum height=25mm] (sum) at (4.3,3.5) {\textbf{Codex handoff summary}\\Progress and key decisions\\Context and preferences\\Next steps and critical references};
\atstage{2}{
  \node[record, text width=5.2cm, minimum height=25mm] (tools) at (12.8,3.5) {\textbf{Retained tool state}\\State from the previous model\\Resume metadata};
  \draw[edge] (sum.east) -- (tools.west);
}
\atstage{3}{
  \draw[boundary] (1.0,0.5) rectangle (15.5,1.55);
  \node[caption] at (8.25,1.0) {Separate cross-session memories pipeline};
}
""")

add("delayed-order", ["8.1", "8.2", "9.2"], [
    "Place and pay for the order on Day 1.",
    "Observe an empty shelf on Days 2 and 3.",
    "Move the context boundary past the original order.",
    "Preserve the commitment until the Day 4 delivery check.",
], r"""
\draw[edge] (1.0,2.9) -- (15.6,2.9);
\foreach \x/\day in {1.7/1,6.0/2,10.3/3,14.6/4}{
  \fill[deckNavy] (\x,2.9) circle (0.07); \node[title] at (\x,3.4) {Day \day};
}
\node[record, text width=3.0cm] at (2.15,4.5) {10 units ordered\\Paid. Due Day 4.};
\atstage{2}{\node[record, text width=5.3cm] at (8.15,4.5) {Days 2--3: empty shelf, no sales};}
\atstage{3}{
  \draw[deckRose,dashed,line width=1.2pt] (4.2,0.8) -- (4.2,5.1);
  \node[caption,text=deckRose,anchor=west] at (4.4,2.2) {Compaction boundary};
}
\atstage{4}{
  \node[main, text width=7.3cm] (open) at (9.1,1.05) {\textbf{Open commitment}\\10 units, paid, expected Day 4};
  \node[card, text width=2.2cm] (check) at (14.6,1.05) {Confirm\\delivery};
  \draw[edge] (open.east) -- (check.west);
}
\node[caption,anchor=west] at (0.5,0.15) {Contrived Vending-Bench teaching case.};
""")

add("compaction-policy", ["9.1"], [
    "Specify the objective and trigger.",
    "Select the source material.",
    "Generate the replacement context.",
    "Check the preserved commitment and revise on failure.",
], r"""
\foreach \k/\x/\name/\text in {1/2.0/Specify/{Next decision\\Trigger},2/6.15/Select/{Keep\\Summarize\\Reference},3/10.3/Generate/{Facts\\Open items\\Sources},4/14.45/Check/{Order\\Payment\\Due date}}{
  \atstage{\k}{\node[main, text width=2.8cm, minimum height=23mm] (p\k) at (\x,3.4) {\textbf{\name}\\\text};}
}
\stepedge{2}{p1.east}{p2.west}
\stepedge{3}{p2.east}{p3.west}
\stepedge{4}{p3.east}{p4.west}
\atstage{4}{\draw[edge,dashed] (p4.south) -- (14.45,1.2) -- node[lab,below] {Failed check: revise selection or summary} (6.15,1.2) -- (p2.south);}
""")

add("replacement-check", ["9.3"], [
    "Show candidate A, which retains only the empty shelf.",
    "Reveal the duplicate-order failure.",
    "Add candidate B with the paid order, date, and source.",
], r"""
\node[record, text width=13.6cm] at (8.25,4.7) {\textbf{Source:} 10 units ordered and paid on Day 1. Delivery expected Day 4.};
\node[lost, text width=5.8cm] (a) at (4.1,3.1) {\textbf{Candidate A}\\SKU-A is out of stock.};
\atstage{2}{
  \node[lost, text width=5.8cm] (bad) at (4.1,1.25) {Places a second order\\Pays again};
  \draw[risk] (a.south) -- (bad.north);
}
\atstage{3}{
  \node[main, text width=5.8cm] (b) at (12.4,3.1) {\textbf{Candidate B}\\10 units, paid, due Day 4\\Source: \texttt{inventory-ledger}, Day 1};
  \node[card, text width=5.8cm] (ok) at (12.4,1.25) {Wait for the pending order\\Confirm delivery on Day 4};
  \draw[edge] (b.south) -- (ok.north);
}
""")

add("evaluation", ["10.1"], [
    "Check the next decision.",
    "Check the facts and source references.",
    "Check for changed meaning or unsupported additions.",
    "Measure original and replacement token counts.",
    "Count the complete run cost, including extra calls.",
], r"""
\node[record, text width=3.2cm] (src) at (2.0,4.4) {Original history};
\node[main, text width=3.2cm] (sum) at (8.25,4.4) {Replacement context};
\node[card, text width=3.2cm] (dec) at (14.5,4.4) {Next decision};
\draw[edge] (src.east) -- (sum.west); \draw[edge] (sum.east) -- (dec.west);
\foreach \k/\x/\name/\txt in {1/1.8/Success/{Correct action?},2/5.0/Evidence/{Order and source?},3/8.2/Faithfulness/{Meaning unchanged?},4/11.4/Compression/{Token counts?},5/14.6/Total work/{All calls and costs?}}{
  \atstage{\k}{\node[main, text width=2.5cm, minimum height=18mm] at (\x,2.0) {\textbf{\name}\\\txt};}
}
\node[caption] at (8.25,0.65) {Repeat with delayed delivery, date updates, fees, and repeated compaction.};
""")

add("stress-tests", ["10.2"], [
    "Carry the paid order through the first compaction.",
    "Add the recurring daily fee.",
    "Revise the delivery date from the source notice.",
    "Check the same commitments after another compaction.",
], r"""
\node[record, text width=3.5cm, minimum height=22mm] (src) at (2.3,3.6) {\textbf{Source records}\\Order paid\\Due Day 4};
\onlystage{1}{\node[main, text width=3.5cm, minimum height=22mm] (s1) at (8.1,3.6) {\textbf{Summary 1}\\Order paid\\Due Day 4};}
\onlystage{2}{\node[main, text width=3.5cm, minimum height=22mm] (s1) at (8.1,3.6) {\textbf{Summary 1}\\Order paid\\Due Day 4\\Daily fee};}
\atstage{3}{\node[main, text width=3.5cm, minimum height=22mm] (s1) at (8.1,3.6) {\textbf{Summary 1}\\Order paid\\Due Day 5\\Daily fee};}
\draw[edge] (src.east) -- (s1.west);
\atstage{2}{
  \node[record, text width=3.5cm] (fee) at (3.2,1.1) {Recurring daily fee};
  \draw[edge] (fee.north) -- (s1.south west);
}
\atstage{3}{
  \node[record, text width=4.5cm] (notice) at (9.2,1.1) {\textbf{Delivery notice}\\Revised date: Day 5};
  \draw[edge] (notice.north) -- (s1.south);
}
\atstage{4}{
  \node[main, text width=3.5cm, minimum height=22mm] (s2) at (14.0,3.6) {\textbf{Summary 2}\\Order paid\\Due Day 5\\Daily fee};
  \draw[edge] (s1.east) -- (s2.west);
}
\node[caption] at (8.25,0.2) {Contrived stress test. Check the commitments and their source references.};
""")

add("state-bridge", ["11.1"], [
    "Identify the context that survives compaction.",
    "Place it inside the execution state for next week.",
], r"""
\node[main, text width=5.5cm, minimum height=21mm] (ctx) at (4.0,3.0) {\textbf{Surviving context}\\Facts, decisions, open commitments};
\atstage{2}{
  \draw[boundary] (9.0,1.25) rectangle (16.0,4.65);
  \node[title] at (12.5,4.2) {Execution state};
  \node[record, text width=5.2cm, minimum height=17mm] (state) at (12.5,2.85) {Context to preserve\\Checkpoint and resume};
  \draw[edge] (ctx.east) -- (state.west);
}
\node[caption] at (8.25,0.6) {Next week: state ownership, checkpoints, resumption, and replay.};
""")


def run(command):
    subprocess.run(command, cwd=SRC, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*")
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    SRC.mkdir(parents=True, exist_ok=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    preamble = "\\input{" + Path(relpath(SHARED, SRC)).as_posix() + "}\n" + STYLE
    (SRC / "standalone-style.tex").write_text(preamble)
    manifest = []
    for fig in FIGURES:
        name = fig["name"]
        body = "\\begin{tikzpicture}\n\\canvas{16.5}{" + str(fig["height"]) + "}\n" + fig["body"] + "\n\\end{tikzpicture}\n"
        (SRC / f"{name}.tikz").write_text(body)
        stages = [f"{name}-{i}.png" for i in range(1, len(fig["steps"]) + 1)]
        manifest.append({
            "name": name, "topics": fig["topics"], "source": f"src/{name}.tikz",
            "canvas_cm": [16.5, fig["height"]], "stages": stages,
            "steps": fig["steps"], "takeaway": "Repeat the final figure state and reveal the takeaway.",
        })
        if args.source_only or (args.only and name not in args.only):
            continue
        dimensions = set()
        hashes = set()
        for i, image in enumerate(stages, 1):
            stem = f"{name}-{i}"
            wrapper = "\\def\\stage{" + str(i) + "}\n\\input{standalone-style.tex}\n\\begin{document}\n\\input{" + name + ".tikz}\n\\end{document}\n"
            tex = BUILD / f"{stem}.tex"
            tex.write_text(wrapper)
            try:
                run(["tectonic", "-Z", f"search-path={SRC}", "--keep-logs", "--outdir", str(BUILD), str(tex)])
            except subprocess.CalledProcessError as e:
                print(e.stdout.decode(errors="replace"))
                raise
            log = (BUILD / f"{stem}.log").read_text(errors="replace")
            if re.search(r"(?:Overfull|Missing character|^! )", log, re.M):
                raise RuntimeError(f"TeX text check failed: {stem}")
            run(["pdftoppm", "-r", "240", "-png", "-singlefile", str(BUILD / f"{stem}.pdf"), str(ROOT / stem)])
            data = (ROOT / image).read_bytes()
            dimensions.add(struct.unpack(">II", data[16:24]))
            digest = hashlib.sha256(data).hexdigest()
            if digest in hashes:
                raise RuntimeError(f"Unchanged stage: {stem}")
            hashes.add(digest)
        if len(dimensions) != 1:
            raise RuntimeError(f"Canvas changed between stages: {name}: {dimensions}")
        tiles = []
        for i in range(1, len(stages) + 1):
            x = 0.5 + ((i - 1) % 2) * 8.4
            y = -((i - 1) // 2) * 3.25
            pdf = (BUILD / f"{name}-{i}.pdf").as_posix()
            tiles.append(r"\node[anchor=north west,inner sep=0] at (" + f"{x},{y}" + r") {\includegraphics[width=8cm]{" + pdf + "}};")
            tiles.append(r"\node[font=\sffamily\bfseries\small,anchor=south west] at (" + f"{x},{y + 0.05}" + ") {" + f"Stage {i}" + "};")
        strip = "\\input{standalone-style.tex}\n\\begin{document}\n\\begin{tikzpicture}\n" + "\n".join(tiles) + "\n\\end{tikzpicture}\n\\end{document}\n"
        strip_tex = BUILD / f"{name}-steps.tex"
        strip_tex.write_text(strip)
        run(["tectonic", "-Z", f"search-path={SRC}", "--outdir", str(BUILD), str(strip_tex)])
        run(["pdftoppm", "-r", "140", "-png", "-singlefile", str(BUILD / f"{name}-steps.pdf"), str(ROOT / f"{name}-steps")])
        print(f"{name}: {len(stages)} distinct stages, fixed canvas {next(iter(dimensions))}", flush=True)
    (ROOT / "figures.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
