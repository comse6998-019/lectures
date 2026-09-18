# Week 2 / Unit 1 — Half II: What connects the steps?

**Course:** COMS E6998-019 — Design of Production Agentic Systems  
**Meeting:** September 18, 2026  
**Scope:** The first 30 minutes of Half II / Block B, after the break  
**Companion:** [Half I plan](/Users/rkrsn/COMSE6998-019/lectures/lecture-2--2026-09-18/lec1-plan.md)  
**Status:** Teaching plan; code and traces are preparation tasks.

The remaining 20-minute homework/domain segment is reserved for a separate document.

## 1. Purpose and teaching order

Half I introduced architectural mechanisms and showed a serial agent built up through a reactive loop, planning, validation, and reflection. Half II explains the execution machinery that connects those steps.

Follow the syllabus's execution concepts in order:

1. State schema and transitions.
2. Conditional routing and feedback loops.
3. Termination and observed outcomes.
4. Tool signatures and the dispatch cycle.
5. Execution authority.

**Each block is content-first:** introduce the concept and why it matters, then inspect the corresponding code in the existing agent, then use a selected execution or trajectory to make it concrete.

Use the same investigation and the same `read_file` and `search` tools from Half I. V1's brief preview of state, signatures, dispatch, routing, and terminal statuses becomes a sustained explanation here. The final serial graph supplies the planning/validation/reflection examples.

By the end, students should be able to identify the state connecting two steps, explain why an edge was taken, trace a requested action to actual execution, and name the component that enforces a stopping or execution rule.

## 2. Timing

Times are relative to the start of Half II.

| Time | Duration | Block | Content first | Then code and demonstration |
| --- | ---: | --- | --- | --- |
| 0–7 | 7 min | State schema and transitions | 4 min: typed records, transitions, reducers, and context/state/durability. | 3 min: a worked investigation schema and one before/after state update. |
| 7–13 | 6 min | Conditional routing and feedback loops | 3 min: executable decisions over state, back edges, and exit predicates. | 3 min: the agent's routing functions and two different returns to the planner. |
| 13–18 | 5 min | Termination and observed outcomes | 3 min: completion, declared stopping, and absence of a terminal event. | 2 min: three short trace excerpts and the predicates behind the declared endings. |
| 18–25 | 7 min | Tool signatures and dispatch | 3 min: contracts, schemas, effects, and the request/result boundary. | 4 min: one native tool request followed through actual local execution. |
| 25–30 | 5 min | Execution authority | 2 min: proposal versus execution; decision timing versus ownership. | 3 min: a deliberately invalid request refused by the dispatcher. |

## 3. State schema and transitions — 7 minutes

Open with AIMA §2.4.7's three state representations, atomic, factored, and structured, moved here from Part A's Section 1 on September 16: the instance's result is atomic, the state record is factored (which is what makes one reducer per field and mechanical validation over named fields possible), and a patch or a test failure is structured. Draft text is parked in `notes/sections/deferred/state-representations.tex`.

### Content first: what connects one step to the next?

Introduce state as the runtime's structured record of the investigation. A typed schema describes the fields and their intended values. Runtime validation is a separate mechanism: Python's `TypedDict` annotations do not themselves check incoming data.

Use this conceptual transition:

```text
current state + observed input/event → update → next state
```

“Input” here includes a model response or tool observation, as well as the initial task. Explain the implementation in two parts: a node produces an update; the runtime applies that update to the current state using the field's update rule. External/model results are explicit inputs to the transition, rather than assumed deterministic consequences of the previous state.

**Reducers** specify how a field incorporates an update. An append rule retains previous entries and adds new ones; replacement installs the new value. This choice determines what a later step can see.

Keep three terms distinct:

| Term | Meaning in this class |
| --- | --- |
| Model context | The instructions, selected history, observations, and other material supplied to a particular model invocation. |
| Runtime state | The record the controller maintains between steps, including fields that need not enter every model call. |
| Durable state | State persisted in a form that can survive process termination and support recovery. |

Recall Lecture 1's process-kill question. It tests durability: in-memory state is still state even if the process loses it on termination. Persistence and recovery receive their fuller treatment in the later course units.

