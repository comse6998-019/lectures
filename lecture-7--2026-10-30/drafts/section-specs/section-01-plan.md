# Section 1 plan: OpenShell through two access checks

Lecture 7 · November 6, 2026

**Status: complete plan proposed for instructor review.** The instructor has agreed to the teaching sequence below. Approval of this complete plan, the detailed spec, and the slides are separate steps.

## What this review decides

Review the objective, scope, teaching sequence, and proposed timing. Exact commands, policy excerpts, slide content, diagrams, and build instructions belong in the detailed spec after this plan is approved.

**Proposed section boundary:** use this continuous worked example for the first 42 minutes of Part I. It combines the overview's earlier components, policy, and live-demo sections. The instructor has removed the separate eight-minute HW2 responsibilities segment. Leave the remaining eight minutes available for questions or demo overrun as a working pacing proposal; the agreed first-half total remains 50 minutes.

## Purpose and starting point

Students implemented the triage workflow in HW1 and already know its Bandit, classification, patching, and answer-key rules. Use that familiarity to move quickly into OpenShell. Their attendance at Lecture 6 and their operating-system background vary. Rahul stopped a few slides after that lecture's policy discussion.

Begin with a brief host run of the existing `HW1-sol` and an answer-key read, then use the access to explain why and how we constrain the process doing that work. Introduce processes, files, connections, containers, and permissions as the example needs them. The HW1 workflow serves as the familiar baseline.

By the end, students should be able to:

- Connect the familiar HW1 agent's file operations, subprocesses, and model calls to the restrictions configured in OpenShell.
- Explain how a process can attempt an access outside the application's intended workflow.
- Locate the workload, image, running sandbox, runtime, supervisor, gateway, and kernel in the example.
- Read the relevant filesystem and network grants and predict the two probes' outcomes.
- Explain the evidence that the sandbox restricts access while the agent continues its assigned work.

## Instructor decisions preserved

- Assume minimal background in processes, containers, and operating-system permissions.
- Start with the existing `HW1-sol` directly. The instructor's latest feedback supersedes the earlier Cyberbird migration choice.
- Keep the host opening brief: students already know the HW1 workflow and answer-key withholding rule.
- Show the full Bandit → classify → patch loop on the host first, then inside OpenShell.
- Use the same small OWASP slice, including a true positive and a false positive.
- Anchor the OpenShell explanation in an answer-key read we want to restrict.
- Complete the filesystem example through policy and sandbox verification before moving to an unapproved network request.
- Use another model API provider as the proposed network destination. The exact provider remains open.
- Drop the separate eight-minute HW2 responsibilities segment.
- Present this lecture on November 6, 2026.

The [decision history](section-01-decisions.json) retains the answers verbatim. The sequence agreement covers these choices; the complete plan is awaiting review.

## Teaching sequence and proposed pacing

| Time | Teaching step | What students see and learn |
| --- | --- | --- |
| 0:00–0:02 | Familiar host baseline and access | Run `HW1-sol` on the small OWASP slice and show its report and patch. Make the direct answer-key read that anchors the OpenShell explanation. Treat both as familiar HW1 material and move directly to the access boundary. |
| 0:02–0:10 | OpenShell around the operation | Build the execution picture around that file read. Introduce the agent process and its children, the image and running sandbox, and the runtime's role in applying restrictions. Locate the kernel's filesystem enforcement. Locate the gateway and supervisor so students can distinguish setup from the handling of a running workload. |
| 0:10–0:17 | Filesystem policy | Read the small relevant portion of `policy.yaml`. Identify required code and runtime reads, writable workspace, and the answer key's exclusion. Explain how a broad directory grant could admit the key. Predict both an allowed read and the denied read. |
| 0:17–0:29 | Sandbox loop and file check | Show launch from the lecture demo image containing `HW1-sol`, its runtime, and installed dependencies; its build and verification happen during demo preparation before class. Repeat the complete agent loop on a fresh copy of the same slice and inspect its result. Run a direct file-read probe inside the sandbox. Compare the allowed operation and the answer-key denial with the host result. Tie the observations back to the policy and kernel. |
| 0:29–0:40 | Unapproved provider and network policy | Introduce a connection to another model provider as the next access to restrict. Compare an approved provider request with the unapproved destination using the same calling program. Extend the execution picture to the supervisor's network checks; read the relevant network rule and inspect the observed denial. Explain the role of provider credentials at the level needed to understand the request. |
| 0:40–0:42 | Consolidate the example | Return to the two accesses and identify the policy decision, enforcing component, and confirming evidence. Close Part I's worked example. |

