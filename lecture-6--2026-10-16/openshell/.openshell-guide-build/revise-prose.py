from pathlib import Path
root=Path('.openshell-guide-build')
changes={
'foundations.html':{
'Build the foundations':'Processes, authority, and isolation',
'Locate the trust boundaries':'Architecture and trust boundaries',
'Read the repository as a system':'Source structure and interface contracts',
'Learn the words before the architecture':'Processes and operating-system resources',
'Separate intelligence, authority, and execution':'Action selection, authority, and execution',
'Understand what expertise requires':'Scope and evidence',
'Distinguish the three planes':'Control, data, and infrastructure',
'Step through one request':'A mediated network request',
'Know the deployment exception':'The Windows deployment exception',
'Recognize the Rust shapes':'Rust types and concurrency',
'Read a feature in five passes':'Tracing an operation across components',
'Understand the message contracts':'Public and private message contracts',
'OpenShell gives an agent a place to run and controls the authority available to its programs.':'OpenShell provides execution environments in which policy limits the authority of workload programs.',
'An AI agent combines a model with a program that can take actions. The model can choose a command, but an ordinary process runs that command. A coding agent can start a shell, run Python, read a repository, install a package, or call an API. These actions eventually reach the operating system.':'An AI agent combines a model with a program that can perform actions. The model selects a command; a process executes it. Starting a shell, running Python, reading a repository, installing a package, and calling an API all require operations that the operating system controls.',
'OpenShell operates at that boundary. A policy declares permitted access. Runtime components enforce that access. Management components create environments, distribute configuration, store state, and connect users to workloads.':'OpenShell separates the declaration of authority from its enforcement. A policy declares permitted access. Runtime components enforce that access, while management components create environments, distribute configuration, store state, and connect users to workloads.',
'A <strong>workload</strong> is the program or collection of programs that runs inside that environment. A shell is a workload. An agent and all its subprocesses are also a workload. OpenShell can run useful programs without an AI model.':'A <strong>workload</strong> is a program, or collection of programs, running in an execution environment. A shell is a workload; an agent together with its subprocesses is another. OpenShell therefore applies to ordinary programs as well as model-driven agents.',
'The model selects actions. Policy defines permitted authority. The runtime executes actions within that authority. These responsibilities remain distinct even when the same agent helps draft a policy change.':'Action selection and authorization are distinct operations. A model selects an action, policy specifies the permitted authority, and the runtime executes the action subject to that authority. An agent that proposes a policy change does not thereby acquire the authority to approve it.',
'Consider a coding task: read a project, edit a function, run tests, and send a patch to GitHub. The agent needs filesystem writes, child processes, and selected network access. The provider credential also needs a destination boundary. Each requirement belongs to a different part of the system.':'For example, a coding task may require reading a project, editing a function, running tests, and sending a patch to GitHub. The corresponding authority includes filesystem access, process creation, and selected network access. An attached provider credential also has an endpoint binding. These requirements belong to different enforcement mechanisms.',
'A useful design question':'The unit of analysis',
'For each action, identify the actor, requested resource, enforcing component, and evidence of the decision. This question works at every depth of the repository.':'An access decision has an actor, a requested resource, an enforcing component, and evidence on which the decision depends. Identifying these elements relates the architecture to individual code paths.',
'A container supplies part of the isolation boundary. OpenShell adds workload policy, mediated networking, provider credentials, lifecycle management, and review workflows. The exact boundary depends on the selected compute driver.':'Container isolation supplies part of the boundary. OpenShell adds workload policy, mediated networking, provider credentials, lifecycle management, and policy-review workflows. The resulting boundary depends on the selected compute driver.',
'Reading this document builds a source-backed mental model. The exercises test whether you can predict behavior. The labs connect predictions to observations. Operational expertise also requires practice with your deployment, identity system, network, and failure modes.':'The source code establishes how the studied revision implements these mechanisms. The exercises require predictions from that model; the experiments describe observations that can test those predictions. Operational conclusions also depend on the deployment, identity system, network, and failure conditions.',
"By the end, you can explain a sandbox's creation, trace a blocked request, distinguish policy analysis from runtime enforcement, and locate the responsible code. You can also identify assumptions that a claim depends on.":"The account develops four recurring questions: how a sandbox becomes usable, why a request is permitted or denied, what a policy analysis establishes, and which component owns a behavior. Each answer must retain the assumptions under which it holds.",
'This edition describes commit <code>be7af99ff2eacba807d82b69adb0c3d4eaa32158</code>, studied on October 5, 2026. Source links pin that revision. Commands illustrate that checkout. Use matching installed CLI help before doing a lab against a different release.':'This edition describes commit <code>be7af99ff2eacba807d82b69adb0c3d4eaa32158</code>, studied on October 5, 2026. Source links and command examples refer to that revision. Commands for another release require comparison with its installed CLI help.',
'Follow an operation across ownership boundaries. Then study the implementation within each boundary.':'An operation crosses several component interfaces. Those interfaces identify the responsibilities that its implementation must preserve.',
'A comment explains intended behavior. A function shows implemented behavior. A test records an expected behavior under its fixture. All three help, but each answers a different question.':'Comments, implementation, and tests provide different kinds of evidence. A comment states intent. A function defines a code path. A test states an expected result under a particular fixture. Agreement among them supports an explanation; disagreement requires examination of the current call path.',
'A good diagnosis identifies the failing boundary before changing permissions.':'Diagnosis therefore begins by identifying the failing boundary.',
'For creation, begin at <code>sandbox_create</code> in the CLI. Continue through the gateway handler and <code>ComputeRuntime</code>. Then read the selected driver\'s provisioning path. The supervisor startup code explains what happens after provisioning.':'The creation path begins at <code>sandbox_create</code> in the CLI and continues through the gateway handler, <code>ComputeRuntime</code>, and the selected driver. Supervisor startup follows provisioning.',
'For an outgoing request, begin at the sandbox network broker. Continue through identity resolution, supervisor admission, request inspection, and upstream relay. These paths explain where a change belongs.':'The outgoing-request path passes through the sandbox network broker, identity resolution, supervisor admission, request inspection, and upstream relay. The component that owns a decision determines where a change to that decision belongs.'},
'practice.html':{
'Use clients and interpret observations':'Clients, operations, and observations',
'Diagnose by the failing boundary':'Diagnosis by enforcement boundary',
'Practice with controlled labs':'Controlled experiments',
'Demonstrate expert reasoning':'Exercises on system behavior',
'Keep the vocabulary precise':'Glossary',
'Choose the correct client layer':'Client implementations',
'Respect durable admission and uncertain outcomes':'Durable admission and uncertain outcomes',
'Distinguish connect, exec, and forwarding':'Connection, execution, and forwarding',
'Distinguish three observation channels':'Observation channels',
'Handle observation loss':'Observation loss',
'Use a boundary-first sequence':'A diagnostic procedure',
'Explore a small policy model':'A simplified admission model',
'Use a source-study routine':'Reasoning from invariants and tests',
'Client APIs express intentions. Status, streams, and logs provide different evidence about their outcomes.':'Client APIs request operations. Status, streams, and logs provide distinct evidence about the resulting state.',
'A practical application creates a sandbox, waits for readiness, runs work, collects a terminal result, and requests cleanup. Each step can fail separately.':'A typical client creates a sandbox, waits for readiness, starts work, collects a terminal result, and requests cleanup. Each operation has its own failure conditions.',
'What it tells you':'Evidence supplied',
'What to avoid inferring':'Unsupported inference',
'A failed request is evidence to classify before it is a reason to widen policy.':'A failed request identifies an unresolved condition. It does not, by itself, establish that policy is too restrictive.',
'Consider a tool that reports a timeout. The failure can occur before provisioning, during DNS, at connection admission, during TLS, in HTTP policy, during credential substitution, or at the upstream service. The same user-facing symptom can hide different causes.':'A timeout can arise before provisioning completes, during DNS, at connection admission, during TLS, in HTTP policy, during credential substitution, or at the upstream service. The reported symptom therefore underdetermines the cause. Diagnosis requires evidence from the relevant boundary.',
'This illustration models one REST endpoint with a read-only rule and an optional provider credential. It does not parse or execute OpenShell policy. It omits overlapping rules, executable ancestry, address restrictions, and protocol errors.':'The following model represents one REST endpoint, a read-only request rule, and an optional provider credential. It illustrates the separation of checks. It neither parses nor executes OpenShell policy and omits overlapping rules, executable ancestry, address restrictions, and protocol errors.',
'Predict admission for one illustrative request':'Admission for an illustrative request',
'A useful experiment is to select POST and switch between enforce and audit. Then change the destination. Audit changes the request-level outcome; it does not grant a previously forbidden destination.':'For POST, changing the request mode from enforce to audit changes rejection into an allowed request with an audit violation. Changing the destination to an unapproved host still produces denial. Request-level audit does not grant destination access.',
'Predict the outcome, run one experiment, and compare the observation with the responsible code.':'A controlled experiment compares a predicted result with an observation under stated conditions.',
'These labs are instructions for your own practice. They were not executed while preparing this document. The source-reading and standalone prover labs work without a running sandbox fleet. Runtime labs require a working gateway and a workload image with Bash and curl.':'The experiments below are procedures, not reported results: they were not executed during this source study. Source tracing and standalone prover checks do not require a running sandbox fleet. Runtime experiments require a working gateway and a workload image containing Bash and curl.',
'Lab A: trace creation without starting infrastructure':'Experiment A: creation and durable state',
'Lab B: observe deny, allow, and request-level enforcement':'Experiment B: network admission and request enforcement',
'Lab C: find a formal counterexample locally':'Experiment C: a policy-containment counterexample',
'Lab D: follow one real regression test':'Experiment D: socket identity in a regression test',
'Lab A answer:':'Exercise A.',
'Lab B answer:':'Exercise B.',
'Lab sources:':'Experiment sources:',
'Expertise shows up in precise predictions, bounded claims, and the ability to locate evidence.':'The following cases test whether the system model supports precise predictions and appropriately limited conclusions.',
'Answer these scenarios before revealing the explanations. For each answer, name the boundary, the evidence, and the limitation. A correct component name alone is not enough.':'For each case, identify the responsible boundary, the supporting evidence, and the limit of the conclusion. The explanations are concealed until the question is expanded.',
'Has it earned permission to connect?':'Does that establish permission to connect?',
'Pick one invariant, such as “unapproved TCP opens never reach an upstream server.” Write its responsible components and assumptions. Follow the failure path as carefully as the successful path. Then inspect tests for races, retries, and invalid identities.':'An invariant states a property that must hold under specified assumptions. For example, a claim that unapproved TCP connections cannot reach an upstream server depends on the broker, supervisor, and surrounding isolation. Its justification must cover failure paths as well as successful paths. Tests for races, retries, and invalid identities help examine those assumptions.',
'For a proposed change, identify its owner: schema, gateway admission, driver provisioning, isolation backend, supervisor policy, or client behavior. List the other contracts affected by that change. Public protobuf fields, persisted payloads, policy semantics, and SDK behavior can outlive an individual process.':'A change has an owning component: schema, gateway admission, driver provisioning, isolation backend, supervisor policy, or client implementation. It may also affect contracts owned elsewhere. Public protobuf fields, persisted payloads, policy semantics, and SDK behavior can outlive an individual process.',
'Run the narrow relevant checks first. The repository uses <code>mise</code> to define repeatable tasks. Unit tests exercise local logic. Integration tests connect components. End-to-end and conformance tests exercise deployed or installed systems across drivers.':'The repository defines repeatable checks through <code>mise</code>. Unit tests exercise local logic; integration tests exercise interactions among components. End-to-end and conformance tests examine deployed or installed systems across drivers. The relevant check depends on the contract affected by a change.',
'Use the same term for the same responsibility.':'The terms below retain the meanings used throughout this account.',
'A policy ecosystem, its policy language, and the embedded Rust evaluator used for OpenShell network policy.':'A policy system, its policy language, and the embedded Rust evaluator used for OpenShell network policy.'}}
for name,replacements in changes.items():
 p=root/name;s=p.read_text()
 for old,new in replacements.items():
  if old not in s: raise SystemExit(f'Missing {name}: {old}')
  s=s.replace(old,new)
 s=s.replace('Check your understanding:', 'Exercise.')
 s=s.replace('<p class="sources">Read ', '<p class="sources">Sources: ')
 s=s.replace('<p class="sources">Start with ', '<p class="sources">Sources: ')
 s=s.replace('<p class="sources">Compare ', '<p class="sources">Sources: ')
 p.write_text(s)