**Grounding:** AIMA §§2.1 and 2.4 connect observations, agent programs, and internal state. LangGraph's State, Schema, and Reducers sections provide the implementation reference; see the reading map below.

### Then the demo: the investigation record

Show the corresponding fields in the prepared agent. The names below describe their roles; align the displayed names with the actual implementation.

| Field or group | What it holds | Update policy to explain |
| --- | --- | --- |
| Task and repository identity | The input being investigated and its source version. | Retain throughout the investigation. |
| Current plan and progress | Intended subgoals and their current status. | Replace with an updated snapshot. |
| Tool observations | Recorded results from source searches and reads. | Append within an attempt. |
| Evidence references | Source locations supporting investigation claims. | Append or merge using an explicitly defined rule. |
| Candidate finding | The current proposed assessment and explanation. | Replace. |
| Validation | The latest acceptance decision and reasons. | Replace. |
| Reflections | Guidance retained from unsuccessful attempts. | Append across attempts. |
| Attempt and step counters | Execution progress used by routing and stopping rules. | Update explicitly under runtime control. |
| Usage ledger | Per-call usage records. | Append; preserve accounting across attempt resets. |
| Terminal outcome and reason | The declared result of ending the run, when one exists. | Set when the runtime records termination. |

Demonstrate one tool result becoming an observation and evidence reference. Put these three views side by side:

1. State before the tool result.
2. The node's update and the resulting state.
3. The next model input assembled from that state.

Point out a runtime field, such as an attempt counter, that the model need not receive verbatim. State and context have different purposes even when much of their content overlaps.

Use the reflection reset to explain one reducer trap: appending an empty list does not clear accumulated observations. The new attempt must explicitly start with fresh attempt-local fields while retaining reflections, identity, and overall accounting. Archived traces remain available separately.

**Check for understanding:** Which record changes after a tool call, and which part of that record is actually sent to the next model invocation?

## 4. Conditional routing and feedback loops — 6 minutes

### Content first: routing is executable logic over state

A routing function inspects state and selects the next node. Predicates implement its branches. A prompt can influence values produced by a model, but runtime code interprets those values and takes an edge.

Separate three responsibilities:

- A model may propose a tool action, plan, finding, or validation judgment.
- The runtime records the relevant result in state.
- A routing function applies the permitted transition rules and execution limits.

Loops are back edges. Each needs an exit predicate, and the system needs a mechanism that makes stopping enforceable. An acceptance condition alone does not ensure eventual acceptance; the demo's attempt and overall execution limits bound further work.

**Dynamic execution paths need not change the graph definition.** Different state values can select different paths through the same graph.

### Then the demo: inspect the actual conditional edges

Start with the baseline's decision to execute a requested tool or submit a finding. Then open the validator route:

| Relevant state | Next action |
| --- | --- |
| Candidate accepted under the configured checks | Record completion and return the finding. |
| Candidate rejected; another attempt is permitted | Run reflection, retain guidance, initialize a fresh attempt, and invoke the planner. |
| Candidate rejected; another attempt is not permitted | Record a declared unresolved stop. |

Show that the router is executable code and does not require a separate model call to interpret its own control rules.

The current Half I plan also contains an in-run return to the planner after a planned step fails. Use the prepared fault trace to distinguish it from the outer reflection loop:

| Return to planner | Trigger | State treatment |
| --- | --- | --- |
| In-run plan revision | A planned step remains unsuccessful after the configured runtime retry. | Retain the current attempt's observations and progress; provide the failed subgoal and error to the planner. |
| New attempt after reflection | The validator rejects an attempt and the runtime allows another. | Retain reflective guidance and overall accounting; reset attempt-local plan, observations, and candidate. |

In the fault trace, identify the runtime-owned retry and the later model-proposed plan revision. Detailed retry/backoff/idempotency policy belongs to the later reliability material; here it illustrates component ownership.

**Check for understanding:** Which state values explain this back edge, and what stops it from being taken again?

## 5. Termination and observed outcomes — 5 minutes