**0:42–0:50: available time.** Proposed use: questions and demo overrun. There is no separate HW2 debrief in this interval.

**Argument carried by the example:** useful work has a concrete access footprint. We express the intended footprint in policy, locate its enforcement, and test both useful operations and prohibited accesses.

The filesystem example reaches its payoff before the network example starts. The architecture picture grows with the explanation. Its precise drawing and slide arrangement will be reviewed in the spec. The proposed pacing reduces the former nine-minute HW1 opening to two minutes and uses the seven minutes for filesystem policy, sandbox launch and checks, and network policy. Rehearsal will check that the host baseline fits.

## Evidence and preparation

Use the instructor's existing `HW1-sol` as the demonstration application. This exact two-case host/sandbox comparison still needs preparation and rehearsal.

**Image preparation is included in the implementation work for this lecture, after spec approval.** Build and verify a container image from `HW1-sol`, its runtime, and its required installed dependencies during that phase of this collaboration. Deliver the image, reproducible build instructions, and checked launch commands for the instructor to use in class. The image supplies the application environment; `policy.yaml` supplies the sandbox's access restrictions when the sandbox starts.

Prepare the small fixture and model endpoint before class. Reset the workspace between runs so students can compare equivalent starting points. Keep the answer-key teaching probe separate from the model's input.

The detailed spec and rehearsal must establish:

- The full loop completes on both runs, with inspectable classifications and a patch.
- The answer-key file exists and ordinary permissions permit the controlled read; the sandbox policy supplies the restriction being demonstrated. A successful allowed read supplies a second control.
- The probe runs directly inside the sandbox, so the class can distinguish an application-level refusal from the operating system's enforcement.
- The network comparison uses the same caller and isolates the destination change. Observations distinguish a policy denial from DNS, connectivity, or provider-authentication failure.
- Filesystem and network evidence are presented through their appropriate outputs. Historical course captures show filesystem denials through process errors and network denials through supervisor records.

Use the existing captures as preparation references. Capture this new example during rehearsal so an interruption in the live run has a faithful fallback. Mark any replayed output clearly. If time runs short, use the captured sandbox trace and trim secondary component detail while preserving both access checks.

## Scope and transition

Cover enough of OpenShell's component model, policy, launch, and credentials to explain the two access checks. Image construction and demonstration setup are preparation tasks. Their exact procedure belongs in the spec and supporting notes. Use `HW1-sol` directly throughout this example.

Connect the access examples to HW2 where relevant during the demonstration. The separate assignment-responsibilities debrief has been removed. Its coverage of per-alert MCP checks, CodeAct responsibilities, and submission artifacts is outside this section's planned teaching sequence. The brief remains the authority for those obligations.

After the break, Part II begins its separate literature-led discussion of context and compaction. State ownership, durable context, checkpointing, resumption, and replay remain next week's subject.

## Source anchors for the detailed spec

- [HW2 brief](../../../../hw2-tool-boundary/briefs/hw2.tex): fixed and per-alert restrictions; `policy.yaml`; direct staff probes; image and launch requirements. It originally promises a Cyberbird classroom run; the instructor has now selected `HW1-sol` for this demonstration. The brief remains the authority for assignment obligations.
- [Lecture 6 OpenShell guide](../../../lecture-6--2026-10-16/openshell/openshell-student-edition.html): the execution picture and the broad-versus-narrow answer-key example. Its source edition and historical run version are recorded in the guide.
- [HW2 feasibility results](../../../../instructor-materials/hw2/feasibility/results.md) and [Cyberbird captures](../../../../instructor-materials/hw2/feasibility/cyberbird/): historical observations for checking policy behavior and interpreting evidence. They establish prior tests on their recorded applications and versions; this `HW1-sol` demonstration still needs rehearsal.
- [Lecture overview](../lecture7-overview.md): approved broad lecture direction and half-lengths. Its original within-half section boundaries are superseded only if this proposal is approved.

## After plan review

Apply the instructor's annotations and record the plan decision. After plan approval, work together on a separate Markdown spec, beginning with the host opening and answer-key example. Review that complete spec separately in Plannotator before producing slides.

[Plan and spec register](README.md)