### Content first: two declared endings and one incomplete observation

Teach three cases without treating all three as terminal states:

| What the trace establishes | Interpretation |
| --- | --- |
| A verdict was reached and completion was recorded | A completed assessment under the runtime's acceptance rules. |
| A stop and its reason were recorded | A declared end to execution without completing the intended assessment. |
| No terminal event was observed | Completion has not been established by the available trace. |

The third case is not automatically `error`. The run might still be active, have been interrupted, or have an incomplete trace. An observed exception is additional evidence; the absence of a terminal event alone does not identify its cause.

Errors and terminal outcomes are also distinct. A recoverable tool error can occur during a run that later completes successfully. Conversely, a process can disappear before it records a terminal outcome.

Keep the finding separate from execution status. For example, `Other: insufficient information` can be a completed assessment. A declared resource stop can instead carry partial evidence without a completed finding.

Termination is determined by predicates the runtime evaluates. A model's statement that it is finished supplies a proposed result; the controller applies the application's completion rules and records the outcome. Reaching a framework `END` node alone does not explain whether the application completed its task or stopped for another reason.

Signpost Week 3: stopping conditions and token-budget admission/accounting will receive their detailed treatment there.

### Then the demo: inspect three trace excerpts

Prepare excerpts showing:

1. An accepted finding followed by a completion event.
2. A declared stop caused by the attempt or execution limit, with its reason and available evidence.
3. A deliberately interrupted or truncated trace with no observed terminal event; label how the excerpt was produced.

For the first two, point to the predicate and code that recorded the outcome. For the third, state only what is supported by the available record. Do not label an actually unfinished run as a successful or declared-stopped run.

Use the existing trace conventions and retain distinct token-usage categories. Detailed token arithmetic is outside this block.

**Check for understanding:** Does this trace establish an accepted finding, a declared stop, or only that no terminal event was observed?

## 6. Tool signatures and the dispatch cycle — 7 minutes

### Content first: a tool contract spans description and execution

Use **tool contract** for the complete specification:

- Tool name and purpose.
- Typed arguments and their constraints.
- Typed success result and error representation.
- Side-effect class, such as read-only source inspection.
- Execution constraints, such as the permitted repository root.

The model-facing definition commonly includes a name, description, and argument schema. The result type and effect policy may be specified and enforced in runtime code rather than represented as first-class fields in a provider's tool definition.

The model sees the tool description and requests an operation. Its response does not itself establish that any tool ran.

Trace the complete local cycle:

```text
Model tool request
    → parse and validate arguments
    → check execution policy
    → dispatch to the registered implementation
    → obtain and validate/normalize the result or error
    → record the observation and update state
    → construct the next model input
```

Distinguish an invalid or refused request from a permitted invocation that returns a tool error. Both can be represented as observations, but they describe different events.

**Research connection:** SWE-agent studies the action/observation interface and its effect on agent behavior. Use that paper for interface motivation; use the native tool-use documentation for this specific request/result protocol.

### Then the demo: what the model saw versus what ran

Use one `read_file` call from the existing investigation. Show these artifacts in order:

| View | What to point out |
| --- | --- |
| Model input | Tool definition and currently supplied evidence. |
| Model response | The actual tool-request ID, name, and arguments. |
| Dispatcher | Name resolution, argument checks, and repository/effect policy checks. |
| Local implementation | The Python function actually invoked, with the validated arguments. |
| Result | Returned source excerpt or tool error, tied to that request. |
| State and next model input | Where the observation is retained and how the next invocation receives it. |

Use the provider's actual request/result representation in the demonstration, and explain any application normalization between that representation and the runtime's internal record.

The demonstration remains sequential. If the model requests several actions in one response, the dispatcher must follow the demo's explicit sequential policy.

**Check for understanding:** Which artifact proves that the function was invoked, and which artifact only records that the model requested it?

## 7. Execution authority — 5 minutes

### Content first: locate the guarantee

State the invariant:

> The model proposes. The runtime controls execution. The runtime may refuse.

Distinguish two dimensions:

1. **Decision timing and ownership:** some choices are prescribed by the programmer; others are deferred to model output during execution. Programmer-written routing and policy code also runs at run time, so decision timing does not by itself identify who chose the policy.
2. **Proposal versus execution:** a requested action or suggested stopping decision becomes effective only through the runtime's execution path.

The runtime's controls must sit on the path that every relevant request traverses. A prompt instruction or a log message does not enforce the boundary.

Use specific component ownership:

| Guarantee | Enforcing component in the demo |
| --- | --- |
| Only registered tools can run | Dispatcher/tool registry. |
| Arguments and paths satisfy the contract | Argument validator and tool access checks before the operation. |
| Source-inspection tools are read-only | Tool implementations and the permissions under which they execute. |
| An exhausted execution allowance prevents another model invocation | Controller's pre-call check. |
| A back edge obeys attempt limits | Runtime routing and attempt accounting. |

The model can propose values relevant to these decisions. It does not gain authority to bypass the enforcing code by describing an action as safe or claiming that it has already run.

### Then the demo: a refused request

Feed the dispatcher a deliberately prepared request for an unregistered tool, or a `read_file` request outside the permitted fixture root. Label it as a constructed request used to exercise the boundary.

Show:

1. The requested operation.
2. The executable policy check that refuses it.
3. The refusal observation recorded in the trace/state.
4. Evidence from the instrumented invocation boundary that the requested operation was not invoked.

Pair it with an allowed request so students can locate the branch leading to actual execution. This avoids relying on the model to spontaneously make a particular invalid request.

Finish with the ownership question:

> If the model requests a forbidden action, which component prevents it from running, and where can we see that guarantee in the implementation?

## 8. Reading and note-writing map

| Source | Selection | Role in this segment |
| --- | --- | --- |
| Russell and Norvig, *AIMA*, fourth edition | §§2.1 and 2.4 | Agent–environment interaction, agent programs, and internal state. Revisit the concepts grounded in Half I. |
| Yang et al., *SWE-agent: Agent-Computer Interfaces Enable Automated Software Engineering*, NeurIPS 2024 | §§2–3 and Figure 3 | Research grounding for usable actions, observations, and tool-interface design. |
| LangGraph Graph API | State, Schema, Reducers, Conditional edges, and END | Implementation reference for the existing demo's mechanics. |
| Native tool-use documentation | One complete client-tool request/result cycle | Exact representation of what the model emits and what the application executes. |
| Python typing documentation | `TypedDict` | Clarify the difference between a declared type and runtime validation. |
| LangGraph persistence documentation | Opening explanation of checkpoints and storage | Instructor reference for the state/durability distinction. |

The detailed notes should define each concept before showing code, include the worked state record and dispatch sequence, and annotate the selected traces. Treat framework/provider method names as implementation references; the study objectives are the transitions, contracts, outcomes, and ownership they implement.

Academic references explain the agent and interface concepts. Framework documentation supports the concrete implementation. The runtime guarantees in this plan must be demonstrated by the prepared code and traces.

## 9. Preparation checklist

- Prepare the existing agent's state schema, one node update, the reducer application, and the resulting next model input.
- Identify the baseline routing function and the two distinct returns to the planner: in-run revision and a fresh attempt after reflection.
- Select the completion, declared-stop, and no-terminal-event trace excerpts, with their provenance.
- Capture one complete native `read_file` request/result cycle through the local dispatcher.
- Prepare the explicitly constructed refused request and the allowed-request comparison at the same invocation boundary.
- Rehearse the five blocks at 7 / 6 / 5 / 7 / 5 minutes, keeping conceptual explanation ahead of code inspection.

## Sources

- [AIMA, fourth-edition contents](https://aima.cs.berkeley.edu/contents.html).
- [SWE-agent, NeurIPS 2024 paper](https://proceedings.neurips.cc/paper_files/paper/2024/file/5a7c947568c1b1328ccc5230172e1e7c-Paper-Conference.pdf).
- [LangGraph Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api).
- [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence).
- [Native tool use with Claude](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview).
- [Python typing: TypedDict](https://docs.python.org/3/library/typing.html#typing.TypedDict).
